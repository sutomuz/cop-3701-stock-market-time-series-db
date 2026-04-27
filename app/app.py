"""
Stock database explorer — Tkinter front end for Oracle queries.
Run from project root: python app/app.py
"""

from __future__ import annotations

import threading
import tkinter as tk
from datetime import date, datetime
from decimal import Decimal
from tkinter import ttk

from db import close_connection, execute_query, fetch_single_column

SQL_DISTINCT_CATEGORIES = (
    "SELECT DISTINCT category_name FROM category "
    "WHERE category_name IS NOT NULL ORDER BY category_name"
)

SQL_DISTINCT_COUNTRIES = (
    "SELECT DISTINCT country FROM symbol_profile "
    "WHERE country IS NOT NULL ORDER BY country"
)

SQL_DISTINCT_EXCHANGES = (
    "SELECT DISTINCT exchange FROM symbol "
    "WHERE exchange IS NOT NULL ORDER BY exchange"
)

SQL_BY_CATEGORY = """
SELECT s.symbol_id, s.ticker, s.name, s.exchange, c.category_name, c.category_type
FROM symbol s
JOIN symbol_category sc ON s.symbol_id = sc.symbol_id
JOIN category c ON sc.category_id = c.category_id
WHERE UPPER(c.category_name) = UPPER(:category_name)
ORDER BY s.ticker
"""

SQL_BY_COUNTRY = """
SELECT s.ticker, s.name, s.exchange, p.country, p.currency, p.description
FROM symbol s
JOIN symbol_profile p ON s.symbol_id = p.symbol_id
WHERE UPPER(p.country) = UPPER(:country)
  AND (:exchange IS NULL OR UPPER(s.exchange) = UPPER(:exchange))
ORDER BY s.ticker
"""

SQL_RANGE_DAYS = """
SELECT s.ticker, d.trade_date, d.open, d.high, d.low, d.close,
       (d.high - d.low) / NULLIF(d.open, 0) AS range_vs_open
FROM symbol s
JOIN daily_price d ON s.symbol_id = d.symbol_id
WHERE d.trade_date BETWEEN :start_date AND :end_date
  AND (d.high - d.low) / NULLIF(d.open, 0) >= :min_range
ORDER BY range_vs_open DESC, d.trade_date DESC
"""

SQL_CATEGORY_HISTORY = """
SELECT s.ticker, s.name, c.category_name, c.category_type, sc.assigned_date
FROM symbol s
JOIN symbol_category sc ON s.symbol_id = sc.symbol_id
JOIN category c ON sc.category_id = c.category_id
WHERE UPPER(s.ticker) = UPPER(:ticker)
ORDER BY sc.assigned_date DESC, c.category_name
"""

SQL_VOLUME_LEADERS = """
SELECT s.ticker, s.name,
       SUM(d.volume) AS total_volume,
       COUNT(*) AS num_days
FROM symbol s
JOIN daily_price d ON s.symbol_id = d.symbol_id
WHERE d.trade_date BETWEEN :start_date AND :end_date
GROUP BY s.symbol_id, s.ticker, s.name
HAVING SUM(NVL(d.volume, 0)) > 0
ORDER BY total_volume DESC
FETCH FIRST :top_n ROWS ONLY
"""


def format_cell(value) -> str:
    if value is None:
        return ""
    if isinstance(value, datetime):
        return value.strftime("%Y-%m-%d %H:%M:%S")
    if isinstance(value, date):
        return value.strftime("%Y-%m-%d")
    if isinstance(value, Decimal):
        f = float(value)
        if f == int(f):
            return str(int(f))
        return f"{f:.6g}"
    if isinstance(value, float):
        if value == int(value):
            return str(int(value))
        return f"{value:.6g}"
    return str(value)


def parse_date(s: str) -> date:
    s = s.strip()
    try:
        return datetime.strptime(s, "%Y-%m-%d").date()
    except ValueError as exc:
        raise ValueError("Use dates in YYYY-MM-DD form.") from exc


class StockExplorerApp:
    def __init__(self) -> None:
        self.root = tk.Tk()
        self.root.title("Stock database explorer")
        self.root.minsize(720, 480)

        style = ttk.Style()
        if "clam" in style.theme_names():
            style.theme_use("clam")

        self._field_vars: dict[str, tk.StringVar] = {}
        self._field_widgets: dict[str, ttk.Widget] = {}
        self._input_container: ttk.Frame | None = None
        self._busy = False

        # Cached dropdown values; None = not loaded yet, [] = load failed/empty.
        self._categories: list[str] | None = None
        self._countries: list[str] | None = None
        self._exchanges: list[str] | None = None

        self._build_ui()
        self._load_dropdown_values()

    def _build_ui(self) -> None:
        main = ttk.Frame(self.root, padding=10)
        main.pack(fill=tk.BOTH, expand=True)

        ttk.Label(main, text="Stock database explorer", font=("", 14, "bold")).pack(
            anchor=tk.W
        )
        ttk.Label(
            main,
            text="Pick a report, fill in the fields, then click Run query.",
        ).pack(anchor=tk.W, pady=(0, 8))

        row1 = ttk.Frame(main)
        row1.pack(fill=tk.X, pady=(0, 8))
        ttk.Label(row1, text="Feature:").pack(side=tk.LEFT, padx=(0, 8))
        self.feature_var = tk.StringVar()
        self.feature_keys = [
            "category",
            "country",
            "range_days",
            "history",
            "volume",
        ]
        self.feature_labels = {
            "category": "Stocks in a category",
            "country": "Stocks by country (optional exchange)",
            "range_days": "Days with a wide high–low range",
            "history": "Category history for one stock",
            "volume": "Busiest stocks by total volume",
        }
        combo = ttk.Combobox(
            row1,
            textvariable=self.feature_var,
            values=[self.feature_labels[k] for k in self.feature_keys],
            state="readonly",
            width=48,
        )
        combo.pack(side=tk.LEFT)
        combo.bind("<<ComboboxSelected>>", lambda _e: self._rebuild_inputs())
        self.feature_combo = combo
        self.feature_var.set(self.feature_labels[self.feature_keys[0]])

        self._input_container = ttk.LabelFrame(main, text="Inputs", padding=8)
        self._input_container.pack(fill=tk.X, pady=(0, 8))
        self._rebuild_inputs()

        btn_row = ttk.Frame(main)
        btn_row.pack(fill=tk.X, pady=(0, 4))
        self.run_btn = ttk.Button(
            btn_row, text="Run query", command=self._on_run)
        self.run_btn.pack(side=tk.LEFT)

        self.status_var = tk.StringVar(value="Ready.")
        ttk.Label(main, textvariable=self.status_var, foreground="#333").pack(
            anchor=tk.W, pady=(4, 8)
        )

        tree_frame = ttk.Frame(main)
        tree_frame.pack(fill=tk.BOTH, expand=True)
        self.tree = ttk.Treeview(tree_frame, show="headings")
        vsb = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL,
                            command=self.tree.yview)
        hsb = ttk.Scrollbar(tree_frame, orient=tk.HORIZONTAL,
                            command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        self.tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")
        tree_frame.rowconfigure(0, weight=1)
        tree_frame.columnconfigure(0, weight=1)

        self.root.protocol("WM_DELETE_WINDOW", self._on_close)

    def _on_close(self) -> None:
        close_connection()
        self.root.destroy()

    def _current_key(self) -> str:
        label = self.feature_var.get()
        for k, v in self.feature_labels.items():
            if v == label:
                return k
        return self.feature_keys[0]

    def _clear_input_container(self) -> None:
        assert self._input_container is not None
        for w in self._input_container.winfo_children():
            w.destroy()
        self._field_vars.clear()
        self._field_widgets.clear()

    def _add_field(
        self,
        row: int,
        key: str,
        label: str,
        hint: str = "",
        values: list[str] | None = None,
        readonly: bool = False,
    ) -> None:
        """Add a labeled input. If `values` is provided, render a Combobox."""
        assert self._input_container is not None
        ttk.Label(self._input_container, text=label).grid(
            row=row, column=0, sticky=tk.W, padx=(0, 8), pady=2
        )
        var = tk.StringVar()
        self._field_vars[key] = var
        widget: ttk.Widget
        if values is not None:
            state = "readonly" if readonly else "normal"
            widget = ttk.Combobox(
                self._input_container,
                textvariable=var,
                values=values,
                state=state,
                width=38,
            )
        else:
            widget = ttk.Entry(self._input_container,
                               textvariable=var, width=40)
        widget.grid(row=row, column=1, sticky=tk.W, pady=2)
        self._field_widgets[key] = widget
        if hint:
            ttk.Label(self._input_container, text=hint, foreground="#666").grid(
                row=row, column=2, sticky=tk.W, padx=(8, 0), pady=2
            )

    def _rebuild_inputs(self) -> None:
        self._clear_input_container()
        key = self._current_key()
        assert self._input_container is not None
        if key == "category":
            self._add_field(
                0,
                "category_name",
                "Category",
                hint="Pick or type a category",
                values=self._categories or [],
            )
        elif key == "country":
            self._add_field(
                0,
                "country",
                "Country",
                hint="Pick or type a country",
                values=self._countries or [],
            )
            self._add_field(
                1,
                "exchange",
                "Exchange (optional)",
                hint="Leave blank for any",
                values=[""] + (self._exchanges or []),
            )
        elif key == "range_days":
            self._add_field(0, "start_date", "Start date", "YYYY-MM-DD")
            self._add_field(1, "end_date", "End date", "YYYY-MM-DD")
            self._add_field(
                2,
                "min_range",
                "Minimum range vs open",
                "e.g. 0.05 = 5% (high−low)/open",
            )
        elif key == "history":
            self._add_field(0, "ticker", "Ticker", "e.g. AAPL")
        elif key == "volume":
            self._add_field(0, "start_date", "Start date", "YYYY-MM-DD")
            self._add_field(1, "end_date", "End date", "YYYY-MM-DD")
            self._add_field(2, "top_n", "How many rows", "e.g. 10")

    def _load_dropdown_values(self) -> None:
        """Background-load distinct category/country/exchange values for combo inputs."""

        def work() -> None:
            try:
                cats = fetch_single_column(SQL_DISTINCT_CATEGORIES)
            except Exception:  # noqa: BLE001
                cats = []
            try:
                countries = fetch_single_column(SQL_DISTINCT_COUNTRIES)
            except Exception:  # noqa: BLE001
                countries = []
            try:
                exchanges = fetch_single_column(SQL_DISTINCT_EXCHANGES)
            except Exception:  # noqa: BLE001
                exchanges = []
            self.root.after(
                0,
                lambda: self._apply_dropdown_values(
                    cats, countries, exchanges),
            )

        threading.Thread(target=work, daemon=True).start()

    def _apply_dropdown_values(
        self,
        categories: list[str],
        countries: list[str],
        exchanges: list[str],
    ) -> None:
        self._categories = categories
        self._countries = countries
        self._exchanges = exchanges
        # Update any currently displayed combo without losing typed input.
        for key, values in (
            ("category_name", categories),
            ("country", countries),
            ("exchange", [""] + exchanges),
        ):
            widget = self._field_widgets.get(key)
            if isinstance(widget, ttk.Combobox):
                widget["values"] = values

    def _collect_params(self) -> tuple[str, dict]:
        key = self._current_key()
        g = self._field_vars

        if key == "category":
            name = g["category_name"].get().strip()
            if not name:
                raise ValueError("Please enter a category name.")
            return SQL_BY_CATEGORY, {"category_name": name}

        if key == "country":
            country = g["country"].get().strip()
            if not country:
                raise ValueError("Please enter a country.")
            ex = g["exchange"].get().strip()
            return SQL_BY_COUNTRY, {
                "country": country,
                "exchange": ex.upper() if ex else None,
            }

        if key == "range_days":
            start = parse_date(g["start_date"].get())
            end = parse_date(g["end_date"].get())
            if end < start:
                raise ValueError("End date must be on or after start date.")
            rng = float(g["min_range"].get().strip())
            return SQL_RANGE_DAYS, {
                "start_date": start,
                "end_date": end,
                "min_range": rng,
            }

        if key == "history":
            t = g["ticker"].get().strip()
            if not t:
                raise ValueError("Please enter a ticker.")
            return SQL_CATEGORY_HISTORY, {"ticker": t}

        if key == "volume":
            start = parse_date(g["start_date"].get())
            end = parse_date(g["end_date"].get())
            if end < start:
                raise ValueError("End date must be on or after start date.")
            n = int(g["top_n"].get().strip())
            if n < 1:
                raise ValueError("How many rows must be at least 1.")
            return SQL_VOLUME_LEADERS, {
                "start_date": start,
                "end_date": end,
                "top_n": n,
            }

        raise ValueError("Unknown feature.")

    def _set_results(self, columns: list[str], rows: list) -> None:
        self.tree.delete(*self.tree.get_children())
        self.tree["columns"] = columns
        for c in columns:
            self.tree.heading(c, text=c.replace("_", " ").title())
            self.tree.column(c, width=120, minwidth=64, stretch=tk.YES)
        for row in rows:
            self.tree.insert("", tk.END, values=tuple(
                format_cell(v) for v in row))

    def _on_run(self) -> None:
        if self._busy:
            return
        try:
            sql, params = self._collect_params()
        except ValueError as e:
            self.status_var.set(str(e))
            return

        self._busy = True
        self.run_btn.state(["disabled"])
        self.status_var.set("Running query…")

        def work() -> None:
            try:
                columns, rows = execute_query(sql, params)
                self.root.after(
                    0, lambda c=columns, r=rows: self._finish_ok(c, r)
                )
            except Exception as e:  # noqa: BLE001 — show DB errors in UI
                msg = str(e)
                self.root.after(0, lambda m=msg: self._finish_err(m))

        threading.Thread(target=work, daemon=True).start()

    def _finish_ok(self, columns: list[str], rows: list) -> None:
        self._set_results(columns, rows)
        self.status_var.set(f"Done — {len(rows)} row(s).")
        self._busy = False
        self.run_btn.state(["!disabled"])

    def _finish_err(self, message: str) -> None:
        self.status_var.set(f"Error: {message}")
        self._busy = False
        self.run_btn.state(["!disabled"])

    def run(self) -> None:
        try:
            self.root.mainloop()
        finally:
            close_connection()


def main() -> None:
    StockExplorerApp().run()


if __name__ == "__main__":
    main()

# Stock database explorer (Tkinter)

Small desktop app that connects to the same Oracle database as the project’s `dataload.py` and runs five ready-made reports. Pick a report, fill in the form, and click **Run query**. Results show in a table below.

## Setup

This app connects through **`python-oracledb` in thick mode** because the class database requires native network encryption (you will see `DPY-3001: Native Network Encryption and Data Integrity is only supported in python-oracledb thick mode` in thin mode). Thick mode needs **Oracle Instant Client** installed on your computer. Each user sets the client folder with an environment variable—no paths are hardcoded in `db.py`.

### 1. Install Oracle Instant Client (one time per computer)

1. Go to the Oracle download page: [Oracle Instant Client downloads](https://www.oracle.com/database/technologies/instant-client/downloads.html).
2. Pick the page for your OS (Windows x64, macOS, or Linux x86-64).
3. Download **Basic** (or **Basic Light** if you want a smaller download; Basic Light works for English-only).
4. **Unzip** the file to a folder you will remember. Examples:
   - Windows: `C:\oracle\instantclient_23_0`
   - macOS: `/opt/oracle/instantclient_23_0`
   - Linux: `/opt/oracle/instantclient_23_0`
5. **Windows only:** if prompted, install the **Microsoft Visual C++ Redistributable** (Oracle’s download page links to it). Without it, the client libraries will not load.
6. **macOS only:** follow the extra unquarantine step on Oracle’s page (run the included `.dmg` or `xattr -dr com.apple.quarantine <folder>`), otherwise macOS blocks the libraries.

> Tip: The folder you keep is the one that contains files like `oci.dll` (Windows), `libclntsh.dylib` (macOS), or `libclntsh.so` (Linux). That’s the path you’ll point `ORACLE_LIB_DIR` at in the next step.

### 2. Tell the app where Instant Client lives

Set `ORACLE_LIB_DIR` in the **same terminal** you’ll use to run the app. If the folder is already on your system `PATH` (Windows) or `LD_LIBRARY_PATH` (Linux) / `DYLD_LIBRARY_PATH` (macOS), you can skip this.

**Windows (PowerShell):**

```powershell
$env:ORACLE_LIB_DIR = "C:\oracle\instantclient_23_0"
```

**Windows (Command Prompt):**

```bat
set ORACLE_LIB_DIR=C:\oracle\instantclient_23_0
```

**macOS / Linux:**

```bash
export ORACLE_LIB_DIR=/opt/oracle/instantclient_23_0
```

To make this permanent on Windows, open *System Properties → Environment Variables* and add `ORACLE_LIB_DIR`. On macOS/Linux, add the `export` line to your shell profile (e.g. `~/.zshrc` or `~/.bashrc`).

### 3. Python virtual environment (recommended)

From a terminal opened in the project folder (the one that contains `app/` and `dataload.py`):

```text
python -m venv .venv
```

### 4. Activate the venv

**Windows (PowerShell):**

```powershell
.\.venv\Scripts\Activate.ps1
```

**Windows (Command Prompt):**

```bat
.venv\Scripts\activate.bat
```

**macOS / Linux:**

```bash
source .venv/bin/activate
```

### 5. Install dependencies

```text
pip install -r app/requirements.txt
```

### 6. Run the app

Same terminal (so `ORACLE_LIB_DIR` is still set and the venv is active), from the project folder:

```text
python app/app.py
```

Login information (`USERNAME`, `PASSWORD`, `DSN`) is stored in `db.py` and matches `dataload.py` so the class project stays in one place.

### Troubleshooting

- **`DPY-3001: Native Network Encryption ... only supported in python-oracledb thick mode`** — Instant Client isn’t being loaded. Make sure step 1 finished and that `ORACLE_LIB_DIR` points at the right folder in the terminal you’re using.
- **`DPI-1047: Cannot locate a 64-bit Oracle Client library`** (Windows) — the Visual C++ Redistributable isn’t installed, `ORACLE_LIB_DIR` is wrong, or you downloaded the 32-bit client with 64-bit Python (they must match; most people want 64-bit for both).
- **`ORA-12514 / ORA-12541`** — DSN in `db.py` is wrong or the service is down. The DSN already matches `dataload.py`; if that script also fails, it’s a connectivity/credentials issue, not Instant Client.
- **Nothing in the Category / Country dropdowns** — the app loads those lists from the DB on startup. A connection error there means the rest of the app won’t work either; fix the above first.

---

## Features and queries

Each feature below is available from the **Feature** dropdown. The SQL shown is exactly what the app runs.

### 1. Stocks in a category

**What it does:** You type a category name (for example an industry or sector label from your data). The app lists every stock tied to that category, with ticker, name, exchange, and category details. Useful for seeing everything grouped under one label.

**SQL:**

```sql
SELECT s.symbol_id, s.ticker, s.name, s.exchange, c.category_name, c.category_type
FROM symbol s
JOIN symbol_category sc ON s.symbol_id = sc.symbol_id
JOIN category c ON sc.category_id = c.category_id
WHERE UPPER(c.category_name) = UPPER(:category_name)
ORDER BY s.ticker
```

---

### 2. Stocks by country (optional exchange)

**What it does:** You enter a country. You can also enter an exchange to narrow the list, or leave exchange blank to include all exchanges. The app shows matching stocks plus currency and description from the profile table.

**SQL:**

```sql
SELECT s.ticker, s.name, s.exchange, p.country, p.currency, p.description
FROM symbol s
JOIN symbol_profile p ON s.symbol_id = p.symbol_id
WHERE UPPER(p.country) = UPPER(:country)
  AND (:exchange IS NULL OR UPPER(s.exchange) = UPPER(:exchange))
ORDER BY s.ticker
```

---

### 3. Days with a wide high–low range

**What it does:** You choose a start and end date (`YYYY-MM-DD`) and a minimum “swing” size. The swing is \((\text{high} - \text{low}) / \text{open}\). The app lists trading days that are at least that active—helpful for spotting unusually wide days.

**SQL:**

```sql
SELECT s.ticker, d.trade_date, d.open, d.high, d.low, d.close,
       (d.high - d.low) / NULLIF(d.open, 0) AS range_vs_open
FROM symbol s
JOIN daily_price d ON s.symbol_id = d.symbol_id
WHERE d.trade_date BETWEEN :start_date AND :end_date
  AND (d.high - d.low) / NULLIF(d.open, 0) >= :min_range
ORDER BY range_vs_open DESC, d.trade_date DESC
```

---

### 4. Category history for one stock

**What it does:** You enter a ticker symbol. The app shows every category that stock was linked to, with assignment dates, newest first. Handy for questions like “when did this label get applied?”

**SQL:**

```sql
SELECT s.ticker, s.name, c.category_name, c.category_type, sc.assigned_date
FROM symbol s
JOIN symbol_category sc ON s.symbol_id = sc.symbol_id
JOIN category c ON sc.category_id = c.category_id
WHERE UPPER(s.ticker) = UPPER(:ticker)
ORDER BY sc.assigned_date DESC, c.category_name
```

---

### 5. Busiest stocks by total volume

**What it does:** You pick a date range and how many rows you want (for example 10). The app adds up volume per stock over that window and shows the largest totals first.

**SQL:**

```sql
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
```

---

## Files in this folder

| File | Purpose |
|------|---------|
| `app.py` | Tkinter window, forms, and running the SQL |
| `db.py` | Oracle client path, connection settings, `execute_query` |
| `requirements.txt` | Python dependency (`oracledb`) |

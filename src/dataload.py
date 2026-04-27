import os
from pathlib import Path

import pandas as pd
import oracledb
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

oracle_lib_dir = os.getenv("ORACLE_LIB_DIR")
if oracle_lib_dir:
    oracledb.init_oracle_client(lib_dir=oracle_lib_dir)

USERNAME = os.getenv("DB_USERNAME")
PASSWORD = os.getenv("DB_PASSWORD")
DSN = os.getenv("DB_DSN")

conn = oracledb.connect(user=USERNAME, password=PASSWORD, dsn=DSN)
cursor = conn.cursor()


def load_table(file, table, cols, sql_override=None):
    file_path = BASE_DIR / file
    df = pd.read_csv(file_path)

    if table == "DAILY_PRICE":
        df = df.head(5000)

    if table == "DAILY_PRICE":
        numeric_cols = ["open", "high", "low", "close", "adj_close", "volume"]
        for col in numeric_cols:
            df[col] = pd.to_numeric(df[col], errors="coerce")
        df["adj_close"] = df["adj_close"].where(
            pd.notnull(df["adj_close"]), None)
        df["volume"] = df["volume"].where(pd.notnull(df["volume"]), None)
        df = df.dropna(subset=["open", "high", "low", "close"])
    if sql_override is None:
        placeholders = ", ".join([f":{i+1}" for i in range(len(cols))])
        sql = f"INSERT INTO {table} ({', '.join(cols)}) VALUES ({placeholders})"
    else:
        sql = sql_override
    rows = [tuple(row) for row in df[cols].itertuples(index=False, name=None)]
    cursor.executemany(sql, rows)
    conn.commit()
    print(f"{table} loaded")


load_table(
    "data/symbol.csv",
    "SYMBOL",
    ["symbol_id", "ticker", "name", "exchange"]
)
load_table(
    "data/category.csv",
    "CATEGORY",
    ["category_id", "category_name", "category_type"]
)
load_table(
    "data/symbol_profile.csv",
    "SYMBOL_PROFILE",
    ["symbol_id", "currency", "country", "description"]
)
load_table(
    "data/symbol_category.csv",
    "SYMBOL_CATEGORY",
    ["symbol_id", "category_id", "assigned_date"],
    """
    INSERT INTO SYMBOL_CATEGORY (symbol_id, category_id, assigned_date)
    VALUES (:1, :2, TO_DATE(:3, 'YYYY-MM-DD'))
    """
)
load_table(
    "data/daily_price.csv",
    "DAILY_PRICE",
    ["symbol_id", "trade_date", "open", "high",
        "low", "close", "adj_close", "volume"],
    """
    INSERT INTO DAILY_PRICE
    (symbol_id, trade_date, open, high, low, close, adj_close, volume)
    VALUES (:1, TO_DATE(:2, 'YYYY-MM-DD'), :3, :4, :5, :6, :7, :8)
    """
)

cursor.close()
conn.close()
print("All data loaded successfully.")

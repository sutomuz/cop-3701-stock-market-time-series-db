import os
import pandas as pd

STOCKS_PATH = "stocks"
ETFS_PATH = "etfs"
META_FILE = "symbols_valid_meta.csv"
OUTPUT_PATH = "data"

os.makedirs(OUTPUT_PATH, exist_ok=True)
meta_df = pd.read_csv(META_FILE)

symbols = []
symbol_profiles = []
daily_prices = []
symbol_categories = []

categories = [
    (10, "Stock", "Equity"),
    (11, "ETF", "Fund")
]

symbol_id = 1
symbol_map = {}

MAX_SYMBOLS = 120

def process_folder(folder_path, category_id):
    global symbol_id

    for file in os.listdir(folder_path):
        if not file.endswith(".csv"):
            continue
        ticker = file.replace(".csv", "")
        if ticker not in meta_df["Symbol"].values:
            continue
        if symbol_id > MAX_SYMBOLS:
            break
        file_path = os.path.join(folder_path, file)
        df = pd.read_csv(file_path)
        if df.empty:
            continue

        name = meta_df.loc[meta_df["Symbol"] == ticker, "Security Name"].values[0]
        exchange = meta_df.loc[meta_df["Symbol"] == ticker, "Listing Exchange"].values[0]
        symbols.append((symbol_id, ticker, name, exchange))
        symbol_profiles.append((symbol_id, "USD", "USA", name))
        symbol_categories.append((symbol_id, category_id, "2020-01-01"))

        for _, row in df.iterrows():
            daily_prices.append((
                symbol_id,
                row["Date"],
                row["Open"],
                row["High"],
                row["Low"],
                row["Close"],
                row["Adj Close"],
                row["Volume"]
            ))

        symbol_map[ticker] = symbol_id
        symbol_id += 1

process_folder(STOCKS_PATH, 10)
process_folder(ETFS_PATH, 11)

symbol_df = pd.DataFrame(symbols, columns=["symbol_id", "ticker", "name", "exchange"])
profile_df = pd.DataFrame(symbol_profiles, columns=["symbol_id", "currency", "country", "description"])
category_df = pd.DataFrame(categories, columns=["category_id", "category_name", "category_type"])
symbol_category_df = pd.DataFrame(symbol_categories, columns=["symbol_id", "category_id", "assigned_date"])
daily_price_df = pd.DataFrame(daily_prices, columns=["symbol_id", "trade_date", "open", "high", "low", "close", "adj_close", "volume"])

symbol_df.to_csv(f"{OUTPUT_PATH}/symbol.csv", index=False)
profile_df.to_csv(f"{OUTPUT_PATH}/symbol_profile.csv", index=False)
category_df.to_csv(f"{OUTPUT_PATH}/category.csv", index=False)
symbol_category_df.to_csv(f"{OUTPUT_PATH}/symbol_category.csv", index=False)
daily_price_df.to_csv(f"{OUTPUT_PATH}/daily_price.csv", index=False)

print("CSV files generated successfully in /data folder.")
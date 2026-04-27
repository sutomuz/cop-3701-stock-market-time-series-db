# Database Setup from Scratch

This guide explains how to recreate the Stock Market Time-Series Database from the beginning.

## 1. Download the Dataset

Download the stock market dataset from Kaggle and place the raw files in the project folder.

The project expects the following raw dataset files/folders:

```text
stocks/
etfs/
symbols_valid_meta.csv
```

## 2. Create the Database Tables

Connect to Oracle using SQL Developer or another SQL tool.

Run the SQL schema file located at:

```text
sql/create_db.sql
```

This file creates the five main database tables:

- `SYMBOL`
- `SYMBOL_PROFILE`
- `CATEGORY`
- `DAILY_PRICE`
- `SYMBOL_CATEGORY`

The schema also defines the primary keys, composite primary keys, and foreign key relationships.

## 3. Configure Database Credentials

Create a `.env` file in the project root.

Example:

```env
DB_USERNAME=your_username_here
DB_PASSWORD=your_password_here
DB_DSN=db.freesql.com:1521/your_service_name
ORACLE_LIB_DIR=C:\path\to\instantclient
```

The `.env` file is used so database credentials are not hardcoded into the Python files.

## 4. Preprocess the Data

Run:

```bash
python src/preprocess.py
```

This script reads the raw Kaggle dataset, cleans the data, and creates cleaned CSV files inside the `data/` folder.

Generated files:

- `symbol.csv`
- `symbol_profile.csv`
- `category.csv`
- `symbol_category.csv`
- `daily_price.csv`

## 5. Load the Data

Run:

```bash
python src/dataload.py
```

This script reads the cleaned CSV files from the `data/` folder and inserts them into the Oracle database tables.

## 6. Verify the Tables

After loading the data, run these SQL queries:

```sql
SELECT COUNT(*) FROM SYMBOL;
SELECT COUNT(*) FROM CATEGORY;
SELECT COUNT(*) FROM SYMBOL_PROFILE;
SELECT COUNT(*) FROM SYMBOL_CATEGORY;
SELECT COUNT(*) FROM DAILY_PRICE;
```

These queries confirm that data was inserted into each table.

## 7. Run the Application

Run:

```bash
python app/app.py
```

The application connects to the database and allows users to run prepared reports on the stock market data.

## Notes

- The database must be created before running `src/dataload.py`.
- The cleaned CSV files must exist in the `data/` folder before loading data.
- The `.env` file should not be pushed to GitHub.
- Oracle Instant Client may be required depending on the database connection setup.
# SQL Schema

This folder contains the SQL file used to create the database schema.

## File

- `create_db.sql` creates the five project tables:
  - `SYMBOL`
  - `SYMBOL_PROFILE`
  - `CATEGORY`
  - `DAILY_PRICE`
  - `SYMBOL_CATEGORY`

The script also defines the primary keys, composite primary keys, and foreign key relationships.

## How to Use

Open `create_db.sql` in Oracle SQL Developer or another SQL tool connected to the database, then run the script before loading data.

After running the script, use `src/dataload.py` to insert the cleaned CSV data into the tables.
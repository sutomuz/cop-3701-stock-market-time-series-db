# Stock Market Time-Series Database Explorer

A financial database project that stores and analyzes historical stock market time-series data using MySQL and Oracle. The project uses a Kaggle stock market dataset and organizes stock symbols, daily prices, categories, and profile metadata into a structured database.

## Application Domain

This project falls under the financial data management domain because it works with historical stock market data. The database stores stock prices and trading volume data so users can run basic time-series queries and analysis.

The database is implemented in both MySQL and Oracle to compare how each system handles data types, indexing, and query execution.

## Database Application Description

The proposed database stores:

- Stock symbols, including tickers and exchange information
- Daily price records for each symbol
- Category classifications, such as Stock and ETF
- Symbol profile metadata, such as currency, country, and description

The ER design includes:

- Strong entities: `SYMBOL` and `CATEGORY`
- A weak entity: `DAILY_PRICE`, dependent on `SYMBOL`
- An associative entity: `SYMBOL_CATEGORY`
- One-to-one, one-to-many, and many-to-many relationships

## ER Diagram

![ER Diagram](docs/part_b_er_diagram.png)

## Goals

The goal of this project is to build a well-structured database using an existing Kaggle stock market dataset. This project focuses on understanding core database concepts using real-world financial data.

- **Load an existing dataset into a database**  
  Import the financial Kaggle CSV files into Oracle and MySQL.

- **Understand basic table structure**  
  Learn how tables, rows, and columns are used to store stock market data.

- **Practice writing SQL queries**  
  Retrieve stock prices, volumes, and symbol information using queries.

- **Work with date-based data**  
  Query stock data by date or date ranges to understand time-series information.

- **Perform basic analytical queries using SQL**  
  Calculate moving averages, daily price changes, indexing strategies, and simple volatility metrics.

- **Compare behavior across database systems**  
  Observe differences in how MySQL and Oracle handle data types, indexing, and query execution.

## Unique / Challenging Aspects

- Handling large historical time-series datasets efficiently
- Designing a composite primary key for daily stock records
- Implementing a weak entity structure correctly
- Creating many-to-many relationships using an associative entity
- Managing different SQL syntax and data types between Oracle and MySQL

## Project Scope

The scope of this project is limited to working with an existing Kaggle stock market dataset. The project focuses on importing the data, building the database, organizing it into tables, and running SQL queries to retrieve useful information.

This project does not include real-time updates, financial modeling, or prediction systems. The goal is to keep the scope small and manageable while learning database concepts and working with stock market data.

## Intended Users

The intended users are:

- Students learning database concepts
- Faculty demonstrating ER modeling and SQL
- Individuals interested in basic stock market data

## Data Sources

The data used in this project comes from a pre-existing Kaggle dataset containing historical stock market information. The dataset includes stock files, ETF files, and symbol metadata with attributes such as prices, trading volume, and dates.

## Application Features

The application allows users to run prepared reports on the stock database, including:

- Stocks in a category
- Stocks by country
- Days with a wide high-low range
- Category history for one stock
- Busiest stocks by total volume

## Project Structure

```text
app/      Application files
data/     Cleaned CSV files
docs/     ER diagram and setup documentation
sql/      SQL schema file
src/      Data preprocessing and loading scripts
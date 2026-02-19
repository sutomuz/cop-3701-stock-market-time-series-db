# cop-3701-stock-market-time-series-db
A financial database project that stores and analyzes historical stock market time-series data by using MySQL and Oracle, including prices, volume, and basic analytics such as moving averages.

## Application Domain
This project falls under the financial data management domain, as it focuses on working with an existing stock market dataset provided through Kaggle. The application utilizes a structured database to store historical stock prices and trading volume data, supporting basic time-series queries and analysis. The project focuses on organizing, querying, and analyzing the financial data.

The Database is implemented in both MySQL and Oracle to compare how each system handles data types, indexing, and query executions.

## Database Application Description
The proposed database stores:
- Stock symbols (tickers and exchange information)
- Daily price records for each symbol
- Category classifications (Stocks & ETF)
- Symbol profile metadata (currency, country, description)

The ER design includes:
- Strong entities (SYMBOL, CATEGORY)
- A weak entity (DAILY_PRICE, dependent on SYMBOL)
- An associative entity (SYMBOL_CATEGORY)
- One-to-one, one-to-many, and many-to-many relationships

## Goals
The goal of this project is to build a well-structured database using the existing Kaggle stock market dataset. This project focuses on understanding core database concepts using a real-world financial dataset.

- **Load existing dataset into a database**
  Import the financial Kaggle CSV file into Oracle and MySQL.
- **Understand basic table structure**
  Learn how tables, rows, and columns are used to store stock market data.
- **Practice writing simple SQL queries**
  Retrieve stock prices and volumes using queries.
- **Work with data-based data**
  Query stock data by date or date ranges to understand time-series information
- **Perform basic analytical queries using SQL**
  Calculate moving averages, daily price changes, partitions by date, optimized index strategies, and simple volatility metrics.
- **Compare behavior across database systems**
  Observe the differences in how the two databases handled data.

## Unique / Challenging Aspects
- Handling large historical time-series datasets efficiently
- Designing a composite primary key for daily stock records
- Implementing a weak entity structure correctly
- Creating many-to-many relationships using associative entities
- Managing the different SQL syntax and data types between Oracle and MySQL

## Project Scope
The scope of this project is limited to working with an existing stock market dataset that is provided through Kaggle. The project will focus on importing and building the dataset, organizing it into tables, and running SQL queries to get information. This project will also be limited by not including real-time updates, financial modeling, and prediction systems. As the project goal is to keep the scope small and manageable while learning database concepts, and learning about the stock market.

## Intended Users
The intended users are:
- Students' learning database
- Faculty demonstrating ER modeling and SQL
- Individuals interested in basic stock market data

## Data Sources
The data used in this project is from a pre-existing Kaggle dataset containing historical stock market information. The dataset provides stocks, etf, and symbols, which help include attributes such as stock prices, trading volumes, and dates.

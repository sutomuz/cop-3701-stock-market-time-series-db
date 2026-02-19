# Database ER Diagram

## Overwivew
The ER diagram represents the stock market time-series database built from a Kaggle dataset.
The system stores stock symbols, daily prices, categories, and symbol profile information.

## User Groups
- **Students** learning database concepts using financial data
- **Faculty** demonstrating SQL queries and ER modeling.
- **Beginners** exploring historical stock prices and trends.

## ER Diagram
![ER Diagram](partb.png)

## Entity Sumamry
- **SYMBOL** - Strong entity storing ticket information
- **SYMBOL_PROFILE** - One-to-one entity with SYMBOL containing metadata.
- **DAILY_PRICE** - Weak entity dependent on SYMBOL, identified by *(symbol_id, trade_date)*.
- **CATEGORY** - Strong entity defining classifications like stock, ETF, or sector.
- **SYMBOL_CATEGORY** - Associate entity resolving the many-to-many relationship between SYMBOL and CATEGORY.

## Relationships
- **One-to-One:** SYMBOL -> SYMBOL_PROFILE
- **One-to-Many:** SYMBOL -> DAILY_PRICE
- **Many-to-Many:** SYMBOL <-> CATEGORY (via SYMBOL_CATEGORY)

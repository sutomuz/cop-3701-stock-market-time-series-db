# Database ER Diagram

## Overview

The ER diagram represents the stock market time-series database built from a Kaggle dataset. The system stores stock symbols, daily prices, categories, and symbol profile information.

## User Groups

- **Students** learning database concepts using financial data
- **Faculty** demonstrating SQL queries and ER modeling
- **Beginners** exploring historical stock prices and trends

## ER Diagram

![ER Diagram](part_b_er_diagram.png)

## Entity Summary

- **SYMBOL** — Strong entity that stores ticker information, including ticker, name, and exchange.
- **SYMBOL_PROFILE** — One-to-one entity with SYMBOL that stores metadata such as currency, country, and description.
- **DAILY_PRICE** — Weak entity dependent on SYMBOL, identified by the composite key `(symbol_id, trade_date)`.
- **CATEGORY** — Strong entity that defines classifications such as Stock, ETF, or sector.
- **SYMBOL_CATEGORY** — Associative entity that resolves the many-to-many relationship between SYMBOL and CATEGORY.

## Relationships

- **One-to-One:** SYMBOL → SYMBOL_PROFILE
- **One-to-Many:** SYMBOL → DAILY_PRICE
- **One-to-Many:** SYMBOL → SYMBOL_CATEGORY
- **One-to-Many:** CATEGORY → SYMBOL_CATEGORY
- **Many-to-Many:** SYMBOL ↔ CATEGORY through SYMBOL_CATEGORY

## Final Normalized Relational Schema (BCNF)

Based on the ER diagram and functional dependency analysis, the following relations are in Boyce-Codd Normal Form (BCNF).

## SYMBOL

SYMBOL(
  symbol_id PK,
  ticker UNIQUE NOT NULL,
  name,
  exchange
)

## SYMBOL_PROFILE

SYMBOL_PROFILE(
  symbol_id PK FK → SYMBOL(symbol_id),
  currency NOT NULL,
  country NOT NULL,
  description
)

## DAILY_PRICE

DAILY_PRICE(
  symbol_id PK FK → SYMBOL(symbol_id),
  trade_date PK,
  open NOT NULL,
  high NOT NULL,
  low NOT NULL,
  close NOT NULL,
  adj_close,
  volume
)

## CATEGORY

CATEGORY(
  category_id PK,
  category_name NOT NULL,
  category_type
)

## SYMBOL_CATEGORY

SYMBOL_CATEGORY(
  symbol_id PK FK → SYMBOL(symbol_id),
  category_id PK FK → CATEGORY(category_id),
  assigned_date NOT NULL
)

All relations above were checked against their non-trivial functional dependencies and satisfy BCNF. No further decomposition was required.
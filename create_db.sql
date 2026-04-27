DROP TABLE symbol_category CASCADE CONSTRAINTS;
DROP TABLE daily_price CASCADE CONSTRAINTS;
DROP TABLE symbol_profile CASCADE CONSTRAINTS;
DROP TABLE category CASCADE CONSTRAINTS;
DROP TABLE symbol CASCADE CONSTRAINTS;

SELECT COUNT(*) FROM SYMBOL;
SELECT COUNT(*) FROM CATEGORY;
SELECT COUNT(*) FROM SYMBOL_PROFILE;
SELECT COUNT(*) FROM SYMBOL_CATEGORY;
SELECT COUNT(*) FROM DAILY_PRICE;

CREATE TABLE symbol (
   symbol_id NUMBER PRIMARY KEY,
   ticker    VARCHAR2(15) NOT NULL UNIQUE,
   name      VARCHAR2(255),
   exchange  VARCHAR2(30)
);

CREATE TABLE symbol_profile (
   symbol_id   NUMBER PRIMARY KEY,
   currency    CHAR(3) NOT NULL,
   country     VARCHAR2(60) NOT NULL,
   description VARCHAR2(400),
   CONSTRAINT fk_symbol_profile 
      FOREIGN KEY (symbol_id)
      REFERENCES symbol (symbol_id)
);

CREATE TABLE category (
   category_id   NUMBER PRIMARY KEY,
   category_name VARCHAR2(60) NOT NULL,
   category_type VARCHAR2(30)
);

CREATE TABLE daily_price (
   symbol_id  NUMBER,
   trade_date DATE,
   open       NUMBER(12,4) NOT NULL,
   high       NUMBER(12,4) NOT NULL,
   low        NUMBER(12,4) NOT NULL,
   close      NUMBER(12,4) NOT NULL,
   adj_close  NUMBER(12,4),
   volume     NUMBER,
   CONSTRAINT pk_daily_price 
      PRIMARY KEY (symbol_id, trade_date),
   CONSTRAINT fk_daily_price_symbol 
      FOREIGN KEY (symbol_id)
      REFERENCES symbol (symbol_id)
);

CREATE TABLE symbol_category (
   symbol_id     NUMBER,
   category_id   NUMBER,
   assigned_date DATE NOT NULL,
   CONSTRAINT pk_symbol_category 
      PRIMARY KEY (symbol_id, category_id),
   CONSTRAINT fk_symbol_category_symbol 
      FOREIGN KEY (symbol_id)
      REFERENCES symbol (symbol_id),
   CONSTRAINT fk_symbol_category_category 
      FOREIGN KEY (category_id)
      REFERENCES category (category_id)
);

COMMIT;
drop table symbol_category cascade constraints;
drop table daily_price cascade constraints;
drop table symbol_profile cascade constraints;
drop table category cascade constraints;
drop table symbol cascade constraints;

create table symbol (
   symbol_id number primary key,
   ticker    varchar2(15) not null unique,
   name      varchar2(120),
   exchange  varchar2(30)
);

create table symbol_profile (
   symbol_id   number primary key,
   currency    char(3) not null,
   country     varchar2(60) not null,
   description varchar2(400),
   constraint fk_symbol_profile foreign key ( symbol_id )
      references symbol ( symbol_id )
);

create table category (
   category_id   number primary key,
   category_name varchar2(60) not null,
   category_type varchar2(30)
);

create table daily_price (
   symbol_id  number,
   trade_date date,
   open       number(12,4) not null,
   high       number(12,4) not null,
   low        number(12,4) not null,
   close      number(12,4) not null,
   adj_close  number(12,4),
   volume     number,
   constraint pk_daily_price primary key ( symbol_id,
                                           trade_date ),
   constraint fk_daily_price_symbol foreign key ( symbol_id )
      references symbol ( symbol_id )
);

create table symbol_category (
   symbol_id     number,
   category_id   number,
   assigned_date date not null,
   constraint pk_symbol_category primary key ( symbol_id,
                                               category_id ),
   constraint fk_symbol_category_symbol foreign key ( symbol_id )
      references symbol ( symbol_id ),
   constraint fk_symbol_category_category foreign key ( category_id )
      references category ( category_id )
);
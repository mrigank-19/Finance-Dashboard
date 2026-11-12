import pandas as pd
import numpy as np

# --- Database connection setup (merged in from db_connect.py) ---
# Loads DB_PASSWORD from .env (never hardcoded), builds the SQLAlchemy
# connection string, and creates the engine used for all DB operations below.
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine

load_dotenv()
db_password = os.getenv("DB_PASSWORD")
engine = create_engine(f"mysql+pymysql://root:{db_password}@localhost:3306/finance_dashboard")

try:
    connection = engine.connect()
    print("Connected successfully")
    connection.close()
except Exception as e:
    print("Connection failed:", e)

# --- Load and clean the transactions CSV ---
df = pd.read_csv('account_statement.csv')
df['date_only'] = pd.to_datetime(df['Transaction Date'], format="%d-%m-%Y %H:%M").dt.date

df['Amount'] = df['Amount'].str.replace(',', '', regex=False)
df['Amount'] = df['Amount'].astype(float)

mapping = {
    'DR' : 'debit',
    'CR' : 'credit'
}

df['txn_type'] = df['Dr / Cr'].map(mapping)
print(df.head())

print(df['txn_type'].unique())

# ----- Load and clean the holdings CSV -----

stocks_df = pd.read_csv('stock_holdings.csv')

mf_df = pd.read_csv('mf_holdings.csv')

# ---- duplication checking transactions ---#

committed_rows = 0

from sqlalchemy import text

check_query = text("""
    SELECT COUNT(*) FROM transactions
    WHERE account_id = :account_id
    AND transaction_date = :transaction_date
    AND amount = :amount
    AND description = :description
""")

insert_query = text("""
    INSERT INTO transactions (account_id, transaction_date, amount, description, txn_type, merchant, is_recurring)
    VALUES (:account_id, :transaction_date, :amount, :description, :txn_type, :merchant, :is_recurring)
""")

with engine.connect() as conn:
    for i in range(0, len(df)):
        result = conn.execute(check_query, {
            "account_id": 1,
            "transaction_date": df.iloc[i]['date_only'],
            "amount": df.iloc[i]['Amount'],
            "description": df.iloc[i]['Description']
        })
        count = result.scalar()  # gets the single number back from COUNT(*)
        if(count == 0):
            committed_rows += 1
            conn.execute(insert_query, {
                "account_id": 1,
                "transaction_date": df.iloc[i]['date_only'],
                "amount": df.iloc[i]['Amount'],
                "description": df.iloc[i]['Description'],
                "txn_type": df.iloc[i]['txn_type'],
                "merchant": None,  # Placeholder for merchant
                "is_recurring": False  # Placeholder for is_recurring
            })
    conn.commit() # Commit the transaction after all inserts are done

# --- duplication checking holdings --- #

check_stock_query = text("""
    SELECT count(*) FROM holdings
    WHERE account_id = :account_id
    AND isin = :isin
""")

check_mf_query = text("""
    SELECT count(*) FROM holdings
    WHERE account_id = :account_id
    AND folio_number = :folio_number
""")

insert_query = text("""
    INSERT INTO holdings (account_id, instrument_name, instrument_type, quantity, avg_buy_price, current_price, isin, folio_number)
    VALUES (:account_id, :instrument_name, :instrument_type, :quantity, :avg_buy_price, :current_price, :isin, :folio_number)
""")

with engine.connect() as conn:
    for i in range(0, len(stocks_df)):
        result = conn.execute(check_stock_query, {
            "account_id": 1,
            "isin": stocks_df.iloc[i]['ISIN']
        })
        count = result.scalar()
        if(count == 0):
            committed_rows += 1
            conn.execute(insert_query, {
                "account_id": 1,
                "instrument_name": stocks_df.iloc[i]['Stock Name'],
                "instrument_type": "stocks",
                "quantity": stocks_df.iloc[i]['Quantity'],
                "avg_buy_price": stocks_df.iloc[i]['Average Price'],
                "current_price": stocks_df.iloc[i]['Closing Price'],
                "isin": stocks_df.iloc[i]['ISIN'],
                "folio_number": None
            })
        else :
            conn.execute(text("""
                UPDATE holdings
                SET quantity = :quantity, avg_buy_price = :avg_buy_price, current_price = :current_price
                WHERE account_id = :account_id AND isin = :isin
            """), {
                "quantity": stocks_df.iloc[i]['Quantity'],
                "avg_buy_price": stocks_df.iloc[i]['Average Price'],
                "current_price": stocks_df.iloc[i]['Closing Price'],
                "account_id": 1,
                "isin": stocks_df.iloc[i]['ISIN']
            })

    for i in range(0, len(mf_df)):
        result = conn.execute(check_mf_query, {
            "account_id": 1,
            "folio_number": mf_df.iloc[i]['Folio Number']
        })
        count = result.scalar()
        if(count == 0):
            committed_rows += 1
            conn.execute(insert_query, {
                "account_id": 1,
                "instrument_name": mf_df.iloc[i]['Mutual Fund Name'],
                "instrument_type": "mf",
                "quantity": mf_df.iloc[i]['Total Units'],
                "avg_buy_price": mf_df.iloc[i]['Average NAV'],
                "current_price": mf_df.iloc[i]['Current NAV'],
                "isin": None,
                "folio_number": mf_df.iloc[i]['Folio Number']
            })
        else:
            conn.execute(text("""
                UPDATE holdings
                SET quantity = :quantity, avg_buy_price = :avg_buy_price, current_price = :current_price
                WHERE account_id = :account_id AND folio_number = :folio_number
            """), {
                "quantity": mf_df.iloc[i]['Total Units'],
                "avg_buy_price": mf_df.iloc[i]['Average NAV'],
                "current_price": mf_df.iloc[i]['Current NAV'],
                "account_id": 1,
                "folio_number": mf_df.iloc[i]['Folio Number']
            })
    conn.commit() # Commit the transaction after all inserts are done
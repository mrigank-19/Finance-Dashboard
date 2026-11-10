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

# --- Load and clean the CSV ---
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

print(len(df))

# ---- duplication checking ---#

# print(df.iloc[0]['date_only'], df.iloc[0]['Amount'], df.iloc[0]['Description'])
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

print(f"Committed {committed_rows} new rows to the database.")    





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
df['date_only'] = pd.to_datetime(df['Transaction Date'], format="%d-%m-%Y %H:%M").dt.strftime('%d-%m-%Y')

df['Amount'] = df['Amount'].str.replace(',', '', regex=False)
df['Amount'] = df['Amount'].astype(float)

mapping = {
    'DR' : 'debit',
    'CR' : 'credit'
}

df['txn_type'] = df['Dr / Cr'].map(mapping)
print(df.head())

print(df['txn_type'].unique())
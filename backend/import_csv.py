import pandas as pd
import numpy as np

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
import pandas as pd
from sqlalchemy import text
from db import engine


def import_transactions(file_path, account_id):
    df = pd.read_csv(file_path)
    df["date_only"] = pd.to_datetime(
        df["Transaction Date"], format="%d-%m-%Y %H:%M"
    ).dt.date

    df["Amount"] = df["Amount"].str.replace(",", "", regex=False)
    df["Amount"] = df["Amount"].astype(float)

    mapping = {"DR": "debit", "CR": "credit"}

    df["txn_type"] = df["Dr / Cr"].map(mapping)

    print(df["txn_type"].unique())

    committed_rows = 0
    duplicate_rows = 0

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
            result = conn.execute(
                check_query,
                {
                    "account_id": account_id,
                    "transaction_date": df.iloc[i]["date_only"],
                    "amount": df.iloc[i]["Amount"],
                    "description": df.iloc[i]["Description"],
                },
            )
            count = result.scalar()  # gets the single number back from COUNT(*)
            if count == 0:
                committed_rows += 1
                conn.execute(
                    insert_query,
                    {
                        "account_id": account_id,
                        "transaction_date": df.iloc[i]["date_only"],
                        "amount": df.iloc[i]["Amount"],
                        "description": df.iloc[i]["Description"],
                        "txn_type": df.iloc[i]["txn_type"],
                        "merchant": None,  # Placeholder for merchant
                        "is_recurring": False,  # Placeholder for is_recurring
                    },
                )
            else :
                duplicate_rows += 1
        conn.commit()  # Commit the transaction after all inserts are done

    return committed_rows, duplicate_rows

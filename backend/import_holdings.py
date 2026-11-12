import pandas as pd
from sqlalchemy import text
from db import engine

def import_stock_holdings(file_path, account_id):
    stocks_df = pd.read_csv(file_path)

    committed_rows = 0
    duplicate_rows = 0

    check_stock_query = text("""
        SELECT count(*) FROM holdings
        WHERE account_id = :account_id
        AND isin = :isin
    """)

    insert_query = text("""
        INSERT INTO holdings (account_id, instrument_name, instrument_type, quantity, avg_buy_price, current_price, isin, folio_number)
        VALUES (:account_id, :instrument_name, :instrument_type, :quantity, :avg_buy_price, :current_price, :isin, :folio_number)
    """)

    with engine.connect() as conn:
        for i in range(0, len(stocks_df)):
            result = conn.execute(check_stock_query, {
                "account_id": account_id,
                "isin": stocks_df.iloc[i]['ISIN']
            })
            count = result.scalar()
            if(count == 0):
                committed_rows += 1
                conn.execute(insert_query, {
                    "account_id": account_id,
                    "instrument_name": stocks_df.iloc[i]['Stock Name'],
                    "instrument_type": "stocks",
                    "quantity": stocks_df.iloc[i]['Quantity'],
                    "avg_buy_price": stocks_df.iloc[i]['Average Price'],
                    "current_price": stocks_df.iloc[i]['Closing Price'],
                    "isin": stocks_df.iloc[i]['ISIN'],
                    "folio_number": None
                })
            else :
                duplicate_rows += 1
                conn.execute(text("""
                    UPDATE holdings
                    SET quantity = :quantity, avg_buy_price = :avg_buy_price, current_price = :current_price
                    WHERE account_id = :account_id AND isin = :isin
                """), {
                    "quantity": stocks_df.iloc[i]['Quantity'],
                    "avg_buy_price": stocks_df.iloc[i]['Average Price'],
                    "current_price": stocks_df.iloc[i]['Closing Price'],
                    "account_id": account_id,
                    "isin": stocks_df.iloc[i]['ISIN']
                })
        conn.commit()

    return committed_rows, duplicate_rows

def import_mf_holdings(file_path, account_id):
    mf_df = pd.read_csv(file_path)

    committed_rows = 0
    duplicate_rows = 0

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
        for i in range(0, len(mf_df)):
            result = conn.execute(check_mf_query, {
                "account_id": account_id,
                "folio_number": mf_df.iloc[i]['Folio Number']
            })
            count = result.scalar()
            if(count == 0):
                committed_rows += 1
                conn.execute(insert_query, {
                    "account_id": account_id,
                    "instrument_name": mf_df.iloc[i]['Mutual Fund Name'],
                    "instrument_type": "mf",
                    "quantity": mf_df.iloc[i]['Total Units'],
                    "avg_buy_price": mf_df.iloc[i]['Average NAV'],
                    "current_price": mf_df.iloc[i]['Current NAV'],
                    "isin": None,
                    "folio_number": mf_df.iloc[i]['Folio Number']
                })
            else :
                duplicate_rows += 1
                conn.execute(text("""
                    UPDATE holdings
                    SET quantity = :quantity, avg_buy_price = :avg_buy_price, current_price = :current_price
                    WHERE account_id = :account_id AND folio_number = :folio_number
                """), {
                    "quantity": mf_df.iloc[i]['Total Units'],
                    "avg_buy_price": mf_df.iloc[i]['Average NAV'],
                    "current_price": mf_df.iloc[i]['Current NAV'],
                    "account_id": account_id,
                    "folio_number": mf_df.iloc[i]['Folio Number']
                })
        conn.commit()
    return committed_rows, duplicate_rows
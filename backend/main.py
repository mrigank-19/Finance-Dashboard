from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from import_transactions import import_transactions
from import_holdings import import_stock_holdings, import_mf_holdings
import shutil
import os
from db import engine
from sqlalchemy import text

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Hello from FastAPI"}


@app.post("/import/transactions")
async def import_transactions_endpoint(file: UploadFile = File(...), account_id: int = Form(...)):
    temp_path = f"temp_{file.filename}"
    with open(temp_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    added, duplicates = import_transactions(temp_path, account_id)

    os.remove(temp_path)

    with engine.connect() as conn:
        conn.execute(text("""
            INSERT INTO import_log (account_id, import_type, number_rows_added, duplicate_rows) VALUES (:account_id,:import_type,:number_rows_added, :duplicate_rows)
        """),
            {
                "account_id": account_id,
                "import_type": "bank",
                "number_rows_added": added,
                "duplicate_rows": duplicates
            }
        )
        conn.commit()

    return {"rows_added": added, "duplicate_rows": duplicates}

@app.post("/import/holdings/stocks")
async def import_stock_holdings_endpoint(file: UploadFile = File(...), account_id: int = Form(...)):
    temp_path = f"temp_{file.filename}"
    with open(temp_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    added, duplicates = import_stock_holdings(temp_path, account_id)

    os.remove(temp_path)

    with engine.connect() as conn:
        conn.execute(
            text("""
                INSERT INTO import_log (account_id, import_type, number_rows_added, duplicate_rows) VALUES (:account_id,:import_type,:number_rows_added, :duplicate_rows)
            """),
            {
                "account_id": account_id,
                "import_type": "stock",
                "number_rows_added": added,
                "duplicate_rows": duplicates
            }
        )
        conn.commit()

    return {"rows_added": added, "duplicate_rows": duplicates}

@app.post("/import/holdings/mf")
async def import_mf_holdings_endpoint(file: UploadFile = File(...), account_id: int = Form(...)):
    temp_path = f"temp_{file.filename}"
    with open(temp_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    added, duplicates = import_mf_holdings(temp_path, account_id)

    os.remove(temp_path)

    with engine.connect() as conn:
        conn.execute(
            text("""
                INSERT INTO import_log (account_id, import_type, number_rows_added, duplicate_rows) VALUES (:account_id,:import_type,:number_rows_added, :duplicate_rows)
            """),
            {
                "account_id": account_id,
                "import_type": "mf",
                "number_rows_added": added,
                "duplicate_rows": duplicates
            }
        )
        conn.commit()

    return {"rows_added": added, "duplicate_rows": duplicates}


@app.get("/import/history")
def get_import_history():
    with engine.connect() as conn:
        result = conn.execute(text("SELECT * FROM import_log ORDER BY imported_at DESC"))
        rows = [dict(row._mapping) for row in result]
    return rows
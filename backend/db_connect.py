import os
from dotenv import load_dotenv

load_dotenv()

db_password = os.getenv("DB_PASSWORD")

from sqlalchemy import create_engine

engine = create_engine(f"mysql+pymysql://root:{db_password}@localhost:3306/finance_dashboard")

try:
    connection = engine.connect()
    print("Connected successfully")
    connection.close()
except Exception as e:
    print("Connection failed:", e)
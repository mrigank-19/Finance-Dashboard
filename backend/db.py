import os
from dotenv import load_dotenv
from sqlalchemy import create_engine

load_dotenv()
db_password = os.getenv("DB_PASSWORD")
engine = create_engine(f"mysql+pymysql://root:{db_password}@localhost:3306/finance_dashboard")
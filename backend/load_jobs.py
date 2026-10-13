import os
import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine

# Load environment variables
load_dotenv()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CSV_FILE = os.path.join(BASE_DIR, "../data/jobs.csv")

# AWS RDS PostgreSQL credentials from .env
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")

DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
engine = create_engine(DATABASE_URL)

if os.path.exists(CSV_FILE):
    jobs = pd.read_csv(CSV_FILE)
    jobs.to_sql("jobs", engine, if_exists="replace", index=False)
    print("✅ Jobs successfully loaded into AWS RDS PostgreSQL!")
else:
    print(f"❌ Error: {CSV_FILE} not found!")
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

# Load environment variables from .env file
load_dotenv()

# ---- AWS RDS PostgreSQL Connection ----
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")

# SQLAlchemy connection string for PostgreSQL
DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# Create engine
engine = create_engine(DATABASE_URL)


def create_database():
    """Create the jobs table in AWS RDS if it doesn't exist."""
    with engine.connect() as connection:
        connection.execute(text("""
            CREATE TABLE IF NOT EXISTS jobs (
                id SERIAL PRIMARY KEY,
                job_title TEXT,
                company TEXT,
                location TEXT,
                skills TEXT,
                description TEXT
            )
        """))
        connection.commit()
    print("✅ AWS RDS PostgreSQL database table created successfully!")


def get_connection():
    """Return a database engine connection."""
    return engine.connect()


if __name__ == "__main__":
    create_database()
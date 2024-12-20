from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os

POSTGRES_HOST = os.getenv("POSTGRES_HOST", "localhost")
POSTGRES_DB = os.getenv("POSTGRES_DB", "airflow")
POSTGRES_USER = os.getenv("POSTGRES_USER", "airflow")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "airflow")

DATABASE_URL = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:5432/{POSTGRES_DB}"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

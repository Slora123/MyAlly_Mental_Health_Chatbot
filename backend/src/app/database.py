import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
from .models import Base

from pathlib import Path
root_env = Path(__file__).resolve().parents[3] / ".env"
load_dotenv(dotenv_path=root_env)

# We expect POSTGRES_URL in .env
# Ensure you use postgresql:// not postgres://
SQLALCHEMY_DATABASE_URL = os.getenv("POSTGRES_URL", "sqlite:///./myally.db")

# SQLite needs connect_args={"check_same_thread": False}, Postgres doesn't
connect_args = {}
if SQLALCHEMY_DATABASE_URL.startswith("sqlite"):
    connect_args = {"check_same_thread": False}

engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

import os
from sqlalchemy import create_engine
from dotenv import load_dotenv

load_dotenv()

def get_connection():
    """
    Returns a SQLAlchemy engine connection.
    """
    database_url = os.getenv("DATABASE_URL", "sqlite:///./habitcore.db")
    # Handle postgresql:// vs postgres:// for SQLAlchemy 1.4+
    if database_url.startswith("postgres://"):
        database_url = database_url.replace("postgres://", "postgresql://", 1)
    
    return create_engine(database_url)

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Database connection URL (using SQLite)
DATABASE_URL = "sqlite:///./database.db"

# Create a database engine
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

# Session factory for handling database connections
SessionLocal = sessionmaker(autocommit = False, autoflush = False, bind = engine)

# Base class for SQLAlchemy models
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db  # Provide a database session
    finally:
        db.close()  # Ensure session is closed after use

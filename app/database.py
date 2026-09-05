"""
FraudShield Database Configuration

SQLAlchemy setup supporting both SQLite (local dev) and PostgreSQL (production).
"""

import os
from sqlalchemy import create_engine, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

# Database URL from environment variable
# Default: SQLite for local development/testing
# Production: Set DATABASE_URL to postgresql://user:password@host:port/database
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "sqlite:///./fraudshield.db"
)

# Render provides DATABASE_URL with postgres:// which SQLAlchemy doesn't support
# Need to replace with postgresql://
if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

_db_available = True

try:
    engine_args = {}
    if DATABASE_URL.startswith("sqlite"):
        engine_args["connect_args"] = {"check_same_thread": False}
    else:
        engine_args["pool_size"] = 5
        engine_args["max_overflow"] = 10
        
    engine = create_engine(
        DATABASE_URL,
        pool_pre_ping=True,
        **engine_args
    )
    
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
    except Exception as e:
        print(f"Warning: Database connection failed: {e}")
        _db_available = False
except Exception as e:
    print(f"Warning: Could not create database engine: {e}")
    _db_available = False
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
Base = declarative_base()


def get_db():
    """
    Dependency for FastAPI to get database session.
    
    Usage:
        @app.get("/items")
        def read_items(db: Session = Depends(get_db)):
            return db.query(Transaction).all()
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def is_db_available() -> bool:
    """Check if database is available."""
    return _db_available

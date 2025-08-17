"""
Database configuration and session management.
"""

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get database URL from environment or use default SQLite
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./medical_clinic.db")

# Create engine
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Import Base from models
from .models.base import Base


class DatabaseManager:
    """Database manager class for handling database operations."""
    
    def __init__(self):
        """Initialize the database manager."""
        self.engine = engine
        self.SessionLocal = SessionLocal
    
    def create_tables(self):
        """Create all tables in the database."""
        Base.metadata.create_all(bind=self.engine)
    
    def get_session(self) -> Session:
        """Get a new database session."""
        return self.SessionLocal()
    
    def close_session(self, session: Session):
        """Close a database session."""
        session.close()


# Global database manager instance
db_manager = DatabaseManager()


def get_db():
    """Dependency function to get database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

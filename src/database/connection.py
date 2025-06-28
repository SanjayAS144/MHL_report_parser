"""Database connection management."""

import os
from typing import Optional

from sqlalchemy import create_engine, Engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import QueuePool
from loguru import logger

from .models import Base


class DatabaseConnection:
    """Database connection manager."""
    
    def __init__(self, connection_string: Optional[str] = None):
        """Initialize database connection."""
        if connection_string is None:
            connection_string = self._build_connection_string()
        
        self.engine = create_engine(
            connection_string,
            poolclass=QueuePool,
            pool_size=10,
            max_overflow=20,
            pool_pre_ping=True,
            echo=os.getenv('DEBUG', 'false').lower() == 'true'
        )
        
        self.SessionLocal = sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=self.engine
        )
        
        logger.info("Database connection initialized")
    
    def _build_connection_string(self) -> str:
        """Build database connection string from environment variables."""
        host = os.getenv('DB_HOST', 'localhost')
        port = os.getenv('DB_PORT', '5432')
        name = os.getenv('DB_NAME', 'food_tech_analytics')
        user = os.getenv('DB_USER', 'postgres')
        password = os.getenv('DB_PASSWORD', '')
        
        if not password:
            raise ValueError("DB_PASSWORD environment variable is required")
        
        return f"postgresql://{user}:{password}@{host}:{port}/{name}"
    
    def create_tables(self) -> bool:
        """Create all database tables."""
        try:
            Base.metadata.create_all(bind=self.engine)
            logger.info("Database tables created successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to create database tables: {e}")
            return False
    
    def get_session(self) -> Session:
        """Get database session."""
        return self.SessionLocal()
    
    def close(self):
        """Close database connection."""
        if hasattr(self, 'engine'):
            self.engine.dispose()
            logger.info("Database connection closed")


# Global database connection instance
_db_connection: Optional[DatabaseConnection] = None


def get_database_connection() -> DatabaseConnection:
    """Get global database connection instance."""
    global _db_connection
    if _db_connection is None:
        _db_connection = DatabaseConnection()
    return _db_connection


def get_session() -> Session:
    """Get database session."""
    return get_database_connection().get_session()


def close_database_connection():
    """Close global database connection."""
    global _db_connection
    if _db_connection is not None:
        _db_connection.close()
        _db_connection = None 
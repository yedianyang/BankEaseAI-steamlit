"""Database configuration and session management."""

from sqlalchemy import create_engine, event, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
from typing import Generator
import logging

from .config import settings

logger = logging.getLogger(__name__)

# Create database engine
if settings.DATABASE_URL.startswith("sqlite"):
    # SQLite-specific configuration
    engine = create_engine(
        settings.DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        echo=settings.DEBUG
    )

    # Enable WAL mode for SQLite
    @event.listens_for(engine, "connect")
    def set_sqlite_pragma(dbapi_conn, connection_record):
        cursor = dbapi_conn.cursor()
        cursor.execute("PRAGMA journal_mode=WAL")
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

else:
    # PostgreSQL or other database
    engine = create_engine(
        settings.DATABASE_URL,
        pool_size=settings.DB_POOL_SIZE,
        max_overflow=settings.DB_MAX_OVERFLOW,
        echo=settings.DEBUG
    )

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
Base = declarative_base()


def get_db() -> Generator[Session, None, None]:
    """Get database session.

    Yields:
        Database session

    Example:
        ```python
        from fastapi import Depends

        @app.get("/users")
        def get_users(db: Session = Depends(get_db)):
            return db.query(User).all()
        ```
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Initialize database.

    Creates all tables defined in models.
    """
    from .models import User, BankAccount, File, Transaction, UsageLog

    logger.info("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables created successfully")


def drop_db():
    """Drop all database tables.

    WARNING: This will delete all data!
    """
    logger.warning("Dropping all database tables...")
    Base.metadata.drop_all(bind=engine)
    logger.warning("All database tables dropped")


def reset_db():
    """Reset database (drop and recreate).

    WARNING: This will delete all data!
    """
    drop_db()
    init_db()
    logger.info("Database reset complete")


class DatabaseManager:
    """Database management utilities."""

    @staticmethod
    def create_tables():
        """Create all database tables."""
        init_db()

    @staticmethod
    def drop_tables():
        """Drop all database tables."""
        drop_db()

    @staticmethod
    def reset_tables():
        """Reset all database tables."""
        reset_db()

    @staticmethod
    def get_session() -> Session:
        """Get a new database session.

        Returns:
            Database session (must be closed manually)
        """
        return SessionLocal()

    @staticmethod
    def close_session(db: Session):
        """Close database session.

        Args:
            db: Database session to close
        """
        db.close()

    @staticmethod
    def test_connection() -> bool:
        """Test database connection.

        Returns:
            True if connection successful
        """
        try:
            db = SessionLocal()
            db.execute(text("SELECT 1"))
            db.close()
            logger.info("Database connection test successful")
            return True
        except Exception as e:
            logger.error(f"Database connection test failed: {e}")
            return False


# Convenience exports
db_manager = DatabaseManager()

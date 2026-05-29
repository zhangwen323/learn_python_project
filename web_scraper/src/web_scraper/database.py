"""Database engine creation, session management, and init."""

from pathlib import Path
from sqlalchemy import create_engine, Engine
from sqlalchemy.orm import Session

from .models import Base


def get_engine(db_path: str = "books.db") -> Engine:
    """Create a SQLAlchemy engine for SQLite."""
    return create_engine(f"sqlite:///{db_path}", echo=False)


def init_db(db_path: str = "books.db") -> None:
    """Create all tables if they don't exist."""
    engine = get_engine(db_path)
    Base.metadata.create_all(engine)


def get_session(db_path: str = "books.db") -> Session:
    """Return a new SQLAlchemy session."""
    engine = get_engine(db_path)
    return Session(engine)


def count_books(db_path: str = "books.db") -> int:
    """Return the total number of books in the database."""
    from .models import Book
    with get_session(db_path) as session:
        return session.query(Book).count()


def clear_books(db_path: str = "books.db") -> None:
    """Delete all books from the database."""
    from .models import Book
    with get_session(db_path) as session:
        session.query(Book).delete()
        session.commit()

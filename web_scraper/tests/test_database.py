"""Tests for database and pipeline modules."""

import pytest
from web_scraper.database import init_db, get_session, count_books, clear_books
from web_scraper.models import Book, Base
from web_scraper.pipeline import clean_price, clean_rating, bookdata_to_model
from web_scraper.scraper import BookData


def test_clean_price_standard():
    assert clean_price("£51.77") == 51.77


def test_clean_price_with_comma():
    assert clean_price("£1,234.56") == 1234.56


def test_clean_price_empty():
    assert clean_price("") is None


def test_clean_price_no_digits():
    assert clean_price("free") is None


def test_clean_rating():
    assert clean_rating("One") == 1
    assert clean_rating("Three") == 3
    assert clean_rating("Five") == 5


def test_clean_rating_invalid():
    assert clean_rating("Ten") is None
    assert clean_rating("") is None


def test_bookdata_to_model():
    data = BookData(
        title="Test Book",
        price_gbp="£10.99",
        rating_text="Four",
        availability="In stock",
        category="Fiction",
        image_url="http://example.com/img.jpg",
        detail_url="http://example.com/book/1",
    )
    book = bookdata_to_model(data)
    assert book.title == "Test Book"
    assert book.price_gbp == 10.99
    assert book.rating == 4
    assert book.category == "Fiction"


def test_init_db_creates_tables(tmp_path):
    db_path = str(tmp_path / "test.db")
    init_db(db_path)
    # Verify the file exists
    assert (tmp_path / "test.db").exists()


def test_insert_and_query(tmp_path):
    db_path = str(tmp_path / "test.db")
    init_db(db_path)

    with get_session(db_path) as session:
        book = Book(title="Hello", price_gbp=9.99, rating=3, category="Test")
        session.add(book)
        session.commit()

    assert count_books(db_path) == 1

    with get_session(db_path) as session:
        result = session.query(Book).first()
        assert result.title == "Hello"
        assert result.price_gbp == 9.99


def test_clear_books(tmp_path):
    db_path = str(tmp_path / "test.db")
    init_db(db_path)

    with get_session(db_path) as session:
        session.add(Book(title="A", price_gbp=1.0, rating=1, category="X"))
        session.add(Book(title="B", price_gbp=2.0, rating=2, category="Y"))
        session.commit()

    assert count_books(db_path) == 2
    clear_books(db_path)
    assert count_books(db_path) == 0


def test_unique_constraint(tmp_path):
    """Duplicate title+detail_url should be rejected."""
    db_path = str(tmp_path / "test.db")
    init_db(db_path)

    with get_session(db_path) as session:
        b1 = Book(title="Same", detail_url="http://x.com/1", price_gbp=1.0)
        b2 = Book(title="Same", detail_url="http://x.com/1", price_gbp=2.0)
        session.add(b1)
        session.commit()
        session.add(b2)
        import sqlalchemy.exc
        with pytest.raises(sqlalchemy.exc.IntegrityError):
            session.flush()

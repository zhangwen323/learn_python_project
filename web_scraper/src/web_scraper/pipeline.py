"""Pipeline: orchestrate scrape → clean → store."""

import logging
import re

from sqlalchemy.exc import IntegrityError

from .scraper import BookData, scrape_all_books
from .models import Book
from .database import get_session, init_db

logger = logging.getLogger(__name__)

# Map rating words to integers
RATING_MAP = {"One": 1, "Two": 2, "Three": 3, "Four": 4, "Five": 5}


def clean_price(price_str: str) -> float | None:
    """Convert '£51.77' → 51.77. Returns None on failure."""
    if not price_str:
        return None
    match = re.search(r"[\d,.]+", price_str)
    if not match:
        return None
    return float(match.group().replace(",", ""))


def clean_rating(rating_text: str) -> int | None:
    """Convert 'Three' → 3."""
    return RATING_MAP.get(rating_text)


def bookdata_to_model(data: BookData) -> Book:
    """Convert raw BookData to a SQLAlchemy Book model instance."""
    return Book(
        title=data.title,
        price_gbp=clean_price(data.price_gbp),
        rating=clean_rating(data.rating_text),
        availability=data.availability,
        category=data.category,
        image_url=data.image_url,
        detail_url=data.detail_url,
    )


def run_pipeline(db_path: str = "books.db", limit: int | None = None) -> int:
    """Run the full pipeline: scrape books, clean data, store to database.

    Returns the number of new books added.
    """
    init_db(db_path)

    logger.info("Starting scrape...")
    raw_books = scrape_all_books(limit=limit)
    logger.info("Scraped %d raw books", len(raw_books))

    new_count = 0
    skip_count = 0

    with get_session(db_path) as session:
        for data in raw_books:
            # Skip books with no title
            if not data.title:
                skip_count += 1
                continue

            book = bookdata_to_model(data)
            session.add(book)
            try:
                session.flush()  # trigger constraint check
                new_count += 1
            except IntegrityError:
                session.rollback()
                skip_count += 1

        session.commit()

    logger.info("Done: %d new books added, %d duplicates/skipped", new_count, skip_count)
    return new_count

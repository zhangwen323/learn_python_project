"""Tests for reports and export modules."""

import pandas as pd
from pathlib import Path

from web_scraper.reports import price_distribution, price_vs_rating, category_counts, rating_pie
from web_scraper.export import export_data
from web_scraper.database import init_db, get_session
from web_scraper.models import Book


def _make_sample_df() -> pd.DataFrame:
    """Create a sample DataFrame with known values for testing."""
    return pd.DataFrame({
        "id": range(1, 11),
        "title": [f"Book {i}" for i in range(1, 11)],
        "price_gbp": [10.0, 20.0, 30.0, 40.0, 50.0, 15.0, 25.0, 35.0, 45.0, 55.0],
        "rating": [1, 2, 3, 4, 5, 1, 2, 3, 4, 5],
        "availability": ["In stock"] * 10,
        "category": ["A"] * 5 + ["B"] * 3 + ["C"] * 2,
        "image_url": [""] * 10,
        "detail_url": [""] * 10,
    })


def test_price_distribution_creates_file(tmp_path):
    df = _make_sample_df()
    output_dir = str(tmp_path / "charts")
    path = price_distribution(df, output_dir)
    assert path.exists()
    assert path.suffix == ".png"


def test_price_vs_rating_creates_file(tmp_path):
    df = _make_sample_df()
    output_dir = str(tmp_path / "charts")
    path = price_vs_rating(df, output_dir)
    assert path.exists()


def test_category_counts_creates_file(tmp_path):
    df = _make_sample_df()
    output_dir = str(tmp_path / "charts")
    path = category_counts(df, output_dir, top_n=3)
    assert path.exists()


def test_rating_pie_creates_file(tmp_path):
    df = _make_sample_df()
    output_dir = str(tmp_path / "charts")
    path = rating_pie(df, output_dir)
    assert path.exists()


def test_export_csv(tmp_path):
    db_path = str(tmp_path / "test.db")
    init_db(db_path)

    with get_session(db_path) as session:
        for i in range(3):
            session.add(Book(title=f"B{i}", price_gbp=float(i * 10), rating=i + 1, category="X"))
        session.commit()

    output_path = str(tmp_path / "export.csv")
    path = export_data(db_path=db_path, fmt="csv", output_path=output_path)
    assert path.exists()
    content = Path(path).read_text()
    assert "B0" in content
    assert "B2" in content


def test_export_json(tmp_path):
    db_path = str(tmp_path / "test.db")
    init_db(db_path)

    with get_session(db_path) as session:
        session.add(Book(title="Test", price_gbp=9.99, rating=4, category="Fiction"))
        session.commit()

    output_path = str(tmp_path / "export.json")
    path = export_data(db_path=db_path, fmt="json", output_path=output_path)
    assert path.exists()
    content = Path(path).read_text()
    assert '"title":"Test"' in content
    assert '"price_gbp":9.99' in content

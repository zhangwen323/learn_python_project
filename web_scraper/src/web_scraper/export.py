"""Export book data to CSV or JSON."""

import csv
import json
from pathlib import Path

from .reports import load_books_df


def to_csv(df, output_path: str = "output/books.csv") -> Path:
    """Export the books DataFrame to CSV."""
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_path, index=False, quoting=csv.QUOTE_NONNUMERIC)
    return Path(output_path)


def to_json(df, output_path: str = "output/books.json") -> Path:
    """Export the books DataFrame to JSON (records format)."""
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    df.to_json(output_path, orient="records", indent=2, force_ascii=False)
    return Path(output_path)


def export_data(db_path: str = "books.db", fmt: str = "csv", output_path: str | None = None) -> Path:
    """Load data from DB and export in the given format."""
    df = load_books_df(db_path)

    if df.empty:
        raise ValueError("No data in database. Run 'scrape' first.")

    if output_path is None:
        output_path = f"output/books.{fmt}"

    if fmt == "csv":
        return to_csv(df, output_path)
    elif fmt == "json":
        return to_json(df, output_path)
    else:
        raise ValueError(f"Unsupported format: {fmt}. Use 'csv' or 'json'.")

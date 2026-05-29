"""Generate visualization reports from scraped book data."""

from pathlib import Path

import pandas as pd
import matplotlib
matplotlib.use("Agg")  # non-interactive backend
import matplotlib.pyplot as plt
import seaborn as sns

from .database import get_engine


def load_books_df(db_path: str = "books.db") -> pd.DataFrame:
    """Load all books from the database into a pandas DataFrame."""
    engine = get_engine(db_path)
    return pd.read_sql_table("books", engine)


def price_distribution(df: pd.DataFrame, output_dir: str = "output") -> Path:
    """Histogram of book prices."""
    Path(output_dir).mkdir(parents=True, exist_ok=True)

    valid = df[df["price_gbp"].notna()]

    fig, ax = plt.subplots(figsize=(10, 6))
    ax.hist(valid["price_gbp"], bins=30, color="steelblue", edgecolor="white", alpha=0.85)
    ax.set_xlabel("Price (£)")
    ax.set_ylabel("Number of Books")
    ax.set_title("Book Price Distribution")

    # Add summary stats
    mean_price = valid["price_gbp"].mean()
    median_price = valid["price_gbp"].median()
    ax.axvline(mean_price, color="red", linestyle="--", label=f"Mean: £{mean_price:.2f}")
    ax.axvline(median_price, color="orange", linestyle="--", label=f"Median: £{median_price:.2f}")
    ax.legend()

    output_path = Path(output_dir) / "price_distribution.png"
    fig.savefig(output_path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    return output_path


def price_vs_rating(df: pd.DataFrame, output_dir: str = "output") -> Path:
    """Scatter plot of price vs rating."""
    Path(output_dir).mkdir(parents=True, exist_ok=True)

    valid = df[df["price_gbp"].notna() & df["rating"].notna()]

    fig, ax = plt.subplots(figsize=(10, 6))
    sns.boxplot(data=valid, x="rating", y="price_gbp", hue="rating", palette="Blues", legend=False, ax=ax)
    ax.set_xlabel("Rating (stars)")
    ax.set_ylabel("Price (£)")
    ax.set_title("Book Price by Star Rating")

    output_path = Path(output_dir) / "price_vs_rating.png"
    fig.savefig(output_path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    return output_path


def category_counts(df: pd.DataFrame, output_dir: str = "output", top_n: int = 15) -> Path:
    """Bar chart of book counts per category (top N)."""
    Path(output_dir).mkdir(parents=True, exist_ok=True)

    counts = df["category"].value_counts().head(top_n)

    fig, ax = plt.subplots(figsize=(12, 6))
    colors = sns.color_palette("viridis", n_colors=len(counts))
    bars = ax.barh(range(len(counts)), counts.values, color=colors)

    ax.set_yticks(range(len(counts)))
    ax.set_yticklabels(counts.index)
    ax.invert_yaxis()  # top category at top
    ax.set_xlabel("Number of Books")
    ax.set_title(f"Top {top_n} Categories by Book Count")

    # Add count labels
    for bar, count in zip(bars, counts.values):
        ax.text(bar.get_width() + 1, bar.get_y() + bar.get_height() / 2,
                str(count), va="center", fontsize=9)

    output_path = Path(output_dir) / "category_counts.png"
    fig.savefig(output_path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    return output_path


def rating_pie(df: pd.DataFrame, output_dir: str = "output") -> Path:
    """Pie chart of star rating distribution."""
    Path(output_dir).mkdir(parents=True, exist_ok=True)

    valid = df[df["rating"].notna()]
    rating_counts = valid["rating"].value_counts().sort_index()

    labels = [f"{int(r)} Star{'' if r == 1 else 's'}" for r in rating_counts.index]

    fig, ax = plt.subplots(figsize=(8, 8))
    colors = sns.color_palette("YlOrRd", n_colors=len(rating_counts))
    wedges, texts, autotexts = ax.pie(
        rating_counts.values,
        labels=labels,
        autopct="%1.1f%%",
        colors=colors,
        startangle=90,
        pctdistance=0.75,
    )
    for t in autotexts:
        t.set_fontsize(11)
    ax.set_title("Star Rating Distribution")

    output_path = Path(output_dir) / "rating_pie.png"
    fig.savefig(output_path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    return output_path


def generate_all_reports(db_path: str = "books.db", output_dir: str = "output") -> list[Path]:
    """Generate all 4 report charts. Returns list of output file paths."""
    df = load_books_df(db_path)

    if df.empty:
        raise ValueError("No data in database. Run 'scrape' first.")

    paths = [
        price_distribution(df, output_dir),
        price_vs_rating(df, output_dir),
        category_counts(df, output_dir),
        rating_pie(df, output_dir),
    ]
    return paths

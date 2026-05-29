# Web Scraper + Visualization

A CLI tool to scrape book data from [books.toscrape.com](http://books.toscrape.com), store in SQLite, and generate visualization reports.

## Installation

```bash
cd web_scraper
pip install -e .
```

## Usage

### Scrape

```bash
# Scrape all books (~1000) from all categories
web-scraper scrape

# Limit to N books for a quick test
web-scraper scrape --limit 200

# Use a custom database path
web-scraper scrape --db my_books.db
```

### Reports

```bash
# Generate all 4 charts (price distribution, price vs rating, category counts, rating pie)
web-scraper report --all

# Generate a single chart
web-scraper report --type price
web-scraper report --type category

# Custom output directory
web-scraper report --all --output my_charts/
```

### Export

```bash
# Export to CSV
web-scraper export --format csv

# Export to JSON
web-scraper export --format json --output data/books.json
```

## Project Initialization

`pyproject.toml` is a **tool-agnostic** project metadata standard — pip, uv, pdm, and poetry all understand it.

```bash
cd web_scraper
pip install -e .            # editable install
pip install -e ".[dev]"     # with test dependencies
```

### Why editable install (`-e`)?

Without `-e`, pip copies source to `site-packages` — every code change requires reinstall. With `-e`, a link is placed instead, so Python imports directly from the `src/` directory.

## How It Runs

Two invocation methods, both calling `cli.main()`:

| Command | Mechanism |
|---------|-----------|
| `web-scraper` | Entry point declared in `pyproject.toml` — setuptools generates an executable script on `pip install` |
| `python -m web_scraper` | Python runs `__main__.py` inside the package |

## Data Pipeline

```
scraper.py          pipeline.py         models.py            reports.py
  httpx + BS4   →   clean + store   →   SQLAlchemy ORM   →   matplotlib charts
  follow links      deduplicate          SQLite storage       export CSV/JSON
```

The pipeline skeleton is data-source agnostic. To scrape a different website, rewrite `scraper.py` — everything else (database, cleaning, visualization, export) stays the same.

## Report Types

| Chart | File | Description |
|-------|------|-------------|
| Price Distribution | `price_distribution.png` | Histogram with mean/median lines |
| Price vs Rating | `price_vs_rating.png` | Box plot grouped by star rating |
| Category Counts | `category_counts.png` | Horizontal bar chart (top 15 categories) |
| Rating Pie | `rating_pie.png` | Pie chart of 1-5 star distribution |

## Project Structure

```
web_scraper/
├── pyproject.toml
├── README.md
├── src/
│   └── web_scraper/
│       ├── __init__.py      # Package init, version
│       ├── __main__.py      # python -m entry point
│       ├── cli.py           # argparse subcommands + rich output
│       ├── scraper.py       # httpx + BeautifulSoup, pagination
│       ├── models.py        # SQLAlchemy ORM Book model
│       ├── database.py      # Engine, session, init_db
│       ├── pipeline.py      # scrape → clean → store
│       ├── reports.py       # matplotlib + seaborn charts
│       └── export.py        # CSV / JSON export
├── tests/
│   ├── test_scraper.py
│   ├── test_database.py
│   └── test_reports.py
└── output/                  # Generated charts + exports
```

## Running Tests

```bash
pip install -e ".[dev]"
python -m pytest tests/ -v
```

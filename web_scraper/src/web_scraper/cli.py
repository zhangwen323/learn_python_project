"""Command-line interface with subcommands: scrape, report, export."""

import argparse
import logging
import sys
from pathlib import Path

from rich.console import Console
from rich.table import Table
from rich.panel import Panel

from .pipeline import run_pipeline
from .database import count_books
from .reports import generate_all_reports, price_distribution, price_vs_rating, category_counts, rating_pie, load_books_df
from .export import export_data

console = Console()


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="web-scraper",
        description="Scrape book data and generate visualizations",
    )
    sub = parser.add_subparsers(dest="command", help="Available commands")

    # --- scrape ---
    scrape_parser = sub.add_parser("scrape", help="Scrape books and store to database")
    scrape_parser.add_argument(
        "--db", default="books.db", help="SQLite database path (default: books.db)"
    )
    scrape_parser.add_argument(
        "--limit", type=int, default=None, help="Limit the number of books to scrape"
    )

    # --- report ---
    report_parser = sub.add_parser("report", help="Generate visualization charts")
    report_parser.add_argument(
        "--db", default="books.db", help="SQLite database path (default: books.db)"
    )
    report_parser.add_argument(
        "--output", "-o", default="output", help="Output directory for charts (default: output/)"
    )
    report_parser.add_argument(
        "--all", action="store_true", help="Generate all 4 report types"
    )
    report_parser.add_argument(
        "--type", choices=["price", "rating", "category", "pie"],
        help="Generate a single report type"
    )

    # --- export ---
    export_parser = sub.add_parser("export", help="Export data to CSV or JSON")
    export_parser.add_argument(
        "--db", default="books.db", help="SQLite database path (default: books.db)"
    )
    export_parser.add_argument(
        "--format", "-f", choices=["csv", "json"], default="csv",
        help="Export format (default: csv)"
    )
    export_parser.add_argument(
        "--output", "-o", default=None, help="Output file path"
    )

    return parser


def cmd_scrape(args: argparse.Namespace) -> None:
    console.print(Panel.fit("[bold]Web Scraper — Scrape Mode[/bold]", border_style="cyan"))
    console.print(f"Database: [dim]{args.db}[/dim]")

    try:
        count = run_pipeline(db_path=args.db, limit=args.limit)
        total = count_books(args.db)
        console.print(f"\n[bold green]Done![/bold green] {count} new books added.")
        console.print(f"Total books in database: [bold]{total}[/bold]")
    except Exception as e:
        console.print(f"[red]Error during scrape:[/red] {e}")
        sys.exit(1)


def cmd_report(args: argparse.Namespace) -> None:
    console.print(Panel.fit("[bold]Web Scraper — Report Mode[/bold]", border_style="magenta"))

    try:
        df = load_books_df(args.db)
    except Exception as e:
        console.print(f"[red]Error loading database:[/red] {e}")
        sys.exit(1)

    if df.empty:
        console.print("[yellow]No data in database. Run 'web-scraper scrape' first.[/yellow]")
        return

    console.print(f"Loaded [bold]{len(df)}[/bold] books from [dim]{args.db}[/dim]\n")

    if args.type:
        report_funcs = {
            "price": price_distribution,
            "rating": price_vs_rating,
            "category": category_counts,
            "pie": rating_pie,
        }
        path = report_funcs[args.type](df, args.output)
        console.print(f"[green]Report saved:[/green] {path}")
    elif args.all:
        paths = generate_all_reports(args.db, args.output)
        console.print("[green]All reports generated:[/green]")
        for p in paths:
            console.print(f"  - {p}")
    else:
        console.print("[yellow]Use --all to generate all reports, or --type to pick one.[/yellow]")


def cmd_export(args: argparse.Namespace) -> None:
    console.print(Panel.fit("[bold]Web Scraper — Export Mode[/bold]", border_style="green"))

    try:
        path = export_data(db_path=args.db, fmt=args.format, output_path=args.output)
        console.print(f"[green]Data exported to:[/green] {path}")
    except ValueError as e:
        console.print(f"[yellow]{e}[/yellow]")
    except Exception as e:
        console.print(f"[red]Error during export:[/red] {e}")
        sys.exit(1)


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    if args.command == "scrape":
        cmd_scrape(args)
    elif args.command == "report":
        cmd_report(args)
    elif args.command == "export":
        cmd_export(args)
    else:
        parser.print_help()

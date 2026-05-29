"""Command-line interface for file-organizer."""

import argparse
import logging
from pathlib import Path

from rich.console import Console
from rich.progress import track
from rich.table import Table
from rich import print as rprint

from .organizer import scan_files, execute_actions
from .config import load_custom_rules

console = Console()


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="file-organizer",
        description="Organize files in a directory by type (images, documents, videos, etc.)",
    )
    parser.add_argument(
        "directory",
        nargs="?",
        default=".",
        help="Target directory to organize (default: current directory)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview changes without actually moving files",
    )
    parser.add_argument(
        "--config",
        type=Path,
        default=None,
        help="Path to a YAML config file with custom extension-to-category rules",
    )
    parser.add_argument(
        "--conflict",
        choices=["rename", "skip", "overwrite"],
        default="rename",
        help="How to handle file name conflicts (default: rename)",
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Show detailed output including all file moves",
    )
    parser.add_argument(
        "--version",
        action="version",
        version="%(prog)s 0.1.0",
    )
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    directory = Path(args.directory).resolve()

    if not directory.exists():
        console.print(f"[red]Error:[/red] Directory not found: {directory}")
        raise SystemExit(1)

    if not directory.is_dir():
        console.print(f"[red]Error:[/red] Not a directory: {directory}")
        raise SystemExit(1)

    # Load custom rules
    try:
        custom_rules = load_custom_rules(args.config)
    except (FileNotFoundError, ValueError) as e:
        console.print(f"[red]Error loading config:[/red] {e}")
        raise SystemExit(1)

    # Scan
    console.print(f"\n[bold]Scanning[/bold] {directory} ...")
    actions = scan_files(directory, custom_rules)

    if not actions:
        console.print("[yellow]No files found to organize.[/yellow]")
        return

    # Show summary
    _print_summary(actions)

    if args.dry_run:
        console.print("\n[bold yellow]--- Dry Run: No files will be moved ---[/bold yellow]\n")
        _print_action_table(actions)
        return

    # Confirm
    console.print(f"\n[bold]Ready to organize {len(actions)} file(s).[/bold]")
    response = input("Proceed? [y/N]: ").strip().lower()
    if response not in ("y", "yes"):
        console.print("[dim]Cancelled.[/dim]")
        return

    # Execute
    results = execute_actions(actions, dry_run=False, on_conflict=args.conflict)

    moved = sum(1 for _, s in results if s in ("moved", "overwritten", "renamed"))
    skipped = sum(1 for _, s in results if s == "skipped")

    console.print(f"\n[bold green]Done:[/bold green] {moved} file(s) organized", end="")
    if skipped:
        console.print(f", [yellow]{skipped} skipped[/yellow]")
    else:
        console.print()

    if args.verbose:
        _print_result_table(results)


def _print_summary(actions: list) -> None:
    """Print a category summary of planned actions."""
    from collections import Counter
    counts = Counter(a.category for a in actions)

    table = Table(title="Summary by Category")
    table.add_column("Category", style="cyan")
    table.add_column("Count", style="green", justify="right")

    for cat, count in sorted(counts.items()):
        table.add_row(cat, str(count))

    table.add_row("", "---")
    table.add_row("[bold]Total[/bold]", f"[bold]{len(actions)}[/bold]")
    console.print(table)


def _print_action_table(actions: list) -> None:
    """Print a detailed table of planned moves."""
    table = Table(title="Planned Moves", show_lines=False)
    table.add_column("File", style="white")
    table.add_column("Category", style="cyan")
    table.add_column("Target", style="dim")

    for a in actions:
        table.add_row(a.source.name, a.category, str(a.target.relative_to(a.source.parent.parent)))

    console.print(table)


def _print_result_table(results: list) -> None:
    """Print results after execution."""
    table = Table(title="Results")
    table.add_column("File", style="white")
    table.add_column("Status", style="green")
    table.add_column("Target", style="dim")

    status_styles = {
        "moved": "green",
        "renamed": "yellow",
        "overwritten": "magenta",
        "skipped": "dim",
    }

    for action, status in results:
        style = status_styles.get(status, "white")
        table.add_row(
            action.source.name,
            f"[{style}]{status}[/{style}]",
            str(action.target),
        )

    console.print(table)

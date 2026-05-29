"""Core file organizing logic: scan, classify, preview, move."""

from pathlib import Path
from dataclasses import dataclass

from .rules import resolve_category, get_target_dir


@dataclass
class FileAction:
    """Represents a planned or executed file move."""
    source: Path
    target: Path
    category: str


def scan_files(
    directory: Path,
    custom_rules: dict[str, str] | None = None,
    exclude_dirs: set[str] | None = None,
) -> list[FileAction]:
    """Scan a directory and build a list of planned moves.

    Skips directories and hidden files. Files without extensions go to 'others'.
    """
    if exclude_dirs is None:
        exclude_dirs = set()

    actions: list[FileAction] = []

    for item in directory.iterdir():
        if item.is_dir():
            continue
        if item.name.startswith("."):
            continue

        suffix = item.suffix
        category = resolve_category(suffix, custom_rules)
        target_dir = get_target_dir(directory, category)
        target_path = target_dir / item.name

        # Skip if the target dir is inside the source file's path (shouldn't happen,
        # but guard against edge cases like already-organized files)
        if target_path == item:
            continue

        actions.append(
            FileAction(source=item, target=target_path, category=category)
        )

    return actions


def execute_actions(
    actions: list[FileAction],
    dry_run: bool = False,
    on_conflict: str = "rename",
) -> list[tuple[FileAction, str]]:
    """Execute a list of file moves. Returns results with status.

    on_conflict:
        - "rename": append a counter to the filename (default)
        - "skip": skip the file
        - "overwrite": replace the existing file
    """
    results: list[tuple[FileAction, str]] = []

    for action in actions:
        target = action.target
        status = "moved"

        if target.exists():
            if on_conflict == "skip":
                results.append((action, "skipped"))
                continue
            elif on_conflict == "overwrite":
                if not dry_run:
                    target.unlink()
                status = "overwritten"
            else:  # rename
                target = _resolve_name(action.target)
                action = FileAction(
                    source=action.source, target=target, category=action.category
                )
                status = "renamed"

        if not dry_run:
            target.parent.mkdir(parents=True, exist_ok=True)
            action.source.rename(target)

        results.append((action, status))

    return results


def _resolve_name(target: Path) -> Path:
    """Append a counter to filename if it already exists, e.g. 'file (1).txt'."""
    stem = target.stem
    suffix = target.suffix
    parent = target.parent
    counter = 1

    while True:
        new_name = f"{stem} ({counter}){suffix}"
        new_path = parent / new_name
        if not new_path.exists():
            return new_path
        counter += 1

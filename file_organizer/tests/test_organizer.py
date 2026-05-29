"""Tests for the core organizer logic."""

import tempfile
from pathlib import Path

from file_organizer.organizer import scan_files, execute_actions, FileAction


def _make_files(tmp_path: Path, *names: str) -> list[Path]:
    """Helper: create empty files and return their paths."""
    paths = []
    for name in names:
        p = tmp_path / name
        p.write_text("")
        paths.append(p)
    return paths


def test_scan_files_with_default_rules(tmp_path: Path):
    _make_files(tmp_path, "photo.jpg", "doc.pdf", "song.mp3", "code.py")

    actions = scan_files(tmp_path)

    categories = {a.source.name: a.category for a in actions}
    assert categories["photo.jpg"] == "images"
    assert categories["doc.pdf"] == "documents"
    assert categories["song.mp3"] == "audio"
    assert categories["code.py"] == "code"


def test_scan_files_unknown_extension(tmp_path: Path):
    _make_files(tmp_path, "mystery.abcdef")
    actions = scan_files(tmp_path)
    assert len(actions) == 1
    assert actions[0].category == "others"


def test_scan_files_skips_directories(tmp_path: Path):
    (tmp_path / "subdir").mkdir()
    _make_files(tmp_path, "file.txt")

    actions = scan_files(tmp_path)
    assert len(actions) == 1
    assert actions[0].source.name == "file.txt"


def test_scan_files_skips_hidden_files(tmp_path: Path):
    _make_files(tmp_path, ".hidden", "visible.txt")

    actions = scan_files(tmp_path)
    names = {a.source.name for a in actions}
    assert ".hidden" not in names
    assert "visible.txt" in names


def test_scan_files_with_custom_rules(tmp_path: Path):
    _make_files(tmp_path, "data.csv")
    custom = {".csv": "spreadsheets"}

    actions = scan_files(tmp_path, custom_rules=custom)
    assert actions[0].category == "spreadsheets"


def test_dry_run_does_not_move(tmp_path: Path):
    _make_files(tmp_path, "photo.jpg", "notes.txt")

    actions = scan_files(tmp_path)
    results = execute_actions(actions, dry_run=True)

    assert len(results) == 2
    # Files should still be in original location
    assert (tmp_path / "photo.jpg").exists()
    assert (tmp_path / "notes.txt").exists()
    # Target dirs should NOT be created in dry-run
    assert not (tmp_path / "images").exists()
    assert not (tmp_path / "documents").exists()


def test_execute_moves_files(tmp_path: Path):
    _make_files(tmp_path, "photo.jpg", "notes.txt")

    actions = scan_files(tmp_path)
    results = execute_actions(actions, dry_run=False)

    assert len(results) == 2
    assert not (tmp_path / "photo.jpg").exists()
    assert not (tmp_path / "notes.txt").exists()
    assert (tmp_path / "images" / "photo.jpg").exists()
    assert (tmp_path / "documents" / "notes.txt").exists()


def test_conflict_rename(tmp_path: Path):
    """When a file already exists in target, rename should append a counter."""
    _make_files(tmp_path, "photo.jpg")
    (tmp_path / "images").mkdir()
    (tmp_path / "images" / "photo.jpg").write_text("existing")

    actions = scan_files(tmp_path)
    results = execute_actions(actions, dry_run=False, on_conflict="rename")

    action, status = results[0]
    assert status == "renamed"
    assert (tmp_path / "images" / "photo (1).jpg").exists()
    assert action.target.name == "photo (1).jpg"


def test_conflict_skip(tmp_path: Path):
    _make_files(tmp_path, "photo.jpg")
    (tmp_path / "images").mkdir()
    (tmp_path / "images" / "photo.jpg").write_text("existing")

    actions = scan_files(tmp_path)
    results = execute_actions(actions, dry_run=False, on_conflict="skip")

    _, status = results[0]
    assert status == "skipped"
    assert (tmp_path / "photo.jpg").exists()  # not moved


def test_conflict_overwrite(tmp_path: Path):
    _make_files(tmp_path, "photo.jpg")
    (tmp_path / "images").mkdir()
    (tmp_path / "images" / "photo.jpg").write_text("existing")

    actions = scan_files(tmp_path)
    results = execute_actions(actions, dry_run=False, on_conflict="overwrite")

    _, status = results[0]
    assert status == "overwritten"
    assert not (tmp_path / "photo.jpg").exists()
    assert (tmp_path / "images" / "photo.jpg").exists()


def test_empty_directory(tmp_path: Path):
    actions = scan_files(tmp_path)
    assert actions == []


def test_target_path_correct(tmp_path: Path):
    _make_files(tmp_path, "script.py")
    actions = scan_files(tmp_path)
    assert actions[0].target == tmp_path / "code" / "script.py"
    assert actions[0].source == tmp_path / "script.py"

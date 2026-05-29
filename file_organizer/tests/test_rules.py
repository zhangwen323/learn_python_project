"""Tests for the rules engine."""

import pytest
from pathlib import Path
from file_organizer.rules import resolve_category, get_target_dir, DEFAULT_RULES


def test_known_extensions():
    assert resolve_category(".jpg") == "images"
    assert resolve_category(".pdf") == "documents"
    assert resolve_category(".mp4") == "videos"
    assert resolve_category(".mp3") == "audio"
    assert resolve_category(".zip") == "archives"
    assert resolve_category(".py") == "code"
    assert resolve_category(".exe") == "binaries"


def test_unknown_extension():
    assert resolve_category(".xyz") == "others"


def test_no_extension():
    assert resolve_category("") == "others"


def test_case_insensitive():
    assert resolve_category(".JPG") == "images"
    assert resolve_category(".Pdf") == "documents"


def test_custom_rules_override():
    custom = {".txt": "notes", ".jpg": "photos"}
    assert resolve_category(".txt", custom) == "notes"
    assert resolve_category(".jpg", custom) == "photos"
    assert resolve_category(".pdf", custom) == "documents"  # fallback


def test_get_target_dir():
    base = Path("/home/user/downloads")
    assert get_target_dir(base, "images") == Path("/home/user/downloads/images")


def test_default_rules_are_comprehensive():
    assert len(DEFAULT_RULES) > 40
    assert all(k.startswith(".") for k in DEFAULT_RULES)
    assert all(v for v in DEFAULT_RULES.values())

"""Tests for config loading."""

import tempfile
from pathlib import Path

import pytest
import yaml

from file_organizer.config import load_custom_rules


def test_load_valid_config():
    config_path = Path(tempfile.mktemp(suffix=".yaml"))
    config_path.write_text(".csv: spreadsheets\n.txt: notes\n", encoding="utf-8")
    try:
        rules = load_custom_rules(config_path)
        assert rules == {".csv": "spreadsheets", ".txt": "notes"}
    finally:
        config_path.unlink()


def test_empty_config():
    config_path = Path(tempfile.mktemp(suffix=".yaml"))
    config_path.write_text("", encoding="utf-8")
    try:
        rules = load_custom_rules(config_path)
        assert rules == {}
    finally:
        config_path.unlink()


def test_none_config():
    assert load_custom_rules(None) == {}


def test_missing_file():
    with pytest.raises(FileNotFoundError):
        load_custom_rules(Path("/nonexistent/config.yaml"))


def test_auto_add_dot_prefix():
    config_path = Path(tempfile.mktemp(suffix=".yaml"))
    config_path.write_text("csv: data\n", encoding="utf-8")
    try:
        rules = load_custom_rules(config_path)
        assert rules == {".csv": "data"}
    finally:
        config_path.unlink()


def test_invalid_format():
    config_path = Path(tempfile.mktemp(suffix=".yaml"))
    config_path.write_text("- item1\n- item2\n", encoding="utf-8")
    try:
        with pytest.raises(ValueError, match="mapping"):
            load_custom_rules(config_path)
    finally:
        config_path.unlink()

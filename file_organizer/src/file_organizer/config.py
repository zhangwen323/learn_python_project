"""Configuration loading from YAML files."""

from pathlib import Path

import yaml


def load_custom_rules(config_path: Path | None) -> dict[str, str]:
    """Load custom extension-to-category mapping from a YAML config file.

    Expected format:
        .jpg: images
        .txt: notes
        .py: scripts
    """
    if config_path is None:
        return {}

    if not config_path.exists():
        raise FileNotFoundError(f"Config file not found: {config_path}")

    with open(config_path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)

    if data is None:
        return {}

    if not isinstance(data, dict):
        raise ValueError("Config file must contain a YAML mapping")

    rules: dict[str, str] = {}
    for key, value in data.items():
        if not isinstance(key, str) or not isinstance(value, str):
            raise ValueError(f"Invalid rule entry: {key}={value}, both must be strings")
        key = key.strip().lower()
        if not key.startswith("."):
            key = f".{key}"
        rules[key] = value.strip().lower()

    return rules

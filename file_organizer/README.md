# File Organizer

A CLI tool to automatically organize files in a directory by type (images, documents, videos, code, etc.).

## Installation

```bash
cd file_organizer
pip install -e .
```

## Usage

```bash
# Preview changes without moving anything
file-organizer . --dry-run

# Show detailed preview
file-organizer ~/Downloads --dry-run --verbose

# Execute organization
file-organizer ~/Downloads

# Use custom category rules
file-organizer . --config my_rules.yaml

# Conflict handling: rename (default), skip, or overwrite
file-organizer . --conflict rename
```

## Project Initialization

`pyproject.toml` is a **tool-agnostic** project metadata standard — pip, uv, pdm, and poetry all understand it. It does not mean the project was built with uv.

### With pip (current)

```bash
cd file_organizer
pip install -e .            # editable install, code changes take effect immediately
pip install -e ".[dev]"     # with test dependencies (pytest)
```

### With uv (faster alternative)

```bash
cd file_organizer
uv sync                     # auto-creates venv + installs deps
uv run file-organizer . --dry-run
```

If migrating to uv, the `[build-system]` block in `pyproject.toml` would switch from `setuptools` to `hatchling` or `flit-core`, but the rest of the file stays the same.

### Why editable install (`-e`)?

Without `-e`, pip copies the source to `site-packages` — every code change requires reinstall. With `-e`, a link is placed instead, so Python imports directly from the `src/` directory. Edit code, run immediately.

---

## How It Runs

Two invocation methods, both calling `cli.main()`:

| Command | Mechanism |
|---------|-----------|
| `file-organizer` | Entry point declared in `pyproject.toml` line 22 — setuptools generates an executable script on `pip install` |
| `python -m file_organizer` | Python runs `__main__.py` inside the package |

**`pyproject.toml` entry point:**

```toml
[project.scripts]
file-organizer = "file_organizer.cli:main"
```

This tells setuptools: "create a command named `file-organizer` that imports `main` from `file_organizer.cli` and calls it." The generated script is placed in your Python environment's `bin/` (or `Scripts/` on Windows) and becomes available on `PATH`.

**`__main__.py`:**

```python
from .cli import main
main()
```

When you run `python -m file_organizer`, Python looks for `__main__.py` in the package and executes it. Useful during development when you don't want to reinstall after every change (the `-e` editable install already handles this, but `-m` works without any install).

## Default Categories

| Category | Extensions |
|----------|------------|
| images | .jpg, .jpeg, .png, .gif, .bmp, .svg, .webp, .ico, .tiff, .tif, .raw |
| documents | .pdf, .doc, .docx, .xls, .xlsx, .ppt, .pptx, .txt, .md, .rst, .csv, .json, .xml, .yaml, .yml, .toml |
| videos | .mp4, .mkv, .avi, .mov, .wmv, .flv, .webm, .m4v |
| audio | .mp3, .wav, .flac, .aac, .ogg, .wma, .m4a |
| archives | .zip, .tar, .gz, .bz2, .xz, .7z, .rar |
| code | .py, .js, .ts, .jsx, .tsx, .java, .c, .cpp, .h, .hpp, .rs, .go, .rb, .php, .html, .css, .scss, .sql, .sh, .bat, .ps1 |
| binaries | .exe, .dll, .so, .dylib, .bin, .msi |

Files with unrecognized extensions go to `others/`. Hidden files (starting with `.`) are skipped.

## Custom Rules

Create a YAML file to override or extend default category mappings:

```yaml
# my_rules.yaml
.csv: spreadsheets
.txt: notes
.jpg: photos
```

Then run:

```bash
file-organizer . --config my_rules.yaml
```

Keys without a leading dot get one added automatically (`csv` → `.csv`).

## Project Structure

```
file_organizer/
├── pyproject.toml
├── README.md
├── src/
│   └── file_organizer/
│       ├── __init__.py      # Package init, version
│       ├── __main__.py      # python -m entry point
│       ├── cli.py           # argparse + rich output
│       ├── organizer.py     # Core scan / classify / move logic
│       ├── rules.py         # Default extension → category map
│       └── config.py        # YAML config loader
└── tests/
    ├── test_rules.py
    ├── test_config.py
    └── test_organizer.py
```

## Running Tests

```bash
pip install -e ".[dev]"
python -m pytest tests/ -v
```

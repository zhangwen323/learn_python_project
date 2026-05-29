"""Default rules and rule resolution for file categorization."""

from pathlib import Path

DEFAULT_RULES: dict[str, str] = {
    # Images
    ".jpg": "images",
    ".jpeg": "images",
    ".png": "images",
    ".gif": "images",
    ".bmp": "images",
    ".svg": "images",
    ".webp": "images",
    ".ico": "images",
    ".tiff": "images",
    ".tif": "images",
    ".raw": "images",
    # Documents
    ".pdf": "documents",
    ".doc": "documents",
    ".docx": "documents",
    ".xls": "documents",
    ".xlsx": "documents",
    ".ppt": "documents",
    ".pptx": "documents",
    ".txt": "documents",
    ".md": "documents",
    ".rst": "documents",
    ".csv": "documents",
    ".json": "documents",
    ".xml": "documents",
    ".yaml": "documents",
    ".yml": "documents",
    ".toml": "documents",
    # Videos
    ".mp4": "videos",
    ".mkv": "videos",
    ".avi": "videos",
    ".mov": "videos",
    ".wmv": "videos",
    ".flv": "videos",
    ".webm": "videos",
    ".m4v": "videos",
    # Audio
    ".mp3": "audio",
    ".wav": "audio",
    ".flac": "audio",
    ".aac": "audio",
    ".ogg": "audio",
    ".wma": "audio",
    ".m4a": "audio",
    # Archives
    ".zip": "archives",
    ".tar": "archives",
    ".gz": "archives",
    ".bz2": "archives",
    ".xz": "archives",
    ".7z": "archives",
    ".rar": "archives",
    # Code
    ".py": "code",
    ".js": "code",
    ".ts": "code",
    ".jsx": "code",
    ".tsx": "code",
    ".java": "code",
    ".c": "code",
    ".cpp": "code",
    ".h": "code",
    ".hpp": "code",
    ".rs": "code",
    ".go": "code",
    ".rb": "code",
    ".php": "code",
    ".html": "code",
    ".css": "code",
    ".scss": "code",
    ".sql": "code",
    ".sh": "code",
    ".bat": "code",
    ".ps1": "code",
    # Executables / Binaries
    ".exe": "binaries",
    ".dll": "binaries",
    ".so": "binaries",
    ".dylib": "binaries",
    ".bin": "binaries",
    ".msi": "binaries",
}


def resolve_category(extension: str, custom_rules: dict[str, str] | None = None) -> str:
    """Return the category for a file extension. Custom rules override defaults."""
    ext = extension.lower()
    if custom_rules and ext in custom_rules:
        return custom_rules[ext]
    return DEFAULT_RULES.get(ext, "others")


def get_target_dir(base_path: Path, category: str) -> Path:
    """Return the target directory for a given category."""
    return base_path / category

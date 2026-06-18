# tools/scan.py
"""
Scan a directory relative to PROJECT_ROOT.
"""

from pathlib import Path
from config import PROJECT_ROOT
from tools.utils import safe_resolve  # Import fungsi terpusat


def scan_directory(raw_path: str) -> str:
    """
    Scan and return a directory listing of `raw_path` (relative to PROJECT_ROOT).
    Returns an ERROR string on failure.
    """
    path = safe_resolve(raw_path)
    if path is None:
        return (
            f"ERROR: Path '{raw_path}' resolves outside the project root "
            f"({PROJECT_ROOT}). Only relative paths inside the project are allowed."
        )

    if not path.exists():
        return f"ERROR: Directory not found: '{path.relative_to(PROJECT_ROOT)}'"

    if not path.is_dir():
        return f"ERROR: '{raw_path}' is a file, not a directory. Use [READ:] instead."

    try:
        items = sorted(path.iterdir())
        files = [f"- {item.name}" for item in items]
        return f"SUCCESS: Directory scan → {path.relative_to(PROJECT_ROOT)}\n\n" + "\n".join(files)
    except PermissionError:
        return f"ERROR: Permission denied scanning '{raw_path}'."
    except Exception as exc:
        return f"ERROR: Unexpected error scanning '{raw_path}': {exc}"
# tools/read.py
"""
Read a file relative to PROJECT_ROOT.
Sanitises the path to prevent directory traversal and absolute path tricks.
"""

from pathlib import Path
from config import PROJECT_ROOT
from tools.utils import safe_resolve  # Import fungsi terpusat


def read_file(raw_path: str) -> str:
    """
    Read and return the contents of `raw_path` (relative to PROJECT_ROOT).

    Returns an ERROR string on failure so the agent can self-correct.
    """
    path = safe_resolve(raw_path)
    if path is None:
        return (
            f"ERROR: Path '{raw_path}' resolves outside the project root "
            f"({PROJECT_ROOT}). Only relative paths inside the project are allowed."
        )

    if not path.exists():
        return f"ERROR: File not found: '{path.relative_to(PROJECT_ROOT)}'"

    if not path.is_file():
        return f"ERROR: '{raw_path}' is a directory, not a file. Use [SCAN:] instead."

    try:
        content = path.read_text(encoding="utf-8")
        return content
    except UnicodeDecodeError:
        return f"ERROR: '{raw_path}' is a binary file and cannot be read as text."
    except PermissionError:
        return f"ERROR: Permission denied reading '{raw_path}'."
    except Exception as exc:
        return f"ERROR: Unexpected error reading '{raw_path}': {exc}"
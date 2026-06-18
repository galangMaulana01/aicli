# tools/utils.py
from pathlib import Path
from config import PROJECT_ROOT


def safe_resolve(raw_path: str) -> Path | None:
    """
    Resolve path relatif ke PROJECT_ROOT.
    Return None jika path keluar dari project root.
    """
    clean = raw_path.lstrip("/\\").strip()
    if clean == "" or clean == ".":
        return PROJECT_ROOT
    resolved = (PROJECT_ROOT / clean).resolve()
    try:
        resolved.relative_to(PROJECT_ROOT)
        return resolved
    except ValueError:
        return None

# tools/edit.py
"""
Write (create or overwrite) a file relative to PROJECT_ROOT.
Parent directories are created automatically.
"""

from pathlib import Path
from config import PROJECT_ROOT
from tools.utils import safe_resolve  # Import fungsi terpusat


def edit_file(raw_path: str, code: str) -> str:
    """
    Write `code` to `raw_path` (relative to PROJECT_ROOT).

    Returns a success or ERROR string.
    """
    path = safe_resolve(raw_path)
    if path is None:
        return (
            f"ERROR: Path '{raw_path}' resolves outside the project root. "
            "Only relative paths inside the project are allowed."
        )

    # Guard against accidentally overwriting this tool itself or config
    protected = {
        PROJECT_ROOT / "config.py", 
        PROJECT_ROOT / "main.py",
        PROJECT_ROOT / "core/agent.py",
        PROJECT_ROOT / "core/llm.py"
    }
    if path in protected:
        return f"ERROR: '{raw_path}' is a protected file."

    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(code, encoding="utf-8")
        return f"SUCCESS: File written ({len(code)} chars, {code.count(chr(10))+1} lines) → {path.relative_to(PROJECT_ROOT)}"
    except PermissionError:
        return f"ERROR: Permission denied writing to '{raw_path}'."
    except Exception as exc:
        return f"ERROR: Unexpected error writing '{raw_path}': {exc}"
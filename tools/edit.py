# tools/edit.py
from pathlib import Path

def edit_file(filepath: str, new_content: str) -> str:
    """
    Mengganti isi file dengan konten baru.
    Jika file belum ada, buat file baru.
    """
    path = Path(filepath)
    try:
        # Pastikan direktori parent ada
        path.parent.mkdir(parents=True, exist_ok=True)
        # Tulis konten
        path.write_text(new_content, encoding="utf-8")
        return f"SUCCESS: File '{filepath}' updated/created."
    except Exception as e:
        return f"ERROR: {str(e)}"

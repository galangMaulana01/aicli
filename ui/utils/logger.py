# utils/logger.py
from pathlib import Path
from datetime import datetime
import json

LOG_FILE = Path("log.jsonl")

def log_interaction(role: str, content: str):
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "role": role,
        "content": content
    }
    try:
        with LOG_FILE.open("a", encoding="utf-8") as f:
            f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")
    except Exception:
        pass  # silently fail, jangan ganggu CLI

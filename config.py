import os
import sys
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# ── NVIDIA API ─────────────────────────────
NVIDIA_API_KEY: str = os.getenv("NVIDIA_API_KEY")

# Model NVIDIA / OpenAI compatible
MODEL_NAME: str = os.getenv("MODEL_NAME")

# ── Token budget ───────────────────────────
MAX_TOKENS: int = int(os.getenv("MAX_TOKENS"))

# ── Project root ────────────────────────────
PROJECT_ROOT: Path = Path(__file__).parent.resolve()

MAX_ITERATIONS: int = int(os.getenv("MAX_ITERATIONS"))

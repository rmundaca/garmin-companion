import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent

# GC_DATA_DIR allows isolating data (tests, alternative installs)
DATA_DIR = Path(os.getenv("GC_DATA_DIR") or (BASE_DIR / "data")).resolve()
TOKEN_DIR = DATA_DIR / "tokens"
DATABASE_URL = f"sqlite:///{DATA_DIR / 'app.db'}"

TOKEN_DIR.mkdir(parents=True, exist_ok=True)

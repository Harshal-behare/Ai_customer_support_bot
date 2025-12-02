import os
import pathlib

BASE_DIR = pathlib.Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "support.sqlite3"
FAQ_PATH = BASE_DIR / "data" / "faqs.json"
STATIC_DIR = BASE_DIR / "static"

DEFAULT_LOW_CONFIDENCE_THRESHOLD = 0.4

# OpenAI configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")

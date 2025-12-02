import os
import pathlib

from dotenv import load_dotenv

BASE_DIR = pathlib.Path(__file__).resolve().parent.parent

# Load environment variables from a local .env file if present
load_dotenv(BASE_DIR / ".env")

DB_PATH = BASE_DIR / "support.sqlite3"
FAQ_PATH = BASE_DIR / "data" / "faqs.json"
STATIC_DIR = BASE_DIR / "app" / "static"

DEFAULT_LOW_CONFIDENCE_THRESHOLD = 0.4

# OpenAI configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

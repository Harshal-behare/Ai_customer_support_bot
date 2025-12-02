import pathlib

BASE_DIR = pathlib.Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "support.sqlite3"
FAQ_PATH = BASE_DIR / "data" / "faqs.json"

DEFAULT_LOW_CONFIDENCE_THRESHOLD = 0.4

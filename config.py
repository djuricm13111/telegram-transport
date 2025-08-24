import os
from zoneinfo import ZoneInfo
from dotenv import load_dotenv

# Učitaj .env iz root-a projekta (pored ovog fajla)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(BASE_DIR, ".env"))

# Konfig
DB_PATH = os.getenv("DB_PATH", os.path.join(BASE_DIR, "ledger.db"))
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TZ = ZoneInfo("Europe/Belgrade")
REMINDER_HOUR = int(os.getenv("REMINDER_HOUR", "19"))

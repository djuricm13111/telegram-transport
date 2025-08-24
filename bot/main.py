import logging
from telegram.ext import Application
from .config import TELEGRAM_TOKEN
from .db import init_db
from .handlers import core as h_core
from .handlers import pairing as h_pair
from .handlers import fund as h_fund
from .handlers import reset as h_reset
from .jobs import reminder as job_reminder


logging.basicConfig(level=logging.INFO)
logging.getLogger("httpx").setLevel(logging.WARNING)

def main():
    if not TELEGRAM_TOKEN:
        raise RuntimeError("Set TELEGRAM_TOKEN env var first (export TELEGRAM_TOKEN=...)")
    init_db()
    app = Application.builder().token(TELEGRAM_TOKEN).build()

    # Handleri
    h_core.add_handlers(app)
    h_pair.add_handlers(app)
    h_fund.add_handlers(app)
    h_reset.add_handlers(app)

    # Poslovi (podsetnik)
    job_reminder.register(app)

    app.run_polling()

if __name__ == "__main__":
    main()

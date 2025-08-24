from datetime import time as dtime
from telegram.ext import ContextTypes
from ..config import TZ, REMINDER_HOUR
from ..db import db
from ..utils import today_bounds_ts

async def _notify_both(ctx, pair, text: str):
    await ctx.bot.send_message(pair["user1"], text)
    await ctx.bot.send_message(pair["user2"], text)

def _has_tx_between(pair_id: str, start_ts: int, end_ts: int) -> bool:
    with db() as conn:
        r = conn.execute("SELECT 1 FROM tx WHERE pair_id=? AND ts BETWEEN ? AND ? LIMIT 1",
                         (pair_id, start_ts, end_ts)).fetchone()
        return r is not None

async def daily_transport_reminder(ctx: ContextTypes.DEFAULT_TYPE):
    start_ts, end_ts = today_bounds_ts(TZ)
    from datetime import datetime
    ds = datetime.now(TZ).strftime("%d.%m.%Y")
    with db() as conn:
        pairs = conn.execute("SELECT * FROM pairs").fetchall()
    for pair in pairs:
        if not _has_tx_between(pair["pair_id"], start_ts, end_ts):
            msg = (f"⏰ Podsetnik ({ds})\n"
                   f"Danas još NIJE unet iznos u transport fond.\n"
                   f"Pošaljite: `+ iznos [napomena]` ili `- iznos [napomena]`")
            await _notify_both(ctx, pair, msg)

def register(app):
    app.job_queue.run_daily(
        daily_transport_reminder,
        time=dtime(REMINDER_HOUR, 0, tzinfo=TZ),
        days=(0,1,2,3,4,5),  # pon–sub
        name="transport-daily-reminder",
    )



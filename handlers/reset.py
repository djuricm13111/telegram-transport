from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CommandHandler, CallbackQueryHandler, ContextTypes
from ..services.pairs import get_pair_by_user, user_belongs, other_of
from ..services.reset_srv import create_reset_request, get_pending_by_token, clear_pending, clear_all_tx
from .core import notify_both

async def reset_cmd(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    pair = get_pair_by_user(uid)
    if not pair:
        return await update.message.reply_text("❗ Prvo uparite naloge: /link → /join")

    token = create_reset_request(pair["pair_id"], uid)
    other = other_of(pair, uid)

    kb = InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("🗑️ Potvrdi reset", callback_data=f"reset2:{token}")],
            [InlineKeyboardButton("✖️ Odbij",          callback_data=f"reset_cancel:{token}")]
        ]
    )
    await ctx.bot.send_message(other, "⚠️ Zatražen je reset fonda na 0. Potvrdi ili odbij:", reply_markup=kb)
    await update.message.reply_text("✅ Tvoj zahtev je poslat. Čeka se reakcija drugog korisnika.")

async def on_action(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    data = q.data or ""
    if not (data.startswith("reset2:") or data.startswith("reset_cancel:")):
        return
    token = data.split(":", 1)[1]
    pend = get_pending_by_token(token)
    if not pend:
        return await q.edit_message_text("❌ Reset zahtev nije pronađen ili je već završen.")
    # par i ovlašćenja
    from ..db import db
    with db() as conn:
        pair = conn.execute("SELECT * FROM pairs WHERE pair_id=?", (pend["pair_id"],)).fetchone()
    if not user_belongs(pair, q.from_user.id):
        return await q.edit_message_text("❌ Nemaš ovlašćenje za ovaj reset.")
    if q.from_user.id == pend["initiator"]:
        return await q.edit_message_text("⏳ Potvrdu/odbijanje mora da da DRUGI korisnik.")

    if data.startswith("reset2:"):
        clear_all_tx(pend["pair_id"])
        clear_pending(token)
        await q.edit_message_text("✅ Fond resetovan na 0.")
        await notify_both(ctx, pair, "🚮 Fond je resetovan na 0.00 RSD")
    else:
        clear_pending(token)
        await q.edit_message_text("❎ Reset je odbijen.")
        await notify_both(ctx, pair, "❎ Reset fonda je odbijen.")

def add_handlers(app):
    app.add_handler(CommandHandler("reset", reset_cmd))
    app.add_handler(CallbackQueryHandler(on_action))

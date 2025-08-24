import uuid
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CommandHandler, CallbackQueryHandler, ContextTypes
from ..services.pairs import upsert_pair, list_pairs, set_active_pair, get_active_pair
import asyncio

LINK_CODES = {}  # RAM: code -> owner_id

async def link(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    code = uuid.uuid4().hex[:8]
    LINK_CODES[code] = uid
    await update.message.reply_text(f"🔗 Tvoj kod: {code}\nDrugi korisnik neka pošalje: /join {code}")

async def join(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    if len(ctx.args) != 1:
        return await update.message.reply_text("Koristi: /join <kod>")
    code = ctx.args[0]
    owner = LINK_CODES.pop(code, None)
    if not owner or owner == uid:
        return await update.message.reply_text("❌ Kod nevažeći.")
    pair_id = uuid.uuid4().hex[:8]
    pair_id = upsert_pair(owner, uid, pair_id)
    await update.message.reply_text("✅ Upareni ste!")
    await ctx.bot.send_message(owner, "✅ Upareni ste!")

# ----- Lista parova i biranje aktivnog -----
async def _user_label(ctx, uid: int) -> str:
    """Vrati @username ako postoji, inače first_name, pa ID kao fallback."""
    try:
        chat = await ctx.bot.get_chat(uid)
        if getattr(chat, "username", None):
            return f"@{chat.username}"
        return chat.first_name or str(uid)
    except Exception:
        return str(uid)

async def _pair_label(ctx, row, viewer_id: int) -> str:
    """Lep prikaz para. Preferiramo prikaz '@partner' u DM-u."""
    a = await _user_label(ctx, row["user1"])
    b = await _user_label(ctx, row["user2"])
    partner = b if viewer_id == row["user1"] else a
    # Ako želiš da vidiš oba imena, koristi: return f"{a} ↔ {b}"
    return f"{partner}"

async def parovi(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    rows = list_pairs(uid)
    if not rows:
        return await update.message.reply_text("Nema parova. Napravi: /link → /join")

    # Napravi labele asinhrono (više poziva ka get_chat)
    labels = await asyncio.gather(*[_pair_label(ctx, r, uid) for r in rows])

    buttons = [[InlineKeyboardButton(labels[i], callback_data=f"use:{rows[i]['pair_id']}")]
               for i in range(len(rows))]
    kb = InlineKeyboardMarkup(buttons)

    cur = get_active_pair(uid)
    if cur:
        active_label = await _pair_label(ctx, cur, uid)
    else:
        active_label = "nema"

    await update.message.reply_text(f"📂 Tvoji parovi (aktivan: {active_label}):", reply_markup=kb)

async def use_cmd(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    if not ctx.args:
        return await parovi(update, ctx)  # pokaži listu
    pair_id = ctx.args[0]
    try:
        set_active_pair(uid, pair_id)
    except Exception:
        return await update.message.reply_text("❌ Taj par ne postoji.")
    await update.message.reply_text(f"✅ Aktiviran par: {pair_id}")

async def on_pair_action(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    if not (q.data or "").startswith("use:"):
        return
    uid = q.from_user.id
    pair_id = q.data.split(":", 1)[1]
    try:
        set_active_pair(uid, pair_id)
    except Exception:
        return await q.edit_message_text("❌ Taj par ne postoji.")

    # Dohvati red para da bismo formatirali labelu
    from ..db import db
    with db() as conn:
        row = conn.execute("SELECT * FROM pairs WHERE pair_id=?", (pair_id,)).fetchone()
    label = await _pair_label(ctx, row, uid)
    await q.edit_message_text(f"✅ Aktiviran par: {label}")


def add_handlers(app):
    app.add_handler(CommandHandler("link", link))
    app.add_handler(CommandHandler("join", join))
    app.add_handler(CommandHandler("parovi", parovi))
    app.add_handler(CommandHandler("use", use_cmd))
    app.add_handler(CallbackQueryHandler(on_pair_action))

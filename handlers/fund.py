import re
from telegram import Update
from telegram.ext import CommandHandler, MessageHandler, ContextTypes, filters
from ..services.pairs import get_active_pair, user_belongs
from ..services.ledger import add_tx, get_history
from ..utils import parse_amount, rsd, when
from .core import transport_text, notify_both

async def _add_tx(update: Update, ctx: ContextTypes.DEFAULT_TYPE, sign: int):
    uid = update.effective_user.id
    pair = get_active_pair(uid)
    if not pair:
        return await update.message.reply_text("❗ Nema aktivnog para. Izaberi: /parovi ili /use <pair_id>")

    args = ctx.args
    text_fallback = (update.message.text or "").strip()
    if not args:
        m = re.match(r"^[+\-]\s*([0-9][0-9.,]*)\s*(.*)$", text_fallback)
        if m:
            amount_s, note = m.group(1), m.group(2)
        else:
            verb = "uplata" if sign > 0 else "trošak"
            return await update.message.reply_text(
                f"Koristi: {'+' if sign>0 else '-'} <iznos> [napomena] (npr. {('+' if sign>0 else '-') } 58.800 {verb})"
            )
    else:
        amount_s = args[0]
        note = " ".join(args[1:]) if len(args) > 1 else ""

    try:
        val = parse_amount(amount_s)
        if val <= 0: raise ValueError()
    except Exception:
        return await update.message.reply_text("❌ Iznos mora biti pozitivan broj (npr. 58.800 / 58,800 / 58800).")

    rec = add_tx(pair["pair_id"], uid, sign * val, note)
    header = ("➕ Uplata " if sign > 0 else "➖ Trošak ") + rsd(val)
    if note: header += f" · {note}"
    balance = await transport_text(ctx, pair)
    actor = update.effective_user.first_name or str(uid)
    text = f"{header}\n👤 {actor}\n🕒 {when(rec['ts'])}\n{balance}"
    await notify_both(ctx, pair, text)

async def plus_cmd(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    return await _add_tx(update, ctx, +1)

async def minus_cmd(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    return await _add_tx(update, ctx, -1)

async def transport(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    pair = get_active_pair(uid)
    if not pair:
        return await update.message.reply_text("❗ Nema aktivnog para. /parovi → izaberi")
    await update.message.reply_text(await transport_text(ctx, pair))

async def istorija(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    pair = get_active_pair(uid)
    if not pair:
        return await update.message.reply_text("❗ Nema aktivnog para. /parovi → izaberi")
    try:
        n = int(ctx.args[0]) if ctx.args else 10
        n = max(1, min(n, 50))
    except Exception:
        n = 10
    rows = get_history(pair["pair_id"], n)
    if not rows: return await update.message.reply_text("Nema stavki.")
    lines = []
    for r in rows:
        sign = "➕" if r["amount"] > 0 else "➖"
        who = str(r["actor"])
        try:
            chat = await ctx.bot.get_chat(r["actor"])
            who = chat.first_name or who
        except Exception:
            pass
        note = f" · {r['note']}" if r["note"] else ""
        lines.append(f"{when(r['ts'])} — {sign} {rsd(abs(r['amount']))} — {who}{note}")
    bal = await transport_text(ctx, pair)
    await update.message.reply_text("📜 Istorija:\n" + "\n".join(lines) + f"\n\n{bal}")

# shortcuts: "+ …", "- …"
async def text_shortcuts(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    msg = update.effective_message  # radi i za message i za channel_post/edited_message
    #TODO
    if not msg or not msg.text:
        return 
    t = (update.message.text or "").strip()
    if t.startswith("+"):
        return await _add_tx(update, ctx, +1)
    if t.startswith("-"):
        return await _add_tx(update, ctx, -1)

def add_handlers(app):
    app.add_handler(CommandHandler("plus", plus_cmd))
    app.add_handler(CommandHandler("minus", minus_cmd))
    app.add_handler(CommandHandler("transport", transport))
    app.add_handler(CommandHandler("istorija", istorija))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_shortcuts))

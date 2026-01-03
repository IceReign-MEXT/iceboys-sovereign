import os
import asyncio
import logging
import threading
import random
import httpx # Add this to requirements.txt
from flask import Flask, send_from_directory, jsonify
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, CallbackQueryHandler
from telegram.constants import ParseMode

# --- TARGET ACQUISITION ---
COMMANDER_ID = 6453658778
MAIN_CHANNEL_ID = -1002384609234
RENDER_URL = "https://iceboys-sovereign.onrender.com"

raw_tokens = os.environ.get("BOT_TOKENS", "")
BOT_TOKENS = [t.strip() for t in raw_tokens.split(",") if t.strip()]

app = Flask(__name__, static_folder='.')

# --- SELF-WAKING LOGIC (KEEP ALIVE) ---
async def self_ping_loop():
    """Pings the /health endpoint internally to prevent Render from sleeping"""
    await asyncio.sleep(60) # Wait for startup
    while True:
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{RENDER_URL}/health")
                logging.info(f"Self-Ping Status: {response.status_code}")
        except Exception as e:
            logging.error(f"Self-Ping Failed: {e}")
        await asyncio.sleep(600) # Ping every 10 minutes

@app.route('/health')
def health_check():
    return jsonify({"status": "optimal", "nodes": len(BOT_TOKENS)}), 200

@app.route('/')
def home():
    return send_from_directory('.', 'index.html')

# --- BOT LOGIC ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id == COMMANDER_ID:
        text = "❄️ <b>COMMANDER MEX ROBERT IDENTIFIED</b>\n────────────────────\nStatus: <b>Immortal</b>"
        buttons = InlineKeyboardMarkup([
            [InlineKeyboardButton("📢 BROADCAST TO CHANNELS", callback_data='admin_broadcast')],
            [InlineKeyboardButton("📊 VIEW VAULT STATS", url=RENDER_URL)]
        ])
    else:
        text = "❄️ <b>SOVEREIGN V15 NEXUS</b>\n────────────────────\nStatus: <b>Optimal</b>"
        buttons = InlineKeyboardMarkup([
            [InlineKeyboardButton("🔍 TRACK WHALE WALLET", url=RENDER_URL)],
            [InlineKeyboardButton("⚔️ INITIATE VOLUME WAR (0.5 SOL)", callback_data='war')]
        ])
    await update.message.reply_text(text, reply_markup=buttons, parse_mode=ParseMode.HTML)

# --- ENGINE BOOT ---
async def start_node(token, is_master=False):
    try:
        await asyncio.sleep(random.uniform(1.0, 5.0))
        builder = ApplicationBuilder().token(token).build()
        builder.add_handler(CommandHandler("start", start))

        await builder.initialize()
        await builder.start()

        if is_master:
            # Start the self-ping loop only on the master bot
            asyncio.create_task(self_ping_loop())

        await builder.updater.start_polling(drop_pending_updates=True)
        while True: await asyncio.sleep(100)
    except Exception as e:
        logging.error(f"Node Error: {e}")

async def run_fleet():
    tasks = []
    for i, token in enumerate(BOT_TOKENS):
        tasks.append(start_node(token, is_master=(i == 0)))
    await asyncio.gather(*tasks)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    threading.Thread(target=lambda: app.run(host='0.0.0.0', port=port, use_reloader=False), daemon=True).start()
    asyncio.run(run_fleet())

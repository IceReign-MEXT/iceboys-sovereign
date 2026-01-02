import os
import asyncio
import logging
import threading
import random
from flask import Flask, send_from_directory, jsonify
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, CallbackQueryHandler
from telegram.constants import ParseMode

# --- TARGET ACQUISITION ---
COMMANDER_ID = 6453658778  # Mex Robert
MAIN_CHANNEL_ID = -1002384609234  # @ICEGODSICEDEVILS

raw_tokens = os.environ.get("BOT_TOKENS", "")
BOT_TOKENS = [t.strip() for t in raw_tokens.split(",") if t.strip()]
SOL_VAULT = "8dtuyskTtsB78DFDPWZszarvDpedwftKYCoMdZwjHbxy"

app = Flask(__name__, static_folder='.')

# --- RENDER HEALTH CHECK FIX ---
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
        text = "❄️ <b>COMMANDER MEX ROBERT IDENTIFIED</b>\n────────────────────\nAdmin Access: <b>Granted</b>"
        buttons = InlineKeyboardMarkup([
            [InlineKeyboardButton("📢 BROADCAST TO CHANNELS", callback_data='admin_broadcast')],
            [InlineKeyboardButton("📊 VIEW VAULT STATS", url="https://iceboys-sovereign.onrender.com")]
        ])
    else:
        text = "❄️ <b>SOVEREIGN V15 NEXUS</b>\n────────────────────\nStatus: <b>Optimal</b>"
        buttons = InlineKeyboardMarkup([
            [InlineKeyboardButton("🔍 TRACK WHALE WALLET", url="https://iceboys-sovereign.onrender.com")],
            [InlineKeyboardButton("⚔️ INITIATE VOLUME WAR (0.5 SOL)", callback_data='war')]
        ])
    await update.message.reply_text(text, reply_markup=buttons, parse_mode=ParseMode.HTML)

async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if query.data == 'admin_broadcast' and query.from_user.id == COMMANDER_ID:
        msg = "🚀 <b>ICEGODS SOVEREIGN ALERT</b>\n\nNexus Nodes are initiating volume protocols.\nJoin: <a href='https://iceboys-sovereign.onrender.com'>Terminal Link</a>"
        await context.bot.send_message(chat_id=MAIN_CHANNEL_ID, text=msg, parse_mode=ParseMode.HTML)
        await query.answer("Broadcast Sent!")

# --- MULTI-BOT NODE WITH CONFLICT RESOLUTION ---
async def start_node(token):
    try:
        # Crucial: Staggered start to prevent simultaneous API hits
        await asyncio.sleep(random.uniform(1.0, 5.0))
        builder = ApplicationBuilder().token(token).build()
        builder.add_handler(CommandHandler("start", start))
        builder.add_handler(CallbackQueryHandler(handle_callback))

        await builder.initialize()
        await builder.start()
        # drop_pending_updates=True is the killer of the Conflict Error
        await builder.updater.start_polling(drop_pending_updates=True)
        while True: await asyncio.sleep(100)
    except Exception as e:
        logging.error(f"Node Conflict/Error: {e}")

async def run_fleet():
    tasks = [start_node(t) for t in BOT_TOKENS if t]
    await asyncio.gather(*tasks)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    threading.Thread(target=lambda: app.run(host='0.0.0.0', port=port, use_reloader=False), daemon=True).start()
    asyncio.run(run_fleet())

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
COMMANDER_ID = 6453658778  # Mex Robert
MAIN_CHANNEL_ID = -1002384609234  # @ICEGODSICEDEVILS

raw_tokens = os.environ.get("BOT_TOKENS", "")
BOT_TOKENS = [t.strip() for t in raw_tokens.split(",") if t.strip()]
SOL_VAULT = "8dtuyskTtsB78DFDPWZszarvDpedwftKYCoMdZwjHbxy"

app = Flask(__name__, static_folder='.')

# --- COMMANDER PRIVILEGES ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    # Check if the user is the Commander
    if user_id == COMMANDER_ID:
        text = (
            "❄️ <b>COMMANDER MEX ROBERT IDENTIFIED</b>\n"
            "────────────────────\n"
            "The Sovereign Fleet is at your disposal. All 36 nodes are synchronized.\n\n"
            "<b>ADMIN ACCESS GRANTED:</b>"
        )
        buttons = InlineKeyboardMarkup([
            [InlineKeyboardButton("📢 BROADCAST TO CHANNELS", callback_data='admin_broadcast')],
            [InlineKeyboardButton("📊 VIEW VAULT STATS", url="https://iceboys-sovereign.onrender.com")],
            [InlineKeyboardButton("⚔️ TEST STRIKE SEQUENCE", callback_data='war')]
        ])
    else:
        # Standard User View
        text = (
            "❄️ <b>SOVEREIGN V15 NEXUS</b>\n"
            "────────────────────\n"
            "Institutional Tracking & Volume Warfare.\n"
            "Status: <b>Optimal</b>"
        )
        buttons = InlineKeyboardMarkup([
            [InlineKeyboardButton("🔍 TRACK WHALE WALLET", url="https://iceboys-sovereign.onrender.com")],
            [InlineKeyboardButton("⚔️ INITIATE VOLUME WAR (0.5 SOL)", callback_data='war')]
        ])

    await update.message.reply_text(text, reply_markup=buttons, parse_mode=ParseMode.HTML)

async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == 'admin_broadcast':
        if query.from_user.id != COMMANDER_ID: return

        broadcast_text = (
            "🚀 <b>ICEGODS SOVEREIGN STRIKE ALERT</b>\n\n"
            "The Nexus has detected a new liquidity pool. "
            "All 36 bots are now initializing volume protocols.\n\n"
            "Join the elite: <a href='https://iceboys-sovereign.onrender.com'>Terminal Link</a>"
        )
        try:
            await context.bot.send_message(chat_id=MAIN_CHANNEL_ID, text=broadcast_text, parse_mode=ParseMode.HTML)
            await query.edit_message_text("✅ <b>BROADCAST SENT TO @ICEGODSICEDEVILS</b>", parse_mode=ParseMode.HTML)
        except Exception as e:
            await query.edit_message_text(f"❌ Error: {e}", parse_mode=ParseMode.HTML)

# --- ENGINE BOOT ---
async def start_node(token):
    try:
        builder = ApplicationBuilder().token(token).build()
        builder.add_handler(CommandHandler("start", start))
        builder.add_handler(CallbackQueryHandler(handle_callback))
        await builder.initialize()
        await builder.start()
        await builder.updater.start_polling(drop_pending_updates=True)
        while True: await asyncio.sleep(100)
    except: pass

async def run_fleet():
    tasks = [start_node(t) for t in BOT_TOKENS if t]
    await asyncio.gather(*tasks)

@app.route('/')
def home():
    return send_from_directory('.', 'index.html')

if __name__ == "__main__":
    threading.Thread(target=lambda: app.run(host='0.0.0.0', port=10000), daemon=True).start()
    asyncio.run(run_fleet())

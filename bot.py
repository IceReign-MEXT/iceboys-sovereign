import os
import asyncio
import logging
import threading
from flask import Flask, send_from_directory
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, CallbackQueryHandler
from telegram.constants import ParseMode

# --- ENV LOAD ---
raw_tokens = os.environ.get("BOT_TOKENS", "")
BOT_TOKENS = [t.strip() for t in raw_tokens.split(",") if t.strip()]
CHANNEL_ID = "@ICEBOYSIBS_Marketing" # <-- Your marketing channel
SOL_VAULT = "8dtuyskTtsB78DFDPWZszarvDpedwftKYCoMdZwjHbxy"

app = Flask(__name__, static_folder='.')

# --- TOOLS: THE MELTER & TRACKER ---
async def broadcast_to_channel(context, message):
    """Broadcasting whale alerts to your marketing channel"""
    try:
        await context.bot.send_message(chat_id=CHANNEL_ID, text=message, parse_mode=ParseMode.HTML)
    except Exception as e:
        print(f"Broadcast Error: {e}")

# --- BOT COMMANDS ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "❄️ <b>SOVEREIGN V15 NEXUS</b>\n"
        "<i>Web3 Marketing & Institutional Liquidity</i>\n"
        "────────────────────\n"
        "<b>[TRACKER]</b>: Discover Whale PNL & Win-rates.\n"
        "<b>[MELTER]</b>: Automated IBS Token Liquidity Burns.\n"
        "<b>[STRIKE]</b>: Execute 36-node Volume Wars."
    )
    buttons = InlineKeyboardMarkup([
        [InlineKeyboardButton("🔍 TRACK WHALE WALLET", url="https://iceboys-sovereign.onrender.com")],
        [InlineKeyboardButton("⚔️ INITIATE VOLUME WAR (0.5 SOL)", callback_data='war')],
        [InlineKeyboardButton("👑 ELITE SUBSCRIPTION (2.5 SOL)", callback_data='sub')]
    ])
    await update.message.reply_text(text, reply_markup=buttons, parse_mode=ParseMode.HTML)

async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == 'sub':
        text = (
            "👑 <b>ELITE MEMBERSHIP ARMED</b>\n\n"
            "By subscribing, you gain access to the Private Whale Stream. "
            "Every 2.5 SOL payment is automatically used to <b>MELT</b> IBS Liquidity.\n\n"
            f"Vault: <code>{SOL_VAULT}</code>\n"
            "Fee: 2.5 SOL / Month\n"
            "────────────────────\n"
            "<i>Status: Awaiting Verification on Helius...</i>"
        )
        await query.edit_message_text(text, parse_mode=ParseMode.HTML)
        # Alert the master channel that a potential subscriber is checking in
        await broadcast_to_channel(context, f"💎 <b>New Lead:</b> A user is viewing Elite Subscription protocols.")

# --- MULTI-BOT NODE ---
async def start_node(token):
    try:
        app_bot = ApplicationBuilder().token(token).build()
        app_bot.add_handler(CommandHandler("start", start))
        app_bot.add_handler(CallbackQueryHandler(handle_callback))
        await app_bot.initialize()
        await app_bot.start()
        await app_bot.updater.start_polling(drop_pending_updates=True)
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

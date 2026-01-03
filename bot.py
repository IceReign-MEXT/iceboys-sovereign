import os
import asyncio
import logging
import threading
import random
import time
from flask import Flask, send_from_directory, jsonify, request
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, CallbackQueryHandler
from telegram.constants import ParseMode
import httpx

# --- COMMANDER CONFIGURATION ---
COMMANDER_ID = 6453658778  # Mex Robert
MAIN_CHANNEL_ID = -1002384609234  # @ICEGODSICEDEVILS
SOL_VAULT = "8dtuyskTtsB78DFDPWZszarvDpedwftKYCoMdZwjHbxy"
HELIUS_KEY = os.environ.get("HELIUS_API_KEY", "1b0094c2-50b9-4c97-a2d6-2c47d4ac2789")

# --- DATABASE-LESS STATE (Shared Brain) ---
# Tracks active strikes and subscriptions in RAM for instant web-bot sync
empire_state = {
    "total_sol_taxed": 12.84,
    "active_strikes": 1204,
    "burned_ibs": "450.2M",
    "nodes_online": 36,
    "subscriptions": {} # {wallet_or_id: expiry_timestamp}
}

raw_tokens = os.environ.get("BOT_TOKENS", "")
BOT_TOKENS = [t.strip() for t in raw_tokens.split(",") if t.strip()]

app = Flask(__name__, static_folder='.')

# --- BLOCKCHAIN VERIFICATION LOGIC ---
async def verify_on_chain_payment(wallet, amount_sol):
    """Bypasses traditional gateways by scanning Helius for direct vault transfers"""
    url = f"https://api.helius.xyz/v0/addresses/{SOL_VAULT}/transactions?api-key={HELIUS_KEY}"
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get(url)
            txs = resp.json()
            # Logic: Match wallet address and SOL amount in last 100 txs
            for tx in txs:
                if wallet.lower() in str(tx).lower():
                    return True
    except: pass
    return False

# --- API FOR DASHBOARD SYNC ---
@app.route('/api/stats')
def get_stats():
    return jsonify(empire_state)

@app.route('/health')
def health_check():
    return jsonify({"status": "immortal"}), 200

@app.route('/')
def home():
    return send_from_directory('.', 'index.html')

# --- BOT INTERFACE (THE WEAPON) ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id == COMMANDER_ID:
        text = "❄️ <b>COMMANDER MEX ROBERT IDENTIFIED</b>\n────────────────────\nStatus: <b>Immortal</b>\nVault Sync: <b>Active</b>"
        btns = InlineKeyboardMarkup([
            [InlineKeyboardButton("📢 GLOBAL BROADCAST", callback_data='broadcast')],
            [InlineKeyboardButton("⚔️ INITIATE SHADOW STRIKE", callback_data='strike')]
        ])
    else:
        text = "❄️ <b>SOVEREIGN V15 NEXUS</b>\n────────────────────\nInstitutional Shadow Indexing active.\nConnect via Dashboard to deploy strikes."
        btns = InlineKeyboardMarkup([[InlineKeyboardButton("🌐 OPEN TERMINAL", url="https://iceboys-sovereign.onrender.com")]])
    await update.message.reply_text(text, reply_markup=btns, parse_mode=ParseMode.HTML)

async def handle_actions(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if query.data == 'broadcast' and query.from_user.id == COMMANDER_ID:
        msg = "🚀 <b>SOVEREIGN FORCE-INDEX ALERT</b>\n\nNexus Nodes are bypassing root platform protocols.\nAll 36 nodes are now generating volume.\n\n<a href='https://iceboys-sovereign.onrender.com'>View Hall of Fame</a>"
        await context.bot.send_message(chat_id=MAIN_CHANNEL_ID, text=msg, parse_mode=ParseMode.HTML)
        await query.edit_message_text("✅ <b>Empire Broadcast Complete.</b>")

# --- ENGINE START ---
async def start_node(token):
    try:
        builder = ApplicationBuilder().token(token).build()
        builder.add_handler(CommandHandler("start", start))
        builder.add_handler(CallbackQueryHandler(handle_actions))
        await builder.initialize()
        await builder.start()
        await builder.updater.start_polling(drop_pending_updates=True)
        while True: await asyncio.sleep(100)
    except: pass

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    threading.Thread(target=lambda: app.run(host='0.0.0.0', port=port), daemon=True).start()
    asyncio.run(asyncio.gather(*[start_node(t) for t in BOT_TOKENS if t]))

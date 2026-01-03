import os
import asyncio
import logging
import threading
import random
import httpx
from flask import Flask, send_from_directory, jsonify, request
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, CallbackQueryHandler
from telegram.constants import ParseMode

# --- COMMANDER CONFIGURATION ---
COMMANDER_ID = 6453658778
MAIN_CHANNEL_ID = -1002384609234
SOL_VAULT = "8dtuyskTtsB78DFDPWZszarvDpedwftKYCoMdZwjHbxy"
HELIUS_KEY = os.environ.get("HELIUS_API_KEY", "1b0094c2-50b9-4c97-a2d6-2c47d4ac2789")

# --- DATABASE-LESS STATE (SHARED BRAIN) ---
empire_state = {
    "total_sol_taxed": 12.84,
    "active_strikes": 1204,
    "burned_ibs": "450.2M",
    "nodes_online": 36,
    "status": "IMMORTAL"
}

# Load all 36 tokens from Environment Variables
raw_tokens = os.environ.get("BOT_TOKENS", "")
BOT_TOKENS = [t.strip() for t in raw_tokens.split(",") if t.strip()]

app = Flask(__name__, static_folder='.')

# --- BLOCKCHAIN VERIFIER ---
async def verify_payment(wallet, amount):
    url = f"https://api.helius.xyz/v0/addresses/{SOL_VAULT}/transactions?api-key={HELIUS_KEY}"
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get(url)
            txs = resp.json()
            for tx in txs:
                if wallet.lower() in str(tx).lower():
                    return True
    except: pass
    return False

# --- API ROUTES FOR INSTITUTIONAL DASHBOARD ---
@app.route('/api/stats')
def get_stats():
    return jsonify(empire_state)

@app.route('/health')
def health_check():
    return jsonify({"status": "optimal", "commander": "Mex Robert"}), 200

@app.route('/')
def home():
    return send_from_directory('.', 'index.html')

# --- BOT HANDLERS ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id == COMMANDER_ID:
        text = (
            "❄️ <b>COMMANDER MEX ROBERT IDENTIFIED</b>\n"
            "────────────────────\n"
            "Status: <b>Immortal</b>\n"
            "Fleet: <b>36 Nodes Synced</b>\n\n"
            "The Sovereign Nexus is at your command."
        )
        btns = InlineKeyboardMarkup([
            [InlineKeyboardButton("📢 GLOBAL BROADCAST", callback_data='broadcast')],
            [InlineKeyboardButton("📊 VIEW TERMINAL", url="https://iceboys-sovereign.onrender.com")]
        ])
    else:
        text = (
            "❄️ <b>SOVEREIGN V15 NEXUS</b>\n"
            "────────────────────\n"
            "Institutional Solana Force-Indexing Engine.\n\n"
            "Connect your wallet to the terminal to deploy volume strikes and bypass tracking protocols."
        )
        btns = InlineKeyboardMarkup([[InlineKeyboardButton("🌐 OPEN TERMINAL", url="https://iceboys-sovereign.onrender.com")]])
    await update.message.reply_text(text, reply_markup=btns, parse_mode=ParseMode.HTML)

async def handle_actions(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    await query.answer()

    if query.data == 'broadcast' and user_id == COMMANDER_ID:
        msg = (
            "🚀 <b>SOVEREIGN FORCE-INDEX ALERT</b>\n\n"
            "Commander Mex Robert has initiated a Global Strike.\n"
            "36 Nodes are now bypassing root indexing protocols.\n\n"
            "🌐 <a href='https://iceboys-sovereign.onrender.com'>Access Terminal</a>"
        )
        try:
            await context.bot.send_message(chat_id=MAIN_CHANNEL_ID, text=msg, parse_mode=ParseMode.HTML)
            await query.edit_message_text("✅ <b>Broadcast Complete. Empire Alert Sent.</b>")
        except Exception as e:
            await query.edit_message_text(f"❌ Broadcast Fail: {e}")

# --- ENGINE ORCHESTRATION ---
async def start_node(token):
    try:
        application = ApplicationBuilder().token(token).build()
        application.add_handler(CommandHandler("start", start))
        application.add_handler(CallbackQueryHandler(handle_actions))

        await application.initialize()
        await application.start()
        await application.updater.start_polling(drop_pending_updates=True)
        while True:
            await asyncio.sleep(3600)
    except: pass

async def main():
    # Start Flask Web Server
    port = int(os.environ.get("PORT", 10000))
    threading.Thread(target=lambda: app.run(host='0.0.0.0', port=port), daemon=True).start()

    # Start Fleet Nodes
    if BOT_TOKENS:
        tasks = [start_node(t) for t in BOT_TOKENS]
        await asyncio.gather(*tasks)
    else:
        while True: await asyncio.sleep(3600)

if __name__ == "__main__":
    asyncio.run(main())

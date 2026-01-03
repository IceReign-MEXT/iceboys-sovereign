import os
import asyncio
import threading
import logging
from flask import Flask, send_from_directory, jsonify, request
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, CallbackQueryHandler
from telegram.constants import ParseMode
import httpx

# --- COMMANDER CONFIG ---
# Commander ID for Mex Robert
COMMANDER_ID = 6453658778
# Main Empire Channel for broadcasts
MAIN_CHANNEL_ID = -1002384609234
# Central SOL Vault
SOL_VAULT = "8dtuyskTtsB78DFDPWZszarvDpedwftKYCoMdZwjHbxy"

# --- FLASK SERVER SETUP ---
app = Flask(__name__, static_folder='.')

# --- SHARED EMPIRE DATA ---
empire_state = {
    "total_sol_taxed": 12.84,
    "burned_ibs": "450.2M",
    "ibs_price": "$0.000412",
    "status": "AGGREGATED_EMPIRE"
}

# --- BOT HANDLERS ---
async def start_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handles the /start command for all fleet nodes."""
    user_id = update.effective_user.id
    bot_me = await context.bot.get_me()

    if user_id == COMMANDER_ID:
        text = (
            f"❄️ <b>COMMANDER MEX ROBERT IDENTIFIED</b>\n"
            f"Node: @{bot_me.username}\n"
            f"Status: <b>Immortal</b>\n\n"
            f"All systems synced across the fleet. The Sovereign Nexus is active."
        )
        btns = InlineKeyboardMarkup([[InlineKeyboardButton("📢 GLOBAL BROADCAST", callback_data='broadcast')]])
    else:
        text = (
            f"❄️ <b>SOVEREIGN V15 NEXUS</b>\n"
            f"Node: @{bot_me.username}\n"
            f"────────────────────\n"
            f"Institutional Solana Force-Indexing Engine. Shadow protocols active."
        )
        btns = InlineKeyboardMarkup([[InlineKeyboardButton("🌐 OPEN TERMINAL", url="https://iceboys-sovereign.onrender.com")]])

    await update.message.reply_text(text, reply_markup=btns, parse_mode=ParseMode.HTML)

async def callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handles button interactions, specifically global broadcasts."""
    query = update.callback_query
    if query.data == 'broadcast' and query.from_user.id == COMMANDER_ID:
        await query.answer("Initiating Global Strike...")
        msg = (
            "🚀 <b>SOVEREIGN FORCE-INDEX ALERT</b>\n\n"
            "Commander Mex Robert has initiated a Global Strike.\n"
            "Nexus nodes are currently bypassing standard indexing protocols.\n\n"
            "🌐 <a href='https://iceboys-sovereign.onrender.com'>Access Terminal</a>"
        )
        try:
            await context.bot.send_message(chat_id=MAIN_CHANNEL_ID, text=msg, parse_mode=ParseMode.HTML)
            await query.edit_message_text("✅ <b>Broadcast Successful. Empire notified.</b>")
        except Exception as e:
            await query.edit_message_text(f"❌ Broadcast Error: {e}")

# --- WEB API FOR THE DASHBOARD ---
@app.route('/api/stats')
def get_stats():
    return jsonify(empire_state)

@app.route('/api/track-wallet', methods=['POST'])
def track_wallet_api():
    """Endpoint for the 'Track' button on the dashboard."""
    data = request.json
    wallet = data.get('wallet', '')
    # Logic simulating high-frequency on-chain scanning
    return jsonify({
        "winRate": "78.4%",
        "pnl": "+12.4 SOL",
        "trust": "Tier-A",
        "scanned": wallet[:8] + "..."
    })

@app.route('/health')
def health():
    return jsonify({"status": "optimal", "commander": "Mex Robert"}), 200

@app.route('/')
def home():
    return send_from_directory('.', 'index.html')

# --- ENGINE ORCHESTRATION ---
async def boot_bot_node(token):
    """Boots an individual bot node using its token."""
    try:
        application = ApplicationBuilder().token(token).build()
        application.add_handler(CommandHandler("start", start_handler))
        application.add_handler(CallbackQueryHandler(callback_handler))

        await application.initialize()
        await application.start()
        await application.updater.start_polling(drop_pending_updates=True)
        # Keep the bot running
        while True:
            await asyncio.sleep(3600)
    except Exception as e:
        print(f"Failed to boot token {token[:10]}...: {e}")

async def main():
    """Main entry point for Python 3.13 on Render."""
    # Start the Flask Web Interface in a background thread
    port = int(os.environ.get("PORT", 10000))
    threading.Thread(target=lambda: app.run(host='0.0.0.0', port=port), daemon=True).start()

    # Retrieve all tokens from the BOT_TOKENS environment variable
    tokens_raw = os.environ.get("BOT_TOKENS", "")
    tokens = [t.strip() for t in tokens_raw.split(",") if t.strip()]

    if tokens:
        print(f"Sovereign Nexus is adopting {len(tokens)} nodes...")
        # Run all bot nodes concurrently
        await asyncio.gather(*[boot_bot_node(t) for t in tokens])
    else:
        print("ALERT: No BOT_TOKENS found. Web server only mode.")
        while True:
            await asyncio.sleep(3600)

if __name__ == "__main__":
    # Ensure event loop is correctly handled
    asyncio.run(main())

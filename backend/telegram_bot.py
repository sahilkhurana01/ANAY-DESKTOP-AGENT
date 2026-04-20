# backend/telegram_bot.py
# Telegram se message bhejo → ANAY tumhare PC pe kaam karta hai
# 
# SETUP:
# 1. @BotFather pe jao Telegram mein
# 2. /newbot karo → naam do "ANAY" → username do "anay_yourname_bot"
# 3. Token copy karo → .env mein TELEGRAM_BOT_TOKEN=<token> daalo
# 4. pip install python-telegram-bot requests

import os
import asyncio
import requests
import base64
import logging
import time
from io import BytesIO
from telegram import Update
from telegram.ext import (
    ApplicationBuilder, CommandHandler,
    MessageHandler, filters, ContextTypes
)
from dotenv import load_dotenv

# Load env from current directory
env_path = os.path.join(os.path.dirname(__file__), ".env")
load_dotenv(dotenv_path=env_path)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ANAY_Telegram")

TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
ANAY_API = "http://127.0.0.1:8000/api/chat"
ALLOWED_USER_ID = os.getenv("TELEGRAM_ALLOWED_USER_ID")

def send_to_anay(message: str, retries: int = 1) -> str:
    """Send message to ANAY backend and get reply with retry logic"""
    for attempt in range(retries + 1):
        try:
            res = requests.post(ANAY_API,
                               json={"message": message},
                               timeout=90)  # Increased from 30 to 90
            data = res.json()
            reply = data.get("reply", data.get("text", "Kuch hua nahi yaar"))
            tools = data.get("tool_calls", [])
            model = data.get("model", "")
            
            if tools:
                tool_names = [t["name"] for t in tools]
                reply += f"\n\n[Tools: {', '.join(tool_names)}]"
            if model:
                reply += f"\n[{model}]"
            return reply

        except requests.exceptions.ReadTimeout:
            if attempt < retries:
                logger.warning(f"Read timeout on attempt {attempt+1}, retrying...")
                time.sleep(2)
                continue
            return "Thoda slow chal raha hai ANAY, dubara bhej yaar 🙄"
        except requests.exceptions.ConnectionError:
            return "ANAY ka backend band hai. PC pe uvicorn start karo!"
        except Exception as e:
            logger.error(f"Error in send_to_anay: {e}")
            return f"Error: {e}"

async def start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Oye yaar! Main ANAY hoon, tera PC control karta hoon Telegram se! 🫡\n"
        "Seedha bol kya karna hai — 'YouTube pe chala', 'Brave khol', etc."
    )

async def handle_message(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    
    # Security: optional allowed user check
    if ALLOWED_USER_ID and user_id != ALLOWED_USER_ID:
        await update.message.reply_text("Abe, tu kaun hai? Access nahi hai tujhe! 🙄")
        return
    
    user_msg = update.message.text
    # Preliminary feedback
    # await update.message.reply_text("Dekh raha hoon... ⚡")
    
    reply = send_to_anay(user_msg)
    await update.message.reply_text(reply)

async def status(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    reply = send_to_anay("system stats bata")
    await update.message.reply_text(f"PC Status:\n{reply}")

async def screenshot(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    if ALLOWED_USER_ID and user_id != ALLOWED_USER_ID:
        return

    try:
        res = requests.post(ANAY_API, json={"message": "take_screenshot"}, timeout=15)
        data = res.json()
        for tool in data.get("tool_calls", []):
            if tool["name"] == "take_screenshot":
                img_b64 = tool["result"]
                img_bytes = base64.b64decode(img_b64)
                await update.message.reply_photo(photo=BytesIO(img_bytes),
                                                  caption="Ye rha tera screen 📸")
                return
        await update.message.reply_text(data.get("text", "Screenshot nahi mila yaar"))
    except Exception as e:
        await update.message.reply_text(f"Screenshot failed: {e}")

def main():
    if not TELEGRAM_TOKEN:
        print("Error: TELEGRAM_BOT_TOKEN missing in .env")
        return

    # Basic instance protection
    pid = os.getpid()
    lock_file = os.path.join(os.path.dirname(__file__), "telegram_bot.pid")
    
    # Check if another instance is likely running
    if os.path.exists(lock_file):
        try:
            with open(lock_file, "r") as f:
                old_pid = int(f.read().strip())
            import psutil
            if psutil.pid_exists(old_pid):
                print(f"Warning: Another bot instance (PID {old_pid}) is already running. Exiting.")
                return
        except: pass

    with open(lock_file, "w") as f:
        f.write(str(pid))

    print(f"ANAY Telegram Bot start ho raha hai... (PID: {pid})")
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("status", status))
    app.add_handler(CommandHandler("screenshot", screenshot))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    print("Bot chal raha hai! Telegram pe message bhejo.")
    app.run_polling()

if __name__ == "__main__":
    main()

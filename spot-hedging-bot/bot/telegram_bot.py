# bot/telegram_bot.py
import sys
import os
import asyncio

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from apscheduler.schedulers.background import BackgroundScheduler
from telegram.constants import ChatAction

from exchanges.bybit_api import get_spot_price
from risk_engine.delta_calculator import calculate_delta
from config.thresholds import set_threshold, get_threshold
from config.thresholds import user_thresholds
from telegram.ext import Application

app: Application = None  # Global reference to the app
BOT_TOKEN = "7960268313:AAHiZBou5-jdbrK4OEtE3pdGxPd3J914y70"

# --- Telegram Commands ---

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Hello! I’m your Spot Hedging Risk Bot.")

async def price(update: Update, context: ContextTypes.DEFAULT_TYPE):
    price = get_spot_price()
    if price:
        await update.message.reply_text(f"📈 BTC/USDT Spot Price: ${price}")
    else:
        await update.message.reply_text("❌ Failed to fetch price. Try again later.")

async def delta(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        position_size = float(context.args[0])
        price = get_spot_price()
        delta_value = calculate_delta(position_size, price)
        await update.message.reply_text(
            f"📊 Delta Exposure: {delta_value} for {position_size} BTC"
        )
    except (IndexError, ValueError):
        await update.message.reply_text(
            "❗ Usage: /delta <position_size> (e.g. /delta 2.5)"
        )

async def setrisk(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        threshold = float(context.args[0])
        user_id = update.effective_user.id
        set_threshold(user_id, threshold)
        await update.message.reply_text(f"✅ Risk threshold set to {threshold} delta.")
    except (IndexError, ValueError):
        await update.message.reply_text(
            "❗ Usage: /setrisk <delta_limit> (e.g. /setrisk 3.0)"
        )

async def checkrisk(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        user_id = update.effective_user.id
        threshold = get_threshold(user_id)
        if threshold is None:
            await update.message.reply_text(
                "⚠️ No threshold set. Use /setrisk <limit> first."
            )
            return
        position_size = float(context.args[0])
        price = get_spot_price()
        delta_val = calculate_delta(position_size, price)
        if delta_val > threshold:
            await update.message.reply_text(
                f"🚨 Alert: Delta {delta_val} exceeds threshold {threshold}!"
            )
        else:
            await update.message.reply_text(
                f"✅ Delta {delta_val} is within threshold {threshold}."
            )
    except (IndexError, ValueError):
        await update.message.reply_text("❗ Usage: /checkrisk <position_size>")

# --- Background Monitoring ---

def start_background_monitoring(app, loop):
    scheduler = BackgroundScheduler()

    def monitor_users():
        for user_id, threshold in user_thresholds.items():
            position_size = 2.5
            price = get_spot_price()
            delta_val = calculate_delta(position_size, price)

            if delta_val > threshold:
                async def send_alert():
                    await app.bot.send_message(
                        chat_id=user_id,
                        text=f"🚨 Background Alert: Delta {delta_val} > Threshold {threshold}!"
                    )
                try:
                    asyncio.run_coroutine_threadsafe(send_alert(), loop)
                except Exception as e:
                    print(f"Error alerting user {user_id}: {e}")

    scheduler.add_job(monitor_users, "interval", seconds=10)
    scheduler.start()

# --- Main ---

def main():
    global app
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("price", price))
    app.add_handler(CommandHandler("delta", delta))
    app.add_handler(CommandHandler("setrisk", setrisk))
    app.add_handler(CommandHandler("checkrisk", checkrisk))

    loop = asyncio.get_event_loop()
    start_background_monitoring(app, loop)

    print("Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()

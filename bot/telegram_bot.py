import sys
import os
import asyncio

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from telegram import Update
from telegram.constants import ChatAction, ParseMode
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, Application,CallbackQueryHandler
from apscheduler.schedulers.background import BackgroundScheduler

from exchanges.bybit_api import get_spot_price, place_order
from risk_engine.delta_calculator import calculate_delta
from config.thresholds import set_threshold, get_threshold, user_thresholds
from hedging.hedge_logger import init_db, get_hedge_history, log_hedge
from risk_engine.portfolio_risk import calculate_var, max_drawdown
from risk_engine.portfolio_risk import calculate_portfolio_risk
from telegram import InlineKeyboardButton, InlineKeyboardMarkup




app: Application = None
BOT_TOKEN = "7960268313:AAHiZBou5-jdbrK4OEtE3pdGxPd3J914y70"

# --- Escape for MarkdownV2 ---
def escape_markdown(text: str) -> str:
    escape_chars = r'\_*[]()~`>#+-=|{}.!'
    return ''.join(['\\' + c if c in escape_chars else c for c in str(text)])

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
        await update.message.reply_text("❗ Usage: /delta <position_size>")

async def setrisk(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        threshold = float(context.args[0])
        user_id = update.effective_user.id
        set_threshold(user_id, threshold)
        await update.message.reply_text(f"✅ Risk threshold set to {threshold} delta.")
    except (IndexError, ValueError):
        await update.message.reply_text("❗ Usage: /setrisk <delta_limit>")

async def checkrisk(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        user_id = update.effective_user.id
        threshold = get_threshold(user_id)
        if threshold is None:
            await update.message.reply_text("⚠️ No threshold set. Use /setrisk <limit> first.")
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

async def hedge(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        position_size = float(context.args[0])
        user_id = update.effective_user.id

        threshold = get_threshold(user_id)
        if threshold is None:
            await update.message.reply_text("⚠️ Set a threshold first using /setrisk <limit>.")
            return

        price = get_spot_price()
        delta_val = calculate_delta(position_size, price)

        if delta_val > threshold:
            result = place_order("BTCUSDT", "SELL", position_size)
            log_hedge(user_id, "BTCUSDT", delta_val, "AUTO_HEDGE",price)
            await update.message.reply_text(
                f"📉 Hedging triggered!\nDelta: {delta_val} > Threshold: {threshold}\nOrder: {result}"
            )
        else:
            await update.message.reply_text(
                f"✅ No need to hedge. Delta {delta_val} is within threshold {threshold}."
            )

    except (IndexError, ValueError):
        await update.message.reply_text("❗ Usage: /hedge <position_size>")

async def hedge_history(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    logs = get_hedge_history(user_id)

    if not logs:
        await update.message.reply_text("📭 No hedge history found.")
        return

    message = "🧾 *Hedge History:*\n\n"
    for log in logs:
        timestamp, asset, delta, method, price= log
        message += (
            f"• `{escape_markdown(timestamp)}`: {escape_markdown(asset)}, "
            f"Δ\\={escape_markdown(delta)}, method\\={escape_markdown(method)},"
            f"price\\={escape_markdown(price)}\n"
        )

    await update.message.reply_text(message, parse_mode=ParseMode.MARKDOWN_V2)
async def portfolio_analytics(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        # Simulated historical prices — in real-world, fetch from API or DB
        prices = [100, 98, 96, 99, 101, 95]
        position_value = 10000  # Simulated portfolio value
        volatility = 0.02       # Simulated daily volatility (2%)

        var_95 = calculate_var(position_value, volatility, confidence=0.95)
        mdd = max_drawdown(prices)

        message = (
            "📊 *Portfolio Risk Analytics:*\n\n"
            f"• Value at Risk (95%): ${var_95:.2f}\n"
            f"• Max Drawdown: {mdd * 100:.2f}%\n"
        )

        await update.message.reply_text(message, parse_mode="Markdown")

    except Exception as e:
        await update.message.reply_text(f"❌ Error calculating analytics: {e}")
async def portfolio_risk(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        position_size = float(context.args[0])  # e.g. /portfolio_risk 3.0
        price = get_spot_price()
        var, drawdown = calculate_portfolio_risk(position_size, price)

        message = (
            f"📊 *Portfolio Risk Analytics:*\n\n"
            f"• *Value at Risk (95%)*: ${var:.2f}\n"
            f"• *Max Drawdown*: {drawdown:.2f}%"
        )
        await update.message.reply_text(message, parse_mode="Markdown")

    except (IndexError, ValueError):
        await update.message.reply_text("❗ Usage: /portfolio_risk <position_size>")
async def menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("📉 Hedge Now", callback_data="hedge_now")],
        [InlineKeyboardButton("📊 View Analytics", callback_data="view_analytics")],
        [InlineKeyboardButton("⚙️ Adjust Threshold", callback_data="adjust_threshold")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("🔘 Choose an action:", reply_markup=reply_markup)
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id
    if query.data == "hedge_now":
        await query.edit_message_text("👉 Use /hedge <position_size> to manually hedge.")
    elif query.data == "view_analytics":
        await query.edit_message_text("👉 Use /portfolio_risk <position_size> to view analytics.")
    elif query.data == "adjust_threshold":
        await query.edit_message_text("👉 Use /setrisk <limit> to adjust your threshold.")
async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        # ✅ Check DB
        init_db()  # Will create the DB/table if not exists, confirming DB works

        # ✅ Check spot price
        price = get_spot_price()

        if price:
            await update.message.reply_text(
                f"✅ Bot is operational!\n\n📈 BTC Spot Price: ${price}\n🗂️ DB Connection: Successful"
            )
        else:
            await update.message.reply_text(
                "⚠️ Bot is running, but failed to fetch BTC price."
            )
    except Exception as e:
        await update.message.reply_text(f"❌ Error in bot status: {e}")


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
    init_db()
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("price", price))
    app.add_handler(CommandHandler("delta", delta))
    app.add_handler(CommandHandler("setrisk", setrisk))
    app.add_handler(CommandHandler("checkrisk", checkrisk))
    app.add_handler(CommandHandler("hedge", hedge))
    app.add_handler(CommandHandler("hedge_history", hedge_history))
    app.add_handler(CommandHandler("portfolio_analytics", portfolio_analytics))
    app.add_handler(CommandHandler("portfolio_risk", portfolio_risk))
    app.add_handler(CommandHandler("menu", menu))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(CommandHandler("status", status))


    loop = asyncio.get_event_loop()
    start_background_monitoring(app, loop)

    print("Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()

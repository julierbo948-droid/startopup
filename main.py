import os
import json
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters
from database import init_user, get_db_balance, update_balance

# API & Wallet Logic (ယခင်ကအတိုင်း)
ADMIN_ID = int(os.getenv("ADMIN_ID"))

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await init_user(update.effective_user.id)
    await update.message.reply_text("🚀 Bot is running on Docker with MongoDB!")

async def balance_report(update: Update, context: ContextTypes.DEFAULT_TYPE):
    bal = await get_db_balance(update.effective_user.id)
    await update.message.reply_text(f"👛 Your Bot Balance: {bal:.4f} TON")

def main():
    app = Application.builder().token(os.getenv("BOT_TOKEN")).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.Regex(r'^\.bal'), balance_report))
    app.run_polling()

if __name__ == "__main__":
    main()

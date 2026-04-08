import os
import json
import logging
import requests
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters
from tonsdk.contract.wallet import Wallets
from tonsdk.crypto import mnemonic_to_wallet_key
from tonsdk.utils import to_nano

# Database functions ကို ခေါ်ယူခြင်း
from database import init_user, get_db_balance, update_balance

# Configuration
ADMIN_ID = int(os.getenv("ADMIN_ID"))
API_KEY = os.getenv("TONCENTER_API_KEY")
MNEMONIC = os.getenv("MNEMONIC").split()
BASE_URL = "https://toncenter.com/api/v2"

# --- WALLET ENGINE ---
def get_wallet():
    # mnemonic list ကို public key/private key အဖြစ် ပြောင်းပြီးသားဖြစ်စေ
    # version="v4r2" ဆိုတာက သင့်အကောင့်အမျိုးအစားဖြစ်တဲ့ v4R2 ကို ခေါ်လိုက်တာပါ
    _wallet = Wallets.from_mnemonic(
        mnemonic=MNEMONIC,
        version="v4r2",
        workchain=0
    )
    return _wallet, _wallet.private_key

def get_onchain_balance(address):
    url = f"{BASE_URL}/getAddressInformation?address={address}&api_key={API_KEY}"
    try:
        res = requests.get(url).json()
        return int(res['result']['balance']) / 10**9 if res.get('ok') else 0
    except: return 0

# --- BOT COMMANDS ---

async def start_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    await init_user(user_id)
    msg = "🚀 <b>Star Bot Engine Active!</b>\n\n"
    msg += ".bal - Check Balances\n.topup - Get Deposit Address\n.price - View Star Prices\n.star - Buy Stars\n.send - Transfer TON"
    await update.message.reply_text(msg, parse_mode="HTML")

async def balance_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    db_bal = await get_db_balance(update.effective_user.id)
    wallet, _ = get_wallet()
    onchain = get_onchain_balance(wallet.address.to_string(True, True, True))
    
    msg = f"👛 <b>Balances</b>\n├ DB Balance: {db_bal:.4f} TON\n└ On-chain: {onchain:.4f} TON"
    await update.message.reply_text(msg, parse_mode="HTML")

async def topup_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    wallet, _ = get_wallet()
    addr = wallet.address.to_string(True, True, True)
    await update.message.reply_text(f"📥 <b>Deposit Address:</b>\n<code>{addr}</code>", parse_mode="HTML")

async def price_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    with open('packages.json', 'r') as f:
        pkgs = json.load(f)
    msg = "⭐ <b>Prices:</b>\n" + "\n".join([f"• {k} Stars = {v} TON" for k,v in pkgs.items()])
    await update.message.reply_text(msg, parse_mode="HTML")

async def buy_star_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID: return
    try:
        target, amount = context.args[0], context.args[1]
        with open('packages.json', 'r') as f: pkgs = json.load(f)
        cost = pkgs.get(amount)
        
        if not cost or await get_db_balance(ADMIN_ID) < cost:
            return await update.message.reply_text("❌ မအောင်မြင်ပါ။ လက်ကျန်ငွေ သို့မဟုတ် Package စစ်ပါ။")
            
        await update_balance(ADMIN_ID, -cost)
        await update.message.reply_text(f"✅ Success! Sent {amount} Stars to {target}.")
    except: await update.message.reply_text("Usage: .star @user 100")

async def send_ton_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID: return
    await update.message.reply_text("📤 Blockchain Transfer Logic is processing...")

# --- MAIN ---
def main():
    app = Application.builder().token(os.getenv("BOT_TOKEN")).build()
    app.add_handler(CommandHandler("start", start_cmd))
    app.add_handler(MessageHandler(filters.Regex(r'^\.bal'), balance_cmd))
    app.add_handler(MessageHandler(filters.Regex(r'^\.topup'), topup_cmd))
    app.add_handler(MessageHandler(filters.Regex(r'^\.price'), price_cmd))
    app.add_handler(MessageHandler(filters.Regex(r'^\.star'), buy_star_cmd))
    app.add_handler(MessageHandler(filters.Regex(r'^\.send'), send_ton_cmd))
    app.run_polling()

if __name__ == "__main__":
    main()

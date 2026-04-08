import os
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

load_dotenv()
client = AsyncIOMotorClient(os.getenv("MONGO_URL"))
db = client.star_bot_db
users_col = db.users

async def init_user(user_id):
    user = await users_col.find_one({"_id": user_id})
    if not user:
        await users_col.insert_one({"_id": user_id, "balance": 0.0})

async def get_db_balance(user_id):
    user = await users_col.find_one({"_id": user_id})
    return user["balance"] if user else 0.0

async def update_balance(user_id, amount):
    await users_col.update_one(
        {"_id": user_id},
        {"$inc": {"balance": amount}},
        upsert=True
    )

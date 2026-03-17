"""
Seed shop for garden
"""
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from database import Database

db = Database()

SEEDS = {
    'wheat': {
        'name': '🌾 Wheat',
        'price': 50,
        'sell_price': 120,
        'growth_time': 3600,  # 1 hour
        'xp': 10
    },
    'corn': {
        'name': '🌽 Corn',
        'price': 100,
        'sell_price': 250,
        'growth_time': 7200,  # 2 hours
        'xp': 20
    },
    'tomato': {
        'name': '🍅 Tomato',
        'price': 150,
        'sell_price': 400,
        'growth_time': 10800,  # 3 hours
        'xp': 35
    },
    'sunflower': {
        'name': '🌻 Sunflower',
        'price': 200,
        'sell_price': 550,
        'growth_time': 14400,  # 4 hours
        'xp': 50
    },
    'rose': {
        'name': '🌹 Rose',
        'price': 500,
        'sell_price': 1500,
        'growth_time': 28800,  # 8 hours
        'xp': 100
    },
    'pumpkin': {
        'name': '🎃 Pumpkin',
        'price': 1000,
        'sell_price': 3500,
        'growth_time': 57600,  # 16 hours
        'xp': 250
    }
}

async def command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show seed shop."""
    user_id = update.effective_user.id
    
    user = db.get_user(user_id)
    if not user:
        await update.message.reply_text("❌ Register first!")
        return
    
    text = "🌱 **Seed Shop**\n\n"
    text += f"💰 Your Money: {user.get('money', 0):,} coins\n\n"
    text += "**Available Seeds**:\n\n"
    
    keyboard = []
    
    for seed_id, seed in SEEDS.items():
        profit = seed['sell_price'] - seed['price']
        text += f"{seed['name']}\n"
        text += f"  💰 Buy: {seed['price']} | Sell: {seed['sell_price']} (+{profit})\n"
        text += f"  ⏱️ Growth: {seed['growth_time']//3600}h | XP: +{seed['xp']}\n\n"
        
        keyboard.append([InlineKeyboardButton(
            f"Buy {seed['name']} - {seed['price']}💰",
            callback_data=f"buy_seed_{seed_id}"
        )])
    
    keyboard.append([InlineKeyboardButton("🌾 View My Seeds", callback_data="view_seeds")])
    
    await update.message.reply_text(
        text,
        parse_mode='Markdown',
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def buy_seed(update: Update, context: ContextTypes.DEFAULT_TYPE, user_id: int, seed_type: str = None):
    """Buy a seed."""
    query = update.callback_query
    
    if not seed_type:
        data = query.data
        seed_type = data.replace("buy_seed_", "")
    
    if seed_type not in SEEDS:
        await query.answer("Invalid seed type!")
        return
    
    seed = SEEDS[seed_type]
    user = db.get_user(user_id)
    
    if user['money'] < seed['price']:
        await query.answer("❌ Not enough money!")
        return
    
    # Deduct money and add seed
    db.update_user(user_id, {'$inc': {'money': -seed['price']}})
    db.add_to_inventory(user_id, f"{seed_type}_seed", 1)
    
    await query.answer(f"✅ Bought {seed['name']}!")
    
    # Refresh shop
    await command(update, context)

from telegram.ext import CommandHandler

seeds_handler = CommandHandler('seeds', command)

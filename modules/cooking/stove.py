"""
Stove management for cooking
"""
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from database import Database
from telegram.ext import CommandHandler
db = Database()

STOVE_TYPES = {
    'basic': {
        'name': '🔥 Basic Stove',
        'price': 5000,
        'slots': 1,
        'efficiency': 1.0
    },
    'gas': {
        'name': '🔥 Gas Stove',
        'price': 15000,
        'slots': 2,
        'efficiency': 1.2
    },
    'electric': {
        'name': '⚡ Electric Stove',
        'price': 40000,
        'slots': 3,
        'efficiency': 1.5
    },
    'industrial': {
        'name': '🏭 Industrial Kitchen',
        'price': 100000,
        'slots': 5,
        'efficiency': 2.0
    }
}

async def command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show stove shop."""
    user_id = update.effective_user.id
    
    user = db.get_user(user_id)
    if not user:
        await update.message.reply_text("❌ Register first!")
        return
    
    # Check current stove
    stove = db.get_stove(user_id)
    
    text = "🔥 **Stove Shop**\n\n"
    
    if stove:
        current_type = stove.get('type', 'basic')
        current = STOVE_TYPES.get(current_type, STOVE_TYPES['basic'])
        text += f"👨‍🍳 **Your Current Stove**: {current['name']}\n"
        text += f"   Slots: {current['slots']} | Efficiency: {current['efficiency']}x\n\n"
        text += "⬆️ **Upgrade Options**:\n\n"
    else:
        text += "❌ **No Stove!** You need one to cook.\n\n"
    
    text += "**Available Stoves**:\n\n"
    
    keyboard = []
    for stove_id, stove_data in STOVE_TYPES.items():
        text += f"{stove_data['name']}\n"
        text += f"   💰 Price: {stove_data['price']:,} coins\n"
        text += f"   🍳 Slots: {stove_data['slots']} (cook multiple items)\n"
        text += f"   ⚡ Efficiency: {stove_data['efficiency']}x speed\n\n"
        
        # Only show buy button if user doesn't have it or it's an upgrade
        if not stove or (stove and stove_data['price'] > STOVE_TYPES.get(stove.get('type', 'basic'), {}).get('price', 0)):
            keyboard.append([InlineKeyboardButton(
                f"Buy {stove_data['name']}",
                callback_data=f"buy_stove_{stove_id}"
            )])
    
    keyboard.append([InlineKeyboardButton("👨‍🍳 Start Cooking", callback_data="goto_cook")])
    
    await update.message.reply_text(
        text,
        parse_mode='Markdown',
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def buy_stove(update: Update, context: ContextTypes.DEFAULT_TYPE, user_id: int, stove_type: str = None):
    """Buy or upgrade stove."""
    query = update.callback_query
    
    if not stove_type:
        data = query.data
        stove_type = data.replace("buy_stove_", "")
    
    if stove_type not in STOVE_TYPES:
        await query.answer("Invalid stove type!")
        return
    
    stove_data = STOVE_TYPES[stove_type]
    user = db.get_user(user_id)
    
    if user['money'] < stove_data['price']:
        await query.answer("❌ Not enough money!")
        return
    
    # Check if already owns this or better
    current = db.get_stove(user_id)
    if current:
        current_price = STOVE_TYPES.get(current.get('type', 'basic'), {}).get('price', 0)
        if current_price >= stove_data['price']:
            await query.answer("You already have this or better!")
            return
    
    # Deduct money and set stove
    db.update_user(user_id, {'$inc': {'money': -stove_data['price']}})
    db.set_stove(user_id, {
        'type': stove_type,
        'slots': stove_data['slots'],
        'efficiency': stove_data['efficiency'],
        'purchased_at': datetime.now()
    })
    
    await query.answer(f"✅ Purchased {stove_data['name']}!")
    await query.edit_message_text(
        f"🔥 **Purchase Successful!**\n\n"
        f"You now own: {stove_data['name']}\n"
        f"Use /cook to start cooking delicious meals!"
)

from telegram.ext import CommandHandler

stove_handler = CommandHandler('stove', command)

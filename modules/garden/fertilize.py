"""
Garden fertilizing system
"""
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from database import Database
from datetime import datetime, timedelta

db = Database()

FERTILIZER_TYPES = {
    'basic': {'name': '🧪 Basic Fertilizer', 'price': 100, 'speed_boost': 0.3, 'duration': 24},
    'premium': {'name': '⚗️ Premium Fertilizer', 'price': 500, 'speed_boost': 0.6, 'duration': 48},
    'organic': {'name': '🌿 Organic Fertilizer', 'price': 1000, 'speed_boost': 1.0, 'duration': 72}
}

async def command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Fertilize plants."""
    user_id = update.effective_user.id
    
    user = db.get_user(user_id)
    if not user:
        await update.message.reply_text("❌ Register first!")
        return
    
    # Get garden
    garden = db.get_garden(user_id)
    if not garden or not garden.get('plants'):
        await update.message.reply_text("🌱 You have no plants! Use /plant first.")
        return
    
    # Check inventory for fertilizer
    inventory = db.get_inventory(user_id)
    fertilizers = {k: v for k, v in inventory.items() if k.endswith('_fertilizer')}
    
    text = "🧪 **Fertilize Plants**\n\n"
    text += f"**Your Plants** ({len(garden['plants'])}):\n"
    
    for i, plant in enumerate(garden['plants']):
        status = "🟢" if not plant.get('fertilized_until') or datetime.now() > plant['fertilized_until'] else "🟡"
        text += f"{status} Plant {i+1}: {plant['type']} (Growth: {plant['growth']}%)\n"
    
    text += "\n**Your Fertilizers**:\n"
    if fertilizers:
        for f_type, qty in fertilizers.items():
            f_name = FERTILIZER_TYPES.get(f_type.replace('_fertilizer', ''), {}).get('name', f_type)
            text += f"• {f_name}: {qty}\n"
    else:
        text += "❌ No fertilizers! Buy with /seeds\n"
    
    keyboard = []
    for f_id, f_data in FERTILIZER_TYPES.items():
        keyboard.append([InlineKeyboardButton(
            f"Buy {f_data['name']} - {f_data['price']}💰", 
            callback_data=f"buy_fertilizer_{f_id}"
        )])
    
    keyboard.append([InlineKeyboardButton("🧪 Use Fertilizer", callback_data="fertilize_use")])
    
    await update.message.reply_text(
        text,
        parse_mode='Markdown',
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def buy_fertilizer(update: Update, context: ContextTypes.DEFAULT_TYPE, user_id: int, f_type: str = None):
    """Buy fertilizer."""
    query = update.callback_query
    
    if not f_type:
        # Extract from callback data
        data = query.data
        f_type = data.replace("buy_fertilizer_", "")
    
    if f_type not in FERTILIZER_TYPES:
        await query.answer("Invalid fertilizer type!")
        return
    
    f_data = FERTILIZER_TYPES[f_type]
    user = db.get_user(user_id)
    
    if user['money'] < f_data['price']:
        await query.answer("❌ Not enough money!")
        return
    
    # Deduct money and add fertilizer
    db.update_user(user_id, {'$inc': {'money': -f_data['price']}})
    db.add_to_inventory(user_id, f"{f_type}_fertilizer", 1)
    
    await query.answer(f"✅ Bought {f_data['name']}!")
    await query.edit_message_text(
        f"✅ Purchased {f_data['name']}!\n"
        f"Speed boost: +{int(f_data['speed_boost']*100)}%\n"
        f"Duration: {f_data['duration']}h"
    )

async def use_fertilizer(update: Update, context: ContextTypes.DEFAULT_TYPE, plant_index: int = 0, f_type: str = 'basic'):
    """Apply fertilizer to a plant."""
    user_id = update.effective_user.id
    
    # Check if has fertilizer
    if not db.has_item(user_id, f"{f_type}_fertilizer"):
        await update.message.reply_text("❌ You don't have this fertilizer!")
        return
    
    garden = db.get_garden(user_id)
    if not garden or plant_index >= len(garden.get('plants', [])):
        await update.message.reply_text("❌ Invalid plant!")
        return
    
    f_data = FERTILIZER_TYPES[f_type]
    
    # Apply fertilizer
    fertilized_until = datetime.now() + timedelta(hours=f_data['duration'])
    db.update_plant(user_id, plant_index, {
        'fertilized': True,
        'fertilized_until': fertilized_until,
        'growth_speed': 1 + f_data['speed_boost']
    })
    
    # Remove from inventory
    db.remove_from_inventory(user_id, f"{f_type}_fertilizer", 1)
    
    await update.message.reply_text(
        f"🧪 **Fertilizer Applied!**\n\n"
        f"Plant {plant_index + 1} is now fertilized!\n"
        f"⚡ Growth speed: +{int(f_data['speed_boost']*100)}%\n"
        f"⏱️ Duration: {f_data['duration']} hours"
)
  

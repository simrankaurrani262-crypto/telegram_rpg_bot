"""
Cooking system
"""
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler
from database import Database
from datetime import datetime, timedelta

db = Database()

# Recipe database
RECIPES = {
    'bread': {
        'name': '🍞 Bread',
        'ingredients': {'wheat': 3},
        'cook_time': 300,  # 5 minutes
        'sell_price': 200,
        'energy': 20,
        'xp': 15
    },
    'popcorn': {
        'name': '🍿 Popcorn',
        'ingredients': {'corn': 2},
        'cook_time': 180,
        'sell_price': 350,
        'energy': 30,
        'xp': 25
    },
    'salad': {
        'name': '🥗 Salad',
        'ingredients': {'tomato': 2, 'wheat': 1},
        'cook_time': 600,
        'sell_price': 600,
        'energy': 50,
        'xp': 40
    },
    'soup': {
        'name': '🍲 Vegetable Soup',
        'ingredients': {'tomato': 3, 'corn': 2},
        'cook_time': 1200,
        'sell_price': 1200,
        'energy': 80,
        'xp': 70
    },
    'cake': {
        'name': '🎂 Cake',
        'ingredients': {'wheat': 5, 'pumpkin': 1},
        'cook_time': 3600,
        'sell_price': 5000,
        'energy': 150,
        'xp': 200
    }
}

SELECTING_RECIPE = 1

async def command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show cooking menu."""
    user_id = update.effective_user.id
    
    user = db.get_user(user_id)
    if not user:
        await update.message.reply_text("❌ Register first!")
        return
    
    # Check if user has stove
    stove = db.get_stove(user_id)
    if not stove:
        await update.message.reply_text(
            "🔥 You need a stove to cook!\n"
            "Buy one with /stove"
        )
        return
    
    text = "👨‍🍳 **Cooking Station**\n\n"
    
    # Show active cooking
    active_cooking = stove.get('active_cooking')
    if active_cooking:
        time_left = active_cooking['end_time'] - datetime.now()
        if time_left.total_seconds() > 0:
            mins, secs = divmod(int(time_left.total_seconds()), 60)
            text += f"⏳ **Cooking**: {active_cooking['recipe_name']}\n"
            text += f"   Time left: {mins}m {secs}s\n\n"
        else:
            text += "✅ **Cooking Complete!** Use /cook to collect.\n\n"
    
    # Show available recipes
    text += "**Available Recipes**:\n\n"
    inventory = db.get_inventory(user_id)
    
    keyboard = []
    for recipe_id, recipe in RECIPES.items():
        # Check if user has ingredients
        can_cook = True
        missing = []
        for ing, qty in recipe['ingredients'].items():
            if inventory.get(ing, 0) < qty:
                can_cook = False
                missing.append(f"{ing} ({inventory.get(ing, 0)}/{qty})")
        
        status = "✅" if can_cook else "❌"
        text += f"{status} {recipe['name']}\n"
        text += f"   Ingredients: {', '.join([f'{v}x{k}' for k,v in recipe['ingredients'].items()])}\n"
        text += f"   Time: {recipe['cook_time']//60}m | Value: {recipe['sell_price']}💰\n\n"
        
        if can_cook:
            keyboard.append([InlineKeyboardButton(
                f"Cook {recipe['name']}",
                callback_data=f"recipe_cook_{recipe_id}"
            )])
    
    if not keyboard:
        text += "❌ You don't have enough ingredients!\n"
        text += "Harvest crops with /harvest or buy seeds with /seeds"
    
    keyboard.append([InlineKeyboardButton("🍽️ My Cooked Food", callback_data="view_cooked")])
    
    await update.message.reply_text(
        text,
        parse_mode='Markdown',
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def handle_recipe_callback(update: Update, context: ContextTypes.DEFAULT_TYPE, data: str):
    """Handle recipe selection."""
    query = update.callback_query
    await query.answer()
    
    if data.startswith("recipe_cook_"):
        recipe_id = data.replace("recipe_cook_", "")
        await start_cooking(query, context, recipe_id)

async def start_cooking(query, context, recipe_id):
    """Start cooking a recipe."""
    user_id = query.from_user.id
    
    if recipe_id not in RECIPES:
        await query.edit_message_text("❌ Invalid recipe!")
        return
    
    recipe = RECIPES[recipe_id]
    stove = db.get_stove(user_id)
    
    # Check if stove is busy
    if stove.get('active_cooking'):
        await query.answer("Stove is busy!")
        return
    
    # Check ingredients again
    inventory = db.get_inventory(user_id)
    for ing, qty in recipe['ingredients'].items():
        if inventory.get(ing, 0) < qty:
            await query.answer(f"Missing {ing}!")
            return
    
    # Deduct ingredients
    for ing, qty in recipe['ingredients'].items():
        db.remove_from_inventory(user_id, ing, qty)
    
    # Start cooking
    end_time = datetime.now() + timedelta(seconds=recipe['cook_time'])
    db.update_stove(user_id, {
        'active_cooking': {
            'recipe_id': recipe_id,
            'recipe_name': recipe['name'],
            'end_time': end_time,
            'started_at': datetime.now()
        }
    })
    
    await query.edit_message_text(
        f"👨‍🍳 **Cooking Started!**\n\n"
        f"Recipe: {recipe['name']}\n"
        f"Duration: {recipe['cook_time']//60} minutes\n"
        f"Come back later to collect your food!"
    )

async def collect_cooking(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Collect finished cooking."""
    user_id = update.effective_user.id
    stove = db.get_stove(user_id)
    
    if not stove or not stove.get('active_cooking'):
        await update.message.reply_text("❌ Nothing is cooking!")
        return
    
    cooking = stove['active_cooking']
    if datetime.now() < cooking['end_time']:
        time_left = cooking['end_time'] - datetime.now()
        mins, secs = divmod(int(time_left.total_seconds()), 60)
        await update.message.reply_text(f"⏳ Wait {mins}m {secs}s more!")
        return
    
    # Cooking done, give food
    recipe = RECIPES[cooking['recipe_id']]
    
    # Add to inventory
    db.add_to_inventory(user_id, f"cooked_{cooking['recipe_id']}", 1)
    
    # Clear stove
    db.update_stove(user_id, {'$unset': {'active_cooking': 1}})
    
    # Give XP
    db.update_user(user_id, {'$inc': {'experience': recipe['xp']}})
    
    await update.message.reply_text(
        f"✅ **Cooking Complete!**\n\n"
        f"You made: {recipe['name']}\n"
        f"Value: {recipe['sell_price']}💰\n"
        f"Energy: +{recipe['energy']}\n"
        f"XP: +{recipe['xp']}"
)

from telegram.ext import CommandHandler

cook_handler = CommandHandler('cook', command)

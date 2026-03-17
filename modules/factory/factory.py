"""
Factory management system - FIXED VERSION
"""
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from database import Database
from datetime import datetime, timedelta

db = Database()

FACTORY_TYPES = {
    'small': {
        'name': '🏭 Small Factory',
        'price': 50000,
        'workers': 5,
        'production_rate': 1.0
    },
    'medium': {
        'name': '🏭 Medium Factory',
        'price': 150000,
        'workers': 15,
        'production_rate': 1.5
    },
    'large': {
        'name': '🏭 Large Factory',
        'price': 500000,
        'workers': 50,
        'production_rate': 2.5
    },
    'industrial': {
        'name': '🌆 Industrial Complex',
        'price': 2000000,
        'workers': 200,
        'production_rate': 5.0
    }
}

PRODUCTS = {
    'wood': {'name': '🪵 Wood', 'materials': {}, 'base_time': 60, 'sell_price': 50},
    'furniture': {'name': '🪑 Furniture', 'materials': {'wood': 5}, 'base_time': 300, 'sell_price': 400},
    'tools': {'name': '🔧 Tools', 'materials': {'wood': 3, 'metal': 2}, 'base_time': 600, 'sell_price': 800},
    'electronics': {'name': '💻 Electronics', 'materials': {'metal': 5, 'plastic': 3}, 'base_time': 1800, 'sell_price': 2500}
}

async def command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show factory management."""
    user_id = update.effective_user.id
    
    user = db.get_user(user_id)
    if not user:
        await update.message.reply_text("❌ Register first!")
        return
    
    factory = db.get_factory(user_id)
    
    if not factory:
        # Show purchase options
        text = "🏭 **Factory Shop**\n\n"
        text += "You don't own a factory yet!\n\n"
        
        keyboard = []
        for f_id, f_data in FACTORY_TYPES.items():
            text += f"{f_data['name']}\n"
            text += f"💰 Price: {f_data['price']:,} coins\n"
            text += f"👷 Workers: {f_data['workers']}\n"
            text += f"⚡ Production: {f_data['production_rate']}x\n\n"
            
            keyboard.append([InlineKeyboardButton(
                f"Buy {f_data['name']}",
                callback_data=f"factory_buy_{f_id}"
            )])
        
        await update.message.reply_text(
            text,
            parse_mode='Markdown',
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return
    
    # Show factory status
    f_type = FACTORY_TYPES.get(factory.get('type', 'small'), FACTORY_TYPES['small'])
    
    text = f"🏭 **Your {f_type['name']}**\n\n"
    text += f"👷 Workers: {len(factory.get('workers', []))}/{f_type['workers']}\n"
    text += f"⚡ Efficiency: {f_type['production_rate']}x\n\n"
    
    # Show active production
    active = factory.get('active_production', [])
    if active:
        text += "🔨 **Active Production**:\n"
        for prod in active:
            time_left = prod['end_time'] - datetime.now()
            if time_left.total_seconds() > 0:
                mins = int(time_left.total_seconds() // 60)
                text += f"• {prod['product']} - {mins}m left\n"
            else:
                text += f"• {prod['product']} - ✅ Ready!\n"
        text += "\n"
    
    # Show storage
    storage = factory.get('storage', {})
    if storage:
        text += "📦 **Storage**:\n"
        for item, qty in storage.items():
            text += f"• {item}: {qty}\n"
        text += "\n"
    
    # Calculate income
    daily_income = calculate_factory_income(user_id)
    text += f"💰 Est. Daily Income: {daily_income:,} coins\n\n"
    
    keyboard = [
        [InlineKeyboardButton("👷 Hire Workers", callback_data="factory_hire")],
        [InlineKeyboardButton("🔨 Start Production", callback_data="factory_produce")],
        [InlineKeyboardButton("📦 Collect Goods", callback_data="factory_collect")],
        [InlineKeyboardButton("⬆️ Upgrade Factory", callback_data="factory_upgrade")]
    ]
    
    await update.message.reply_text(
        text,
        parse_mode='Markdown',
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

def calculate_factory_income(user_id):
    """Calculate estimated daily income."""
    factory = db.get_factory(user_id)
    if not factory:
        return 0
    
    f_type = FACTORY_TYPES.get(factory.get('type', 'small'))
    workers = len(factory.get('workers', []))
    rate = f_type['production_rate']
    
    # Simplified calculation
    return int(workers * rate * 1000)

async def buy_factory(update: Update, context: ContextTypes.DEFAULT_TYPE, factory_type: str):
    """Purchase a factory."""
    query = update.callback_query
    user_id = query.from_user.id
    
    if factory_type not in FACTORY_TYPES:
        await query.answer("Invalid factory type!")
        return
    
    f_data = FACTORY_TYPES[factory_type]
    user = db.get_user(user_id)
    
    if user['money'] < f_data['price']:
        await query.answer
    if user['money'] < f_data['price']:
        await query.answer("❌ Not enough money!")
        return
    
    # Check if already has factory
    if db.get_factory(user_id):
        await query.answer("You already own a factory!")
        return
    
    # Create factory
    db.create_factory(user_id, {
        'type': factory_type,
        'workers': [],
        'storage': {},
        'active_production': [],
        'total_produced': 0,
        'total_earnings': 0,
        'created_at': datetime.now()
    })
    
    # Deduct money
    db.update_user(user_id, {'$inc': {'money': -f_data['price']}})
    
    await query.answer(f"✅ Purchased {f_data['name']}!")
    await query.edit_message_text(
        f"🏭 **Factory Purchased!**\n\n"
        f"You now own: {f_data['name']}\n"
        f"Start hiring workers with /hire\n"
        f"Begin production with /production"
)

from telegram.ext import CommandHandler

factory_handler = CommandHandler('factory', command)

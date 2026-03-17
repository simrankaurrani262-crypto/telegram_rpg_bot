"""
Production management for factory
"""
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from database import Database
from datetime import datetime, timedelta

db = Database()

PRODUCTS = {
    'wood': {
        'name': '🪵 Wood',
        'materials': {},
        'base_time': 300,  # 5 min
        'sell_price': 50,
        'unlock_level': 1
    },
    'furniture': {
        'name': '🪑 Furniture',
        'materials': {'wood': 5},
        'base_time': 1800,  # 30 min
        'sell_price': 400,
        'unlock_level': 2
    },
    'tools': {
        'name': '🔧 Tools',
        'materials': {'metal': 3, 'wood': 2},
        'base_time': 3600,  # 1 hour
        'sell_price': 800,
        'unlock_level': 3
    },
    'electronics': {
        'name': '📱 Electronics',
        'materials': {'metal': 5, 'plastic': 3, 'rare_elements': 1},
        'base_time': 7200,  # 2 hours
        'sell_price': 2500,
        'unlock_level': 5
    },
    'cars': {
        'name': '🚗 Cars',
        'materials': {'metal': 20, 'electronics': 5, 'plastic': 10},
        'base_time': 28800,  # 8 hours
        'sell_price': 15000,
        'unlock_level': 10
    }
}

async def command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show production menu."""
    user_id = update.effective_user.id
    
    factory = db.get_factory(user_id)
    if not factory:
        await update.message.reply_text("❌ You need a factory! Use /factory")
        return
    
    workers = factory.get('workers', [])
    if not workers:
        await update.message.reply_text("❌ Hire workers first! Use /hire")
        return
    
    # Calculate production capacity
    total_efficiency = sum(w['efficiency'] for w in workers)
    f_type = db.get_factory_type(user_id)
    factory_bonus = f_type['production_rate']
    
    text = f"🔨 **Production Management**\n\n"
    text += f"👷 Workers: {len(workers)}\n"
    text += f"⚡ Total Efficiency: {total_efficiency:.1f}x\n"
    text += f"🏭 Factory Bonus: {factory_bonus}x\n\n"
    
    # Show active production
    active = factory.get('active_production', [])
    slots = len(workers)  # One slot per worker
    
    text += f"**Active Production** ({len(active)}/{slots} slots):\n"
    if active:
        for prod in active:
            time_left = prod['end_time'] - datetime.now()
            if time_left.total_seconds() > 0:
                progress = 100 - (time_left.total_seconds() / prod['total_time'] * 100)
                bar = "█" * int(progress/10) + "░" * (10 - int(progress/10))
                text += f"• {prod['name']} [{bar}] {int(progress)}%\n"
            else:
                text += f"• {prod['name']} - ✅ Ready to collect!\n"
    else:
        text += "No active production\n"
    
    text += "\n**Available Products**:\n\n"
    
    keyboard = []
    for p_id, p_data in PRODUCTS.items():
        # Calculate time with bonuses
        actual_time = int(p_data['base_time'] / (total_efficiency * factory_bonus))
        
        text += f"{p_data['name']}\n"
        if p_data['materials']:
            mats = ', '.join([f"{v}x{k}" for k,v in p_data['materials'].items()])
            text += f"   Materials: {mats}\n"
        text += f"   Time: {actual_time//60}m | Value: {p_data['sell_price']}💰\n\n"
        
        keyboard.append([InlineKeyboardButton(
            f"Produce {p_data['name']}",
            callback_data=f"produce_{p_id}"
        )])
    
    keyboard.append([InlineKeyboardButton("📦 Collect All", callback_data="produce_collect")])
    
    await update.message.reply_text(
        text,
        parse_mode='Markdown',
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def start_production(update: Update, context: ContextTypes.DEFAULT_TYPE, product_id: str):
    """Start producing an item."""
    query = update.callback_query
    user_id = query.from_user.id
    
    if product_id not in PRODUCTS:
        await query.answer("Invalid product!")
        return
    
    product = PRODUCTS[product_id]
    factory = db.get_factory(user_id)
    
    # Check materials
    storage = factory.get('storage', {})
    for mat, qty in product['materials'].items():
        if storage.get(mat, 0) < qty:
            await query.answer(f"Missing {mat}!")
            return
    
    # Check available slot
    workers = factory.get('workers', [])
    active = factory.get('active_production', [])
    if len(active) >= len(workers):
        await query.answer("No free production slots!")
        return
    
    # Deduct materials
    for mat, qty in product['materials'].items():
        db.remove_from_factory_storage(user_id, mat, qty)
    
    # Calculate production time
    total_efficiency = sum(w['efficiency'] for w in workers)
    f_type = db.get_factory_type(user_id)
    actual_time = int(product['base_time'] / (total_efficiency * f_type['production_rate']))
    
    # Add to production queue
    end_time = datetime.now() + timedelta(seconds=actual_time)
    production = {
        'product_id': product_id,
        'name': product['name'],
        'started_at': datetime.now(),
        'end_time': end_time,
        'total_time': actual_time,
        'sell_price': product['sell_price']
    }
    
    db.add_factory_production(user_id, production)
    
    await query.answer(f"Started producing {product['name']}!")
    await query.edit_message_text(
        f"🔨 **Production Started**\n\n"
        f"Product: {product['name']}\n"
        f"Duration: {actual_time//60} minutes\n"
        f"Will be ready at {end_time.strftime('%H:%M')}"
    )

async def collect_production(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Collect finished products."""
    user_id = update.effective_user.id
    factory = db.get_factory(user_id)
    
    if not factory:
        await update.message.reply_text("❌ No factory!")
        return
    
    active = factory.get('active_production', [])
    ready = [p for p in active if datetime.now() >= p['end_time']]
    
    if not ready:
        await update.message.reply_text("⏳ Nothing ready yet!")
        return
    
    total_value = 0
    collected = []
    
    for prod in ready:
        # Add to storage or auto-sell
        db.add_to_factory_storage(user_id, prod['product_id'], 1)
        total_value += prod['sell_price']
        collected.append(prod['name'])
        db.remove_factory_production(user_id, prod['product_id'])
    
    # Auto-sell option
    auto_sell = factory.get('auto_sell', False)
    if auto_sell:
        db.update_user(user_id, {'$inc': {'money': total_value}})
        earnings_text = f"💰 Auto-sold for {total_value:,} coins!"
    else:
        earnings_text = f"📦 Stored in factory. Value: {total_value:,}💰"
    
    await update.message.reply_text(
        f"✅ **Collected {len(collected)} items!**\n\n"
        f"Items: {', '.join(collected)}\n"
        f"{earnings_text}\n\n"
        f"Use /factory to manage storage"
    )
    
from telegram.ext import CommandHandler

production_handler = CommandHandler('production', command)

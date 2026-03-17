"""
Hire workers for factory
"""
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from database import Database
from datetime import datetime

db = Database()

WORKER_TYPES = {
    'novice': {'name': '👷 Novice Worker', 'salary': 500, 'efficiency': 1.0},
    'skilled': {'name': '👨‍🔧 Skilled Worker', 'salary': 1500, 'efficiency': 1.5},
    'expert': {'name': '🦾 Expert Worker', 'salary': 4000, 'efficiency': 2.5},
    'master': {'name': '🤖 Master Engineer', 'salary': 10000, 'efficiency': 4.0}
}

async def command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show hire menu."""
    user_id = update.effective_user.id
    
    factory = db.get_factory(user_id)
    if not factory:
        await update.message.reply_text("❌ You need a factory first! Use /factory")
        return
    
    f_type = db.get_factory_type(user_id)
    max_workers = f_type['workers']
    current_workers = len(factory.get('workers', []))
    
    text = f"👷 **Hire Workers**\n\n"
    text += f"Current: {current_workers}/{max_workers} workers\n\n"
    
    # Show current workers
    if factory.get('workers'):
        text += "**Your Team**:\n"
        for worker in factory['workers']:
            w_type = WORKER_TYPES.get(worker['type'])
            text += f"• {w_type['name']} (Eff: {w_type['efficiency']}x)\n"
        text += "\n"
    
    text += "**Available to Hire**:\n\n"
    
    keyboard = []
    for w_id, w_data in WORKER_TYPES.items():
        text += f"{w_data['name']}\n"
        text += f"💰 Daily Salary: {w_data['salary']:,} coins\n"
        text += f"⚡ Efficiency: {w_data['efficiency']}x\n\n"
        
        if current_workers < max_workers:
            keyboard.append([InlineKeyboardButton(
                f"Hire {w_data['name']} - {w_data['salary']}/day",
                callback_data=f"hire_{w_id}"
            )])
    
    if current_workers >= max_workers:
        text += "⚠️ Factory full! Upgrade to hire more.\n"
    
    keyboard.append([InlineKeyboardButton("🔥 Fire Worker", callback_data="hire_fire_menu")])
    
    await update.message.reply_text(
        text,
        parse_mode='Markdown',
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def hire_worker(update: Update, context: ContextTypes.DEFAULT_TYPE, worker_type: str):
    """Hire a specific worker."""
    query = update.callback_query
    user_id = query.from_user.id
    
    if worker_type not in WORKER_TYPES:
        await query.answer("Invalid worker type!")
        return
    
    factory = db.get_factory(user_id)
    f_type = db.get_factory_type(user_id)
    
    if len(factory.get('workers', [])) >= f_type['workers']:
        await query.answer("Factory is full!")
        return
    
    w_data = WORKER_TYPES[worker_type]
    
    # Check if user can afford daily salary
    user = db.get_user(user_id)
    if user['money'] < w_data['salary'] * 7:  # Need 7 days salary upfront
        await query.answer(f"Need {w_data['salary'] * 7:,} coins (7 days salary)!")
        return
    
    # Add worker
    worker = {
        'type': worker_type,
        'hired_at': datetime.now(),
        'efficiency': w_data['efficiency'],
        'salary': w_data['salary'],
        'total_earned': 0
    }
    
    db.add_factory_worker(user_id, worker)
    
    await query.answer(f"✅ Hired {w_data['name']}!")
    await command(update, context)

async def pay_workers(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Pay daily salaries."""
    user_id = update.effective_user.id
    factory = db.get_factory(user_id)
    
    if not factory or not factory.get('workers'):
        return
    
    total_salary = sum(w['salary'] for w in factory['workers'])
    user = db.get_user(user_id)
    
    if user['money'] < total_salary:
        # Workers quit!
        db.clear_factory_workers(user_id)
        await update.message.reply_text(
            "❌ **Workers Quit!**\n"
            f"You couldn't pay {total_salary:,} coins salary.\n"
            "All workers have left!"
        )
        return
    
    # Pay salaries
    db.update_user(user_id, {'$inc': {'money': -total_salary}})
    db.update_worker_earnings(user_id, total_salary)
    
    return total_salary

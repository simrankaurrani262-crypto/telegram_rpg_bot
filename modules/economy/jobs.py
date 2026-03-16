"""
Job system for earning money
"""
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from database import Database
from datetime import datetime, timedelta

db = Database()

JOBS = {
    'beggar': {'name': '🥺 Beggar', 'salary': 50, 'cooldown': 300, 'req_level': 1},
    'farmer': {'name': '👨‍🌾 Farmer', 'salary': 150, 'cooldown': 600, 'req_level': 2},
    'fisher': {'name': '🎣 Fisher', 'salary': 200, 'cooldown': 600, 'req_level': 3},
    'miner': {'name': '⛏️ Miner', 'salary': 350, 'cooldown': 900, 'req_level': 5},
    'chef': {'name': '👨‍🍳 Chef', 'salary': 500, 'cooldown': 1200, 'req_level': 7},
    'merchant': {'name': '💼 Merchant', 'salary': 800, 'cooldown': 1800, 'req_level': 10},
    'banker': {'name': '🏦 Banker', 'salary': 1200, 'cooldown': 3600, 'req_level': 15},
    'developer': {'name': '💻 Developer', 'salary': 2000, 'cooldown': 7200, 'req_level': 20},
    'ceo': {'name': '👔 CEO', 'salary': 5000, 'cooldown': 14400, 'req_level': 30}
}

async def command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show job menu."""
    user_id = update.effective_user.id
    
    user = db.get_user(user_id)
    if not user:
        await update.message.reply_text("❌ Register first!")
        return
    
    current_job = user.get('job', 'beggar')
    job_data = JOBS.get(current_job, JOBS['beggar'])
    
    text = f"💼 **Job Center**\n\n"
    text += f"👤 **Current Job**: {job_data['name']}\n"
    text += f"💰 **Salary**: {job_data['salary']:,}💰\n"
    text += f"⏱️ **Work CD**: {job_data['cooldown']//60} min\n"
    text += f"📊 **Req Level**: {job_data['req_level']}\n\n"
    
    # Check if can work
    last_work = user.get('last_work')
    if last_work:
        time_passed = datetime.now() - last_work
        if time_passed < timedelta(seconds=job_data['cooldown']):
            remaining = timedelta(seconds=job_data['cooldown']) - time_passed
            text += f"⏳ **Next work in**: {remaining.seconds//60} min\n\n"
        else:
            text += "✅ **Ready to work!**\n\n"
    else:
        text += "✅ **Ready to work!**\n\n"
    
    text += "**Available Jobs**:\n"
    keyboard = []
    
    for job_id, job in JOBS.items():
        status = "✅" if user.get('level', 1) >= job['req_level'] else "🔒"
        btn_text = f"{status} {job['name']} ({job['salary']}💰)"
        keyboard.append([InlineKeyboardButton(btn_text, callback_data=f"job_view_{job_id}")])
    
    keyboard.append([InlineKeyboardButton("💪 Work Now", callback_data="job_work")])
    
    await update.message.reply_text(
        text,
        parse_mode='Markdown',
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def work(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Perform work action."""
    user_id = update.effective_user.id
    user = db.get_user(user_id)
    
    job_id = user.get('job', 'beggar')
    job = JOBS.get(job_id, JOBS['beggar'])
    
    # Check cooldown
    last_work = user.get('last_work')
    if last_work:
        time_passed = datetime.now() - last_work
        if time_passed < timedelta(seconds=job['cooldown']):
            remaining = (timedelta(seconds=job['cooldown']) - time_passed).seconds
            await update.message.reply_text(f"⏳ Wait {remaining//60} minutes before working again!")
            return
    
    # Calculate earnings (random bonus)
    import random
    bonus = random.randint(0, job['salary'] // 10)
    earnings = job['salary'] + bonus
    
    # Update user
    db.update_user(user_id, {
        '$inc': {'money': earnings, 'experience': 5},
        '$set': {'last_work': datetime.now()}
    })
    
    # Add transaction
    db.add_transaction(user_id, {
        'type': 'income',
        'amount': earnings,
        'description': f'Worked as {job["name"]}',
        'timestamp': datetime.now()
    })
    
    await update.message.reply_text(
        f"💼 **Work Complete!**\n\n"
        f"You worked as {job['name']} and earned:\n"
        f"💰 {earnings:,} coins (Base: {job['salary']}, Bonus: {bonus})\n"
        f"⭐ +5 XP"
    )

async def change_job(update: Update, context: ContextTypes.DEFAULT_TYPE, new_job: str):
    """Change user's job."""
    user_id = update.effective_user.id
    user = db.get_user(user_id)
    
    if new_job not in JOBS:
        await update.message.reply_text("❌ Invalid job!")
        return
    
    job = JOBS[new_job]
    if user.get('level', 1) < job['req_level']:
        await update.message.reply_text(f"❌ You need level {job['req_level']} for this job!")
        return
    
    db.update_user(user_id, {'$set': {'job': new_job}})
    await update.message.reply_text(f"✅ You are now a {job['name']}")

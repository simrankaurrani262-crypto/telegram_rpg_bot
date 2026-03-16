"""
Admin panel - FIXED
"""
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from database import Database
import os

db = Database()

ADMIN_IDS = [int(x) for x in os.getenv('ADMIN_IDS', '').split(',') if x]

async def command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show admin panel."""
    user_id = update.effective_user.id
    
    if user_id not in ADMIN_IDS:
        await update.message.reply_text("❌ You are not authorized!")
        return
    
    # Get stats
    total_users = db.count_users()
    total_money = db.get_total_money()
    active_today = db.get_active_today()
    
    text = f"🔐 **Admin Panel**\n\n"
    text += f"👥 Total Users: {total_users:,}\n"
    text += f"💰 Total Money: {total_money:,}\n"
    text += f"📊 Active Today: {active_today:,}\n\n"
    
    keyboard = [
        [InlineKeyboardButton("👤 User Management", callback_data="admin_users")],
        [InlineKeyboardButton("📢 Broadcast", callback_data="admin_broadcast")],
        [InlineKeyboardButton("📊 Statistics", callback_data="admin_stats")],
        [InlineKeyboardButton("⚠️ Bans", callback_data="admin_bans")],
        [InlineKeyboardButton("💰 Economy", callback_data="admin_economy")],
        [InlineKeyboardButton("🔧 Maintenance", callback_data="admin_maint")]
    ]
    
    await update.message.reply_text(
        text,
        parse_mode='Markdown',
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def is_admin(user_id: int):
    """Check if user is admin."""
    return user_id in ADMIN_IDS

async def give_money(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Admin command to give money."""
    user_id = update.effective_user.id
    
    if not await is_admin(user_id):
        return
    
    try:
        target_id = int(context.args[0])
        amount = int(context.args[1])
        
        db.update_user(target_id, {'$inc': {'money': amount}})
        await update.message.reply_text(f"✅ Gave {amount:,}💰 to user {target_id}")
    except:
        await update.message.reply_text("Usage: /admin_give <user_id> <amount>")

async def ban_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Ban a user."""
    user_id = update.effective_user.id
    
    if not await is_admin(user_id):
        return
    
    try:
        target_id = int(context.args[0])
        reason = ' '.join(context.args[1:]) if len(context.args) > 1 else 'No reason'
        
        db.ban_user(target_id, reason, user_id)
        await update.message.reply_text(f"🔨 Banned user {target_id}\nReason: {reason}")
    except:
        await update.message.reply_text("Usage: /admin_ban <user_id> <reason>")

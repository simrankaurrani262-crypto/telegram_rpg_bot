"""
/ban command - Ban user (admin only)
"""
from telegram import Update
from telegram.ext import ContextTypes, CommandHandler
from database import db
from config import ADMIN_IDS
import logging

logger = logging.getLogger(__name__)

async def ban_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Ban a user"""
    user_id = update.effective_user.id
    
    if user_id not in ADMIN_IDS:
        await update.message.reply_text("❌ You do not have permission")
        return
    
    if len(context.args) < 2:
        await update.message.reply_text(
            "⛔ <b>BAN USER</b>\n\n"
            "Usage: /ban @username reason",
            parse_mode="HTML"
        )
        return
    
    target_username = context.args[0].lstrip('@')
    reason = ' '.join(context.args[1:])
    
    target = db.db.users.find_one({"username": target_username})
    
    if not target:
        await update.message.reply_text("❌ User not found")
        return
    
    db.ban_user(target['user_id'], reason)
    
    await update.message.reply_text(
        f"✅ <b>USER BANNED</b>\n\n"
        f"User: @{target['username']}\n"
        f"Reason: {reason}",
        parse_mode="HTML"
    )
    
    logger.warning(f"User banned: {target['user_id']} - Reason: {reason}")

ban_handler = CommandHandler('ban', ban_command)
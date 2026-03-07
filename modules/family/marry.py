"""
/marry command - Marry someone
"""
from telegram import Update
from telegram.ext import ContextTypes, CommandHandler
from database import db
import logging

logger = logging.getLogger(__name__)

async def marry_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Marry command"""
    user_id = update.effective_user.id
    
    user = db.get_user(user_id)
    if not user:
        await update.message.reply_text("❌ Please use /start to register first")
        return
    
    family = db.get_family(user_id)
    
    if family.get('partner'):
        partner = db.get_user(family['partner'])
        await update.message.reply_text(
            f"❌ You are already married to @{partner['username']}\n\n"
            f"Use /divorce to end your marriage."
        )
        return
    
    if not context.args:
        await update.message.reply_text(
            "💍 <b>MARRIAGE SYSTEM</b>\n\n"
            "Usage: /marry @username\n\n"
            "To propose to someone, use their username.\n"
            "They will receive a proposal notification.",
            parse_mode="HTML"
        )
        return
    
    target_username = context.args[0].lstrip('@')
    target = db.db.users.find_one({"username": target_username})
    
    if not target:
        await update.message.reply_text("❌ User not found")
        return
    
    if target['user_id'] == user_id:
        await update.message.reply_text("❌ You can't marry yourself!")
        return
    
    target_family = db.get_family(target['user_id'])
    if target_family.get('partner'):
        await update.message.reply_text(f"❌ @{target['username']} is already married")
        return
    
    # Create marriage
    db.add_partner(user_id, target['user_id'])
    
    await update.message.reply_text(
        f"💍 <b>CONGRATULATIONS!</b>\n\n"
        f"You are now married to @{target['username']}!\n\n"
        f"View your family tree with /tree",
        parse_mode="HTML"
    )
    
    logger.info(f"Marriage: {user_id} married {target['user_id']}")

marry_handler = CommandHandler('marry', marry_command)
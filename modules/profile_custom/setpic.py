"""
Set profile picture
"""
from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler
from database import Database

db = Database()

WAITING_PHOTO = 1

async def command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start setpic conversation."""
    await update.message.reply_text(
        "📸 Send me a photo to set as your profile picture!\n\n"
        "Or send /cancel to abort."
    )
    return WAITING_PHOTO

async def start_conv(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Entry point for conversation."""
    return await command(update, context)

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle received photo."""
    user_id = update.effective_user.id
    
    # Get largest photo
    photo = update.message.photo[-1]
    file_id = photo.file_id
    
    # Save to database
    db.update_user(user_id, {'$set': {'profile_pic': file_id}})
    
    await update.message.reply_text(
        "✅ **Profile picture updated!**\n\n"
        "It will be shown in your /profile and family tree!"
    )
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Cancel conversation."""
    await update.message.reply_text("❌ Cancelled.")
    return ConversationHandler.END

async def get_profile_pic(user_id: int):
    """Get user's profile pic."""
    user = db.get_user(user_id)
    return user.get('profile_pic') if user els
  e None

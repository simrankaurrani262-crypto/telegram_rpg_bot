"""
Start command - User registration
"""
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from database import Database

db = Database()

async def command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command - Register new user."""
    user_id = update.effective_user.id
    username = update.effective_user.username
    first_name = update.effective_user.first_name
    
    # Check if user exists
    existing_user = db.get_user(user_id)
    
    if existing_user:
        # Welcome back message
        text = f"👋 Welcome back, {first_name}!\n\n"
        text += f"💰 Money: {existing_user.get('money', 0):,} coins\n"
        text += f"⭐ Level: {existing_user.get('level', 1)}\n"
        text += f"📈 XP: {existing_user.get('experience', 0):,}\n\n"
        text += "Use /help to see all commands!"
        
        keyboard = [
            [InlineKeyboardButton("💰 Balance", callback_data="start_balance"),
             InlineKeyboardButton("👪 Family", callback_data="start_family")],
            [InlineKeyboardButton("🎮 Games", callback_data="start_games"),
             InlineKeyboardButton("📊 Stats", callback_data="start_stats")]
        ]
        
        await update.message.reply_text(
            text,
            parse_mode='Markdown',
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    else:
        # New user registration
        db.create_user(user_id, username or first_name)
        
        text = f"🎉 **Welcome to RPG Bot, {first_name}!**\n\n"
        text += "✅ You have been registered successfully!\n\n"
        text += "🎁 **Starter Bonus:**\n"
        text += "• 1,000 coins\n"
        text += "• 100 health\n"
        text += "• 100 energy\n\n"
        text += "📚 **Quick Start:**\n"
        text += "/help - See all commands\n"
        text += "/daily - Claim daily reward\n"
        text += "/job - Start working\n"
        text += "/family - View family options\n\n"
        text += "🎮 Start your adventure now!"
        
        keyboard = [
            [InlineKeyboardButton("📚 View Help", callback_data="start_help"),
             InlineKeyboardButton("💰 Claim Daily", callback_data="start_daily")],
            [InlineKeyboardButton("👪 Find Family", callback_data="start_family"),
             InlineKeyboardButton("🎮 Play Games", callback_data="start_games")]
        ]
        
        await update.message.reply_text(
            text,
            parse_mode='Markdown',
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

# Alias for backward compatibility
from telegram.ext import CommandHandler

start_handler = CommandHandler("start", command)

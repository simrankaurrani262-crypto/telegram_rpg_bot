"""
Leaderboard commands
"""
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from database import Database

db = Database()

async def command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show general leaderboard."""
    # Get top 10 users by experience
    top_users = db.get_top_users('experience', limit=10)
    
    text = "🏆 **Overall Leaderboard**\n\n"
    
    medals = ['🥇', '🥈', '🥉', '4️⃣', '5️⃣', '6️⃣', '7️⃣', '8️⃣', '9️⃣', '🔟']
    
    for i, user in enumerate(top_users):
        medal = medals[i] if i < 10 else f"{i+1}."
        username = user.get('username') or f"User{user['user_id']}"
        level = user.get('level', 1)
        xp = user.get('experience', 0)
        
        text += f"{medal} **{username}**\n"
        text += f"   Level {level} ({xp:,} XP)\n\n"
    
    # Get user's rank
    user_id = update.effective_user.id
    user_rank = db.get_user_rank(user_id, 'experience')
    
    if user_rank:
        text += f"📊 Your Rank: #{user_rank}\n"
    
    keyboard = [
        [InlineKeyboardButton("💰 Money", callback_data="lb_money"),
         InlineKeyboardButton("👪 Family", callback_data="lb_family")],
        [InlineKeyboardButton("⭐ XP", callback_data="lb_xp"),
         InlineKeyboardButton("🏆 Wins", callback_data="lb_wins")]
    ]
    
    await update.message.reply_text(
        text,
        parse_mode='Markdown',
        reply_markup=InlineKeyboardMarkup(keyboard)
    
    )

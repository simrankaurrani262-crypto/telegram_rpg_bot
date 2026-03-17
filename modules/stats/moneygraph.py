"""
Money/Rich list leaderboard
"""
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from database import Database

db = Database()

async def command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show richest players leaderboard."""
    # Get top 10 richest users
    top_users = db.get_top_users('money', limit=10)
    
    text = "💰 **Richest Players**\n\n"
    
    medals = ['🥇', '🥈', '🥉', '4️⃣', '5️⃣', '6️⃣', '7️⃣', '8️⃣', '9️⃣', '🔟']
    
    total_money = 0
    
    for i, user in enumerate(top_users):
        medal = medals[i] if i < 10 else f"{i+1}."
        username = user.get('username') or f"User{user['user_id']}"
        money = user.get('money', 0)
        bank = user.get('bank', 0)
        total = money + bank
        total_money += total
        
        text += f"{medal} **{username}**\n"
        text += f"   👛 {money:,} | 🏦 {bank:,} = **{total:,}**💰\n\n"
    
    # Add statistics
    text += f"📊 **Economy Stats**\n"
    text += f"Top 10 Total: {total_money:,}💰\n"
    
    # Get user's rank
    user_id = update.effective_user.id
    user = db.get_user(user_id)
    
    if user:
        user_rank = db.get_user_rank(user_id, 'money')
        user_total = user.get('money', 0) + user.get('bank', 0)
        text += f"\n📍 Your Position: #{user_rank} ({user_total:,}💰)"
    
    keyboard = [
        [InlineKeyboardButton("🏆 Overall", callback_data="lb_overall"),
         InlineKeyboardButton("👪 Family", callback_data="lb_family")],
        [InlineKeyboardButton("📊 Graph", callback_data="money_graph")]
    ]
    
    await update.message.reply_text(
        text,
        parse_mode='Markdown',
        reply_markup=InlineKeyboardMarkup(keyboard)
    
    )

from telegram.ext import CommandHandler

moneygraph_handler = CommandHandler('moneygraph', command)

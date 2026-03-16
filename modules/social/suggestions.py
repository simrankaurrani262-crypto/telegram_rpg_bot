"""
Friend suggestions system
"""
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from database import Database
import random

db = Database()

async def command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show friend suggestions."""
    user_id = update.effective_user.id
    
    user = db.get_user(user_id)
    if not user:
        await update.message.reply_text("❌ Register first!")
        return
    
    suggestions = generate_suggestions(user_id)
    
    text = "🎯 **Friend Suggestions**\n\n"
    text += "People you may know based on:\n"
    text += "• Mutual friends\n• Family connections\n• Activity patterns\n• Similar levels\n\n"
    
    if not suggestions:
        text += "😕 No suggestions found right now. Check back later!"
        await update.message.reply_text(text, parse_mode='Markdown')
        return
    
    keyboard = []
    for sugg in suggestions[:5]:
        text += f"👤 **{sugg['username'] or 'User'}**\n"
        text += f"   Level: {sugg['level']} | Reason: {sugg['reason']}\n\n"
        keyboard.append([
            InlineKeyboardButton(f"➕ Add {sugg['username'] or 'User'}", 
                               callback_data=f"request_add_{sugg['user_id']}")
        ])
    
    keyboard.append([InlineKeyboardButton("🔄 Refresh", callback_data="suggestions_refresh")])
    
    await update.message.reply_text(
        text,
        parse_mode='Markdown',
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

def generate_suggestions(user_id):
    """Generate friend suggestions based on various factors."""
    suggestions = []
    current_friends = set(db.get_friends(user_id))
    current_friends.add(user_id)  # Exclude self
    
    # 1. Mutual friends (friends of friends)
    friends = db.get_friends(user_id)
    for friend_id in friends:
        friend_friends = db.get_friends(friend_id)
        for ff_id in friend_friends:
            if ff_id not in current_friends and ff_id != user_id:
                ff_user = db.get_user(ff_id)
                if ff_user:
                    suggestions.append({
                        'user_id': ff_id,
                        'username': ff_user.get('username'),
                        'level': ff_user.get('level', 1),
                        'reason': 'Mutual friend'
                    })
    
    # 2. Family connections (siblings' friends, cousins, etc.)
    family = db.get_family(user_id)
    for member_id in family.get('siblings', []) + family.get('cousins', []):
        if member_id not in current_friends:
            member = db.get_user(member_id)
            if member:
                suggestions.append({
                    'user_id': member_id,
                    'username': member.get('username'),
                    'level': member.get('level', 1),
                    'reason': 'Family connection'
                })
    
    # 3. Similar level players
    user_level = db.get_user(user_id).get('level', 1)
    similar_users = db.get_users_by_level_range(user_level - 2, user_level + 2, limit=10)
    for u in similar_users:
        if u['user_id'] not in current_friends and u['user_id'] != user_id:
            suggestions.append({
                'user_id': u['user_id'],
                'username': u.get('username'),
                'level': u.get('level', 1),
                'reason': 'Similar level'
            })
    
    # Remove duplicates and shuffle
    seen = set()
    unique_suggestions = []
    for s in suggestions:
        if s['user_id'] not in seen:
            seen.add(s['user_id'])
            unique_suggestions.append(s)
    
    random.shuffle(unique_suggestions)
    return unique_suggestions[:1
0]

"""
User ratings system
"""
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from database import Database

db = Database()

async def command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show user ratings."""
    user_id = update.effective_user.id
    
    user = db.get_user(user_id)
    if not user:
        await update.message.reply_text("❌ Register first with /start")
        return
    
    # Get ratings
    ratings_given = db.get_ratings_given(user_id)
    ratings_received = db.get_ratings_received(user_id)
    
    # Calculate average
    if ratings_received:
        avg_rating = sum(r['rating'] for r in ratings_received) / len(ratings_received)
        stars = "⭐" * int(avg_rating) + "☆" * (5 - int(avg_rating))
    else:
        avg_rating = 0
        stars = "☆☆☆☆☆"
    
    text = f"📊 **Your Ratings**\n\n"
    text += f"⭐ **Average Rating**: {avg_rating:.1f}/5.0 {stars}\n"
    text += f"📝 **Total Reviews**: {len(ratings_received)}\n"
    text += f"👥 **Rated by**: {len(set(r['from_user'] for r in ratings_received))} users\n\n"
    
    if ratings_received:
        text += "**Recent Reviews**:\n"
        for r in ratings_received[-3:]:
            from_user = db.get_user(r['from_user'])
            text += f"• {'⭐' * r['rating']} by {from_user['username'] or 'Anonymous'}\n"
            if r.get('comment'):
                text += f"  💬 {r['comment'][:50]}...\n"
    
    text += f"\n📤 **Ratings Given**: {len(ratings_given)}\n"
    
    keyboard = [
        [InlineKeyboardButton("⭐ Rate Someone", callback_data="rate_user")],
        [InlineKeyboardButton("📜 My Reviews", callback_data="my_reviews")]
    ]
    
    await update.message.reply_text(
        text,
        parse_mode='Markdown',
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def rate_user(update: Update, context: ContextTypes.DEFAULT_TYPE, target_id: int, rating: int, comment: str = None):
    """Rate a user."""
    user_id = update.effective_user.id
    
    # Prevent self-rating
    if user_id == target_id:
        return False, "You cannot rate yourself!"
    
    # Check if already rated
    existing = db.get_rating(user_id, target_id)
    if existing:
        return False, "You have already rated this user!"
    
    # Save rating
    db.add_rating({
        'from_user': user_id,
        'to_user': target_id,
        'rating': rating,
        'comment': comment,
        'timestamp': datetime.now()
    })
    
    return True, "Rating submitted!"

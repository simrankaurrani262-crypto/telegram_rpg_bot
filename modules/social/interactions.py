"""
Social interactions between users
"""
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from database import Database
from datetime import datetime, timedelta

db = Database()

INTERACTIONS = {
    'hug': {'emoji': '🤗', 'text': 'hugged', 'cooldown': 5},
    'kiss': {'emoji': '💋', 'text': 'kissed', 'cooldown': 10},
    'slap': {'emoji': '👋', 'text': 'slapped', 'cooldown': 5},
    'poke': {'emoji': '👉', 'text': 'poked', 'cooldown': 3},
    'highfive': {'emoji': '🙌', 'text': 'high-fived', 'cooldown': 5},
    'pat': {'emoji': '🐱', 'text': 'patted', 'cooldown': 5},
    'cuddle': {'emoji': '🤱', 'text': 'cuddled', 'cooldown': 10},
    'wave': {'emoji': '👋', 'text': 'waved at', 'cooldown': 2}
}

async def command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show interaction menu."""
    user_id = update.effective_user.id
    
    keyboard = []
    row = []
    for action, data in INTERACTIONS.items():
        btn = InlineKeyboardButton(f"{data['emoji']} {action.capitalize()}", 
                                  callback_data=f"interact_{action}")
        row.append(btn)
        if len(row) == 2:
            keyboard.append(row)
            row = []
    if row:
        keyboard.append(row)
    
    text = "🎭 **Social Interactions**\n\n"
    text += "Choose an action and then mention the user!\n"
    text += "Example: After clicking 'Hug', reply to a user or type their username"
    
    await update.message.reply_text(
        text,
        parse_mode='Markdown',
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def handle_interaction(update: Update, context: ContextTypes.DEFAULT_TYPE, 
                           action: str, target_id: int = None):
    """Handle specific interaction."""
    user_id = update.effective_user.id
    
    if not target_id:
        await update.message.reply_text("❌ Please reply to a user or mention them!")
        return
    
    if user_id == target_id:
        await update.message.reply_text("❌ You can't interact with yourself!")
        return
    
    # Check cooldown
    last_interaction = db.get_last_interaction(user_id, action)
    cooldown_minutes = INTERACTIONS[action]['cooldown']
    if last_interaction and (datetime.now() - last_interaction) < timedelta(minutes=cooldown_minutes):
        remaining = cooldown_minutes - (datetime.now() - last_interaction).seconds // 60
        await update.message.reply_text(f"⏳ Wait {remaining} minutes before {action}ing again!")
        return
    
    target = db.get_user(target_id)
    if not target:
        await update.message.reply_text("❌ User not found!")
        return
    
    # Record interaction
    db.record_interaction(user_id, target_id, action)
    
    # Update relationship score
    db.update_relationship_score(user_id, target_id, 1 if action not in ['slap'] else -1)
    
    emoji = INTERACTIONS[action]['emoji']
    text = INTERACTIONS[action]['text']
    
    await update.message.reply_text(
        f"{emoji} **{update.effective_user.first_name}** {text} **{target.get('username', 'User')}**!\n"
        f"💕 Relationship score +1"
    )

async def interact_callback(update: Update, context: ContextTypes.DEFAULT_TYPE, action: str):
    """Handle interaction button click."""
    query = update.callback_query
    await query.answer()
    
    await query.edit_message_text(
        f"{INTERACTIONS[action]['emoji']} You selected **{action}**.\n\n"
        f"Now reply to a user's message or type:\n"
        f"`/interact {action} @username`",
        parse_mode='Markdown'
)

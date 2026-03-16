"""
Family and social relations management
"""
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from database import Database

db = Database()

async def command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show user's relations."""
    user_id = update.effective_user.id
    
    # Get user data
    user = db.get_user(user_id)
    if not user:
        await update.message.reply_text("❌ You need to register first! Use /start")
        return
    
    # Get family relations
    family_data = db.get_family(user_id)
    
    text = f"👥 **{update.effective_user.first_name}'s Relations**\n\n"
    
    # Partner
    if family_data.get('partner'):
        partner = db.get_user(family_data['partner'])
        text += f"❤️ **Partner**: {partner['username'] or partner['user_id']}\n"
    else:
        text += "❤️ **Partner**: Single\n"
    
    # Parents
    parents = family_data.get('parents', [])
    if parents:
        text += f"\n👨‍👩‍👧 **Parents** ({len(parents)}):\n"
        for parent_id in parents[:5]:  # Show max 5
            parent = db.get_user(parent_id)
            text += f"  • {parent['username'] or 'Unknown'}\n"
    
    # Children
    children = family_data.get('children', [])
    if children:
        text += f"\n👶 **Children** ({len(children)}):\n"
        for child_id in children[:5]:
            child = db.get_user(child_id)
            text += f"  • {child['username'] or 'Unknown'}\n"
    
    # Siblings
    siblings = family_data.get('siblings', [])
    if siblings:
        text += f"\n🧑‍🤝‍🧑 **Siblings** ({len(siblings)}):\n"
        for sib_id in siblings[:5]:
            sib = db.get_user(sib_id)
            text += f"  • {sib['username'] or 'Unknown'}\n"
    
    # Friends count
    friends = db.get_friends(user_id)
    text += f"\n🤝 **Friends**: {len(friends)}\n"
    
    # Relation status
    text += f"\n📊 **Relation Status**: {user.get('relation_status', 'Neutral')}\n"
    
    keyboard = [
        [InlineKeyboardButton("➕ Add Friend", callback_data="relation_add")],
        [InlineKeyboardButton("👪 View Family Tree", callback_data="relation_tree")]
    ]
    
    await update.message.reply_text(
        text, 
        parse_mode='Markdown',
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE, data: str):
    """Handle relation callbacks."""
    query = update.callback_query
    
    if data == "relation_add":
        await query.edit_message_text(
            "👥 Send the username or ID of the person you want to add as friend:\n"
            "(Use /requests to see pending requests)"
        )
    elif data == "relation_tree":
        await query.edit_message_text("Use /tree to generate your family tree image!")

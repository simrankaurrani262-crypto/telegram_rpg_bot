"""
Friend and relation requests management
"""
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from database import Database

db = Database()

async def command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show pending requests."""
    user_id = update.effective_user.id
    
    # Get pending friend requests
    friend_requests = db.get_friend_requests(user_id)
    # Get pending family requests (adoption, marriage)
    family_requests = db.get_family_requests(user_id)
    # Get pending trade requests
    trade_requests = db.get_trade_requests(user_id)
    
    text = "📨 **Your Requests**\n\n"
    
    total = len(friend_requests) + len(family_requests) + len(trade_requests)
    if total == 0:
        text += "✅ No pending requests!\n\n"
        text += "Use /suggestions to find friends or /marry, /adopt for family!"
    else:
        if friend_requests:
            text += f"👥 **Friend Requests** ({len(friend_requests)}):\n"
            for req in friend_requests:
                from_user = db.get_user(req['from_user'])
                text += f"• From: {from_user.get('username', 'Unknown')}\n"
        
        if family_requests:
            text += f"\n👪 **Family Requests** ({len(family_requests)}):\n"
            for req in family_requests:
                from_user = db.get_user(req['from_user'])
                text += f"• {req['type'].capitalize()}: {from_user.get('username', 'Unknown')}\n"
        
        if trade_requests:
            text += f"\n💰 **Trade Requests** ({len(trade_requests)}):\n"
            for req in trade_requests:
                from_user = db.get_user(req['from_user'])
                text += f"• From: {from_user.get('username', 'Unknown')} - {req['item']}\n"
    
    keyboard = [
        [InlineKeyboardButton("✅ Accept All", callback_data="request_accept_all")],
        [InlineKeyboardButton("❌ Decline All", callback_data="request_decline_all")],
        [InlineKeyboardButton("🔍 View Details", callback_data="request_details")]
    ]
    
    await update.message.reply_text(
        text,
        parse_mode='Markdown',
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE, data: str):
    """Handle request callbacks."""
    query = update.callback_query
    user_id = query.from_user.id
    
    if data == "request_accept_all":
        # Accept all pending requests
        db.accept_all_requests(user_id)
        await query.edit_message_text("✅ All requests accepted!")
    elif data == "request_decline_all":
        db.decline_all_requests(user_id)
        await query.edit_message_text("❌ All requests declined!")
    elif data == "request_details":
        # Show detailed view with individual accept/decline buttons
        await show_request_details(update, context, user_id)
    elif data.startswith("request_accept_"):
        request_id = data.replace("request_accept_", "")
        db.accept_request(request_id)
        await query.answer("✅ Accepted!")
    elif data.startswith("request_decline_"):
        request_id = data.replace("request_decline_", "")
        db.decline_request(request_id)
        await query.answer("❌ Declined!")

async def show_request_details(update: Update, context: ContextTypes.DEFAULT_TYPE, user_id: int):
    """Show detailed request view."""
    friend_requests = db.get_friend_requests(user_id)
    
    if not friend_requests:
        await update.callback_query.edit_message_text("No pending requests!")
        return
    
    text = "📨 **Pending Friend Requests**:\n\n"
    keyboard = []
    
    for req in friend_requests:
        from_user = db.get_user(req['from_user'])
        username = from_user.get('username', 'Unknown')
        text += f"• {username} (Level {from_user.get('level', 1)})\n"
        keyboard.append([
            InlineKeyboardButton(f"✅ Accept {username}", callback_data=f"request_accept_{req['_id']}"),
            InlineKeyboardButton(f"❌ Decline", callback_data=f"request_decline_{req['_id']}")
        ])
    
    await update.callback_query.edit_message_text(
        text,
        parse_mode='Markdown',
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def send_friend_request(update: Update, context: ContextTypes.DEFAULT_TYPE, target_id: int):
    """Send a friend request."""
    user_id = update.effective_user.id
    
    if user_id == target_id:
        await update.message.reply_text("❌ You can't add yourself!")
        return False
    
    # Check if already friends
    if db.are_friends(user_id, target_id):
        await update.message.reply_text("❌ You are already friends!")
        return False
    
    # Check if request already sent
    if db.has_pending_request(user_id, target_id):
        await update.message.reply_text("⏳ Request already pending!")
        return False
    
    db.create_friend_request(user_id, target_id)
    await update.message.reply_text("✅ Friend request sent!")
    return 
True

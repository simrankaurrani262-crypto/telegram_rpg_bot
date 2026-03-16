"""
Settings toggle system
"""
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from database import Database

db = Database()

SETTINGS = {
    'notifications': {
        'name': '🔔 Notifications',
        'description': 'Get notified about game events',
        'default': True
    },
    'dark_mode': {
        'name': '🌙 Dark Mode',
        'description': 'Dark theme for images',
        'default': False
    },
    'sounds': {
        'name': '🔊 Sound Effects',
        'description': 'Play sounds in messages',
        'default': True
    },
    'auto_work': {
        'name': '⚡ Auto Work',
        'description': 'Automatically collect job earnings',
        'default': False
    },
    'privacy': {
        'name': '🔒 Privacy Mode',
        'description': 'Hide stats from other players',
        'default': False
    },
    'compact': {
        'name': '📱 Compact Mode',
        'description': 'Shorter message format',
        'default': False
    }
}

async def command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show settings menu."""
    user_id = update.effective_user.id
    
    user = db.get_user(user_id)
    if not user:
        await update.message.reply_text("❌ Register first!")
        return
    
    # Get current settings
    settings = user.get('settings', {})
    
    text = "⚙️ **Bot Settings**\n\n"
    text += "Click to toggle settings:\n\n"
    
    keyboard = []
    for setting_id, setting in SETTINGS.items():
        current = settings.get(setting_id, setting['default'])
        status = "✅ ON" if current else "❌ OFF"
        
        text += f"{setting['name']}: {status}\n"
        text += f"   _{setting['description']}_\n\n"
        
        keyboard.append([InlineKeyboardButton(
            f"{setting['name']}: {status}",
            callback_data=f"toggle_{setting_id}"
        )])
    
    keyboard.append([InlineKeyboardButton("🔄 Reset to Default", callback_data="toggle_reset")])
    keyboard.append([InlineKeyboardButton("💾 Save & Close", callback_data="toggle_save")])
    
    await update.message.reply_text(
        text,
        parse_mode='Markdown',
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def toggle_setting(update: Update, context: ContextTypes.DEFAULT_TYPE, user_id: int, setting_id: str):
    """Toggle a specific setting."""
    query = update.callback_query
    
    if setting_id == 'reset':
        db.update_user(user_id, {'$set': {'settings': {}}})
        await query.answer("Settings reset!")
        await command(update, context)
        return
    
    if setting_id == 'save':
        await query.edit_message_text("✅ Settings saved!")
        return
    
    if setting_id not in SETTINGS:
        await query.answer("Invalid setting!")
        return
    
    # Get current value
    user = db.get_user(user_id)
    settings = user.get('settings', {})
    current = settings.get(setting_id, SETTINGS[setting_id]['default'])
    
    # Toggle
    new_value = not current
    settings[setting_id] = new_value
    
    db.update_user(user_id, {'$set': {'settings': settings}})
    
    await query.answer(f"{SETTINGS[setting_id]['name']} {'enabled' if new_value else 'disabled'}!")
    
    # Refresh menu
    await command(update, context)

def get_setting(user_id: int, setting_id: str):
    """Get a specific setting value."""
    user = db.get_user(user_id)
    if not user:
        return SETTINGS.get(setting_id, {}).get('default', False)
    
    settings = user.get('settings', {})
    return settings.get(setting_id, SETTINGS.get(setting_id, {}).get('default', Fal
se))

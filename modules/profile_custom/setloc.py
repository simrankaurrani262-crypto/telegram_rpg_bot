"""
Set location for map
"""
from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler
from database import Database

db = Database()

WAITING_LOCATION = 1

CITIES = {
    'new_york': {'name': '🗽 New York', 'region': 'North America'},
    'london': {'name': '🇬🇧 London', 'region': 'Europe'},
    'tokyo': {'name': '🗼 Tokyo', 'region': 'Asia'},
    'sydney': {'name': '🇦🇺 Sydney', 'region': 'Oceania'},
    'dubai': {'name': '🏜️ Dubai', 'region': 'Middle East'},
    'paris': {'name': '🗼 Paris', 'region': 'Europe'},
    'berlin': {'name': '🏛️ Berlin', 'region': 'Europe'},
    'moscow': {'name': '🏰 Moscow', 'region': 'Europe'},
    'beijing': {'name': '🏯 Beijing', 'region': 'Asia'},
    'mumbai': {'name': '🕌 Mumbai', 'region': 'Asia'},
    'rio': {'name': '🏖️ Rio de Janeiro', 'region': 'South America'},
    'cairo': {'name': '🏺 Cairo', 'region': 'Africa'}
}

async def command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show location menu."""
    text = "📍 **Set Your Location**\n\n"
    text += "Choose a city or send your location:\n\n"
    
    for city_id, city in CITIES.items():
        text += f"{city['name']} - {city['region']}\n"
    
    text += "\nOr type any city name manually!"
    
    await update.message.reply_text(text, parse_mode='Markdown')
    return WAITING_LOCATION

async def start_conv(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Entry point."""
    return await command(update, context)

async def handle_location(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle location input."""
    user_id = update.effective_user.id
    text = update.message.text.strip()
    
    # Check if it's a known city
    location = None
    for city_id, city in CITIES.items():
        if text.lower() in city_id or text.lower() in city['name'].lower():
            location = {
                'city_id': city_id,
                'name': city['name'],
                'region': city['region']
            }
            break
    
    # If not found, use as custom location
    if not location:
        location = {
            'city_id': 'custom',
            'name': text,
            'region': 'Unknown'
        }
    
    # Save
    db.update_user(user_id, {'$set': {'location': location}})
    
    await update.message.reply_text(
        f"✅ **Location set!**\n\n"
        f"📍 {location['name']}\n"
        f"🌍 {location['region']}\n\n"
        f"Use /showmap to see players near you!"
    )
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Cancel."""
    await update.message.reply_text("❌ Cancelled.")
    return ConversationHandl
er.END

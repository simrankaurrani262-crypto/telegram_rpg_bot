"""
Show world map with players
"""
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from database import Database

db = Database()

async def command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show map with players."""
    user_id = update.effective_user.id
    
    user = db.get_user(user_id)
    if not user:
        await update.message.reply_text("❌ Register first!")
        return
    
    my_location = user.get('location')
    
    text = "🗺️ **World Map**\n\n"
    
    if not my_location:
        text += "❌ You haven't set your location!\n"
        text += "Use /setloc to choose your city.\n\n"
    
    # Get all players with locations
    all_players = db.get_users_with_locations()
    
    # Group by region
    regions = {}
    for player in all_players:
        loc = player.get('location', {})
        region = loc.get('region', 'Unknown')
        if region not in regions:
            regions[region] = []
        regions[region].append(player)
    
    text += "**Players by Region**:\n\n"
    
    for region, players in sorted(regions.items()):
        text += f"🌍 **{region}**: {len(players)} players\n"
        # Show top 3 cities in region
        cities = {}
        for p in players:
            city = p.get('location', {}).get('name', 'Unknown')
            cities[city] = cities.get(city, 0) + 1
        
        for city, count in sorted(cities.items(), key=lambda x: -x[1])[:3]:
            marker = "📍" if my_location and city == my_location.get('name') else "  "
            text += f"{marker} {city}: {count}\n"
        text += "\n"
    
    # Find nearby players
    if my_location:
        nearby = [p for p in all_players 
                 if p.get('location', {}).get('region') == my_location.get('region')
                 and p['user_id'] != user_id]
        
        text += f"👥 **Players in your region**: {len(nearby)}\n"
        for p in nearby[:5]:
            text += f"• {p.get('username', 'Unknown')} - {p.get('location', {}).get('name')}\n"
    
    keyboard = [
        [InlineKeyboardButton("📍 Update Location", callback_data="map_setloc")],
        [InlineKeyboardButton("🔍 Find Nearest Players", callback_data="map_nearby")],
        [InlineKeyboardButton("📊 Regional Leaderboard", callback_data="map_regional")]
    ]
    
    await update.message.reply_text(
        text,
        parse_mode='Markdown',
        reply_markup=InlineKeyboardMarkup(keyboard)
)
  

"""
Waifu/Anime character collection system
"""
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from database import Database
import random

db = Database()

# Waifu database
WAIFUS = [
    {'id': 1, 'name': 'Rem', 'anime': 'Re:Zero', 'rarity': 'SSR', 'image': 'rem.jpg'},
    {'id': 2, 'name': 'Mikasa', 'anime': 'Attack on Titan', 'rarity': 'SR', 'image': 'mikasa.jpg'},
    {'id': 3, 'name': 'Asuna', 'anime': 'Sword Art Online', 'rarity': 'SR', 'image': 'asuna.jpg'},
    {'id': 4, 'name': 'Zero Two', 'anime': 'Darling in the Franxx', 'rarity': 'SSR', 'image': 'zerotwo.jpg'},
    {'id': 5, 'name': 'Megumin', 'anime': 'Konosuba', 'rarity': 'R', 'image': 'megumin.jpg'},
    {'id': 6, 'name': 'Saber', 'anime': 'Fate', 'rarity': 'SSR', 'image': 'saber.jpg'},
    {'id': 7, 'name': 'Emilia', 'anime': 'Re:Zero', 'rarity': 'SR', 'image': 'emilia.jpg'},
    {'id': 8, 'name': 'Hinata', 'anime': 'Naruto', 'rarity': 'R', 'image': 'hinata.jpg'},
    {'id': 9, 'name': 'Taiga', 'anime': 'Toradora', 'rarity': 'R', 'image': 'taiga.jpg'},
    {'id': 10, 'name': 'Mai', 'anime': 'Bunny Girl Senpai', 'rarity': 'SR', 'image': 'mai.jpg'}
]

RARITY_RATES = {
    'N': 50,   # Normal 50%
    'R': 30,   # Rare 30%
    'SR': 15,  # Super Rare 15%
    'SSR': 4,  # Super Super Rare 4%
    'UR': 1    # Ultra Rare 1%
}

RARITY_COLORS = {
    'N': '⬜',
    'R': '🟦',
    'SR': '🟪',
    'SSR': '🟨',
    'UR': '🟥'
}

async def command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show waifu collection."""
    user_id = update.effective_user.id
    
    user = db.get_user(user_id)
    if not user:
        await update.message.reply_text("❌ Register first!")
        return
    
    collection = db.get_waifu_collection(user_id)
    
    text = f"💖 **Your Waifu Collection**\n\n"
    text += f"Collected: {len(collection)}/{len(WAIFUS)}\n"
    
    # Count by rarity
    rarity_counts = {}
    for w in collection:
        r = w.get('rarity', 'N')
        rarity_counts[r] = rarity_counts.get(r, 0) + 1
    
    text += f"Rarity: "
    for r in ['UR', 'SSR', 'SR', 'R', 'N']:
        if r in rarity_counts:
            text += f"{RARITY_COLORS[r]}{rarity_counts[r]} "
    text += "\n\n"
    
    # Show collection
    if collection:
        text += "**Your Waifus**:\n"
        for waifu in collection[-10:]:  # Show last 10
            emoji = RARITY_COLORS.get(waifu['rarity'], '⬜')
            text += f"{emoji} {waifu['name']} ({waifu['anime']})\n"
    else:
        text += "📭 Collection empty!\n"
    
    text += "\n**Summon Rates**:\n"
    for rarity, rate in RARITY_RATES.items():
        text += f"{RARITY_COLORS[rarity]} {rarity}: {rate}%\n"
    
    keyboard = [
        [InlineKeyboardButton("🎲 Summon (1000💰)", callback_data="waifu_summon")],
        [InlineKeyboardButton("🎁 Free Summon", callback_data="waifu_free")],
        [InlineKeyboardButton("📊 View All", callback_data="waifu_all")],
        [InlineKeyboardButton("💝 Set Favorite", callback_data="waifu_fav")]
    ]
    
    await update.message.reply_text(
        text,
        parse_mode='Markdown',
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def summon(update: Update, context: ContextTypes.DEFAULT_TYPE, free: bool = False):
    """Summon a waifu."""
    query = update.callback_query
    user_id = query.from_user.id
    
    if not free:
        user = db.get_user(user_id)
        if user['money'] < 1000:
            await query.answer("❌ Need 1000 coins!")
            return
    
    # Determine rarity
    roll = random.randint(1, 100)
    cumulative = 0
    rarity = 'N'
    for r, rate in sorted(RARITY_RATES.items(), key=lambda x: -x[1]):
        cumulative += rate
        if roll <= cumulative:
            rarity = r
            break
    
    # Get random waifu of that rarity
    available = [w for w in WAIFUS if w['rarity'] == rarity]
    if not available:
        available = WAIFUS
    
    waifu = random.choice(available)
    
    # Check if already owned
    collection = db.get_waifu_collection(user_id)
    already_have = any(w['id'] == waifu['id'] for w in collection)
    
    if not free:
        db.update_user(user_id, {'$inc': {'money': -1000}})
    
    if not already_have:
        db.add_waifu_to_collection(user_id, waifu)
        result = "✨ NEW!"
    else:
        # Convert to shards or coins
        shards = {'N': 1, 'R': 2, 'SR': 5, 'SSR': 10, 'UR': 20}.get(rarity, 1)
        db.update_user(user_id, {'$inc': {'waifu_shards': shards}})
        result = f"♻️ Duplicate (+{shards} shards)"
    
    await query.answer(f"Summoned {waifu['name']}!")
    await query.edit_message_text(
        f"🎉 **Summon Result**\n\n"
        f"{RARITY_COLORS[rarity]} **{waifu['name']}**\n"
        f"📺 {waifu['anime']}\n"
        f"💎 Rarity: {rarity}\n"
        f"📝 {result}\n\n"
        f"Use /waifu to summon more!"
    )

async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE, data: str):
    """Handle waifu callbacks."""
    if data == "waifu_summon":
        await summon(update, context, free=False)
    elif data == "waifu_free":
        # Check cooldown for free summon
        await summon(update, context, free=True)
    elif data == "waifu_all":
        await show_all_waifus(update, context)
    elif data == "waifu_fav":
        await set_favorite(update, context)

async def show_all_waifus(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show all available waifus."""
    text = "📚 **All Waifus**\n\n"
    
    for rarity in ['UR', 'SSR', 'SR', 'R', 'N']:
        waifus = [w for w in WAIFUS if w['rarity'] == rarity]
        if waifus:
            text += f"{RARITY_COLORS[rarity]} **{rarity}**:\n"
            for w in waifus:
                text += f"  • {w['name']} - {w['anime']}\n"
            text += "\n"
    
    await update.callback_query.edit_message_text(text, parse_mode='Markdown')

async def set_favorite(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Set favorite waifu."""
    await update.callback_query.edit_message_text(
        "💝 Send the name of your favorite waifu from your collection!"
)

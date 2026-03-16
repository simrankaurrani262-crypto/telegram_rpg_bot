"""
Inline query handlers for @botname queries
"""
from telegram import (
    InlineQueryResultArticle, 
    InputTextMessageContent,
    InlineKeyboardButton,
    InlineKeyboardMarkup
)
from telegram.ext import ContextTypes
from database import Database

db = Database()

async def handle_inline(update, context):
    """Handle inline queries."""
    query = update.inline_query.query
    user_id = update.inline_query.from_user.id
    
    if not query:
        # Show default suggestions
        results = get_default_results()
    elif query.startswith('waifu'):
        results = await search_waifus(query.replace('waifu ', ''))
    elif query.startswith('stats'):
        results = await get_user_stats(user_id)
    elif query.startswith('market'):
        results = await search_market(query.replace('market ', ''))
    elif query.startswith('price'):
        results = await check_prices(query.replace('price ', ''))
    else:
        results = await general_search(query)
    
    await update.inline_query.answer(results, cache_time=10)

def get_default_results():
    """Get default inline suggestions."""
    return [
        InlineQueryResultArticle(
            id='1',
            title='📊 My Stats',
            description='Show your RPG stats',
            input_message_content=InputTextMessageContent('/profile'),
            thumb_url='https://cdn-icons-png.flaticon.com/512/2928/2928750.png'
        ),
        InlineQueryResultArticle(
            id='2',
            title='💰 Balance',
            description='Check your money',
            input_message_content=InputTextMessageContent('/balance'),
            thumb_url='https://cdn-icons-png.flaticon.com/512/2474/2474450.png'
        ),
        InlineQueryResultArticle(
            id='3',
            title='🎲 Games',
            description='Play mini-games',
            input_message_content=InputTextMessageContent('/lottery'),
            thumb_url='https://cdn-icons-png.flaticon.com/512/1041/1041916.png'
        ),
        InlineQueryResultArticle(
            id='4',
            title='👨‍👩‍👧 Family',
            description='View family tree',
            input_message_content=InputTextMessageContent('/family'),
            thumb_url='https://cdn-icons-png.flaticon.com/512/4129/4129437.png'
        )
    ]

async def search_waifus(search_term):
    """Search waifu database."""
    from modules.anime.waifu import WAIFUS
    
    results = []
    matching = [w for w in WAIFUS if search_term.lower() in w['name'].lower()]
    
    for waifu in matching[:5]:
        rarity_emoji = {'N': '⬜', 'R': '🟦', 'SR': '🟪', 'SSR': '🟨', 'UR': '🟥'}.get(waifu['rarity'], '⬜')
        
        results.append(InlineQueryResultArticle(
            id=f"waifu_{waifu['id']}",
            title=f"{rarity_emoji} {waifu['name']}",
            description=f"{waifu['anime']} - {waifu['rarity']}",
            input_message_content=InputTextMessageContent(
                f"💖 **{waifu['name']}**\n"
                f"📺 {waifu['anime']}\n"
                f"💎 Rarity: {waifu['rarity']}\n"
                f"Use /waifu to collect!"
            ),
            thumb_url=f"https://example.com/waifu/{waifu['image']}"  # Replace with actual URL
        ))
    
    return results

async def get_user_stats(user_id):
    """Get user stats for inline."""
    user = db.get_user(user_id)
    if not user:
        return []
    
    text = (
        f"📊 **Stats for {user.get('username', 'User')}**\n\n"
        f"💰 Money: {user.get('money', 0):,}\n"
        f"🏦 Bank: {user.get('bank', 0):,}\n"
        f"⭐ Level: {user.get('level', 1)}\n"
        f"📈 XP: {user.get('experience', 0)}\n"
        f"👨‍🌾 Job: {user.get('job', 'Beggar')}"
    )
    
    return [
        InlineQueryResultArticle(
            id='stats',
            title='📊 My RPG Stats',
            description=f"Level {user.get('level', 1)} | {user.get('money', 0):,} coins",
            input_message_content=InputTextMessageContent(text),
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("Open Profile", url=f"https://t.me/your_bot?start=profile")]
            ])
        )
    ]

async def search_market(search_term):
    """Search market listings."""
    listings = db.search_market_listings(search_term)
    
    results = []
    for item in listings[:5]:
        results.append(InlineQueryResultArticle(
            id=f"market_{item['_id']}",
            title=f"🛒 {item['name']} - {item['price']:,}💰",
            description=f"Seller: {item.get('seller_name', 'Unknown')} | Stock: {item['quantity']}",
            input_message_content=InputTextMessageContent(
                f"🛒 **Market Listing**\n\n"
                f"Item: {item['name']}\n"
                f"Price: {item['price']:,}💰\n"
                f"Seller: {item.get('seller_name', 'Unknown')}\n\n"
                f"Use /stand to browse full market!"
            )
        ))
    
    return results

async def check_prices(item_name):
    """Check item prices."""
    # Get average market price
    avg_price = db.get_average_price(item_name)
    
    return [
        InlineQueryResultArticle(
            id='price',
            title=f'💰 Price Check: {item_name}',
            description=f'Average: {avg_price:,} coins' if avg_price else 'No data',
            input_message_content=InputTextMessageContent(
                f"💰 **Price Check: {item_name}**\n\n"
                f"Market Average: {avg_price:,}💰\n" if avg_price else "No market data available\n"
                f"Use /shop for official prices"
            )
        )
    ]

async def general_search(query):
    """General search across all features."""
    results = []
    
    # Search commands
    commands = {
        'money': ('/balance', 'Check your balance'),
        'work': ('/job', 'Work and earn money'),
        'family': ('/family', 'View family'),
        'garden': ('/garden', 'Your farm'),
        'games': ('/lottery', 'Play games'),
        'help': ('/help', 'Get help')
    }
    
    for cmd, (path, desc) in commands.items():
        if query.lower() in cmd or query.lower() in desc.lower():
            results.append(InlineQueryResultArticle(
                id=f"cmd_{cmd}",
                title=f"⌨️ {path}",
                description=desc,
                input_message_content=InputTextMessageContent(path)
            ))
    
    return results[:10]

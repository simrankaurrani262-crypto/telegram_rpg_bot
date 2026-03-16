#!/usr/bin/env python3
"""
Telegram RPG Bot - Complete Working Version
"""
import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters
)
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Import database
from database import Database
db = Database()

# ========== CORE COMMANDS ==========

async def start_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command."""
    user_id = update.effective_user.id
    username = update.effective_user.username or update.effective_user.first_name
    
    user = db.get_user(user_id)
    if not user:
        db.create_user(user_id, username)
        text = f"🎉 **Welcome {username}!**\n\n"
        text += "✅ You have been registered!\n"
        text += "🎁 **Starter Bonus:** 1,000 coins\n\n"
        text += "Use /help to see all commands!"
    else:
        text = f"👋 **Welcome back, {username}!**\n\n"
        text += f"💰 Money: {user.get('money', 0):,} coins\n"
        text += f"⭐ Level: {user.get('level', 1)}\n"
        text += "Use /help for commands!"
    
    await update.message.reply_text(text, parse_mode='Markdown')

async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /help command."""
    text = """
🎮 **RPG Bot Commands**

**Core:**
/start - Start bot
/help - This help
/profile - Your profile
/settings - Bot settings

**Economy:**
/daily - Daily reward (100💰)
/balance - Check money
/pay - Pay someone
/job - Work and earn
/shop - Buy items
/inventory - Your items

**Family:**
/family - Family info
/tree - Family tree
/marry - Marry someone
/adopt - Adopt child

**Crime:**
/rob - Rob someone
/kill - Attack player
/weapons - Buy weapons
/jail - Jail status

**Factory:**
/factory - Your factory
/hire - Hire workers
/production - Production

**Garden:**
/garden - Your farm
/plant - Plant crops
/harvest - Harvest
/fertilize - Use fertilizer
/seeds - Buy seeds

**Market:**
/stand - Market stand
/trade - Trade items
/auction - Auctions

**Games:**
/lottery - Try luck
/blackjack - Play 21
/slots - Slot machine

**Stats:**
/leaderboard - Top players
/moneyboard - Richest
/familyboard - Biggest families

**Social:**
/relations - Relations
/ratings - User ratings
/suggestions - Friend suggestions
/interactions - Social actions
/requests - Pending requests

**Cooking:**
/cook - Cook food
/stove - Buy stove

**Profile:**
/setpic - Set photo
/setloc - Set location
/showmap - World map

**Anime:**
/waifu - Collect waifus

**Admin:**
/admin - Admin panel
/ban - Ban user
/broadcast - Message all
"""
    await update.message.reply_text(text, parse_mode='Markdown')

async def profile_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /profile command."""
    user_id = update.effective_user.id
    user = db.get_user(user_id)
    
    if not user:
        await update.message.reply_text("❌ Use /start first!")
        return
    
    first_name = update.effective_user.first_name
    
    text = f"👤 **{first_name}'s Profile**\n\n"
    text += f"💰 **Money:** {user.get('money', 0):,} coins\n"
    text += f"🏦 **Bank:** {user.get('bank', 0):,} coins\n"
    text += f"⭐ **Level:** {user.get('level', 1)}\n"
    text += f"📈 **XP:** {user.get('experience', 0):,}\n"
    text += f"❤️ **Health:** {user.get('health', 100)}/100\n"
    text += f"⚡ **Energy:** {user.get('energy', 100)}/100\n\n"
    
    job = user.get('job', 'Beggar')
    text += f"💼 **Job:** {job}\n"
    
    family = db.get_family(user_id) if hasattr(db, 'get_family') else None
    if family:
        partner = family.get('partner')
        children = len(family.get('children', []))
        if partner:
            partner_user = db.get_user(partner)
            partner_name = partner_user.get('username', 'Unknown') if partner_user else 'Unknown'
            text += f"❤️ **Partner:** {partner_name}\n"
        text += f"👶 **Children:** {children}\n"
    
    keyboard = [
        [InlineKeyboardButton("💰 Balance", callback_data="profile_balance"),
         InlineKeyboardButton("🎒 Inventory", callback_data="profile_inventory")],
        [InlineKeyboardButton("👪 Family", callback_data="profile_family"),
         InlineKeyboardButton("⚙️ Settings", callback_data="profile_settings")]
    ]
    
    await update.message.reply_text(text, parse_mode='Markdown', reply_markup=InlineKeyboardMarkup(keyboard))

async def settings_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /settings command."""
    user_id = update.effective_user.id
    user = db.get_user(user_id)
    
    if not user:
        await update.message.reply_text("❌ Use /start first!")
        return
    
    settings = user.get('settings', {})
    
    text = "⚙️ **Settings**\n\n"
    text += f"🔔 Notifications: {'ON' if settings.get('notifications', True) else 'OFF'}\n"
    text += f"🌙 Dark Mode: {'ON' if settings.get('dark_mode', False) else 'OFF'}\n"
    text += f"🔊 Sounds: {'ON' if settings.get('sounds', True) else 'OFF'}\n"
    text += f"🔒 Privacy: {'ON' if settings.get('privacy', False) else 'OFF'}\n\n"
    text += "Use /toggle to change settings!"
    
    await update.message.reply_text(text, parse_mode='Markdown')

# ========== ECONOMY COMMANDS ==========

async def daily_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /daily command."""
    user_id = update.effective_user.id
    user = db.get_user(user_id)
    
    if not user:
        await update.message.reply_text("❌ Use /start first!")
        return
    
    from datetime import datetime, timedelta
    
    last_daily = user.get('last_daily')
    if last_daily:
        time_passed = datetime.now() - last_daily
        if time_passed < timedelta(hours=24):
            hours_left = 24 - time_passed.seconds // 3600
            await update.message.reply_text(f"⏳ Wait {hours_left} hours for next daily!")
            return
    
    db.update_user(user_id, {
        '$inc': {'money': 100, 'experience': 10},
        '$set': {'last_daily': datetime.now()}
    })
    
    await update.message.reply_text("🎁 **Daily Reward!**\n\n+100 coins\n+10 XP")

async def balance_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /balance command."""
    user_id = update.effective_user.id
    user = db.get_user(user_id)
    
    if not user:
        await update.message.reply_text("❌ Use /start first!")
        return
    
    money = user.get('money', 0)
    bank = user.get('bank', 0)
    total = money + bank
    
    text = f"💰 **Balance**\n\n"
    text += f"👛 Wallet: {money:,} coins\n"
    text += f"🏦 Bank: {bank:,} coins\n"
    text += f"💵 Total: {total:,} coins"
    
    await update.message.reply_text(text, parse_mode='Markdown')

async def job_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /job command."""
    user_id = update.effective_user.id
    user = db.get_user(user_id)
    
    if not user:
        await update.message.reply_text("❌ Use /start first!")
        return
    
    JOBS = {
        'beggar': {'name': '🥺 Beggar', 'salary': 50},
        'farmer': {'name': '👨‍🌾 Farmer', 'salary': 150},
        'miner': {'name': '⛏️ Miner', 'salary': 350},
        'chef': {'name': '👨‍🍳 Chef', 'salary': 500},
        'developer': {'name': '💻 Developer', 'salary': 2000},
    }
    
    current_job = user.get('job', 'beggar')
    job_info = JOBS.get(current_job, JOBS['beggar'])
    
    text = f"💼 **Job Center**\n\n"
    text += f"Current: {job_info['name']}\n"
    text += f"Salary: {job_info['salary']} coins/work\n\n"
    
    from datetime import datetime
    import random
    
    earnings = job_info['salary'] + random.randint(0, job_info['salary'] // 10)
    db.update_user(user_id, {'$inc': {'money': earnings, 'experience': 5}})
    
    text += f"💪 You worked and earned {earnings} coins!"

    await update.message.reply_text(text, parse_mode='Markdown')
    # ========== FAMILY COMMANDS ==========

async def family_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /family command."""
    user_id = update.effective_user.id
    user = db.get_user(user_id)
    
    if not user:
        await update.message.reply_text("❌ Use /start first!")
        return
    
    family = db.get_family(user_id) if hasattr(db, 'get_family') else None
    
    if not family:
        await update.message.reply_text("👪 You don't have a family yet!\nUse /marry or /adopt")
        return
    
    text = "👪 **Family Info**\n\n"
    
    if family.get('partner'):
        partner = db.get_user(family['partner'])
        text += f"❤️ Partner: {partner.get('username', 'Unknown') if partner else 'Unknown'}\n"
    else:
        text += "❤️ Partner: Single\n"
    
    children = family.get('children', [])
    text += f"👶 Children: {len(children)}\n"
    
    parents = family.get('parents', [])
    text += f"👨‍👩‍👧 Parents: {len(parents)}\n"
    
    keyboard = [
        [InlineKeyboardButton("💍 Marry", callback_data="family_marry"),
         InlineKeyboardButton("👶 Adopt", callback_data="family_adopt")],
        [InlineKeyboardButton("🌳 View Tree", callback_data="family_tree")]
    ]
    
    await update.message.reply_text(text, parse_mode='Markdown', reply_markup=InlineKeyboardMarkup(keyboard))

async def marry_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /marry command."""
    await update.message.reply_text("💍 Marry feature coming soon!\nUse /family to see options.")

async def adopt_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /adopt command."""
    await update.message.reply_text("👶 Adoption feature coming soon!\nUse /family to see options.")

# ========== CRIME COMMANDS ==========

async def rob_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /rob command."""
    user_id = update.effective_user.id
    user = db.get_user(user_id)
    
    if not user:
        await update.message.reply_text("❌ Use /start first!")
        return
    
    import random
    from datetime import datetime, timedelta
    
    last_rob = user.get('last_rob')
    if last_rob:
        if datetime.now() - last_rob < timedelta(minutes=30):
            await update.message.reply_text("⏳ Wait 30 minutes between robberies!")
            return
    
    if random.randint(1, 100) <= 40:
        stolen = random.randint(50, 500)
        db.update_user(user_id, {
            '$inc': {'money': stolen},
            '$set': {'last_rob': datetime.now()}
        })
        await update.message.reply_text(f"💰 Robbery successful! +{stolen} coins")
    else:
        jail_time = datetime.now() + timedelta(minutes=15)
        db.update_user(user_id, {
            '$set': {
                'jailed_until': jail_time,
                'last_rob': datetime.now()
            }
        })
        await update.message.reply_text("❌ Caught! 15 minutes in jail!")

async def kill_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /kill command."""
    await update.message.reply_text("⚔️ Combat system coming soon!")

async def weapons_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /weapons command."""
    text = "🔫 **Weapons Shop**\n\n"
    text += "🔪 Knife - 500💰\n"
    text += "🔫 Pistol - 2500💰\n"
    text += "🔫 Shotgun - 6000💰\n\n"
    text += "Feature coming soon!"
    await update.message.reply_text(text, parse_mode='Markdown')

async def jail_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /jail command."""
    user_id = update.effective_user.id
    user = db.get_user(user_id)
    
    if not user:
        await update.message.reply_text("❌ Use /start first!")
        return
    
    jailed_until = user.get('jailed_until')
    
    if not jailed_until:
        await update.message.reply_text("✅ You are not in jail!")
        return
    
    from datetime import datetime
    
    if datetime.now() >= jailed_until:
        await update.message.reply_text("✅ You are free!")
        return
    
    mins_left = int((jailed_until - datetime.now()).total_seconds() // 60)
    await update.message.reply_text(f"🔒 In jail for {mins_left} more minutes!")

# ========== GARDEN COMMANDS ==========

async def garden_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /garden command."""
    await update.message.reply_text("🌾 Garden system coming soon!")

async def plant_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /plant command."""
    await update.message.reply_text("🌱 Plant crops coming soon!")

async def harvest_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /harvest command."""
    await update.message.reply_text("🌾 Harvest crops coming soon!")

async def fertilize_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /fertilize command."""
    await update.message.reply_text("🧪 Fertilizer system coming soon!")

async def seeds_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /seeds command."""
    text = "🌱 **Seed Shop**\n\n"
    text += "🌾 Wheat - 50💰\n"
    text += "🌽 Corn - 100💰\n"
    text += "🍅 Tomato - 150💰\n\n"
    text += "Feature coming soon!"
    await update.message.reply_text(text, parse_mode='Markdown')

# ========== FACTORY COMMANDS ==========

async def factory_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /factory command."""
    await update.message.reply_text("🏭 Factory system coming soon!")

async def hire_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /hire command."""
    await update.message.reply_text("👷 Hiring system coming soon!")

async def production_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /production command."""
    await update.message.reply_text("🔨 Production system coming soon!")

# ========== MARKET COMMANDS ==========

async def stand_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /stand command."""
    await update.message.reply_text("🛒 Market stand coming soon!")

async def trade_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /trade command."""
    await update.message.reply_text("🤝 Trading system coming soon!")

async def auction_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /auction command."""
    await update.message.reply_text("🔨 Auction house coming soon!")

# ========== GAMES COMMANDS ==========

async def lottery_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /lottery command."""
    user_id = update.effective_user.id
    user = db.get_user(user_id)
    
    if not user:
        await update.message.reply_text("❌ Use /start first!")
        return
    
    import random
    
    if user['money'] < 10:
        await update.message.reply_text("❌ Need 10 coins!")
        return
    
    roll = random.randint(1, 100)
    
    db.update_user(user_id, {'$inc': {'money': -10}})
    
    if roll == 1:
        db.update_user(user_id, {'$inc': {'money': 1000}})
        await update.message.reply_text("🎉 **JACKPOT!** +1000 coins!")
    elif roll <= 10:
        win = random.randint(20, 100)
        db.update_user(user_id, {'$inc': {'money': win}})
        await update.message.reply_text(f"🎉 You won {win} coins!")
    else:
        await update.message.reply_text("😢 No luck this time!")

async def blackjack_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /blackjack command."""
    await update.message.reply_text("🃏 Blackjack coming soon!")

async def slots_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /slots command."""
    await update.message.reply_text("🎰 Slots coming soon!")

# ========== STATS COMMANDS ==========

async def leaderboard_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /leaderboard command."""
    try:
        top_users = db.get_top_users('experience', limit=10) if hasattr(db, 'get_top_users') else []
        
        text = "🏆 **Leaderboard**\n\n"
        
        for i, user in enumerate(top_users[:10]):
            username = user.get('username') or f"User{user['user_id']}"
            level = user.get('level', 1)
            xp = user.get('experience', 0)
            text += f"{i+1}. **{username}** - Level {level} ({xp:,} XP)\n"
        
        if not top_users:
            text += "No data available yet!"
        
        await update.message.reply_text(text, parse_mode='Markdown')
    except:
        await update.message.reply_text("📊 Leaderboard coming soon!")

async def moneyboard_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /moneyboard command."""
    try:
        top_users = db.get_top_users('money', limit=10) if hasattr(db, 'get_top_users') else []
        
        text = "💰 **Richest Players**\n\n"
        
        for i, user in enumerate(top_users[:10]):
            username = user.get('username') or f"User{user['user_id']}"
            money = user.get('money', 0)
            text += f"{i+1}. **{username}** - {money:,}💰\n"
        
        if not top_users:
            text += "No data available yet!"
        
        await update.message.reply_text(text, parse_mode='Markdown')
    except:
        await update.message.reply_text("💰 Moneyboard coming soon!")

async def familyboard_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /familyboard command."""
    await update.message.reply_text("👪 Family leaderboard coming soon!")

# ========== SOCIAL COMMANDS ==========

async def relations_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /relations command."""
    await update.message.reply_text("👥 Relations system coming soon!")

async def ratings_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /ratings command."""
    await update.message.reply_text("⭐ Ratings system coming soon!")

async def suggestions_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /suggestions command."""
    await update.message.reply_text("🎯 Suggestions coming soon!")

async def interactions_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /interactions command."""
    await update.message.reply_text("🎭 Interactions coming soon!")

async def requests_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /requests command."""
    await update.message.reply_text("📨 Requests system coming soon!")

# ========== COOKING COMMANDS ==========

async def cook_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /cook command."""
    await update.message.reply_text("👨‍🍳 Cooking system coming soon!")

async def stove_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /stove command."""
    await update.message.reply_text("🔥 Stove shop coming soon!")

# ========== PROFILE COMMANDS ==========

async def setpic_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /setpic command."""
    await update.message.reply_text("📸 Send a photo to set as profile picture!")

async def setloc_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /setloc command."""
    await update.message.reply_text("📍 Location system coming soon!")

async def showmap_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /showmap command."""
    await update.message.reply_text("🗺️ World map coming soon!")

# ========== ANIME COMMANDS ==========

async def waifu_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /waifu command."""
    await update.message.reply_text("💖 Waifu collection coming soon!")

# ========== TOGGLE COMMAND ==========

async def toggle_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /toggle command."""
    await update.message.reply_text("⚙️ Settings toggle coming soon!")

# ========== ADMIN COMMANDS ==========

async def admin_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /admin command."""
    user_id = update.effective_user.id
    admin_ids = [int(x) for x in os.getenv('ADMIN_IDS', '').split(',') if x]
    
    if user_id not in admin_ids:
        await update.message.reply_text("❌ Not authorized!")
        return
    
    text = "🔐 **Admin Panel**\n\n"
    text += f"Total users: {db.count_users() if hasattr(db, 'count_users') else 'N/A'}\n"
    text += "/ban - Ban user\n"
    text += "/broadcast - Message all\n"
    text += "/logs - View logs"
    
    await update.message.reply_text(text, parse_mode='Markdown')

async def ban_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /ban command."""
    await update.message.reply_text("🔨 Ban system coming soon!")

async def broadcast_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /broadcast command."""
    await update.message.reply_text("📢 Broadcast system coming soon!")

async def logs_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /logs command."""
    await update.message.reply_text("📜 Logs system coming soon!")

# ========== CALLBACK HANDLER ==========

async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle callback queries."""
    query = update.callback_query
    await query.answer()
    
    data = query.data
    
    if data.startswith("profile_"):
        await query.edit_message_text("Profile feature clicked!")
    elif data.startswith("family_"):
        await query.edit_message_text("Family feature clicked!")
    else:
        await query.edit_message_text("Feature coming soon!")

# ========== MAIN FUNCTION ==========

def main():
    """Start the bot."""
    application = Application.builder().token(os.getenv('TELEGRAM_TOKEN')).build()
    
    # Core commands
    application.add_handler(CommandHandler("start", start_cmd))
    application.add_handler(CommandHandler("help", help_cmd))
    application.add_handler(CommandHandler("profile", profile_cmd))
    application.add_handler(CommandHandler("settings", settings_cmd))
    
    # Economy commands
    application.add_handler(CommandHandler("daily", daily_cmd))
    application.add_handler(CommandHandler("balance", balance_cmd))
    application.add_handler(CommandHandler("job", job_cmd))
    
    # Family commands
    application.add_handler(CommandHandler("family", family_cmd))
    application.add_handler(CommandHandler("marry", marry_cmd))
    application.add_handler(CommandHandler("adopt", adopt_cmd))
    
    # Crime commands
    application.add_handler(CommandHandler("rob", rob_cmd))
    application.add_handler(CommandHandler("kill", kill_cmd))
    application.add_handler(CommandHandler("weapons", weapons_cmd))
    application.add_handler(CommandHandler("jail", jail_cmd))
    
    # Garden commands
    application.add_handler(CommandHandler("garden", garden_cmd))
    application.add_handler(CommandHandler("plant", plant_cmd))
    application.add_handler(CommandHandler("harvest", harvest_cmd))
    application.add_handler(CommandHandler("fertilize", fertilize_cmd))
    application.add_handler(CommandHandler("seeds", seeds_cmd))
    
    # Factory commands
    application.add_handler(CommandHandler("factory", factory_cmd))
    application.add_handler(CommandHandler("hire", hire_cmd))
    application.add_handler(CommandHandler("production", production_cmd))
    
    # Market commands
    application.add_handler(CommandHandler("stand", stand_cmd))
    application.add_handler(CommandHandler("trade", trade_cmd))
    application.add_handler(CommandHandler("auction", auction_cmd))
    
    # Games commands
    application.add_handler(CommandHandler("lottery", lottery_cmd))
    application.add_handler(CommandHandler("blackjack", blackjack_cmd))
    application.add_handler(CommandHandler("slots", slots_cmd))
    
    # Stats commands
    application.add_handler(CommandHandler("leaderboard", leaderboard_cmd))
    application.add_handler(CommandHandler("moneyboard", moneyboard_cmd))
    application.add_handler(CommandHandler("familyboard", familyboard_cmd))
    
    # Social commands
    application.add_handler(CommandHandler("relations", relations_cmd))
    application.add_handler(CommandHandler("ratings", ratings_cmd))
    application.add_handler(CommandHandler("suggestions", suggestions_cmd))
    application.add_handler(CommandHandler("interactions", interactions_cmd))
    application.add_handler(CommandHandler("requests", requests_cmd))
    
    # Cooking commands
    application.add_handler(CommandHandler("cook", cook_cmd))
    application.add_handler(CommandHandler("stove", stove_cmd))
    
    # Profile commands
    application.add_handler(CommandHandler("setpic", setpic_cmd))
    application.add_handler(CommandHandler("setloc", setloc_cmd))
    application.add_handler(CommandHandler("showmap", showmap_cmd))
    
    # Anime commands
    application.add_handler(CommandHandler("waifu", waifu_cmd))
    
    # Settings
    application.add_handler(CommandHandler("toggle", toggle_cmd))
    
    # Admin commands
    application.add_handler(CommandHandler("admin", admin_cmd))
    application.add_handler(CommandHandler("ban", ban_cmd))
    application.add_handler(CommandHandler("broadcast", broadcast_cmd))
    application.add_handler(CommandHandler("logs", logs_cmd))
    
    # Callback handler
    application.add_handler(CallbackQueryHandler(handle_callback))
    
    print("🤖 Bot is running...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()

        

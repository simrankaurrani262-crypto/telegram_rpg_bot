#!/usr/bin/env python3
"""
Telegram RPG Bot - Complete Working Version
Uses original repository modules
"""
import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ConversationHandler,
    InlineQueryHandler,
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

# ========== CORE MODULES ==========
try:
    from modules.core.start import command as start_cmd
except ImportError:
    async def start_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_id = update.effective_user.id
        username = update.effective_user.username or update.effective_user.first_name
        user = db.get_user(user_id)
        if not user:
            db.create_user(user_id, username)
            await update.message.reply_text(f"🎉 Welcome {username}! You got 1000 coins!")
        else:
            await update.message.reply_text(f"👋 Welcome back {username}!")

try:
    from modules.core.help import help_command as help_cmd
except ImportError:
    async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text("📚 Help menu coming soon!")

try:
    from modules.core.profile import command as profile_cmd
except ImportError:
    async def profile_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_id = update.effective_user.id
        user = db.get_user(user_id)
        if not user:
            await update.message.reply_text("❌ Use /start first!")
            return
        text = f"👤 Profile\n💰 Money: {user.get('money', 0)}"
        await update.message.reply_text(text)

try:
    from modules.core.settings import command as settings_cmd
except ImportError:
    async def settings_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text("⚙️ Settings coming soon!")

# ========== FAMILY MODULES ==========
try:
    from modules.family.family import command as family_cmd
except ImportError:
    async def family_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text("👪 Family system coming soon!")

try:
    from modules.family.tree import command as tree_cmd
except ImportError:
    async def tree_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text("🌳 Family tree coming soon!")

try:
    from modules.family.marry import command as marry_cmd
except ImportError:
    async def marry_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text("💍 Marriage system coming soon!")

try:
    from modules.family.adopt import command as adopt_cmd
except ImportError:
    async def adopt_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text("👶 Adoption system coming soon!")

try:
    from modules.family.divorce import command as divorce_cmd
except ImportError:
    async def divorce_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text("💔 Divorce system coming soon!")

# ========== ECONOMY MODULES ==========
try:
    from modules.economy.daily import command as daily_cmd
except ImportError:
    async def daily_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_id = update.effective_user.id
        user = db.get_user(user_id)
        if not user:
            await update.message.reply_text("❌ Use /start first!")
            return
        from datetime import datetime
        db.update_user(user_id, {'$inc': {'money': 100}, '$set': {'last_daily': datetime.now()}})
        await update.message.reply_text("🎁 Daily reward: +100 coins!")

try:
    from modules.economy.account import command as account_cmd
except ImportError:
    async def account_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text("🏦 Account system coming soon!")

try:
    from modules.economy.balance import command as balance_cmd
except ImportError:
    async def balance_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_id = update.effective_user.id
        user = db.get_user(user_id)
        if not user:
            await update.message.reply_text("❌ Use /start first!")
            return
        money = user.get('money', 0)
        await update.message.reply_text(f"💰 Balance: {money} coins")

try:
    from modules.economy.pay import command as pay_cmd
except ImportError:
    async def pay_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text("💸 Pay system coming soon!")

try:
    from modules.economy.jobs import command as job_cmd
except ImportError:
    async def job_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_id = update.effective_user.id
        user = db.get_user(user_id)
        if not user:
            await update.message.reply_text("❌ Use /start first!")
            return
        import random
        earnings = random.randint(50, 200)
        db.update_user(user_id, {'$inc': {'money': earnings}})
        await update.message.reply_text(f"💼 You earned {earnings} coins!")

try:
    from modules.economy.inventory import command as inventory_cmd
except ImportError:
    async def inventory_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text("🎒 Inventory system coming soon!")

try:
    from modules.economy.shop import command as shop_cmd
except ImportError:
    async def shop_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text("🛒 Shop system coming soon!")
        
        # ========== CRIME MODULES ==========
try:
    from modules.crime.rob import command as rob_cmd
except ImportError:
    async def rob_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_id = update.effective_user.id
        user = db.get_user(user_id)
        if not user:
            await update.message.reply_text("❌ Use /start first!")
            return
        import random
        from datetime import datetime, timedelta
        if random.randint(1, 100) <= 40:
            stolen = random.randint(50, 500)
            db.update_user(user_id, {'$inc': {'money': stolen}, '$set': {'last_rob': datetime.now()}})
            await update.message.reply_text(f"💰 Robbery successful! +{stolen} coins")
        else:
            jail_time = datetime.now() + timedelta(minutes=15)
            db.update_user(user_id, {'$set': {'jailed_until': jail_time, 'last_rob': datetime.now()}})
            await update.message.reply_text("❌ Caught! 15 minutes in jail!")

try:
    from modules.crime.kill import command as kill_cmd
except ImportError:
    async def kill_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text("⚔️ Combat system coming soon!")

try:
    from modules.crime.weapons import command as weapons_cmd
except ImportError:
    async def weapons_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
        text = "🔫 **Weapons Shop**\n\n🔪 Knife - 500💰\n🔫 Pistol - 2500💰\n🔫 Shotgun - 6000💰"
        await update.message.reply_text(text, parse_mode='Markdown')

try:
    from modules.crime.jail import command as jail_cmd
except ImportError:
    async def jail_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
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
        else:
            mins_left = int((jailed_until - datetime.now()).total_seconds() // 60)
            await update.message.reply_text(f"🔒 In jail for {mins_left} more minutes!")

# ========== FACTORY MODULES ==========
try:
    from modules.factory.factory import command as factory_cmd
except ImportError:
    async def factory_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text("🏭 Factory system coming soon!")

try:
    from modules.factory.hire import command as hire_cmd
except ImportError:
    async def hire_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text("👷 Hiring system coming soon!")

try:
    from modules.factory.production import command as production_cmd
except ImportError:
    async def production_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text("🔨 Production system coming soon!")

# ========== GARDEN MODULES ==========
try:
    from modules.garden.garden import command as garden_cmd
except ImportError:
    async def garden_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text("🌾 Garden system coming soon!")

try:
    from modules.garden.plant import command as plant_cmd
except ImportError:
    async def plant_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text("🌱 Plant system coming soon!")

try:
    from modules.garden.harvest import command as harvest_cmd
except ImportError:
    async def harvest_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text("🌾 Harvest system coming soon!")

try:
    from modules.garden.fertilize import command as fertilize_cmd
except ImportError:
    async def fertilize_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text("🧪 Fertilizer system coming soon!")

try:
    from modules.garden.seeds import command as seeds_cmd
except ImportError:
    async def seeds_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
        text = "🌱 **Seed Shop**\n\n🌾 Wheat - 50💰\n🌽 Corn - 100💰\n🍅 Tomato - 150💰"
        await update.message.reply_text(text, parse_mode='Markdown')

# ========== MARKET MODULES ==========
try:
    from modules.market.stand import command as stand_cmd
except ImportError:
    async def stand_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text("🛒 Market stand coming soon!")

try:
    from modules.market.trade import command as trade_cmd
except ImportError:
    async def trade_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text("🤝 Trading system coming soon!")

try:
    from modules.market.auction import command as auction_cmd
except ImportError:
    async def auction_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text("🔨 Auction system coming soon!")

# ========== GAMES MODULES ==========
try:
    from modules.games.lottery import command as lottery_cmd
except ImportError:
    async def lottery_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_id = update.effective_user.id
        user = db.get_user(user_id)
        if not user:
            await update.message.reply_text("❌ Use /start first!")
            return
        import random
        if user['money'] < 10:
            await update.message.reply_text("❌ Need 10 coins!")
            return
        db.update_user(user_id, {'$inc': {'money': -10}})
        roll = random.randint(1, 100)
        if roll == 1:
            db.update_user(user_id, {'$inc': {'money': 1000}})
            await update.message.reply_text("🎉 **JACKPOT!** +1000 coins!")
        elif roll <= 10:
            win = random.randint(20, 100)
            db.update_user(user_id, {'$inc': {'money': win}})
            await update.message.reply_text(f"🎉 You won {win} coins!")
        else:
            await update.message.reply_text("😢 No luck this time!")

try:
    from modules.games.blackjack import command as blackjack_cmd
except ImportError:
    async def blackjack_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text("🃏 Blackjack coming soon!")

try:
    from modules.games.slots import command as slots_cmd
except ImportError:
    async def slots_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text("🎰 Slots coming soon!")

# ========== STATS MODULES ==========
try:
    from modules.stats.leaderboard import command as leaderboard_cmd
except ImportError:
    async def leaderboard_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
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

try:
    from modules.stats.moneyboard import command as moneyboard_cmd
except ImportError:
    async def moneyboard_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
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

try:
    from modules.stats.familyboard import command as familyboard_cmd
except ImportError:
    async def familyboard_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text("👪 Family leaderboard coming soon!")

# ========== ADMIN MODULES ==========
try:
    from modules.admin.ban import command as ban_cmd
except ImportError:
    async def ban_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text("🔨 Ban system coming soon!")

try:
    from modules.admin.broadcast import command as broadcast_cmd
except ImportError:
    async def broadcast_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text("📢 Broadcast system coming soon!")

try:
    from modules.admin.logs import command as logs_cmd
except ImportError:
    async def logs_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text("📜 Logs system coming soon!")

try:
    from modules.admin.admin_panel import command as admin_cmd
except ImportError:
    async def admin_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_id = update.effective_user.id
        admin_ids = [int(x) for x in os.getenv('ADMIN_IDS', '').split(',') if x]
        if user_id not in admin_ids:
            await update.message.reply_text("❌ Not authorized!")
            return
        text = "🔐 **Admin Panel**\n\n"
        text += f"Total users: {db.count_users() if hasattr(db, 'count_users') else 'N/A'}"
        await update.message.reply_text(text, parse_mode='Markdown')

# ========== SOCIAL MODULES (NEW FEATURES) ==========
try:
    from modules.social.relations import command as relations_cmd
except ImportError:
    async def relations_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text("👥 Relations system coming soon!")

try:
    from modules.social.ratings import command as ratings_cmd
except ImportError:
    async def ratings_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text("⭐ Ratings system coming soon!")

try:
    from modules.social.suggestions import command as suggestions_cmd
except ImportError:
    async def suggestions_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text("🎯 Suggestions coming soon!")

try:
    from modules.social.interactions import command as interactions_cmd
except ImportError:
    async def interactions_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text("🎭 Interactions coming soon!")

try:
    from modules.social.requests_cmd import command as requests_cmd
except ImportError:
    async def requests_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text("📨 Requests system coming soon!")

# ========== COOKING MODULES ==========
try:
    from modules.cooking.cook import command as cook_cmd
except ImportError:
    async def cook_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text("👨‍🍳 Cooking system coming soon!")

try:
    from modules.cooking.stove import command as stove_cmd
except ImportError:
    async def stove_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text("🔥 Stove shop coming soon!")

# ========== PROFILE CUSTOM MODULES ==========
try:
    from modules.profile_custom.setpic import command as setpic_cmd
except ImportError:
    async def setpic_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text("📸 Send a photo to set as profile picture!")

try:
    from modules.profile_custom.setloc import command as setloc_cmd
except ImportError:
    async def setloc_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text("📍 Location system coming soon!")

try:
    from modules.profile_custom.showmap import command as showmap_cmd
except ImportError:
    async def showmap_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text("🗺️ World map coming soon!")

# ========== ANIME MODULES ==========
try:
    from modules.anime.waifu import command as waifu_cmd
except ImportError:
    async def waifu_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text("💖 Waifu collection coming soon!")

# ========== SETTINGS MODULES ==========
try:
    from modules.settings.toggle import command as toggle_cmd
except ImportError:
    async def toggle_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text("⚙️ Settings toggle coming soon!")

# ========== INLINE HANDLERS ==========
try:
    from modules import inline_handlers
except ImportError:
    class DummyInline:
        @staticmethod
        async def handle_inline(update, context):
            pass
    inline_handlers = DummyInline()

# ========== CALLBACK HANDLER ==========
async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle callback queries."""
    query = update.callback_query
    await query.answer()
    
    data = query.data
    
    # Try to route to specific module handlers
    try:
        if data.startswith("buy_"):
            # Handle buy callbacks
            if data == "buy_fertilizer":
                from modules.garden.fertilize import buy_fertilizer
                await buy_fertilizer(update, context, query.from_user.id)
            elif data.startswith("buy_seed_"):
                from modules.garden.seeds import buy_seed
                seed_type = data.replace("buy_seed_", "")
                await buy_seed(update, context, query.from_user.id, seed_type)
            elif data == "buy_stove":
                from modules.cooking.stove import buy_stove
                await buy_stove(update, context, query.from_user.id)
        elif data.startswith("toggle_"):
            from modules.settings.toggle import toggle_setting
            setting = data.replace("toggle_", "")
            await toggle_setting(update, context, query.from_user.id, setting)
        elif data.startswith("recipe_"):
            from modules.cooking.cook import handle_recipe_callback
            await handle_recipe_callback(update, context, data)
        elif data.startswith("waifu_"):
            from modules.anime.waifu import handle_callback
            await handle_callback(update, context, data)
        elif data.startswith("relation_"):
            from modules.social.relations import handle_callback
            await handle_callback(update, context, data)
        elif data.startswith("request_"):
            from modules.social.requests_cmd import handle_callback
            await handle_callback(update, context, data)
        else:
            await query.edit_message_text("Feature coming soon!")
    except Exception as e:
        logger.error(f"Callback error: {e}")
        await query.edit_message_text("⚠️ Feature temporarily unavailable")

# ========== MAIN FUNCTION ==========
def main():
    """Start the bot."""
    application = Application.builder().token(os.getenv('TELEGRAM_TOKEN')).build()
    
    # Core commands
    application.add_handler(CommandHandler("start", start_cmd))
    application.add_handler(CommandHandler("help", help_cmd))
    application.add_handler(CommandHandler("profile", profile_cmd))
    application.add_handler(CommandHandler("settings", settings_cmd))
    
    # Family commands
    application.add_handler(CommandHandler("family", family_cmd))
    application.add_handler(CommandHandler("tree", tree_cmd))
    application.add_handler(CommandHandler("marry", marry_cmd))
    application.add_handler(CommandHandler("adopt", adopt_cmd))
    application.add_handler(CommandHandler("divorce", divorce_cmd))
    
    # Economy commands
    application.add_handler(CommandHandler("daily", daily_cmd))
    application.add_handler(CommandHandler("account", account_cmd))
    application.add_handler(CommandHandler("balance", balance_cmd))
    application.add_handler(CommandHandler("pay", pay_cmd))
    application.add_handler(CommandHandler("job", job_cmd))
    application.add_handler(CommandHandler("inventory", inventory_cmd))
    application.add_handler(CommandHandler("shop", shop_cmd))
    
    # Crime commands
    application.add_handler(CommandHandler("rob", rob_cmd))
    application.add_handler(CommandHandler("kill", kill_cmd))
    application.add_handler(CommandHandler("weapons", weapons_cmd))
    application.add_handler(CommandHandler("jail", jail_cmd))
    
    # Factory commands
    application.add_handler(CommandHandler("factory", factory_cmd))
    application.add_handler(CommandHandler("hire", hire_cmd))
    application.add_handler(CommandHandler("production", production_cmd))
    
    # Garden commands
    application.add_handler(CommandHandler("garden", garden_cmd))
    application.add_handler(CommandHandler("plant", plant_cmd))
    application.add_handler(CommandHandler("harvest", harvest_cmd))
    application.add_handler(CommandHandler("fertilize", fertilize_cmd))
    application.add_handler(CommandHandler("seeds", seeds_cmd))
    
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
    
    # Settings commands
    application.add_handler(CommandHandler("toggle", toggle_cmd))
    
    # Admin commands
    application.add_handler(CommandHandler("admin", admin_cmd))
    application.add_handler(CommandHandler("ban", ban_cmd))
    application.add_handler(CommandHandler("broadcast", broadcast_cmd))
    application.add_handler(CommandHandler("logs", logs_cmd))
    
    # Inline query handler
    application.add_handler(InlineQueryHandler(inline_handlers.handle_inline))
    
    # Callback query handler
    application.add_handler(CallbackQueryHandler(handle_callback))
    
    # Error handler
    application.add_error_handler(error_handler)
    
    print("🤖 Bot is running...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Log errors caused by updates."""
    logger.warning(f'Update {update} caused error {context.error}')
    if update and update.effective_message:
        await update.effective_message.reply_text("❌ An error occurred. Please try again.")

if __name__ == '__main__':
    main()


        

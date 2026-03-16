#!/usr/bin/env python3
"""
Telegram RPG Bot - Complete Implementation
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

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Import database first
from database import Database
db = Database()

# Import all modules with error handling
def safe_import(module_path, fallback_name):
    """Safely import a module with fallback."""
    try:
        module = __import__(module_path, fromlist=['command'])
        return module
    except ImportError as e:
        print(f"Warning: Could not import {module_path}: {e}")
        # Create dummy module
        class DummyModule:
            @staticmethod
            async def command(update, context):
                await update.message.reply_text(f"⚠️ {fallback_name} module temporarily unavailable")
        return DummyModule()

# Core modules
from modules.core import start, profile, settings as core_settings
from modules.core.help import help_command
from modules.family import family, tree, marry, adopt, divorce
from modules.economy import daily, account, pay, jobs, inventory, shop, balance
from modules.crime import rob, kill, weapons, jail
from modules.factory import factory, hire, production
from modules.garden import garden, plant, harvest, fertilize, seeds
from modules.market import stand, trade, auction
from modules.games import lottery, blackjack, slots

# Stats modules - with fallback
try:
    from modules.stats.leaderboard import command as leaderboard_cmd
    from modules.stats.moneyboard import command as moneyboard_cmd
    from modules.stats.familyboard import command as familyboard_cmd
except ImportError as e:
    print(f"Stats import error: {e}")
    async def dummy_stats(update, context):
        await update.message.reply_text("📊 Stats module loading...")
    leaderboard_cmd = dummy_stats
    moneyboard_cmd = dummy_stats
    familyboard_cmd = dummy_stats

from modules.admin import ban, broadcast, logs, admin_panel

# Optional modules with fallback
social_relations = safe_import('modules.social.relations', 'Relations')
social_ratings = safe_import('modules.social.ratings', 'Ratings')
social_suggestions = safe_import('modules.social.suggestions', 'Suggestions')
social_interactions = safe_import('modules.social.interactions', 'Interactions')
social_requests = safe_import('modules.social.requests_cmd', 'Requests')

cooking_cook = safe_import('modules.cooking.cook', 'Cooking')
cooking_stove = safe_import('modules.cooking.stove', 'Stove')

profile_setpic = safe_import('modules.profile_custom.setpic', 'SetPic')
profile_setloc = safe_import('modules.profile_custom.setloc', 'SetLoc')
profile_showmap = safe_import('modules.profile_custom.showmap', 'ShowMap')

anime_waifu = safe_import('modules.anime.waifu', 'Waifu')
settings_toggle = safe_import('modules.settings.toggle', 'Toggle')

# Inline handlers
try:
    from modules import inline_handlers
except ImportError:
    class DummyInline:
        @staticmethod
        async def handle_inline(update, context):
            pass
    inline_handlers = DummyInline()

# Conversation states
SET_PIC, SET_LOC = range(2)

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Log errors caused by updates."""
    logger.warning(f'Update {update} caused error {context.error}')
    if update and update.effective_message:
        await update.effective_message.reply_text("❌ An error occurred. Please try again.")

def main():
    """Start the bot."""
    # Create application
    application = Application.builder().token(os.getenv('TELEGRAM_TOKEN')).build()
    
    # Core commands
    application.add_handler(CommandHandler("start", start.command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("profile", profile.command))
    
    # Family commands
    application.add_handler(CommandHandler("family", family.command))
    application.add_handler(CommandHandler("tree", tree.command))
    application.add_handler(CommandHandler("marry", marry.command))
    application.add_handler(CommandHandler("adopt", adopt.command))
    application.add_handler(CommandHandler("divorce", divorce.command))
    
    # Economy commands
    application.add_handler(CommandHandler("daily", daily.command))
    application.add_handler(CommandHandler("account", account.command))
    application.add_handler(CommandHandler("balance", balance.command))
    application.add_handler(CommandHandler("pay", pay.command))
    application.add_handler(CommandHandler("job", jobs.command))
    application.add_handler(CommandHandler("inventory", inventory.command))
    application.add_handler(CommandHandler("shop", shop.command))
    
    # Crime commands
    application.add_handler(CommandHandler("rob", rob.command))
    application.add_handler(CommandHandler("kill", kill.command))
    application.add_handler(CommandHandler("weapons", weapons.command))
    application.add_handler(CommandHandler("jail", jail.command))
    
    # Factory commands
    application.add_handler(CommandHandler("factory", factory.command))
    application.add_handler(CommandHandler("hire", hire.command))
    application.add_handler(CommandHandler("production", production.command))
    
    # Garden commands
    application.add_handler(CommandHandler("garden", garden.command))
    application.add_handler(CommandHandler("plant", plant.command))
    application.add_handler(CommandHandler("harvest", harvest.command))
    application.add_handler(CommandHandler("fertilize", fertilize.command))
    application.add_handler(CommandHandler("seeds", seeds.command))
    
    # Market commands
    application.add_handler(CommandHandler("stand", stand.command))
    application.add_handler(CommandHandler("trade", trade.command))
    application.add_handler(CommandHandler("auction", auction.command))
    
    # Games commands
    application.add_handler(CommandHandler("lottery", lottery.command))
    application.add_handler(CommandHandler("blackjack", blackjack.command))
    application.add_handler(CommandHandler("slots", slots.command))
    
    # Stats commands
    application.add_handler(CommandHandler("leaderboard", leaderboard_cmd))
    application.add_handler(CommandHandler("moneyboard", moneyboard_cmd))
    application.add_handler(CommandHandler("familyboard", familyboard_cmd))
    
    # Social commands
    application.add_handler(CommandHandler("relations", social_relations.command))
    application.add_handler(CommandHandler("ratings", social_ratings.command))
    application.add_handler(CommandHandler("suggestions", social_suggestions.command))
    application.add_handler(CommandHandler("interactions", social_interactions.command))
    application.add_handler(CommandHandler("requests", social_requests.command))
    
    # Cooking commands
    application.add_handler(CommandHandler("cook", cooking_cook.command))
    application.add_handler(CommandHandler("stove", cooking_stove.command))
    
    # Profile commands
    application.add_handler(CommandHandler("setpic", profile_setpic.command))
    application.add_handler(CommandHandler("setloc", profile_setloc.command))
    application.add_handler(CommandHandler("showmap", profile_showmap.command))
    
    # Anime commands
    application.add_handler(CommandHandler("waifu", anime_waifu.command))
    
    # Settings commands
    application.add_handler(CommandHandler("toggle", settings_toggle.command))
    application.add_handler(CommandHandler("settings", core_settings.command))
    
    # Admin commands
    application.add_handler(CommandHandler("admin", admin_panel.command))
    application.add_handler(CommandHandler("ban", ban.command))
    application.add_handler(CommandHandler("broadcast", broadcast.command))
    application.add_handler(CommandHandler("logs", logs.command))
    
    # Conversation handlers (if modules support them)
    try:
        setpic_conv = ConversationHandler(
            entry_points=[CommandHandler("setpic", profile_setpic.start_conv)],
            states={SET_PIC: [MessageHandler(filters.PHOTO, profile_setpic.handle_photo)]},
            fallbacks=[CommandHandler("cancel", profile_setpic.cancel)]
        )
        application.add_handler(setpic_conv)
        
        setloc_conv = ConversationHandler(
            entry_points=[CommandHandler("setloc", profile_setloc.start_conv)],
            states={SET_LOC: [MessageHandler(filters.TEXT & ~filters.COMMAND, profile_setloc.handle_location)]},
            fallbacks=[CommandHandler("cancel", profile_setloc.cancel)]
        )
        application.add_handler(setloc_conv)
    except AttributeError:
        pass  # Modules don't have conversation handlers
    
    # Inline query handler
    application.add_handler(InlineQueryHandler(inline_handlers.handle_inline))
    
    # Callback query handler
    application.add_handler(CallbackQueryHandler(handle_callback))
    
    # Error handler
    application.add_error_handler(error_handler)
    
    # Start the Bot
    print("🤖 Bot is running...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle all callback queries."""
    query = update.callback_query
    await query.answer()
    
    data = query.data
    
    # Handle different callback types
    if data.startswith("buy_"):
        await handle_buy_callback(update, context, data)
    elif data.startswith("toggle_"):
        await handle_toggle_callback(update, context, data)
    elif data.startswith("recipe_"):
        try:
            await cooking_cook.handle_recipe_callback(update, context, data)
        except AttributeError:
            pass
    elif data.startswith("waifu_"):
        try:
            await anime_waifu.handle_callback(update, context, data)
        except AttributeError:
            pass
    elif data.startswith("relation_"):
        try:
            await social_relations.handle_callback(update, context, data)
        except AttributeError:
            pass
    elif data.startswith("request_"):
        try:
            await social_requests.handle_callback(update, context, data)
        except AttributeError:
            pass

async def handle_buy_callback(update: Update, context: ContextTypes.DEFAULT_TYPE, data: str):
    """Handle buy callbacks."""
    query = update.callback_query
    user_id = query.from_user.id
    
    try:
        if data == "buy_fertilizer":
            await fertilize.buy_fertilizer(update, context, user_id)
        elif data.startswith("buy_seed_"):
            seed_type = data.replace("buy_seed_", "")
            await seeds.buy_seed(update, context, user_id, seed_type)
        elif data == "buy_stove":
            await stove.buy_stove(update, context, user_id)
    except Exception as e:
        await query.edit_message_text(f"❌ Error: {str(e)}")

async def handle_toggle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE, data: str):
    """Handle toggle settings callbacks."""
    query = update.callback_query
    user_id = query.from_user.id
    
    try:
        setting = data.replace("toggle_", "")
        await settings_toggle.toggle_setting(update, context, user_id, setting)
    except Exception as e:
        await query.edit_message_text(f"❌ Error: {str(e)}")

if __name__ == '__main__':
    main()
        

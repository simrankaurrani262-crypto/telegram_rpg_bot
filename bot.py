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

# Import all modules
from modules.core import start, help_cmd, profile, settings as core_settings
from modules.family import family, tree, marry, adopt, divorce
from modules.economy import daily, account, pay, jobs, inventory, shop, balance
from modules.crime import rob, kill, weapons, jail
from modules.factory import factory, hire, production
from modules.garden import garden, plant, harvest, fertilize, seeds
from modules.market import stand, trade, auction
from modules.games import lottery, blackjack, slots
from modules.stats import leaderboard, moneyboard, familyboard
from modules.admin import ban, broadcast, logs, admin_panel
from modules.social import relations, ratings, suggestions, interactions, requests_cmd
from modules.cooking import cook, stove
from modules.profile_custom import setpic, setloc, showmap
from modules.anime import waifu
from modules.settings import toggle
from modules import inline_handlers

# Conversation states
SET_PIC, SET_LOC, COOK_RECIPE, TRADE_OFFER = range(4)

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
    application.add_handler(CommandHandler("help", help_cmd.command))
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
    application.add_handler(CommandHandler("leaderboard", leaderboard.command))
    application.add_handler(CommandHandler("moneyboard", moneyboard.command))
    application.add_handler(CommandHandler("familyboard", familyboard.command))
    
    # Social commands (NEW)
    application.add_handler(CommandHandler("relations", relations.command))
    application.add_handler(CommandHandler("ratings", ratings.command))
    application.add_handler(CommandHandler("suggestions", suggestions.command))
    application.add_handler(CommandHandler("interactions", interactions.command))
    application.add_handler(CommandHandler("requests", requests_cmd.command))
    
    # Cooking commands (NEW)
    application.add_handler(CommandHandler("cook", cook.command))
    application.add_handler(CommandHandler("stove", stove.command))
    
    # Profile commands (NEW)
    application.add_handler(CommandHandler("setpic", setpic.command))
    application.add_handler(CommandHandler("setloc", setloc.command))
    application.add_handler(CommandHandler("showmap", showmap.command))
    
    # Anime commands (NEW)
    application.add_handler(CommandHandler("waifu", waifu.command))
    
    # Settings commands (NEW)
    application.add_handler(CommandHandler("toggle", toggle.command))
    application.add_handler(CommandHandler("settings", core_settings.command))
    
    # Admin commands
    application.add_handler(CommandHandler("admin", admin_panel.command))
    application.add_handler(CommandHandler("ban", ban.command))
    application.add_handler(CommandHandler("broadcast", broadcast.command))
    application.add_handler(CommandHandler("logs", logs.command))
    
    # Conversation handlers
    setpic_conv = ConversationHandler(
        entry_points=[CommandHandler("setpic", setpic.start_conv)],
        states={
            SET_PIC: [MessageHandler(filters.PHOTO, setpic.handle_photo)]
        },
        fallbacks=[CommandHandler("cancel", setpic.cancel)]
    )
    application.add_handler(setpic_conv)
    
    setloc_conv = ConversationHandler(
        entry_points=[CommandHandler("setloc", setloc.start_conv)],
        states={
            SET_LOC: [MessageHandler(filters.TEXT & ~filters.COMMAND, setloc.handle_location)]
        },
        fallbacks=[CommandHandler("cancel", setloc.cancel)]
    )
    application.add_handler(setloc_conv)
    
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
    
    if data.startswith("buy_"):
        await handle_buy_callback(update, context, data)
    elif data.startswith("toggle_"):
        await handle_toggle_callback(update, context, data)
    elif data.startswith("recipe_"):
        await cook.handle_recipe_callback(update, context, data)
    elif data.startswith("waifu_"):
        await waifu.handle_callback(update, context, data)
    elif data.startswith("relation_"):
        await relations.handle_callback(update, context, data)
    elif data.startswith("request_"):
        await requests_cmd.handle_callback(update, context, data)

async def handle_buy_callback(update: Update, context: ContextTypes.DEFAULT_TYPE, data: str):
    """Handle buy callbacks."""
    query = update.callback_query
    user_id = query.from_user.id
    
    if data == "buy_fertilizer":
        from modules.garden.fertilize import buy_fertilizer
        await buy_fertilizer(update, context, user_id)
    elif data.startswith("buy_seed_"):
        seed_type = data.replace("buy_seed_", "")
        from modules.garden.seeds import buy_seed
        await buy_seed(update, context, user_id, seed_type)
    elif data == "buy_stove":
        from modules.cooking.stove import buy_stove
        await buy_stove(update, context, user_id)

async def handle_toggle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE, data: str):
    """Handle toggle settings callbacks."""
    query = update.callback_query
    user_id = query.from_user.id
    
    setting = data.replace("toggle_", "")
    from modules.settings.toggle import toggle_setting
    await toggle_setting(update, context, user_id, setting)

if __name__ == '__main__':
    main()
    

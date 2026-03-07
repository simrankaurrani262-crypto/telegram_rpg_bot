"""
Global Button Router
Handles all inline keyboard buttons
"""

from telegram import Update
from telegram.ext import ContextTypes, CallbackQueryHandler

async def button_router(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    data = query.data

    # PROFILE
    if data == "profile":
        await query.edit_message_text("👤 Opening your profile...")

    # GUIDE
    elif data == "guide":
        await query.edit_message_text(
            "📖 <b>Bot Guide</b>\n\n"
            "/daily - Claim daily reward\n"
            "/profile - View profile\n"
            "/family - View family tree\n"
            "/leaderboard - Top players\n"
            "/help - All commands",
            parse_mode="HTML"
        )

    # GAMES
    elif data == "games":
        await query.edit_message_text("🎮 Games menu coming soon!")

    # FAMILY
    elif data == "family":
        await query.edit_message_text("👨‍👩‍👧‍👦 Opening family tree...")

    # ECONOMY
    elif data == "economy":
        await query.edit_message_text("💰 Economy system")

    # STATS
    elif data == "stats":
        await query.edit_message_text("📊 Player stats")

    # SETTINGS
    elif data == "settings":
        await query.edit_message_text("⚙️ Settings menu")

    # LEADERBOARD buttons
    elif data.startswith("lb_"):
        if data == "lb_money":
            await query.edit_message_text("💰 Money Leaderboard")
        elif data == "lb_level":
            await query.edit_message_text("⭐ Level Leaderboard")
        elif data == "lb_family":
            await query.edit_message_text("👨‍👩‍👧‍👦 Family Leaderboard")
        elif data == "lb_factory":
            await query.edit_message_text("🏭 Factory Leaderboard")

button_handler = CallbackQueryHandler(button_router)

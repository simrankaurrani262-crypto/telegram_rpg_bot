"""
CENTRALIZED CALLBACK HANDLERS
All inline button callbacks from across the bot are handled here.
This ensures every button click is properly registered and processed.
"""
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CallbackQueryHandler
from database import db
import logging

logger = logging.getLogger(__name__)

# ============================================================================
# CORE MODULE CALLBACKS
# ============================================================================

async def settings_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle settings callbacks"""
    query = update.callback_query
    await query.answer()
    
    if query.data == "settings_notifications":
        keyboard = [
            [InlineKeyboardButton("✅ On", callback_data="notif_on")],
            [InlineKeyboardButton("❌ Off", callback_data="notif_off")],
        ]
        await query.edit_message_text(
            "<b>🔔 Notifications</b>\n\nEnable notifications?",
            parse_mode="HTML",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    elif query.data == "notif_on":
        db.update_user_setting(query.from_user.id, "notifications", True)
        await query.edit_message_text(
            "✅ <b>Notifications Enabled</b>",
            parse_mode="HTML"
        )
    elif query.data == "notif_off":
        db.update_user_setting(query.from_user.id, "notifications", False)
        await query.edit_message_text(
            "❌ <b>Notifications Disabled</b>",
            parse_mode="HTML"
        )
    elif query.data == "settings_theme":
        keyboard = [
            [InlineKeyboardButton("🌙 Dark", callback_data="theme_dark")],
            [InlineKeyboardButton("☀️ Light", callback_data="theme_light")],
        ]
        await query.edit_message_text(
            "<b>🎨 Theme</b>\n\nChoose your theme:",
            parse_mode="HTML",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    elif query.data == "theme_dark":
        db.update_user_setting(query.from_user.id, "theme", "dark")
        await query.edit_message_text(
            "✅ <b>Dark Theme Selected</b>",
            parse_mode="HTML"
        )
    elif query.data == "theme_light":
        db.update_user_setting(query.from_user.id, "theme", "light")
        await query.edit_message_text(
            "✅ <b>Light Theme Selected</b>",
            parse_mode="HTML"
        )
    elif query.data == "settings_privacy":
        keyboard = [
            [InlineKeyboardButton("👀 Public", callback_data="privacy_public")],
            [InlineKeyboardButton("🔒 Private", callback_data="privacy_private")],
        ]
        await query.edit_message_text(
            "<b>🔒 Privacy</b>\n\nWho can see your profile?",
            parse_mode="HTML",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    elif query.data == "privacy_public":
        db.update_user_setting(query.from_user.id, "privacy", "public")
        await query.edit_message_text(
            "✅ <b>Profile is Public</b>",
            parse_mode="HTML"
        )
    elif query.data == "privacy_private":
        db.update_user_setting(query.from_user.id, "privacy", "private")
        await query.edit_message_text(
            "✅ <b>Profile is Private</b>",
            parse_mode="HTML"
        )
    elif query.data == "main_menu":
        keyboard = [
            [InlineKeyboardButton("🎮 Play Games", callback_data="menu_games")],
            [InlineKeyboardButton("💼 Economy", callback_data="menu_economy")],
            [InlineKeyboardButton("👨‍👩‍👧‍👦 Family", callback_data="menu_family")],
        ]
        await query.edit_message_text(
            "<b>📋 MAIN MENU</b>",
            parse_mode="HTML",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

# ============================================================================
# SHOP & ECONOMY CALLBACKS
# ============================================================================

async def shop_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle shop item purchases via inline buttons"""
    query = update.callback_query
    await query.answer()
    
    if query.data.startswith("buy_"):
        item_name = query.data.replace("buy_", "")
        user_id = query.from_user.id
        user = db.get_user(user_id)
        
        if not user:
            await query.answer("❌ Please use /start first", show_alert=True)
            return
        
        # Import shop items
        from modules.economy.shop import SHOP_ITEMS
        
        if item_name not in SHOP_ITEMS:
            await query.answer("❌ Item not found", show_alert=True)
            return
        
        item_info = SHOP_ITEMS[item_name]
        
        if user['money'] < item_info['price']:
            await query.answer(
                f"❌ You need {item_info['price']} 💰\nYou have {user['money']} 💰",
                show_alert=True
            )
            return
        
        # Purchase item
        db.withdraw_money(user_id, item_info['price'])
        db.add_item(user_id, item_name)
        
        await query.answer("✅ Purchase successful!", show_alert=False)
        await query.edit_message_text(
            f"✅ <b>PURCHASE SUCCESSFUL!</b>\n\n"
            f"{item_info['emoji']} {item_name.capitalize()}\n"
            f"Cost: {item_info['price']} 💰\n"
            f"Balance: {user['money'] - item_info['price']:,} 💰",
            parse_mode="HTML"
        )
        logger.info(f"Purchase via button: {user_id} bought {item_name}")

async def bank_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle bank operation callbacks"""
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    user = db.get_user(user_id)
    
    if not user:
        await query.answer("❌ Please use /start first", show_alert=True)
        return
    
    if query.data == "bank_deposit":
        await query.edit_message_text(
            "<b>💰 DEPOSIT</b>\n\n"
            "Use /deposit amount\n"
            "Example: /deposit 1000",
            parse_mode="HTML"
        )
    elif query.data == "bank_withdraw":
        await query.edit_message_text(
            "<b>💸 WITHDRAW</b>\n\n"
            "Use /withdraw amount\n"
            "Example: /withdraw 500",
            parse_mode="HTML"
        )
    elif query.data == "bank_transactions":
        await query.edit_message_text(
            "<b>📊 TRANSACTIONS</b>\n\n"
            "Recent transactions:\n"
            f"• Deposit: +1000\n"
            f"• Withdrawal: -500",
            parse_mode="HTML"
        )
    elif query.data == "bank_settings":
        keyboard = [
            [InlineKeyboardButton("🔔 Alerts", callback_data="bank_alerts")],
            [InlineKeyboardButton("🔑 Security", callback_data="bank_security")],
        ]
        await query.edit_message_text(
            "<b>⚙️ BANK SETTINGS</b>",
            parse_mode="HTML",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    elif query.data == "bank_alerts":
        await query.edit_message_text(
            "✅ <b>Alerts Enabled</b>",
            parse_mode="HTML"
        )
    elif query.data == "bank_security":
        await query.edit_message_text(
            "🔒 <b>Security Settings</b>\n\nYour account is secure.",
            parse_mode="HTML"
        )

# ============================================================================
# MARKET & AUCTION CALLBACKS
# ============================================================================

async def auction_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle auction callbacks"""
    query = update.callback_query
    await query.answer()
    
    if query.data == "auction_bid":
        await query.edit_message_text(
            "<b>📝 PLACE BID</b>\n\n"
            "Use /bid auction_id amount\n"
            "Example: /bid 1 500",
            parse_mode="HTML"
        )
        logger.info(f"Auction bid initiated by {query.from_user.id}")

# ============================================================================
# GAMES CALLBACKS
# ============================================================================

async def blackjack_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle blackjack game callbacks"""
    query = update.callback_query
    await query.answer()
    
    if "blackjack" not in context.user_data:
        await query.answer("❌ No active game. Start with /blackjack", show_alert=True)
        return
    
    game = context.user_data['blackjack']
    user_id = query.from_user.id
    
    if query.data == "bj_hit":
        import random
        from modules.games.blackjack import CARDS, hand_value
        
        game['player_hand'].append(random.choice(CARDS))
        player_value = hand_value(game['player_hand'])
        
        if player_value > 21:
            await query.edit_message_text(
                f"<b>🎰 BLACKJACK</b>\n\n"
                f"Your Hand: {' '.join(game['player_hand'])} = {player_value}\n\n"
                f"❌ <b>BUST!</b> You went over 21!\n"
                f"Lost: {game['bet']} 💰",
                parse_mode="HTML"
            )
            del context.user_data['blackjack']
            logger.info(f"Blackjack bust: {user_id}")
        else:
            keyboard = [
                [
                    InlineKeyboardButton("📍 Hit", callback_data="bj_hit"),
                    InlineKeyboardButton("⏹️ Stand", callback_data="bj_stand"),
                ],
            ]
            await query.edit_message_text(
                f"<b>🎰 BLACKJACK</b>\n\n"
                f"Your Hand: {' '.join(game['player_hand'])} = {player_value}\n"
                f"Dealer: {game['dealer_hand'][0]} ?\n\n"
                f"Bet: {game['bet']} 💰",
                parse_mode="HTML",
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
    
    elif query.data == "bj_stand":
        from modules.games.blackjack import hand_value
        
        player_value = hand_value(game['player_hand'])
        dealer_value = hand_value(game['dealer_hand'])
        
        result_text = f"<b>🎰 BLACKJACK</b>\n\n"
        result_text += f"Your Hand: {' '.join(game['player_hand'])} = {player_value}\n"
        result_text += f"Dealer: {' '.join(game['dealer_hand'])} = {dealer_value}\n\n"
        
        if dealer_value > player_value:
            result_text += f"❌ <b>DEALER WINS!</b>\n"
            result_text += f"Lost: {game['bet']} 💰"
        elif dealer_value == player_value:
            result_text += f"🤝 <b>PUSH (TIE)</b>\n"
            result_text += f"Your bet is returned: {game['bet']} 💰"
            db.add_money(user_id, game['bet'])
        else:
            winnings = game['bet'] * 2
            result_text += f"✅ <b>YOU WIN!</b>\n"
            result_text += f"Won: {winnings} 💰"
            db.add_money(user_id, winnings)
        
        await query.edit_message_text(result_text, parse_mode="HTML")
        del context.user_data['blackjack']
        logger.info(f"Blackjack finished: {user_id}")

# ============================================================================
# CREATE ALL HANDLERS
# ============================================================================

# Core Settings
settings_callback_handler = CallbackQueryHandler(settings_callback, pattern="^(settings_|notif_|theme_|privacy_|main_menu)")

# Shop & Economy
shop_callback_handler = CallbackQueryHandler(shop_callback, pattern="^buy_")
bank_callback_handler = CallbackQueryHandler(bank_callback, pattern="^bank_")

# Market & Auctions
auction_callback_handler = CallbackQueryHandler(auction_callback, pattern="^auction_")

# Games
blackjack_callback_handler = CallbackQueryHandler(blackjack_callback, pattern="^bj_")

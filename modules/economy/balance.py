"""
Detailed balance and transaction history
"""
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from database import Database

db = Database()

async def command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show detailed balance and transaction history."""
    user_id = update.effective_user.id
    
    user = db.get_user(user_id)
    if not user:
        await update.message.reply_text("❌ Register first with /start")
        return
    
    wallet = user.get('money', 0)
    bank = user.get('bank', 0)
    total = wallet + bank
    
    # Get transaction history
    transactions = db.get_transactions(user_id, limit=10)
    
    text = f"💰 **Financial Overview**\n\n"
    text += f"👛 **Wallet**: {wallet:,}💰\n"
    text += f"🏦 **Bank**: {bank:,}💰\n"
    text += f"💵 **Total Assets**: {total:,}💰\n\n"
    
    # Calculate net worth (items + properties)
    inventory_value = calculate_inventory_value(user_id)
    properties_value = calculate_properties_value(user_id)
    net_worth = total + inventory_value + properties_value
    
    text += f"📊 **Net Worth**: {net_worth:,}💰\n"
    text += f"   • Inventory: {inventory_value:,}💰\n"
    text += f"   • Properties: {properties_value:,}💰\n\n"
    
    if transactions:
        text += "📈 **Recent Transactions**:\n"
        for t in transactions:
            emoji = "🟢" if t['type'] == 'income' else "🔴"
            text += f"{emoji} {t['description']}: {t['amount']:+,.0f}💰\n"
    else:
        text += "📭 No recent transactions"
    
    # Financial stats
    daily_income = db.calculate_daily_income(user_id)
    text += f"\n📅 **Est. Daily Income**: {daily_income:,}💰\n"
    
    keyboard = [
        [InlineKeyboardButton("🏦 Deposit", callback_data="bank_deposit"),
         InlineKeyboardButton("💸 Withdraw", callback_data="bank_withdraw")],
        [InlineKeyboardButton("📜 Full History", callback_data="balance_history"),
         InlineKeyboardButton("📊 Stats", callback_data="balance_stats")]
    ]
    
    await update.message.reply_text(
        text,
        parse_mode='Markdown',
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

def calculate_inventory_value(user_id):
    """Calculate total value of inventory items."""
    inventory = db.get_inventory(user_id)
    total = 0
    for item in inventory:
        item_data = db.get_item(item['item_id'])
        if item_data:
            total += item_data.get('sell_price', 0) * item.get('quantity', 1)
    return total

def calculate_properties_value(user_id):
    """Calculate value of owned properties."""
    properties = db.get_user_properties(user_id)
    total = 0
    for prop in properties:
        total += prop.get('value', 0)
    return to
tal

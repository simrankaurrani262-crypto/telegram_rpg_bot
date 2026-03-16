"""
Player market stand for selling items
"""
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler
from database import Database
from datetime import datetime

db = Database()

SETTING_PRICE, CONFIRMING = range(2)

async def command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show market stand."""
    user_id = update.effective_user.id
    
    user = db.get_user(user_id)
    if not user:
        await update.message.reply_text("❌ Register first!")
        return
    
    # Get or create stand
    stand = db.get_market_stand(user_id)
    if not stand:
        stand = db.create_market_stand(user_id)
    
    text = f"🛒 **{user.get('username', 'Your')} Market Stand**\n\n"
    
    # Show listed items
    items = stand.get('items', [])
    if items:
        text += "**Items for Sale**:\n"
        for item in items:
            text += f"• {item['name']} - {item['price']:,}💰 (Stock: {item['quantity']})\n"
        text += f"\n💰 Total Value: {sum(i['price'] * i['quantity'] for i in items):,} coins\n\n"
    else:
        text += "📭 **No items listed**\n\n"
    
    # Show stats
    sales = stand.get('total_sales', 0)
    revenue = stand.get('total_revenue', 0)
    text += f"📊 **Stats**: {sales} sales | {revenue:,}💰 earned\n\n"
    
    keyboard = [
        [InlineKeyboardButton("➕ List Item", callback_data="stand_list")],
        [InlineKeyboardButton("📦 Inventory", callback_data="stand_inventory")],
        [InlineKeyboardButton("💰 Collect Earnings", callback_data="stand_collect")],
        [InlineKeyboardButton("🔍 Browse Stands", callback_data="stand_browse")]
    ]
    
    await update.message.reply_text(
        text,
        parse_mode='Markdown',
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def list_item_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start listing an item."""
    query = update.callback_query
    user_id = query.from_user.id
    
    inventory = db.get_inventory(user_id)
    if not inventory:
        await query.answer("No items to sell!")
        return
    
    text = "📦 **Select Item to Sell**:\n\n"
    keyboard = []
    
    for item_id, quantity in inventory.items():
        if quantity <= 0:
            continue
        item_data = db.get_item(item_id) or {'name': item_id}
        keyboard.append([InlineKeyboardButton(
            f"{item_data['name']} (x{quantity})",
            callback_data=f"stand_sell_{item_id}"
        )])
    
    await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard))
    return SETTING_PRICE

async def set_price(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Set price for item."""
    query = update.callback_query
    user_id = query.from_user.id
    
    data = query.data
    item_id = data.replace("stand_sell_", "")
    
    context.user_data['selling_item'] = item_id
    
    item_data = db.get_item(item_id) or {'name': item_id}
    await query.edit_message_text(
        f"💰 **Setting Price for {item_data['name']}**\n\n"
        f"Send the price in coins (e.g., 1000):"
    )
    return SETTING_PRICE

async def confirm_listing(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Confirm and create listing."""
    user_id = update.effective_user.id
    
    try:
        price = int(update.message.text)
        if price <= 0:
            raise ValueError
    except ValueError:
        await update.message.reply_text("❌ Invalid price! Send a number:")
        return SETTING_PRICE
    
    item_id = context.user_data.get('selling_item')
    if not item_id:
        await update.message.reply_text("❌ Error! Start again with /stand")
        return ConversationHandler.END
    
    # Check inventory
    inventory = db.get_inventory(user_id)
    if inventory.get(item_id, 0) <= 0:
        await update.message.reply_text("❌ You don't have this item!")
        return ConversationHandler.END
    
    # List item
    item_data = db.get_item(item_id) or {'name': item_id}
    db.list_item_on_stand(user_id, {
        'item_id': item_id,
        'name': item_data['name'],
        'price': price,
        'quantity': 1,
        'listed_at': datetime.now()
    })
    
    # Remove from inventory
    db.remove_from_inventory(user_id, item_id, 1)
    
    await update.message.reply_text(
        f"✅ **Item Listed!**\n\n"
        f"{item_data['name']} - {price:,}💰\n"
        f"Players can now buy from your stand!"
    )
    return ConversationHandler.END

async def buy_from_stand(update: Update, context: ContextTypes.DEFAULT_TYPE, seller_id: int, item_id: str):
    """Buy item from another player's stand."""
    buyer_id = update.effective_user.id
    
    stand = db.get_market_stand(seller_id)
    if not stand:
        await update.message.reply_text("❌ Stand not found!")
        return
    
    # Find item
    item = None
    for i in stand.get('items', []):
        if i['item_id'] == item_id:
            item = i
            break
    
    if not item:
        await update.message.reply_text("❌ Item not found!")
        return
    
    buyer = db.get_user(buyer_id)
    if buyer['money'] < item['price']:
        await update.message.reply_text("❌ Not enough money!")
        return
    
    # Transfer money
    db.update_user(buyer_id, {'$inc': {'money': -item['price']}})
    db.update_user(seller_id, {'$inc': {'money': item['price']}})
    
    # Transfer item
    db.add_to_inventory(buyer_id, item_id, 1)
    db.remove_from_stand(seller_id, item_id)
    
    # Update stats
    db.update_stand_stats(seller_id, item['price'])
    
    await update.message.reply_text(
        f"✅ **Purchase Successful!**\n\n"
        f"You bought {item['name']} for {item['price']:,}💰"
    
)

"""
Weapons shop and management
"""
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from database import Database

db = Database()

WEAPONS = {
    'knife': {
        'name': '🔪 Knife',
        'price': 500,
        'damage': 10,
        'accuracy': 70,
        'durability': 10
    },
    'pistol': {
        'name': '🔫 Pistol',
        'price': 2500,
        'damage': 25,
        'accuracy': 80,
        'durability': 20
    },
    'shotgun': {
        'name': '🔫 Shotgun',
        'price': 6000,
        'damage': 40,
        'accuracy': 65,
        'durability': 15
    },
    'rifle': {
        'name': '🔫 Rifle',
        'price': 12000,
        'damage': 60,
        'accuracy': 85,
        'durability': 25
    },
    'sniper': {
        'name': '🎯 Sniper',
        'price': 25000,
        'damage': 90,
        'accuracy': 95,
        'durability': 20
    },
    'katana': {
        'name': '⚔️ Katana',
        'price': 15000,
        'damage': 50,
        'accuracy': 90,
        'durability': 50
    }
}

async def command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show weapons shop."""
    user_id = update.effective_user.id
    
    user = db.get_user(user_id)
    if not user:
        await update.message.reply_text("❌ Register first!")
        return
    
    # Get user's weapons
    inventory = db.get_inventory(user_id)
    user_weapons = inventory.get('weapons', [])
    
    text = f"🔫 **Weapons Shop**\n\n"
    text += f"💰 Your Money: {user.get('money', 0):,} coins\n\n"
    
    if user_weapons:
        text += "**Your Weapons**:\n"
        for w in user_weapons:
            weapon_data = WEAPONS.get(w['type'], {})
            durability = w.get('durability', weapon_data.get('durability', 0))
            max_dur = weapon_data.get('durability', 0)
            text += f"• {weapon_data.get('name', w['type'])} (DMG: {weapon_data.get('damage', 0)}, Dur: {durability}/{max_dur})\n"
        text += "\n"
    
    text += "**Available Weapons**:\n\n"
    
    keyboard = []
    for weapon_id, weapon in WEAPONS.items():
        text += f"{weapon['name']}\n"
        text += f"  💰 Price: {weapon['price']:,}\n"
        text += f"  ⚔️ Damage: {weapon['damage']} | 🎯 Accuracy: {weapon['accuracy']}%\n"
        text += f"  🔧 Durability: {weapon['durability']} uses\n\n"
        
        # Check if already owned
        owned = any(w['type'] == weapon_id for w in user_weapons)
        if owned:
            btn_text = f"🔧 Repair {weapon['name']}"
        else:
            btn_text = f"Buy {weapon['name']} - {weapon['price']}💰"
        
        keyboard.append([InlineKeyboardButton(btn_text, callback_data=f"weapon_buy_{weapon_id}")])
    
    keyboard.append([InlineKeyboardButton("🔫 Equip Weapon", callback_data="weapon_equip")])
    
    await update.message.reply_text(
        text,
        parse_mode='Markdown',
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def buy_weapon(update: Update, context: ContextTypes.DEFAULT_TYPE, weapon_id: str):
    """Buy or repair a weapon."""
    query = update.callback_query
    user_id = query.from_user.id
    
    if weapon_id not in WEAPONS:
        await query.answer("Invalid weapon!")
        return
    
    weapon = WEAPONS[weapon_id]
    user = db.get_user(user_id)
    
    # Check if already owned
    inventory = db.get_inventory(user_id)
    user_weapons = inventory.get('weapons', [])
    existing = next((w for w in user_weapons if w['type'] == weapon_id), None)
    
    if existing:
        # Repair
        repair_cost = weapon['price'] // 4
        if user['money'] < repair_cost:
            await query.answer(f"Need {repair_cost} coins for repair!")
            return
        
        db.update_user(user_id, {'$inc': {'money': -repair_cost}})
        db.repair_weapon(user_id, weapon_id)
        await query.answer(f"🔧 Repaired {weapon['name']}!")
    else:
        # Buy new
        if user['money'] < weapon['price']:
            await query.answer("Not enough money!")
            return
        
        db.update_user(user_id, {'$inc': {'money': -weapon['price']}})
        db.add_weapon(user_id, {
            'type': weapon_id,
            'durability': weapon['durability'],
            'purchased_at': datetime.now()
        })
        await query.answer(f"✅ Bought {weapon['name']}!")

async def get_equipped_weapon(user_id: int):
    """Get currently equipped weapon."""
    user = db.get_user(user_id)
    return user.get('equipped_weapon')

async def calculate_damage(user_id: int, base_damage: int = 5):
    """Calculate total damage with weapon."""
    weapon_type = await get_equipped_weapon(user_id)
    if not weapon_type:
        return base_damage
    
    weapon_data = WEAPONS.get(weapon_type, {})
    return base_damage + weapon_data.get('damage', 0)

from datetime import datetime

from telegram.ext import CommandHandler

weapon_handler = CommandHandler('weapons', command)
buyweapon_handler = CommandHandler('buyweapon', command)

"""
Help command
"""
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show help menu."""
    text = """
🎮 **RPG Bot Commands**

**Core:**
/start - Register/start bot
/help - Show this help
/profile - View your profile
/settings - Bot settings

**Family:**
/family - Family info
/tree - Family tree image
/marry - Marry someone
/adopt - Adopt someone
/divorce - Divorce partner

**Economy:**
/daily - Daily reward (100💰)
/balance - Detailed balance
/account - Bank account
/pay - Pay someone
/job - Work and earn
/shop - Buy items
/inventory - Your items

**Crime:**
/rob - Rob someone
/kill - Attack player
/weapons - Buy weapons
/jail - Check jail status

**Factory:**
/factory - Your factory
/hire - Hire workers
/production - Manage production

**Garden:**
/garden - Your farm
/plant - Plant crops
/harvest - Harvest crops
/fertilize - Use fertilizer
/seeds - Buy seeds

**Market:**
/stand - Your market stall
/trade - Trade with players
/auction - Auction house

**Social:**
/relations - Family relations
/ratings - User ratings
/suggestions - Friend suggestions
/interactions - Social actions
/requests - Pending requests

**Cooking:**
/cook - Cook food
/stove - Buy/upgrade stove

**Profile:**
/setpic - Set profile photo
/setloc - Set location
/showmap - World map

**Anime:**
/waifu - Collect waifus

**Games:**
/lottery - Try your luck
/blackjack - Play blackjack
/slots - Slot machine

**Stats:**
/leaderboard - Top players
/moneyboard - Richest players
/familyboard - Largest families

**Admin:**
/admin - Admin panel
/ban - Ban user
/broadcast - Send message to all
/logs - View logs

Use /toggle to change settings!
"""
    
    keyboard = [
        [InlineKeyboardButton("💰 Economy", callback_data="help_economy"),
         InlineKeyboardButton("👪 Family", callback_data="help_family")],
        [InlineKeyboardButton("🎮 Games", callback_data="help_games"),
         InlineKeyboardButton("🏭 Factory", callback_data="help_factory")]
    ]
    
    await update.message.reply_text(
        text,
        parse_mode='Markdown',
        reply_markup=InlineKeyboardMarkup(
    keyboard)
    )

from telegram.ext import CommandHandler

help_handler = CommandHandler('help', help_command)

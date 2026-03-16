"""
Family size leaderboard
"""
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from database import Database

db = Database()

async def command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show largest families leaderboard."""
    # Get all families and calculate sizes
    families = db.get_all_families()
    
    # Calculate family sizes
    family_stats = []
    for family in families:
        user_id = family.get('user_id')
        user = db.get_user(user_id)
        if not user:
            continue
        
        # Count total members
        size = 1  # Self
        size += len(family.get('partner', []))
        size += len(family.get('children', []))
        size += len(family.get('parents', []))
        size += len(family.get('siblings', []))
        
        family_stats.append({
            'user_id': user_id,
            'username': user.get('username', f'User{user_id}'),
            'size': size,
            'generations': calculate_generations(family)
        })
    
    # Sort by size
    family_stats.sort(key=lambda x: x['size'], reverse=True)
    
    text = "👪 **Largest Families**\n\n"
    
    medals = ['🥇', '🥈', '🥉', '4️⃣', '5️⃣', '6️⃣', '7️⃣', '8️⃣', '9️⃣', '🔟']
    
    for i, fam in enumerate(family_stats[:10]):
        medal = medals[i] if i < 10 else f"{i+1}."
        text += f"{medal} **{fam['username']} Family**\n"
        text += f"   👥 {fam['size']} members | 🌳 {fam['generations']} generations\n\n"
    
    # Get user's family rank
    user_id = update.effective_user.id
    user_fam = db.get_family(user_id)
    
    if user_fam:
        user_rank = next((i+1 for i, f in enumerate(family_stats) 
                         if f['user_id'] == user_id), None)
        if user_rank:
            user_size = next(f['size'] for f in family_stats 
                           if f['user_id'] == user_id)
            text += f"\n📍 Your Family Rank: #{user_rank} ({user_size} members)"
    
    keyboard = [
        [InlineKeyboardButton("🏆 Overall", callback_data="lb_overall"),
         InlineKeyboardButton("💰 Money", callback_data="lb_money")],
        [InlineKeyboardButton("🌳 View Tree", callback_data="family_tree")]
    ]
    
    await update.message.reply_text(
        text,
        parse_mode='Markdown',
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

def calculate_generations(family):
    """Calculate number of generations in family."""
    generations = 1  # Self
    
    if family.get('parents') or family.get('children'):
        generations += 1
    
    if family.get('grandparents') or family.get('grandchildren'):
        generations += 1
    
    return min(generations, 
    3)

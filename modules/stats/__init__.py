"""
Stats modules
"""
from .leaderboard import command as leaderboard_cmd
from .moneyboard import command as moneyboard_cmd  
from .familyboard import command as familyboard_cmd

# Export commands directly
leaderboard = type('obj', (object,), {'command': leaderboard_cmd})
moneyboard = type('obj', (object,), {'command': moneyboard_cmd})
familyboard = type('obj', (object,), {'command': familyboard_cmd})

__all__ = ['leaderboard', 'moneyboard', 'familyboard']

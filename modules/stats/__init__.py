"""
Stats modules - Simple import
"""
from .leaderboard import command as leaderboard_cmd
from .moneyboard import command as moneyboard_cmd
from .familyboard import command as familyboard_cmd

# Create simple objects with command method
class LeaderboardModule:
    command = staticmethod(leaderboard_cmd)

class MoneyboardModule:
    command = staticmethod(moneyboard_cmd)

class FamilyboardModule:
    command = staticmethod(familyboard_cmd)

leaderboard = LeaderboardModule()
moneyboard = MoneyboardModule()
familyboard = FamilyboardModule()

__all__ = ['leaderboard', 'moneyboard', 'familyboard']

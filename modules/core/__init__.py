"""
Core modules
"""
from .start import command as start_command, start_handler
from .profile import command as profile_command
from .settings import command as settings_command
from .help import help_command

# Create module objects
class StartModule:
    command = staticmethod(start_command)

class ProfileModule:
    command = staticmethod(profile_command)

class SettingsModule:
    command = staticmethod(settings_command)

start = StartModule()
profile = ProfileModule()
settings = SettingsModule()

__all__ = ['start', 'profile', 'settings', 'help_command']

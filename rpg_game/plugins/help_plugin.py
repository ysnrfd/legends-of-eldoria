"""
Help Plugin - Lists all available plugin commands
"""

from __future__ import annotations
from systems.plugins import Plugin, PluginInfo, PluginPriority
from typing import Dict, Any


class HelpPlugin(Plugin):
    """
    Simple help plugin that lists all available plugin commands.
    """
    
    def __init__(self):
        info = PluginInfo(
            id="help_plugin",
            name="Help Plugin",
            version="1.0.0",
            author="YSNRFD",
            description="Provides help information for all plugin commands.",
            dependencies=[],
            conflicts=[],
            priority=PluginPriority.HIGH,
            tags=["help", "utility", "commands"]
        )
        super().__init__(info)
    
    def on_load(self, game) -> bool:
        return True
    
    def on_unload(self, game) -> bool:
        return True
    
    def on_enable(self, game) -> bool:
        return True
    
    def on_disable(self, game) -> bool:
        return True
    
    def register_commands(self, command_system) -> Dict[str, Any]:
        """Register the help command"""
        return {
            "help": {
                "handler": self._cmd_help,
                "help": "Show all available plugin commands",
                "usage": "/help [command]",
                "category": "system"
            },
            "commands": {
                "handler": self._cmd_help,
                "help": "List all available commands (alias for help)",
                "usage": "/commands",
                "category": "system"
            }
        }
    
    def register_hooks(self, event_system) -> Dict:
        """Register event hooks"""
        return {}
    
    def _cmd_help(self, game, args):
        """Display help for all commands or a specific command"""

        # Get all registered commands from the plugin manager
        commands = {}
        if hasattr(game, 'plugin_manager') and game.plugin_manager:
            commands = game.plugin_manager._commands
        
        if not commands:
            return "No plugin commands available."
        
        # If user asked for specific command help
        if args:
            cmd_name = args[0].lower()
            if cmd_name in commands:
                # Try to get command info from all plugins
                help_text = f"Command: /{cmd_name}\n"
                
                # Check each plugin for command metadata
                for plugin in game.plugin_manager.plugins.values():
                    if hasattr(plugin, '_commands') and cmd_name in plugin._commands:
                        callback = plugin._commands[cmd_name]
                        # Try to get docstring or help info
                        if hasattr(callback, '__doc__') and callback.__doc__:
                            help_text += f"\nDescription: {callback.__doc__.strip()}"
                        break
                
                return help_text
            else:
                return f"Unknown command: {cmd_name}\nUse /help to see all commands."
        
        # Build categorized help
        system_cmds = []
        stats_cmds = []
        config_cmds = []
        debug_cmds = []
        other_cmds = []
        
        # Categorize commands based on naming patterns
        for cmd_name in sorted(commands.keys()):
            if cmd_name in ['help', 'commands']:
                system_cmds.append(cmd_name)
            elif 'config' in cmd_name:
                config_cmds.append(cmd_name)
            elif 'stat' in cmd_name:
                stats_cmds.append(cmd_name)
            elif any(x in cmd_name for x in ['debug', 'test', 'bonus', 'reset']):
                debug_cmds.append(cmd_name)
            else:
                other_cmds.append(cmd_name)
        
        help_text = "╔══════════════════════════════════════════════════════════════╗\n"
        help_text += "║                    PLUGIN COMMANDS HELP                      ║\n"
        help_text += "╠══════════════════════════════════════════════════════════════╣\n"
        help_text += "║  Use / before any command. Example: /help                    ║\n"
        help_text += "║  Use /help <command> for details on a specific command.      ║\n"
        help_text += "╚══════════════════════════════════════════════════════════════╝\n\n"
        
        if system_cmds:
            help_text += "📋 SYSTEM COMMANDS:\n"
            for cmd in system_cmds:
                help_text += f"  /{cmd}\n"
            help_text += "\n"
        
        if stats_cmds:
            help_text += "📊 STATISTICS COMMANDS:\n"
            for cmd in stats_cmds:
                help_text += f"  /{cmd}\n"
            help_text += "\n"
        
        if config_cmds:
            help_text += "⚙️  CONFIGURATION COMMANDS:\n"
            for cmd in config_cmds:
                help_text += f"  /{cmd}\n"
            help_text += "\n"
        
        if debug_cmds:
            help_text += "🔧 DEBUG COMMANDS:\n"
            for cmd in debug_cmds:
                help_text += f"  /{cmd}\n"
            help_text += "\n"
        
        if other_cmds:
            help_text += "🎮 OTHER COMMANDS:\n"
            for cmd in other_cmds:
                help_text += f"  /{cmd}\n"
        
        help_text += "\n" + "─" * 60 + "\n"
        help_text += f"Total commands available: {len(commands)}\n"
        help_text += "─" * 60
        
        return help_text


# Plugin instance
plugin = HelpPlugin()

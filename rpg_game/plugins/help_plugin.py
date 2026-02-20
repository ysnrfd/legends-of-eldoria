"""
Help Plugin - Enhanced Command and Plugin Information System
Provides comprehensive help for all plugin commands and system information.
"""

from __future__ import annotations
from systems.plugins import Plugin, PluginInfo, PluginPriority, EventType
from typing import Dict, Any


class HelpPlugin(Plugin):
    """
    Enhanced help plugin with comprehensive command and plugin information.
    
    Features:
    - List all available commands with categories
    - Show detailed help for specific commands
    - List all loaded plugins
    - Show plugin information
    - Event notifications for plugin changes
    """
    
    def __init__(self):
        info = PluginInfo(
            id="help_plugin",
            name="Help Plugin",
            version="2.0.0",
            author="YSNRFD",
            description="Provides comprehensive help information for all plugin commands "
                       "and system features. Includes plugin management and command reference.",
            dependencies=[],
            conflicts=[],
            priority=PluginPriority.HIGH,  # Load early so other plugins can register
            tags=["help", "utility", "commands", "system"]
        )
        super().__init__(info)
        self._command_cache: Dict[str, Dict] = {}
        self._plugin_notifications = True
    
    def on_load(self, game) -> bool:
        """Called when plugin is loaded"""
        print("[Help Plugin] Loaded successfully")
        return True
    
    def on_unload(self, game) -> bool:
        """Called when plugin is unloaded"""
        print("[Help Plugin] Unloaded")
        return True
    
    def on_enable(self, game) -> bool:
        """Called when plugin is enabled"""
        print("[Help Plugin] Enabled - use /help to see available commands")
        return True
    
    def on_disable(self, game) -> bool:
        """Called when plugin is disabled"""
        return True
    
    def register_hooks(self, event_system) -> Dict[EventType, Any]:
        """
        Register event hooks for plugin notifications.
        
        Args:
            event_system: The event system instance
            
        Returns:
            Dict mapping EventType to handler functions
        """
        if self._plugin_notifications:
            return {
                EventType.PLUGIN_LOAD: self._on_plugin_load,
                EventType.PLUGIN_UNLOAD: self._on_plugin_unload,
            }
        return {}
    
    def _on_plugin_load(self, game, data):
        """Handle plugin load event"""
        plugin_id = data.get("plugin_id", "unknown")
        print(f"[Help Plugin] New plugin loaded: {plugin_id}")
    
    def _on_plugin_unload(self, game, data):
        """Handle plugin unload event"""
        plugin_id = data.get("plugin_id", "unknown")
        print(f"[Help Plugin] Plugin unloaded: {plugin_id}")
    
    def register_commands(self, command_system) -> Dict[str, Any]:
        """
        Register all help-related commands.
        
        Args:
            command_system: The command system instance
            
        Returns:
            Dict mapping command names to handler info
        """
        return {
            "help": {
                "handler": self._cmd_help,
                "help": "Show all available plugin commands or detailed help for a specific command",
                "usage": "/help [command]",
                "category": "system",
                "aliases": ["commands", "?"]
            },
            "plugins": {
                "handler": self._cmd_plugins,
                "help": "List all loaded plugins with their status",
                "usage": "/plugins",
                "category": "system"
            },
            "plugin_info": {
                "handler": self._cmd_plugin_info,
                "help": "Show detailed information about a specific plugin",
                "usage": "/plugin_info <plugin_id>",
                "category": "system"
            },
            "plugin_stats": {
                "handler": self._cmd_plugin_stats,
                "help": "Show plugin system statistics",
                "usage": "/plugin_stats",
                "category": "stats"
            }
        }
    
    def _cmd_help(self, game, args, context=None) -> str:
        """
        Display help for all commands or a specific command.
        
        Args:
            game: The main game instance
            args: List of command arguments
            context: Additional context
            
        Returns:
            Formatted help string
        """

        # Get all registered commands from the plugin manager
        commands = {}
        command_info = {}
        if hasattr(game, 'plugin_manager') and game.plugin_manager:
            commands = game.plugin_manager._commands
            command_info = game.plugin_manager._command_info
        
        if not commands:
            return "No plugin commands available."
        
        # If user asked for specific command help
        if args:
            cmd_name = args[0].lower()
            
            # Check aliases in command_info
            for name, info in command_info.items():
                aliases = info.get("aliases", []) if isinstance(info, dict) else []
                if cmd_name in aliases:
                    cmd_name = name
                    break
            
            # Get command info from _command_info (metadata), fallback to _commands (handler)
            cmd_data = command_info.get(cmd_name)
            if cmd_data is None and cmd_name in commands:
                # Fallback for commands without metadata
                cmd_data = {"help": "No detailed information available"}
            
            if cmd_data:
                return self._format_command_help(cmd_name, cmd_data)
            else:
                return f"Unknown command: {cmd_name}\nUse /help to see all commands."
        
        # Build categorized help using command_info for categories
        return self._format_all_commands(commands, command_info)
    
    def _format_command_help(self, cmd_name: str, cmd_info: Any) -> str:
        """Format detailed help for a single command"""
        lines = [
            f"╔══════════════════════════════════════════════════════════════╗",
            f"║  Command: /{cmd_name:<52}║",
            f"╚══════════════════════════════════════════════════════════════╝",
            ""
        ]
        
        if isinstance(cmd_info, dict):
            if "help" in cmd_info:
                lines.append(f"Description: {cmd_info['help']}")
            if "usage" in cmd_info:
                lines.append(f"Usage: {cmd_info['usage']}")
            if "category" in cmd_info:
                lines.append(f"Category: {cmd_info['category']}")
            if "aliases" in cmd_info and cmd_info["aliases"]:
                lines.append(f"Aliases: {', '.join(cmd_info['aliases'])}")
        else:
            lines.append("Description: No detailed information available")
        
        lines.append("")
        lines.append("─" * 62)
        
        return "\n".join(lines)
    
    def _format_all_commands(self, commands: Dict[str, Any], command_info: Dict[str, Dict] = None) -> str:
        """Format help for all commands organized by category"""
        if command_info is None:
            command_info = {}
        
        # Categorize commands
        categories = {
            "system": [],
            "stats": [],
            "config": [],
            "debug": [],
            "info": [],
            "other": []
        }
        
        for cmd_name in sorted(commands.keys()):
            category = "other"
            
            # Get command info from command_info dict (metadata)
            cmd_info = command_info.get(cmd_name, {})
            
            if isinstance(cmd_info, dict):
                category = cmd_info.get("category", "other")
                # Handle aliases mapping
                if cmd_name in ["help", "commands", "?"]:
                    category = "system"
            
            if category in categories:
                categories[category].append(cmd_name)
            else:
                categories["other"].append(cmd_name)
        
        # Build output
        lines = [
            "╔══════════════════════════════════════════════════════════════╗",
            "║                    PLUGIN COMMANDS HELP                      ║",
            "╠══════════════════════════════════════════════════════════════╣",
            "║  Use / before any command. Example: /help                    ║",
            "║  Use /help <command> for details on a specific command.      ║",
            "╚══════════════════════════════════════════════════════════════╝",
            ""
        ]
        
        category_icons = {
            "system": "📋",
            "stats": "📊",
            "config": "⚙️",
            "debug": "🔧",
            "info": "ℹ️",
            "other": "🎮"
        }
        
        category_names = {
            "system": "SYSTEM COMMANDS",
            "stats": "STATISTICS COMMANDS",
            "config": "CONFIGURATION COMMANDS",
            "debug": "DEBUG COMMANDS",
            "info": "INFORMATION COMMANDS",
            "other": "OTHER COMMANDS"
        }
        
        for category in ["system", "stats", "config", "debug", "info", "other"]:
            cmds = categories[category]
            if cmds:
                icon = category_icons.get(category, "•")
                name = category_names.get(category, category.upper())
                lines.append(f"{icon} {name}:")
                for cmd in cmds:
                    lines.append(f"  /{cmd}")
                lines.append("")
        
        lines.append("─" * 62)
        lines.append(f"Total commands available: {len(commands)}")
        lines.append("─" * 62)
        
        return "\n".join(lines)
    
    def _cmd_plugins(self, game, args, context=None) -> str:
        """
        List all loaded plugins.
        
        Args:
            game: The main game instance
            args: List of command arguments
            context: Additional context
            
        Returns:
            Formatted plugin list string
        """

        if not hasattr(game, 'plugin_manager') or not game.plugin_manager:
            return "Plugin manager not available."
        
        plugins = game.plugin_manager.plugins
        
        if not plugins:
            return "No plugins currently loaded."
        
        lines = [
            "╔══════════════════════════════════════════════════════════════╗",
            "║                     LOADED PLUGINS                           ║",
            "╚══════════════════════════════════════════════════════════════╝",
            ""
        ]
        
        for plugin_id, plugin in sorted(plugins.items()):
            info = plugin.info
            status = "✓ Enabled" if plugin.enabled else "✗ Disabled"
            
            lines.append(f"{info.name} (v{info.version})")
            lines.append(f"  ID: {plugin_id}")
            lines.append(f"  Author: {info.author}")
            lines.append(f"  Status: {status}")
            lines.append(f"  Tags: {', '.join(info.tags) if info.tags else 'None'}")
            lines.append("")
        
        lines.append("─" * 62)
        lines.append(f"Total plugins: {len(plugins)}")
        lines.append("─" * 62)
        
        return "\n".join(lines)
    
    def _cmd_plugin_info(self, game, args, context=None) -> str:
        """
        Show detailed information about a specific plugin.
        
        Args:
            game: The main game instance
            args: List of command arguments (plugin_id)
            context: Additional context
            
        Returns:
            Formatted plugin information string
        """

        if not args:
            return "Usage: /plugin_info <plugin_id>\nUse /plugins to see available plugins."
        
        if not hasattr(game, 'plugin_manager') or not game.plugin_manager:
            return "Plugin manager not available."
        
        plugin_id = args[0].lower()
        plugin = game.plugin_manager.get_plugin(plugin_id)
        
        if not plugin:
            return f"Plugin '{plugin_id}' not found.\nUse /plugins to see available plugins."
        
        info = plugin.info
        
        lines = [
            "╔══════════════════════════════════════════════════════════════╗",
            f"║  {info.name[:56]:^56}  ║",
            "╚══════════════════════════════════════════════════════════════╝",
            "",
            f"ID: {info.id}",
            f"Version: {info.version}",
            f"Author: {info.author}",
            f"Status: {'Enabled' if plugin.enabled else 'Disabled'}",
            f"Priority: {info.priority.name}",
            "",
            "Description:",
            f"  {info.description}",
            ""
        ]
        
        if info.dependencies:
            lines.append(f"Dependencies: {', '.join(info.dependencies)}")
        if info.conflicts:
            lines.append(f"Conflicts: {', '.join(info.conflicts)}")
        if info.tags:
            lines.append(f"Tags: {', '.join(info.tags)}")
        
        # Show registered content
        lines.append("")
        lines.append("Registered Content:")
        
        # Check for various content types
        content_types = []
        if hasattr(plugin, 'register_items'):
            content_types.append("Items")
        if hasattr(plugin, 'register_enemies'):
            content_types.append("Enemies")
        if hasattr(plugin, 'get_new_locations'):
            content_types.append("Locations")
        if hasattr(plugin, 'get_new_npcs'):
            content_types.append("NPCs")
        if hasattr(plugin, 'get_new_quests'):
            content_types.append("Quests")
        if hasattr(plugin, 'register_recipes'):
            content_types.append("Recipes")
        
        if content_types:
            lines.append(f"  {', '.join(content_types)}")
        else:
            lines.append("  None")
        
        # Show registered commands
        if hasattr(plugin, '_commands') and plugin._commands:
            lines.append("")
            lines.append(f"Commands: {', '.join(f'/{cmd}' for cmd in plugin._commands.keys())}")
        
        lines.append("")
        lines.append("─" * 62)
        
        return "\n".join(lines)
    
    def _cmd_plugin_stats(self, game, args, context=None) -> str:
        """
        Show plugin system statistics.
        
        Args:
            game: The main game instance
            args: List of command arguments
            context: Additional context
            
        Returns:
            Formatted statistics string
        """

        if not hasattr(game, 'plugin_manager') or not game.plugin_manager:
            return "Plugin manager not available."
        
        pm = game.plugin_manager
        
        # Count content types
        content_stats = {}
        if hasattr(pm, '_content_registries'):
            for content_type, registry in pm._content_registries.items():
                content_stats[content_type] = len(registry)
        
        lines = [
            "╔══════════════════════════════════════════════════════════════╗",
            "║                  PLUGIN SYSTEM STATISTICS                    ║",
            "╚══════════════════════════════════════════════════════════════╝",
            "",
            "Plugin Counts:",
            f"  Total Plugins: {len(pm.plugins)}",
            f"  Enabled: {sum(1 for p in pm.plugins.values() if p.enabled)}",
            f"  Disabled: {sum(1 for p in pm.plugins.values() if not p.enabled)}",
            "",
            "Command Counts:",
            f"  Total Commands: {len(pm._commands)}",
            ""
        ]
        
        if content_stats:
            lines.append("Content Registry:")
            for content_type, count in sorted(content_stats.items()):
                lines.append(f"  {content_type.capitalize()}: {count}")
            lines.append("")
        
        lines.append("─" * 62)
        
        return "\n".join(lines)


# Plugin instance - REQUIRED
plugin = HelpPlugin()

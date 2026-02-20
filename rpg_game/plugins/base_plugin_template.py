"""
================================================================================
Base Plugin Template - Complete Working Reference for Plugin Development
================================================================================

This file serves as a comprehensive template demonstrating the ACTUAL plugin 
architecture used in Legends of Eldoria. Copy this file and modify it to 
create your own plugins.

SUPPORTED PLUGIN STYLES:
1. Class-based (inherit from Plugin) - RECOMMENDED for complex plugins
2. Functional (using PluginBuilder) - Good for simple plugins
3. Decorator-based (using @plugin decorator) - For quick handlers

================================================================================
"""

from __future__ import annotations
from systems.plugins import (
    Plugin, PluginInfo, PluginPriority, PluginBuilder
)
from core.engine import EventType
from typing import Dict, Any


# =============================================================================
# STYLE 1: CLASS-BASED PLUGIN (Traditional Inheritance) - RECOMMENDED
# =============================================================================

class BasePluginTemplate(Plugin):
    """
    Complete plugin template using class-based approach.
    
    This style is recommended for complex plugins with lots of functionality.
    Demonstrates all available features of the plugin system.
    """
    
    def __init__(self):
        # Initialize plugin info
        info = PluginInfo(
            # Required fields
            id="base_plugin_template",
            name="Base Plugin Template",
            version="2.0.0",
            author="YSNRFD",
            description="Comprehensive template demonstrating all plugin features.",
            
            # Dependencies and conflicts
            dependencies=[],           # Plugins that must load before this one
            conflicts=[],            # Plugins that cannot run with this one
            
            # Loading configuration
            priority=PluginPriority.NORMAL,  # Load order (lower = earlier)
            
            # Metadata
            tags=["template", "example", "reference"]
        )
        super().__init__(info)
        
        # Initialize plugin state
        self._state: Dict[str, Any] = {}
        self._config: Dict[str, Any] = {}
    
    # =========================================================================
    # LIFECYCLE METHODS (Required)
    # =========================================================================
    
    def on_load(self, game) -> bool:
        """
        Called when plugin is loaded into memory.
        
        Args:
            game: The main game instance
            
        Returns:
            bool: True if load successful, False otherwise
        """
        print(f"[{self.info.name}] v{self.info.version} loading...")
        
        # Initialize state
        self._state = {
            "loads": 0,
            "events_processed": 0,
            "commands_executed": 0
        }
        
        # Set default configuration
        self._config = {
            "bonus_gold": 100,
            "debug_mode": False,
            "welcome_message": "Template Plugin Loaded!"
        }
        
        return True
    
    def on_unload(self, game) -> bool:
        """
        Called when plugin is being unloaded.
        
        Args:
            game: The main game instance
            
        Returns:
            bool: True if unload successful, False otherwise
        """
        print(f"[{self.info.name}] unloading...")
        print(f"  Stats: {self._state.get('events_processed', 0)} events, "
              f"{self._state.get('commands_executed', 0)} commands")
        return True
    
    def on_enable(self, game) -> bool:
        """
        Called when plugin is enabled.
        
        Args:
            game: The main game instance
            
        Returns:
            bool: True if enable successful, False otherwise
        """
        print(f"[{self.info.name}] enabled!")
        return True
    
    def on_disable(self, game) -> bool:
        """
        Called when plugin is disabled.
        
        Args:
            game: The main game instance
            
        Returns:
            bool: True if disable successful, False otherwise
        """
        print(f"[{self.info.name}] disabled")
        return True
    
    # =========================================================================
    # EVENT HOOKS
    # =========================================================================
    
    def register_hooks(self, event_system) -> Dict[EventType, Any]:
        """
        Register event hooks.
        
        Args:
            event_system: The event system instance
            
        Returns:
            Dict mapping EventType to handler functions
        """
        return {
            EventType.COMBAT_START: self._on_combat_start,
            EventType.COMBAT_END: self._on_combat_end,
            EventType.COMBAT_TURN: self._on_combat_turn,
            EventType.PLAYER_LEVEL_UP: self._on_level_up,
            EventType.PLAYER_DEATH: self._on_player_death,
            EventType.ITEM_PICKUP: self._on_item_pickup,
            EventType.ITEM_EQUIP: self._on_item_equip,
            EventType.ITEM_USE: self._on_item_use,
            EventType.NPC_INTERACT: self._on_npc_interact,
            EventType.QUEST_START: self._on_quest_start,
            EventType.QUEST_COMPLETE: self._on_quest_complete,
            EventType.LOCATION_ENTER: self._on_location_enter,
            EventType.LOCATION_EXIT: self._on_location_exit,
            EventType.TIME_CHANGE: self._on_time_change,
            EventType.WEATHER_CHANGE: self._on_weather_change,
            EventType.GAME_START: self._on_game_start,
            EventType.GAME_SAVE: self._on_game_save,
            EventType.GAME_LOAD: self._on_game_load,
        }
    
    def _track_event(self):
        """Helper to track event processing"""
        self._state["events_processed"] = self._state.get("events_processed", 0) + 1
    
    def _on_combat_start(self, game, data):
        """Handle combat start event"""
        self._track_event()
        player = data.get("player")
        enemies = data.get("enemies", [])
        
        if self._config.get("debug_mode"):
            print(f"[DEBUG] Combat starting against {len(enemies)} enemies")
        
        # Variety bonus for fighting diverse enemies
        if len(enemies) >= 3:
            print(f"[{self.info.name}] ⚔️ Variety bonus activated!")
    
    def _on_combat_end(self, game, data):
        """Handle combat end event"""
        self._track_event()
        player = data.get("player")
        result = data.get("result")
        
        if result == "victory" and player:
            # Apply configured bonus
            bonus = self._config.get("bonus_gold", 100)
            if bonus > 0:
                player.inventory.gold += bonus
                print(f"[{self.info.name}] Victory bonus: +{bonus} gold!")
    
    def _on_combat_turn(self, game, data):
        """Handle combat turn event"""
        self._track_event()
    
    def _on_level_up(self, game, data):
        """Handle player level up event"""
        self._track_event()
        player = data.get("player")
        level = data.get("level", 1)
        
        # Milestone rewards every 5 levels
        if level % 5 == 0:
            print(f"[{self.info.name}] 🎯 Milestone level {level} reached!")
    
    def _on_player_death(self, game, data):
        """Handle player death event"""
        self._track_event()
    
    def _on_item_pickup(self, game, data):
        """Handle item pickup event"""
        self._track_event()
        item = data.get("item")
        
        if item and hasattr(item, 'rarity'):
            rarity = item.rarity
            if rarity.value >= 4:  # Epic or higher
                print(f"[{self.info.name}] ✨ Rare item discovered: {item.name}!")
    
    def _on_item_equip(self, game, data):
        """Handle item equip event"""
        self._track_event()
    
    def _on_item_use(self, game, data):
        """Handle item use event"""
        self._track_event()
    
    def _on_npc_interact(self, game, data):
        """Handle NPC interaction event"""
        self._track_event()
    
    def _on_quest_start(self, game, data):
        """Handle quest start event"""
        self._track_event()
    
    def _on_quest_complete(self, game, data):
        """Handle quest complete event"""
        self._track_event()
    
    def _on_location_enter(self, game, data):
        """Handle location enter event"""
        self._track_event()
        location_id = data.get("location_id")
        
        # Check if this is a template location
        if location_id and location_id.startswith("template_"):
            print(f"[{self.info.name}] Entered template area: {location_id}")
    
    def _on_location_exit(self, game, data):
        """Handle location exit event"""
        self._track_event()
    
    def _on_time_change(self, game, data):
        """Handle time change event"""
        self._track_event()
        new_time = data.get("new_time")
        
        if new_time and new_time.name == "MIDNIGHT":
            print(f"[{self.info.name}] 🌙 The witching hour...")
    
    def _on_weather_change(self, game, data):
        """Handle weather change event"""
        self._track_event()
        new_weather = data.get("new_weather")
        
        if new_weather and new_weather.name == "BLOOD_MOON":
            print(f"[{self.info.name}] 🩸 The blood moon rises!")
    
    def _on_game_start(self, game, data):
        """Handle game start event"""
        self._track_event()
        print(f"[{self.info.name}] {self._config.get('welcome_message', 'Welcome!')}")
    
    def _on_game_save(self, game, data):
        """Handle game save event"""
        self._track_event()
    
    def _on_game_load(self, game, data):
        """Handle game load event"""
        self._track_event()
    
    # =========================================================================
    # COMMANDS
    # =========================================================================
    
    def register_commands(self, command_system) -> Dict[str, Any]:
        """
        Register slash commands.
        
        Args:
            command_system: The command system instance
            
        Returns:
            Dict mapping command names to handler info
        """
        return {
            "template_info": {
                "handler": self._cmd_info,
                "help": "Show template plugin info",
                "category": "system"
            },
            "template_config": {
                "handler": self._cmd_config,
                "help": "Manage plugin configuration",
                "usage": "/template_config [key] [value]",
                "category": "system"
            },
            "template_stats": {
                "handler": self._cmd_stats,
                "help": "Show plugin statistics",
                "category": "stats"
            },
            "template_bonus": {
                "handler": self._cmd_bonus,
                "help": "Give template bonus",
                "category": "debug"
            }
        }
    
    def _track_command(self):
        """Helper to track command execution"""
        self._state["commands_executed"] = self._state.get("commands_executed", 0) + 1
    
    def _cmd_info(self, game, args, context):
        """Display plugin information"""
        self._track_command()
        return (
            f"Plugin: {self.info.name} v{self.info.version}\n"
            f"Author: {self.info.author}\n"
            f"Priority: {self.info.priority.name}\n"
            f"Tags: {', '.join(self.info.tags)}\n"
            f"\n{self.info.description}"
        )
    
    def _cmd_config(self, game, args, context):
        """View or set configuration"""
        self._track_command()
        
        if not args:
            return f"Config: {self._config}"
        
        if len(args) == 1:
            key = args[0]
            return f"{key} = {self._config.get(key, 'Not found')}"
        
        key, value = args[0], args[1]
        old_value = self._config.get(key)
        
        # Parse value
        if value.lower() in ("true", "yes", "1", "on"):
            value = True
        elif value.lower() in ("false", "no", "0", "off"):
            value = False
        else:
            try:
                value = int(value)
            except ValueError:
                try:
                    value = float(value)
                except ValueError:
                    pass  # Keep as string
        
        self._config[key] = value
        
        return f"Set {key}: {old_value} -> {value}"
    
    def _cmd_stats(self, game, args, context):
        """Show plugin statistics"""
        self._track_command()
        return (
            f"Plugin Statistics:\n"
            f"  Events Processed: {self._state.get('events_processed', 0)}\n"
            f"  Commands Executed: {self._state.get('commands_executed', 0)}"
        )
    
    def _cmd_bonus(self, game, args, context):
        """Give template bonus to player"""
        self._track_command()
        if game and hasattr(game, 'player') and game.player:
            bonus = self._config.get("bonus_gold", 100)
            game.player.inventory.gold += bonus
            return f"Template bonus applied: +{bonus} gold!"
        return "No player available"
    
    # =========================================================================
    # CONTENT REGISTRATION
    # =========================================================================
    
    def register_items(self, item_registry) -> Dict[str, Dict]:
        """
        Register items provided by this plugin.
        
        Returns:
            Dict mapping item IDs to item data
        """
        return {
            "template_blade": {
                "name": "Template Blade",
                "item_type": "weapon",
                "rarity": "Rare",
                "value": 500,
                "weight": 3.0,
                "description": "A weapon forged from the essence of templates.",
                "damage_min": 12,
                "damage_max": 24,
                "damage_type": "physical",
                "attack_speed": 1.0,
                "critical_chance": 0.10,
                "level_required": 5
            },
            "template_armor": {
                "name": "Template Plate",
                "item_type": "armor",
                "rarity": "Epic",
                "value": 2000,
                "weight": 15.0,
                "description": "Armor infused with template magic.",
                "slot": "chest",
                "defense": 30,
                "magic_defense": 15,
                "level_required": 15
            },
            "template_potion": {
                "name": "Template Elixir",
                "item_type": "consumable",
                "rarity": "Rare",
                "value": 200,
                "weight": 0.2,
                "description": "A potion crafted from template essence.",
                "hp_restore": 75,
                "mp_restore": 50,
                "use_message": "Template energy flows through you!"
            },
            "template_ring": {
                "name": "Ring of Templates",
                "item_type": "accessory",
                "rarity": "Epic",
                "value": 1500,
                "weight": 0.1,
                "description": "A ring blessed by the template creators.",
                "level_required": 10
            }
        }
    
    def register_enemies(self, enemy_registry) -> Dict[str, Dict]:
        """
        Register enemies provided by this plugin.
        
        Returns:
            Dict mapping enemy IDs to enemy data
        """
        return {
            "template_guardian": {
                "name": "Template Guardian",
                "description": "A construct protecting template secrets.",
                "base_hp": 150,
                "base_mp": 50,
                "base_damage": 25,
                "rarity": "Rare",
                "faction": "construct",
                "resistances": {"physical": 0.3},
                "weaknesses": {"lightning": 1.5}
            },
            "template_wraith": {
                "name": "Template Wraith",
                "description": "A ghostly manifestation of broken templates.",
                "base_hp": 100,
                "base_mp": 150,
                "base_damage": 30,
                "rarity": "Epic",
                "faction": "undead",
                "resistances": {"physical": 0.5, "dark": 0.8},
                "weaknesses": {"holy": 2.0}
            }
        }
    
    def get_new_locations(self) -> Dict[str, Dict]:
        """
        Return new locations added by this plugin.
        
        Returns:
            Dict mapping location IDs to location data
        """
        return {
            "template_sanctum": {
                "name": "Template Sanctum",
                "description": "A peaceful sanctuary where templates are created.",
                "location_type": "special",
                "level_range": [1, 30],
                "connections": ["capital_city"],
                "danger_level": 0,
                "discovery_exp": 200
            },
            "template_dungeon": {
                "name": "Template Vault",
                "description": "A mysterious dungeon with shifting architecture.",
                "location_type": "dungeon",
                "level_range": [10, 20],
                "connections": ["capital_city"],
                "enemies": ["template_guardian", "template_wraith"],
                "danger_level": 4,
                "special_features": {
                    "boss": "template_overlord",
                    "floor_count": 5
                },
                "discovery_exp": 400
            }
        }
    
    def get_new_npcs(self) -> Dict[str, Dict]:
        """
        Return new NPCs added by this plugin.
        
        Returns:
            Dict mapping NPC IDs to NPC data
        """
        return {
            "template_sage": {
                "name": "The Template Sage",
                "description": "An ancient being who has mastered templates.",
                "npc_type": "trainer",
                "location": "template_sanctum",
                "services": ["train", "identify", "enchant"],
                "can_train": ["All"],
                "training_cost": 200,
                "friendship_max": 200,
                "dialogue": {
                    "greeting": {
                        "low_friendship": "\"Welcome to the sanctum.\"",
                        "medium_friendship": "\"Good to see you again.\"",
                        "high_friendship": "\"My faithful student!\""
                    }
                }
            }
        }
    
    def get_new_quests(self) -> Dict[str, Dict]:
        """
        Return new quests added by this plugin.
        
        Returns:
            Dict mapping quest IDs to quest data
        """
        return {
            "template_discovery": {
                "name": "The Template Vault",
                "description": "Explore the mysterious Template Vault.",
                "quest_type": "side",
                "location": "capital_city",
                "level_required": 10,
                "objectives": [
                    {"type": "reach", "target": "template_dungeon", "required": 1,
                     "description": "Find the Template Vault"},
                    {"type": "defeat_boss", "target": "template_overlord", "required": 1,
                     "description": "Defeat the Template Overlord"}
                ],
                "rewards": {
                    "experience": 1500,
                    "gold": 1000,
                    "items": ["template_ring"]
                }
            }
        }
    
    def register_recipes(self, crafting_manager) -> Dict[str, Dict]:
        """
        Register crafting recipes provided by this plugin.
        
        Returns:
            Dict mapping recipe IDs to recipe data
        """
        return {
            "template_blade_recipe": {
                "name": "Template Blade Recipe",
                "category": "weapons",
                "result": "template_blade",
                "result_quantity": 1,
                "ingredients": {"iron_ingot": 3, "magic_crystal": 2},
                "skill_required": "Crafting",
                "skill_level": 10,
                "time": 2,
                "gold_cost": 200,
                "experience": 50
            }
        }


# =============================================================================
# STYLE 2: FUNCTIONAL PLUGIN (Using PluginBuilder)
# =============================================================================

def create_functional_plugin():
    """
    Create a plugin using the fluent builder API.
    Good for simple plugins that don't need complex state.
    """
    def on_load(game):
        print("Functional Plugin loaded!")
        return True
    
    def on_unload(game):
        print("Functional Plugin unloaded!")
        return True
    
    def on_enable(game):
        print("Functional Plugin enabled!")
        return True
    
    def on_disable(game):
        print("Functional Plugin disabled!")
        return True
    
    def on_combat_end(game, data):
        if data.get("result") == "victory":
            print("Victory in functional plugin!")
    
    def cmd_hello(game, args, context):
        return "Hello from functional plugin!"
    
    return (PluginBuilder("functional_template")
        .name("Functional Template Plugin")
        .version("1.0.0")
        .author("Plugin Developer")
        .description("A plugin built with the fluent API")
        .priority(PluginPriority.LOW)
        .tags("functional", "example")
        .on_load(on_load)
        .on_unload(on_unload)
        .on_enable(on_enable)
        .on_disable(on_disable)
        .hook(EventType.COMBAT_END, on_combat_end)
        .command("hello", cmd_hello, "Say hello")
        .content("items", {"func_item": {"name": "Functional Item"}})
        .build())


# =============================================================================
# STYLE 3: MINIMAL PLUGIN (Simplest Possible)
# =============================================================================

class MinimalPlugin(Plugin):
    """The simplest possible plugin."""
    
    def __init__(self):
        super().__init__(PluginInfo(
            id="minimal",
            name="Minimal Plugin",
            version="1.0.0",
            author="Developer",
            description="Minimal example"
        ))
    
    def on_load(self, game) -> bool:
        print("Minimal plugin loaded!")
        return True
    
    def on_unload(self, game) -> bool:
        print("Minimal plugin unloaded!")
        return True
    
    def on_enable(self, game) -> bool:
        return True
    
    def on_disable(self, game) -> bool:
        return True


# =============================================================================
# PLUGIN INSTANCE - REQUIRED
# =============================================================================

# Create the plugin instance for discovery
# Uncomment the style you want to use:

# Style 1: Class-based (RECOMMENDED)
plugin = BasePluginTemplate()

# Style 2: Functional
# plugin = create_functional_plugin()

# Style 3: Minimal
# plugin = MinimalPlugin()


# =============================================================================
# DOCUMENTATION
# =============================================================================

"""
QUICK START GUIDE:
------------------

1. Copy this file to plugins folder
2. Rename the class and plugin_id
3. Customize the content methods
4. The plugin auto-loads on game start

AVAILABLE EVENT TYPES:
---------------------

Combat Events:
- COMBAT_START: Combat begins
- COMBAT_END: Combat ends  
- COMBAT_TURN: Each combat turn

Player Events:
- PLAYER_LEVEL_UP: Player levels up
- PLAYER_DEATH: Player dies

Item Events:
- ITEM_PICKUP: Item picked up
- ITEM_EQUIP: Item equipped
- ITEM_USE: Item used

World Events:
- LOCATION_ENTER: Enter location
- LOCATION_EXIT: Exit location
- TIME_CHANGE: Time changes
- WEATHER_CHANGE: Weather changes

NPC/Quest Events:
- NPC_INTERACT: NPC interaction
- QUEST_START: Quest started
- QUEST_COMPLETE: Quest completed

System Events:
- GAME_START: Game starts
- GAME_SAVE: Game saved
- GAME_LOAD: Game loaded

CONTENT REGISTRATION METHODS:
------------------------------

- register_items(): Return dict of items
- register_enemies(): Return dict of enemies
- get_new_locations(): Return dict of locations
- get_new_npcs(): Return dict of NPCs
- get_new_quests(): Return dict of quests
- register_recipes(): Return dict of recipes

COMMAND HANDLER SIGNATURE:
---------------------------

def cmd_handler(game, args, context):
    game: The main game instance
    args: List of command arguments
    context: Additional context dict
    
    Returns: String response message

EVENT HANDLER SIGNATURE:
------------------------

def event_handler(game, data):
    game: The main game instance
    data: Event data dict (varies by event)
    
    Returns: None (or modified data for some events)
"""

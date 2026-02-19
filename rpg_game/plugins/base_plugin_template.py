"""
================================================================================
Base Plugin Template - Complete Dynamic Plugin Development Reference
================================================================================

This file serves as a comprehensive template for the dynamic plugin architecture.
It demonstrates ALL available features and patterns.

SUPPORTED PLUGIN STYLES:
1. Class-based (inherit from PluginBase)
2. Protocol-based (duck typing with IPlugin)
3. Functional (using PluginBuilder)
4. Decorator-based (using @plugin decorator)
5. Data-only (JSON/YAML files)

================================================================================
"""

from __future__ import annotations
from systems.plugins import (
    PluginBase, PluginInfo, PluginType, PluginPriority,
    EventPriority, IPlugin, IConfigurablePlugin, IHotReloadablePlugin,
    IContentProvider, IEventSubscriber, ICommandProvider,
    FunctionalPlugin, PluginBuilder, hook, command, define_plugin
)
from core.engine import (
    Rarity, DamageType, StatType, StatusEffectType, Weather, TimeOfDay,
    Ability, AbilityType, TargetType, EventType
)
from typing import Dict, List, Any, Tuple, Optional
from dataclasses import dataclass, field
import random


# =============================================================================
# STYLE 1: CLASS-BASED PLUGIN (Traditional Inheritance)
# =============================================================================

class BasePluginTemplate(PluginBase):
    """
    Complete plugin template using class-based approach.
    
    This style is recommended for complex plugins with lots of functionality.
    """
    
    # Instance state for hot reload
    _state: Dict[str, Any] = {}
    
    @property
    def info(self) -> PluginInfo:
        """Plugin metadata - supports all new fields"""
        return PluginInfo(
            # Required fields
            id="base_plugin_template",
            name="Base Plugin Template",
            version="2.0.0",
            author="Plugin Developer",
            description="Comprehensive template demonstrating all dynamic plugin features.",
            
            # Dependencies
            dependencies=[],
            soft_dependencies=["extended_items"],  # Optional dependency
            conflicts=[],
            provides=["template_content"],  # What this plugin provides
            
            # Loading configuration
            priority=PluginPriority.NORMAL.value,
            plugin_type=PluginType.CLASS,
            
            # Version compatibility
            min_game_version="1.0.0",
            max_game_version="",
            api_version="2.0",
            
            # Configuration support
            configurable=True,
            config_schema={
                "bonus_gold": {"type": "integer", "default": 100, "min": 0, "max": 10000},
                "debug_mode": {"type": "boolean", "default": False},
                "welcome_message": {"type": "string", "default": "Welcome!"}
            },
            default_config={
                "bonus_gold": 100,
                "debug_mode": False,
                "welcome_message": "Template Plugin Loaded!"
            },
            
            # Hot reload support
            supports_hot_reload=True,
            reload_priority=50,
            
            # Metadata
            tags=["template", "example", "reference"],
            homepage="https://example.com/plugin",
            license="MIT",
            custom={"category": "development", "stage": "production"}
        )
    
    # =========================================================================
    # LIFECYCLE METHODS
    # =========================================================================
    
    def on_load(self, game):
        """Called when plugin is loaded into memory"""
        print(f"[{self.info.name}] v{self.info.version} loading...")
        
        # Initialize state
        self._state = {
            "loads": 0,
            "events_processed": 0,
            "commands_executed": 0
        }
        
        # Apply configuration
        self._config = self.info.default_config.copy()
    
    def on_unload(self, game):
        """Called when plugin is being unloaded"""
        print(f"[{self.info.name}] unloading...")
        print(f"  Stats: {self._state['events_processed']} events, {self._state['commands_executed']} commands")
    
    def on_enable(self, game):
        """Called when plugin is enabled"""
        print(f"[{self.info.name}] enabled with config: {self._config}")
    
    def on_disable(self, game):
        """Called when plugin is disabled"""
        print(f"[{self.info.name}] disabled")
    
    # =========================================================================
    # CONFIGURATION (IConfigurablePlugin)
    # =========================================================================
    
    def get_config(self) -> Dict[str, Any]:
        """Get current configuration"""
        return self._config.copy()
    
    def set_config(self, config: Dict[str, Any]) -> None:
        """Set configuration"""
        self._config = {**self.info.default_config, **config}
    
    def validate_config(self, config: Dict[str, Any]) -> Tuple[bool, str]:
        """Validate configuration"""
        schema = self.info.config_schema
        
        for key, value in config.items():
            if key not in schema:
                return False, f"Unknown config key: {key}"
            
            spec = schema[key]
            if spec["type"] == "integer":
                if not isinstance(value, int):
                    return False, f"{key} must be an integer"
                if "min" in spec and value < spec["min"]:
                    return False, f"{key} must be >= {spec['min']}"
                if "max" in spec and value > spec["max"]:
                    return False, f"{key} must be <= {spec['max']}"
            elif spec["type"] == "boolean":
                if not isinstance(value, bool):
                    return False, f"{key} must be a boolean"
            elif spec["type"] == "string":
                if not isinstance(value, str):
                    return False, f"{key} must be a string"
        
        return True, ""
    
    def on_config_changed(self, game, key: str, value: Any):
        """Called when a config value changes"""
        print(f"[{self.info.name}] Config changed: {key} = {value}")
    
    # =========================================================================
    # HOT RELOAD (IHotReloadablePlugin)
    # =========================================================================
    
    def on_before_reload(self, game) -> Dict[str, Any]:
        """Save state before hot reload"""
        print(f"[{self.info.name}] Saving state for hot reload...")
        return {
            "state": self._state.copy(),
            "config": self._config.copy()
        }
    
    def on_after_reload(self, game, state: Dict[str, Any]) -> None:
        """Restore state after hot reload"""
        print(f"[{self.info.name}] Restoring state after hot reload...")
        self._state = state.get("state", {})
        self._config = state.get("config", self.info.default_config)
        self._state["loads"] = self._state.get("loads", 0) + 1
    
    # =========================================================================
    # EVENT HOOKS (IEventSubscriber)
    # =========================================================================
    
    def get_event_subscriptions(self) -> Dict[EventType, Any]:
        """Return event subscriptions (alternative to register_hooks)"""
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
    
    def register_hooks(self, event_system) -> Dict[EventType, Any]:
        """Register event hooks with priority support"""
        # Using priority for different handlers
        return {
            EventType.COMBAT_START: (self._on_combat_start, EventPriority.NORMAL),
            EventType.COMBAT_END: (self._on_combat_end, EventPriority.HIGH),
            EventType.PLAYER_LEVEL_UP: (self._on_level_up, EventPriority.NORMAL),
        }
    
    def _track_event(self):
        """Helper to track event processing"""
        self._state["events_processed"] = self._state.get("events_processed", 0) + 1
    
    def _on_combat_start(self, data):
        self._track_event()
        player = data.get("player")
        enemies = data.get("enemies", [])
        
        # Apply debug mode bonus
        if self._config.get("debug_mode"):
            print(f"[DEBUG] Combat starting against {len(enemies)} enemies")
        
        # Variety bonus
        if len(enemies) >= 3:
            print(f"[{self.info.name}] ⚔️ Variety bonus activated!")
        
        return None
    
    def _on_combat_end(self, data):
        self._track_event()
        player = data.get("player")
        result = data.get("result")
        
        if result == "victory":
            # Apply configured bonus
            bonus = self._config.get("bonus_gold", 100)
            if bonus > 0 and player:
                player.inventory.gold += bonus
                print(f"[{self.info.name}] Victory bonus: +{bonus} gold!")
        
        return None
    
    def _on_combat_turn(self, data):
        self._track_event()
        return None
    
    def _on_level_up(self, data):
        self._track_event()
        player = data.get("player")
        level = data.get("level", 1)
        
        # Milestone rewards
        if level % 5 == 0:
            print(f"[{self.info.name}] 🎯 Milestone level {level} reached!")
            
            # Give bonus ability
            if level >= 10:
                bonus_ability = Ability(
                    name="Template Power",
                    description="Power granted by the template.",
                    ability_type=AbilityType.ACTIVE,
                    target_type=TargetType.SINGLE_ENEMY,
                    mp_cost=15,
                    cooldown=3,
                    damage=20 + level,
                    damage_type=DamageType.HOLY
                )
                if player and bonus_ability not in player.abilities:
                    player.abilities.append(bonus_ability)
                    print(f"  ✨ New ability: {bonus_ability.name}!")
        
        return None
    
    def _on_player_death(self, data):
        self._track_event()
        return None
    
    def _on_item_pickup(self, data):
        self._track_event()
        item = data.get("item")
        
        if item and hasattr(item, 'rarity'):
            if item.rarity in [Rarity.EPIC, Rarity.LEGENDARY]:
                print(f"[{self.info.name}] ✨ Rare item discovered: {item.name}!")
        
        return None
    
    def _on_item_equip(self, data):
        self._track_event()
        return None
    
    def _on_item_use(self, data):
        self._track_event()
        return None
    
    def _on_npc_interact(self, data):
        self._track_event()
        return None
    
    def _on_quest_start(self, data):
        self._track_event()
        return None
    
    def _on_quest_complete(self, data):
        self._track_event()
        return None
    
    def _on_location_enter(self, data):
        self._track_event()
        location_id = data.get("location_id")
        
        # Check if this is a template location
        if location_id and location_id.startswith("template_"):
            print(f"[{self.info.name}] Entered template area: {location_id}")
        
        return None
    
    def _on_location_exit(self, data):
        self._track_event()
        return None
    
    def _on_time_change(self, data):
        self._track_event()
        new_time = data.get("new_time")
        
        if new_time == TimeOfDay.MIDNIGHT:
            print(f"[{self.info.name}] 🌙 The witching hour...")
        
        return None
    
    def _on_weather_change(self, data):
        self._track_event()
        new_weather = data.get("new_weather")
        
        if new_weather == Weather.BLOOD_MOON:
            print(f"[{self.info.name}] 🩸 The blood moon rises!")
        
        return None
    
    def _on_game_start(self, data):
        self._track_event()
        print(f"[{self.info.name}] {self._config.get('welcome_message', 'Welcome!')}")
        return None
    
    def _on_game_save(self, data):
        self._track_event()
        return None
    
    def _on_game_load(self, data):
        self._track_event()
        return None
    
    # =========================================================================
    # COMMANDS (ICommandProvider)
    # =========================================================================
    
    def get_commands(self) -> Dict[str, Any]:
        """Return commands (alternative to register_commands)"""
        return {
            "template_info": (self._cmd_info, "Show template plugin info", [], "system"),
            "template_config": (self._cmd_config, "Manage plugin configuration", [], "system"),
            "template_stats": (self._cmd_stats, "Show plugin statistics", [], "debug"),
            "template_bonus": (self._cmd_bonus, "Give template bonus", [], "debug"),
        }
    
    def register_commands(self, command_system) -> Dict[str, Any]:
        """Register commands with full metadata"""
        return {
            "template_info": {
                "handler": self._cmd_info,
                "help": "Show template plugin information",
                "category": "system"
            },
            "template_config": {
                "handler": self._cmd_config,
                "help": "View or set configuration",
                "usage": "/template_config [key] [value]",
                "category": "system"
            },
            "template_stats": {
                "handler": self._cmd_stats,
                "help": "Show plugin statistics",
                "category": "debug"
            }
        }
    
    def _track_command(self):
        """Helper to track command execution"""
        self._state["commands_executed"] = self._state.get("commands_executed", 0) + 1
    
    def _cmd_info(self, game, args, context):
        """Display plugin information"""
        self._track_command()
        info = self.info
        return (
            f"Plugin: {info.name} v{info.version}\n"
            f"Author: {info.author}\n"
            f"Type: {info.plugin_type.value}\n"
            f"Priority: {info.priority}\n"
            f"Tags: {', '.join(info.tags)}\n"
            f"Hot Reload: {'Yes' if info.supports_hot_reload else 'No'}\n"
            f"\n{info.description}"
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
        
        # Parse value
        schema = self.info.config_schema.get(key, {})
        if schema.get("type") == "integer":
            try:
                value = int(value)
            except ValueError:
                return f"Invalid integer: {value}"
        elif schema.get("type") == "boolean":
            value = value.lower() in ("true", "yes", "1", "on")
        
        # Validate
        valid, msg = self.validate_config({key: value})
        if not valid:
            return f"Validation error: {msg}"
        
        # Apply
        old_value = self._config.get(key)
        self._config[key] = value
        self.on_config_changed(game, key, value)
        
        return f"Set {key}: {old_value} -> {value}"
    
    def _cmd_stats(self, game, args, context):
        """Show plugin statistics"""
        self._track_command()
        return (
            f"Plugin Statistics:\n"
            f"  Loads: {self._state.get('loads', 0)}\n"
            f"  Events Processed: {self._state.get('events_processed', 0)}\n"
            f"  Commands Executed: {self._state.get('commands_executed', 0)}"
        )
    
    def _cmd_bonus(self, game, args, context):
        """Give template bonus to player"""
        self._track_command()
        if game and game.player:
            bonus = self._config.get("bonus_gold", 100)
            game.player.inventory.gold += bonus
            return f"Template bonus applied: +{bonus} gold!"
        return "No player available"
    
    # =========================================================================
    # CONTENT REGISTRATION (IContentProvider)
    # =========================================================================
    
    def get_content_types(self) -> List[str]:
        """Return content types this plugin provides"""
        return ["items", "enemies", "locations", "npcs", "quests", "recipes"]
    
    def get_content(self, content_type: str) -> Dict[str, Any]:
        """Return content of a specific type"""
        content_map = {
            "items": self._get_items,
            "enemies": self._get_enemies,
            "locations": self._get_locations,
            "npcs": self._get_npcs,
            "quests": self._get_quests,
            "recipes": self._get_recipes
        }
        
        if content_type in content_map:
            return content_map[content_type]()
        return {}
    
    def register_content(self, content_registry) -> Dict[str, Dict]:
        """Generic content registration - supports any content type"""
        all_content = {}
        for content_type in self.get_content_types():
            content = self.get_content(content_type)
            if content:
                all_content[content_type] = content
        return all_content
    
    def _get_items(self) -> Dict[str, Dict]:
        """Return items added by this plugin"""
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
                "damage_type": "holy",
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
                "stat_bonuses": {"constitution": 3},
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
                "stat_bonuses": {"luck": 4, "charisma": 2},
                "special_effects": ["+15% Experience", "+10% Gold Find"],
                "level_required": 10
            }
        }
    
    def _get_enemies(self) -> Dict[str, Dict]:
        """Return enemies added by this plugin"""
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
    
    def _get_locations(self) -> Dict[str, Dict]:
        """Return locations added by this plugin"""
        return {
            "template_sanctum": {
                "name": "Template Sanctum",
                "description": "A peaceful sanctuary where templates are created and refined.",
                "location_type": "special",
                "level_range": [1, 30],
                "connections": ["capital_city"],
                "danger_level": 0,
                "special_features": {
                    "meditation_bonus": {"exp_mult": 1.5},
                    "free_healing": True
                },
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
    
    def _get_npcs(self) -> Dict[str, Dict]:
        """Return NPCs added by this plugin"""
        return {
            "template_sage": {
                "name": "The Template Sage",
                "description": "An ancient being who has mastered the art of templates.",
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
    
    def _get_quests(self) -> Dict[str, Dict]:
        """Return quests added by this plugin"""
        return {
            "template_discovery": {
                "name": "The Template Vault",
                "description": "Explore the mysterious Template Vault and uncover its secrets.",
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
    
    def _get_recipes(self) -> Dict[str, Dict]:
        """Return crafting recipes added by this plugin"""
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
    
    # =========================================================================
    # LEGACY SUPPORT (Backward Compatibility)
    # =========================================================================
    
    # These methods maintain backward compatibility with older plugin loading
    
    def register_items(self, item_registry):
        return self._get_items()
    
    def register_enemies(self, enemy_registry):
        return self._get_enemies()
    
    def get_new_locations(self):
        return self._get_locations()
    
    def get_new_npcs(self):
        return self._get_npcs()
    
    def get_new_quests(self):
        return self._get_quests()
    
    def register_recipes(self, crafting_manager):
        return self._get_recipes()


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
    
    def on_combat_end(data):
        if data.get("result") == "victory":
            print("Victory in functional plugin!")
    
    def cmd_hello(game, args, context):
        return "Hello from functional plugin!"
    
    return (PluginBuilder("functional_template")
        .name("Functional Template Plugin")
        .version("1.0.0")
        .author("Plugin Developer")
        .description("A plugin built with the fluent API")
        .priority(PluginPriority.LOW.value)
        .tags("functional", "example")
        .supports_hot_reload(True)
        .on_load(on_load)
        .hook(EventType.COMBAT_END, on_combat_end)
        .command("hello", cmd_hello, "Say hello")
        .content("items", {"func_item": {"name": "Functional Item"}})
        .build())


# =============================================================================
# STYLE 3: DECORATOR-BASED PLUGIN
# =============================================================================

# Note: Uncomment to use this style
# @plugin({
#     "id": "decorator_template",
#     "name": "Decorator Plugin Template",
#     "version": "1.0.0",
#     "author": "Plugin Developer",
#     "description": "Plugin using decorators"
# })
# class DecoratorTemplate:
#     
#     @hook(EventType.COMBAT_START)
#     def on_combat_start(self, data):
#         print("Combat starting (decorator plugin)")
#     
#     @command("dec_test", "Test command from decorator plugin")
#     def test_command(self, game, args):
#         return "Decorator plugin test!"


# =============================================================================
# PLUGIN INSTANCE
# =============================================================================

# Required: Create the plugin instance for discovery
plugin = BasePluginTemplate()

# Alternative: Uncomment to use functional plugin instead
# plugin = create_functional_plugin()


# =============================================================================
# ADDITIONAL DOCUMENTATION
# =============================================================================

"""
QUICK START GUIDE:
------------------

1. Copy this file to plugins folder
2. Rename and customize
3. Implement needed methods
4. Plugin auto-loads

SUPPORTED STYLES:
-----------------

1. CLASS-BASED (Recommended for complex plugins):
   - Inherit from PluginBase
   - Override methods as needed
   - Full state management

2. FUNCTIONAL (Recommended for simple plugins):
   - Use PluginBuilder with fluent API
   - Chain method calls
   - No class needed

3. DECORATOR (Recommended for handlers):
   - Use @plugin, @hook, @command decorators
   - Clean, declarative syntax

4. DATA-ONLY (For content-only plugins):
   - Create JSON or YAML file
   - Define items, enemies, etc.
   - No Python code needed

NEW FEATURES IN V2:
-------------------

- Dynamic content types
- Event priorities
- Hot reload support
- Configuration management
- Plugin dependencies
- Soft dependencies
- Plugin protocols (duck typing)
- Command categories
- Event middleware
- Async event handling
- Plugin statistics
- File change detection

EXAMPLE MINIMAL PLUGIN:
-----------------------

from systems.plugins import PluginBase, PluginInfo

class MinimalPlugin(PluginBase):
    @property
    def info(self):
        return PluginInfo(
            id="minimal",
            name="Minimal Plugin",
            version="1.0.0",
            author="Developer",
            description="Minimal example"
        )
    
    def on_load(self, game):
        print("Loaded!")
    
    def on_unload(self, game):
        print("Unloaded!")

plugin = MinimalPlugin()
"""

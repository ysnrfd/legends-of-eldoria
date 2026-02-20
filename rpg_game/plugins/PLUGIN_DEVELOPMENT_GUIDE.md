# LEGENDS OF ELDORIA - Complete Plugin Development Guide

![Version](https://img.shields.io/badge/version-2.0.0-blue)
![Python](https://img.shields.io/badge/python-3.8%2B-green)

**Creator:** YSNRFD | **GitHub:** [github.com/ysnrfd](https://github.com/ysnrfd)

# Plugin Development Guide

## Legends of Eldoria - Dynamic Plugin System

---

## Table of Contents

1. [Introduction](#introduction)
2. [Architecture Overview](#architecture-overview)
3. [Getting Started](#getting-started)
4. [Plugin Metadata](#plugin-metadata)
5. [Plugin Lifecycle](#plugin-lifecycle)
6. [Event System](#event-system)
7. [Command System](#command-system)
8. [Content Registration](#content-registration)
9. [Plugin Dependencies](#plugin-dependencies)
10. [Plugin Styles](#plugin-styles)
11. [API Reference](#api-reference)
12. [Best Practices](#best-practices)
13. [Examples](#examples)
14. [Troubleshooting](#troubleshooting)

---

## Introduction

The Dynamic Plugin System is a fully extensible architecture that allows developers to create modular content for Legends of Eldoria. This system supports multiple plugin formats, dynamic content registration, hot reloading capabilities, inter-plugin communication, and comprehensive event handling.

### Key Features

- **Multiple Plugin Styles**: Class-based inheritance (recommended), functional builder pattern, and minimal implementations
- **Dynamic Content Registration**: Register items, enemies, NPCs, locations, quests, and crafting recipes
- **Event-Driven Architecture**: Hook into game events like combat, exploration, and player actions
- **Command System**: Create custom slash commands with help text and categories
- **Dependency Management**: Define required dependencies, soft dependencies, and plugin conflicts
- **Priority Loading**: Control plugin load order with priority levels
- **Configuration System**: Runtime configuration for plugin settings
- **Thread-Safe Operations**: Built-in locking for concurrent access safety

---

## Architecture Overview

### System Components

```
┌─────────────────────────────────────────────────────────────────────┐
│                         Plugin Manager                              │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐   │
│  │   Plugin Loader  │  │  Event Handlers  │  │ Command Registry │   │
│  └──────────────────┘  └──────────────────┘  └──────────────────┘   │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐   │
│  │ Content Registry │  │  Plugin State    │  │  Config Manager  │   │
│  └──────────────────┘  └──────────────────┘  └──────────────────┘   │
└─────────────────────────────────────────────────────────────────────┘
                                   │
                                   ▼
┌─────────────────────────────────────────────────────────────────────┐
│                          Plugin Instance                            │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐   │
│  │   Plugin Info    │  │   Event Hooks    │  │    Commands      │   │
│  └──────────────────┘  └──────────────────┘  └──────────────────┘   │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐   │
│  │    Content       │  │    Config        │  │     State        │   │
│  └──────────────────┘  └──────────────────┘  └──────────────────┘   │
└─────────────────────────────────────────────────────────────────────┘
```

### Plugin States

The plugin system manages plugins through the following states:

| State | Description |
|-------|-------------|
| `UNDISCOVERED` | Plugin not yet found by the system |
| `DISCOVERED` | Plugin file located and recognized |
| `LOADING` | Plugin file being imported and parsed |
| `RESOLVING` | Dependencies being resolved |
| `INITIALIZING` | Plugin hooks and commands being registered |
| `ENABLED` | Plugin fully operational |
| `DISABLED` | Plugin loaded but not active |
| `ERROR` | Plugin encountered an error during loading |
| `UNLOADING` | Plugin being removed from memory |
| `PENDING_RELOAD` | Plugin awaiting hot reload |
| `HOT_RELOADING` | Plugin being reloaded while game runs |

### Priority Levels

Plugins load in order of priority (lower value = earlier load):

| Priority | Value | Use Case |
|----------|-------|----------|
| `SYSTEM` | 0 | Core system plugins (load first) |
| `CORE` | 25 | Essential functionality plugins |
| `HIGH` | 50 | High priority content mods |
| `NORMAL` | 100 | Standard plugins (default) |
| `LOW` | 150 | Low priority additions |
| `OPTIONAL` | 200 | Optional content (load last) |

---

## Getting Started

### Quick Start: Your First Plugin

Create a new file in the `plugins/` directory with the following structure:

```python
"""
My First Plugin - A simple example
"""
from systems.plugins import Plugin, PluginInfo, PluginPriority
from typing import Dict, Any


class MyFirstPlugin(Plugin):
    """A minimal plugin example."""
    
    def __init__(self):
        info = PluginInfo(
            id="my_first_plugin",
            name="My First Plugin",
            version="1.0.0",
            author="Your Name",
            description="My first plugin for Legends of Eldoria!",
            priority=PluginPriority.NORMAL,
            tags=["example"]
        )
        super().__init__(info)
    
    def on_load(self, game) -> bool:
        print(f"[{self.info.name}] Loading...")
        return True
    
    def on_unload(self, game) -> bool:
        print(f"[{self.info.name}] Unloading...")
        return True
    
    def on_enable(self, game) -> bool:
        print(f"[{self.info.name}] Enabled!")
        return True
    
    def on_disable(self, game) -> bool:
        print(f"[{self.info.name}] Disabled.")
        return True


# REQUIRED: Create the plugin instance
plugin = MyFirstPlugin()
```

### File Structure

```
game/
├── plugins/
│   ├── __init__.py
│   ├── my_plugin.py          # Your plugin file
│   ├── enhanced_combat.py
│   ├── extended_items.py
│   ├── extended_npcs.py
│   ├── extended_world.py
│   └── help_plugin.py
├── systems/
│   └── plugins.py            # Plugin system core
└── core/
    └── engine.py             # Event types and game core
```

### Naming Conventions

- **File names**: Use lowercase with underscores: `my_awesome_plugin.py`
- **Class names**: Use PascalCase: `MyAwesomePlugin`
- **Plugin IDs**: Use lowercase with underscores: `my_awesome_plugin`
- **Commands**: Use lowercase with underscores: `/my_command`

---

## Plugin Metadata

### PluginInfo Dataclass

The `PluginInfo` class contains all metadata about your plugin:

```python
@dataclass
class PluginInfo:
    id: str                          # Unique identifier (required)
    name: str                        # Display name (required)
    version: str = "1.0.0"           # Semantic version
    author: str = "Unknown"          # Author name
    description: str = ""            # Detailed description
    dependencies: List[str] = []     # Required plugins
    soft_dependencies: List[str] = [] # Optional plugins
    conflicts: List[str] = []        # Incompatible plugins
    priority: PluginPriority = PluginPriority.NORMAL
    tags: List[str] = []             # Searchable tags
    min_game_version: str = "1.0.0"  # Minimum game version
    max_game_version: str = ""       # Maximum compatible version
```

### Complete PluginInfo Example

```python
info = PluginInfo(
    id="dragon_expansion",
    name="Dragon Expansion",
    version="2.5.0",
    author="DragonMaster",
    description="Adds 10 new dragon types, dragon riding mechanics, "
               "and a complete dragon storyline with 15 quests.",
    
    # Dependencies
    dependencies=["extended_world"],          # Must load before this plugin
    soft_dependencies=["enhanced_combat"],    # Load before if available
    conflicts=["dragon_nerf"],                # Cannot run with this plugin
    
    # Loading configuration
    priority=PluginPriority.HIGH,             # Load early
    
    # Metadata
    tags=["dragons", "mounts", "quests", "bosses"],
    min_game_version="1.5.0",
    max_game_version="2.0.0"
)
```

### Metadata Best Practices

1. **ID Uniqueness**: Choose a unique, descriptive ID that won't conflict with other plugins
2. **Version Format**: Use semantic versioning (MAJOR.MINOR.PATCH)
3. **Description**: Write a clear description explaining what your plugin adds
4. **Tags**: Include relevant tags for discoverability
5. **Dependencies**: Only mark plugins as required if your plugin cannot function without them

---

## Plugin Lifecycle

### Lifecycle Methods

Every plugin must implement four core lifecycle methods:

```python
class Plugin(ABC):
    @abstractmethod
    def on_load(self, game) -> bool:
        """Called when plugin is loaded into memory."""
        pass
    
    @abstractmethod
    def on_unload(self, game) -> bool:
        """Called when plugin is being unloaded."""
        pass
    
    @abstractmethod
    def on_enable(self, game) -> bool:
        """Called when plugin is enabled."""
        pass
    
    @abstractmethod
    def on_disable(self, game) -> bool:
        """Called when plugin is disabled."""
        pass
```

### Lifecycle Flow

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│   on_load    │────▶│  on_enable   │───▶│    ACTIVE    │
└──────────────┘     └──────────────┘     └──────────────┘
       │                                          │
       │                                          │
       ▼                                          ▼
┌──────────────┐                           ┌──────────────┐
│  on_unload   │◀──────────────────────────│  on_disable  │
└──────────────┘                           └──────────────┘
```

### on_load Method

The `on_load` method is called when the plugin is first loaded into memory. Use this for:

- Initializing internal state variables
- Setting default configuration values
- Preparing resources
- Validating game state

```python
def on_load(self, game) -> bool:
    """Initialize plugin state and configuration."""
    print(f"[{self.info.name}] v{self.info.version} loading...")
    
    # Initialize state tracking
    self._state = {
        "events_processed": 0,
        "commands_executed": 0
    }
    
    # Set default configuration
    self._config = {
        "bonus_gold": 100,
        "debug_mode": False,
        "welcome_message": "Plugin Loaded!"
    }
    
    return True  # Return False to abort loading
```

### on_enable Method

The `on_enable` method is called after successful loading. Use this for:

- Registering with game systems
- Starting background processes
- Performing validation that requires game state

```python
def on_enable(self, game) -> bool:
    """Enable plugin functionality."""
    print(f"[{self.info.name}] enabled!")
    
    # Validate game state
    if not hasattr(game, 'player'):
        print("Warning: Player system not available")
    
    return True
```

### on_disable Method

The `on_disable` method is called when the plugin is being disabled. Use this for:

- Saving plugin state
- Cleaning up temporary resources
- Unregistering from game systems

```python
def on_disable(self, game) -> bool:
    """Disable plugin functionality."""
    print(f"[{self.info.name}] disabled")
    
    # Save any pending data
    self._save_state()
    
    return True
```

### on_unload Method

The `on_unload` method is called when the plugin is being completely removed. Use this for:

- Final cleanup
- Releasing resources
- Logging final statistics

```python
def on_unload(self, game) -> bool:
    """Cleanup plugin resources."""
    print(f"[{self.info.name}] unloading...")
    print(f"  Stats: {self._state.get('events_processed', 0)} events processed")
    return True
```

---

## Event System

### Event Types

The plugin system provides a comprehensive set of event types that plugins can hook into:

#### Combat Events

| Event | Description | Data Provided |
|-------|-------------|---------------|
| `COMBAT_START` | Combat begins | `player`, `enemies` |
| `COMBAT_END` | Combat concludes | `player`, `result` |
| `COMBAT_TURN` | Each combat turn | `player`, `turn_number` |

#### Player Events

| Event | Description | Data Provided |
|-------|-------------|---------------|
| `PLAYER_LEVEL_UP` | Player gains a level | `player`, `level` |
| `PLAYER_DEATH` | Player dies | `player`, `cause` |
| `PLAYER_MOVE` | Player moves | `from_location`, `to_location` |

#### Item Events

| Event | Description | Data Provided |
|-------|-------------|---------------|
| `ITEM_PICKUP` | Item picked up | `player`, `item` |
| `ITEM_EQUIP` | Item equipped | `player`, `item`, `slot` |
| `ITEM_USE` | Item used | `player`, `item` |

#### World Events

| Event | Description | Data Provided |
|-------|-------------|---------------|
| `LOCATION_ENTER` | Enter a location | `player`, `location_id` |
| `LOCATION_EXIT` | Exit a location | `player`, `location_id` |
| `TIME_CHANGE` | Time of day changes | `old_time`, `new_time` |
| `WEATHER_CHANGE` | Weather changes | `old_weather`, `new_weather` |

#### NPC/Quest Events

| Event | Description | Data Provided |
|-------|-------------|---------------|
| `NPC_INTERACT` | NPC interaction | `player`, `npc_id`, `friendship` |
| `QUEST_START` | Quest accepted | `player`, `quest_id` |
| `QUEST_COMPLETE` | Quest completed | `player`, `quest_id`, `rewards` |

#### System Events

| Event | Description | Data Provided |
|-------|-------------|---------------|
| `GAME_START` | Game session starts | `player` |
| `GAME_SAVE` | Game being saved | `player`, `save_data` |
| `GAME_LOAD` | Game being loaded | `player`, `save_data` |
| `PLUGIN_LOAD` | Plugin loaded | `plugin_id` |
| `PLUGIN_UNLOAD` | Plugin unloaded | `plugin_id` |

### Registering Event Hooks

To register event hooks, implement the `register_hooks` method:

```python
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
        EventType.PLAYER_LEVEL_UP: self._on_level_up,
        EventType.ITEM_PICKUP: self._on_item_pickup,
        EventType.LOCATION_ENTER: self._on_location_enter,
        EventType.QUEST_COMPLETE: self._on_quest_complete,
    }
```

### Event Handler Signature

All event handlers follow this signature:

```python
def event_handler(self, game, data) -> None:
    """
    Handle an event.
    
    Args:
        game: The main game instance
        data: Dict containing event-specific data
    """
    pass
```

### Event Handler Examples

#### Combat Start Handler

```python
def _on_combat_start(self, game, data):
    """Handle combat start event."""
    player = data.get("player")
    enemies = data.get("enemies", [])
    
    # Variety bonus for fighting diverse enemies
    if enemies:
        unique_types = len(set(e.name for e in enemies))
        if unique_types >= 3:
            print(f"⚔️ Variety Bonus: +10% experience!")
            player._variety_bonus = 0.10
```

#### Combat End Handler

```python
def _on_combat_end(self, game, data):
    """Handle combat end event."""
    player = data.get("player")
    result = data.get("result")
    
    if result == "victory" and player:
        # Apply bonus
        bonus = self._config.get("bonus_gold", 100)
        if bonus > 0:
            player.inventory.gold += bonus
            print(f"Victory bonus: +{bonus} gold!")
```

#### Level Up Handler

```python
def _on_level_up(self, game, data):
    """Handle player level up event."""
    player = data.get("player")
    level = data.get("level", 1)
    
    # Milestone rewards every 5 levels
    if level % 5 == 0:
        print(f"🎯 Milestone Level {level} reached!")
        
        # Add passive combat bonus
        if not hasattr(player, '_combat_bonuses'):
            player._combat_bonuses = {}
        
        player._combat_bonuses[f"milestone_{level}"] = {
            "critical_chance": 0.02,
            "damage_bonus": level // 2
        }
```

#### Item Pickup Handler

```python
def _on_item_pickup(self, game, data):
    """Handle item pickup event."""
    item = data.get("item")
    player = data.get("player")
    
    if item and hasattr(item, 'rarity'):
        if item.rarity == Rarity.LEGENDARY:
            print(f"🌟 LEGENDARY item found: {item.name}!")
            if player:
                print(f"   This will serve you well, {player.name}!")
        elif item.rarity == Rarity.EPIC:
            print(f"✨ Epic item discovered: {item.name}!")
```

#### Location Enter Handler

```python
def _on_location_enter(self, game, data):
    """Handle location enter event."""
    location_id = data.get("location_id")
    player = data.get("player")
    
    # Check for special locations
    if location_id and location_id.startswith("dragon_"):
        print(f"🐉 You enter dragon territory...")
    
    # Check for secret discoveries
    secrets = self._get_world_secrets()
    for secret_id, secret in secrets.items():
        if secret["location"] == location_id:
            if random.random() < 0.15:  # 15% discovery chance
                print(f"🔍 SECRET DISCOVERED: {secret['name']}!")
```

#### Quest Complete Handler

```python
def _on_quest_complete(self, game, data):
    """Handle quest completion."""
    quest_id = data.get("quest_id")
    player = data.get("player")
    rewards = data.get("rewards", {})
    
    # Track completed quests
    self._state["quests_completed"] = self._state.get("quests_completed", 0) + 1
    
    # Bonus for certain quest types
    if quest_id.startswith("boss_"):
        print("🏆 Boss quest completed! Double rewards!")
        if "gold" in rewards:
            player.inventory.gold += rewards["gold"]
```

### Manual Hook Registration

You can also register hooks directly in `on_enable`:

```python
def on_enable(self, game) -> bool:
    """Enable plugin and register hooks manually."""
    # Access the plugin manager
    pm = game.plugin_manager
    
    # Register individual hooks
    pm._event_handlers[EventType.COMBAT_START].append(self._my_handler)
    
    return True
```

---

## Command System

### Command Handler Signature

All command handlers follow this signature:

```python
def command_handler(self, game, args, context) -> str:
    """
    Handle a command.
    
    Args:
        game: The main game instance
        args: List of command arguments
        context: Dict with additional context (plugin_manager, timestamp, etc.)
        
    Returns:
        String response to display to the player
    """
    pass
```

### Registering Commands

Implement the `register_commands` method:

```python
def register_commands(self, command_system) -> Dict[str, Any]:
    """
    Register slash commands.
    
    Args:
        command_system: The command system instance
        
    Returns:
        Dict mapping command names to handler info
    """
    return {
        "my_command": {
            "handler": self._cmd_my_command,
            "help": "Description of what the command does",
            "usage": "/my_command [argument]",
            "category": "info",
            "aliases": ["mc", "mycmd"]
        },
        "my_other_command": {
            "handler": self._cmd_other,
            "help": "Another command description",
            "category": "config"
        }
    }
```

### Command Categories

| Category | Icon | Purpose |
|----------|------|---------|
| `system` | 📋 | System-level commands |
| `stats` | 📊 | Statistics and information |
| `config` | ⚙️ | Configuration commands |
| `debug` | 🔧 | Debug and development tools |
| `info` | ℹ️ | Information display commands |
| `other` | 🎮 | Miscellaneous commands |

### Command Examples

#### Simple Info Command

```python
def _cmd_info(self, game, args, context) -> str:
    """Display plugin information."""
    return (
        f"Plugin: {self.info.name} v{self.info.version}\n"
        f"Author: {self.info.author}\n"
        f"Description: {self.info.description}"
    )
```

#### Configuration Command

```python
def _cmd_config(self, game, args, context) -> str:
    """View or set configuration values."""
    if not args:
        return f"Config: {self._config}"
    
    if len(args) == 1:
        key = args[0]
        return f"{key} = {self._config.get(key, 'Not found')}"
    
    key, value = args[0], args[1]
    
    # Parse value type
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
    
    old_value = self._config.get(key)
    self._config[key] = value
    
    return f"Set {key}: {old_value} -> {value}"
```

#### Statistics Command

```python
def _cmd_stats(self, game, args, context) -> str:
    """Show plugin statistics."""
    stats = self._combat_stats
    
    total = stats.get("combats_won", 0) + stats.get("combats_lost", 0)
    win_rate = (stats.get("combats_won", 0) / total * 100) if total > 0 else 0
    
    return (
        "Plugin Statistics:\n"
        f"  Combats Started: {stats.get('combats_started', 0)}\n"
        f"  Victories: {stats.get('combats_won', 0)}\n"
        f"  Defeats: {stats.get('combats_lost', 0)}\n"
        f"  Win Rate: {win_rate:.1f}%\n"
        f"  Critical Hits: {stats.get('critical_hits', 0)}\n"
        f"  Max Combo: {stats.get('max_combo', 0)}"
    )
```

#### Command with Arguments

```python
def _cmd_test(self, game, args, context) -> str:
    """Test combat calculations."""
    if not args:
        return "Usage: /combat_test <base_damage> [combo_count]"
    
    try:
        base_damage = int(args[0])
        combo = int(args[1]) if len(args) > 1 else 0
    except ValueError:
        return "Invalid numbers provided"
    
    # Calculate with combo multiplier
    if combo > 0:
        multiplier = 1.1 ** (combo // 3)
        final_damage = int(base_damage * multiplier)
        return (
            f"Combat Test:\n"
            f"  Base Damage: {base_damage}\n"
            f"  Combo: {combo}\n"
            f"  Multiplier: {multiplier:.2f}x\n"
            f"  Final Damage: {final_damage}"
        )
    
    return f"Combat Test: Base damage {base_damage} (no combo bonus)"
```

#### Search Command

```python
def _cmd_search(self, game, args, context) -> str:
    """Search for items."""
    if not args:
        return "Usage: /item_search <query>"
    
    query = args[0].lower()
    items = self._get_all_items()
    
    results = []
    for item_id, item_data in items.items():
        name = item_data.get("name", "").lower()
        item_type = item_data.get("item_type", "").lower()
        if query in name or query in item_type or query in item_id.lower():
            results.append((item_id, item_data))
    
    if not results:
        return f"No items found matching '{args[0]}'"
    
    lines = [f"Search results for '{args[0]}':"]
    for item_id, item_data in results:
        lines.append(f"  • {item_data.get('name')} ({item_data.get('item_type')})")
    
    return "\n".join(lines)
```

---

## Content Registration

### Content Types

Plugins can register the following content types:

| Content Type | Method | Description |
|--------------|--------|-------------|
| Items | `register_items()` | Weapons, armor, consumables, accessories, materials |
| Enemies | `register_enemies()` | Enemy definitions for combat |
| Locations | `get_new_locations()` | New areas to explore |
| NPCs | `get_new_npcs()` | Characters to interact with |
| Quests | `get_new_quests()` | Quest definitions |
| Recipes | `register_recipes()` | Crafting recipes |

### Registering Items

```python
def register_items(self, item_registry) -> Dict[str, Dict]:
    """
    Register items provided by this plugin.
    
    Returns:
        Dict mapping item IDs to item data
    """
    return {
        "thunder_hammer": {
            "name": "Thunder Hammer",
            "item_type": "weapon",
            "rarity": "Epic",
            "value": 3500,
            "weight": 8.0,
            "description": "A massive hammer that crackles with lightning.",
            "damage_min": 18,
            "damage_max": 32,
            "damage_type": "lightning",
            "attack_speed": 0.7,
            "critical_chance": 0.10,
            "two_handed": True,
            "stat_requirements": {"strength": 16},
            "level_required": 12,
            "special_effects": ["Chain Lightning on critical"]
        },
        "dragon_plate": {
            "name": "Dragon Plate Armor",
            "item_type": "armor",
            "rarity": "Legendary",
            "value": 30000,
            "weight": 25.0,
            "description": "Armor forged from the scales of an ancient dragon.",
            "slot": "chest",
            "defense": 50,
            "magic_defense": 30,
            "resistances": {"fire": 0.7, "physical": 0.3},
            "stat_bonuses": {"strength": 5, "constitution": 5},
            "level_required": 25,
            "special_effects": ["Dragon's Fury on hit", "Fire immunity"]
        },
        "mega_potion": {
            "name": "Mega Potion",
            "item_type": "consumable",
            "rarity": "Rare",
            "value": 300,
            "weight": 0.2,
            "description": "A powerful potion that restores both HP and MP.",
            "hp_restore": 100,
            "mp_restore": 75,
            "use_message": "You feel completely revitalized!"
        },
        "ring_of_shadows": {
            "name": "Ring of Shadows",
            "item_type": "accessory",
            "rarity": "Epic",
            "value": 2500,
            "weight": 0.1,
            "description": "A ring that grants power over shadows.",
            "stat_bonuses": {"dexterity": 4, "luck": 3},
            "special_effects": ["Critical Damage +15%", "Evasion +10%"],
            "level_required": 12
        },
        "dragon_scale": {
            "name": "Dragon Scale",
            "item_type": "material",
            "rarity": "Epic",
            "value": 500,
            "weight": 0.5,
            "description": "A scale from a dragon. Used in legendary crafting."
        }
    }
```

### Item Property Reference

#### Weapon Properties

| Property | Type | Description |
|----------|------|-------------|
| `damage_min` | int | Minimum damage |
| `damage_max` | int | Maximum damage |
| `damage_type` | str | Damage type: physical, fire, ice, lightning, holy, dark, void |
| `attack_speed` | float | Attacks per turn (1.0 = normal) |
| `critical_chance` | float | Critical hit chance (0.0-1.0) |
| `critical_damage` | float | Critical damage multiplier |
| `range` | int | Attack range |
| `two_handed` | bool | Requires two hands |

#### Armor Properties

| Property | Type | Description |
|----------|------|-------------|
| `slot` | str | Equipment slot: head, chest, legs, feet, hands |
| `defense` | int | Physical defense |
| `magic_defense` | int | Magical defense |
| `resistances` | dict | Damage type resistances |
| `stat_bonuses` | dict | Stat bonuses when equipped |

#### Consumable Properties

| Property | Type | Description |
|----------|------|-------------|
| `hp_restore` | int | HP restored on use |
| `mp_restore` | int | MP restored on use |
| `effects` | list | Status effects applied |
| `temporary_effects` | list | Temporary buffs with duration |
| `use_message` | str | Message displayed on use |

### Registering Enemies

```python
def register_enemies(self, enemy_registry) -> Dict[str, Dict]:
    """
    Register enemies provided by this plugin.
    
    Returns:
        Dict mapping enemy IDs to enemy data
    """
    return {
        "elite_knight": {
            "name": "Elite Knight",
            "description": "A highly trained warrior in gleaming armor.",
            "base_hp": 200,
            "base_mp": 50,
            "base_damage": 30,
            "rarity": "Rare",
            "faction": "human",
            "abilities": ["shield_bash", "power_strike"],
            "resistances": {"physical": 0.3},
            "weaknesses": {"lightning": 1.5},
            "drops": {"gold": [50, 150], "items": ["knight_armor"]}
        },
        "shadow_assassin": {
            "name": "Shadow Assassin",
            "description": "A deadly killer emerging from darkness.",
            "base_hp": 100,
            "base_mp": 80,
            "base_damage": 40,
            "rarity": "Epic",
            "faction": "assassin",
            "abilities": ["backstab", "shadow_step", "poison_blade"],
            "resistances": {"physical": 0.2, "dark": 0.5},
            "weaknesses": {"holy": 1.5},
            "drops": {"gold": [100, 300], "items": ["assassin_dagger"]}
        }
    }
```

### Enemy Property Reference

| Property | Type | Description |
|----------|------|-------------|
| `name` | str | Display name |
| `description` | str | Flavor text |
| `base_hp` | int | Base health points |
| `base_mp` | int | Base mana points |
| `base_damage` | int | Base damage |
| `rarity` | str | Common, Uncommon, Rare, Epic, Legendary |
| `faction` | str | Enemy faction for grouping |
| `abilities` | list | Special abilities |
| `resistances` | dict | Damage type resistances (0.0-1.0) |
| `weaknesses` | dict | Damage type weaknesses (>1.0) |
| `drops` | dict | Gold range and item drops |

### Registering Locations

```python
def get_new_locations(self) -> Dict[str, Dict]:
    """
    Return new locations added by this plugin.
    
    Returns:
        Dict mapping location IDs to location data
    """
    return {
        "dragon_peak": {
            "name": "Dragon's Peak",
            "description": "The highest mountain where dragons nest.",
            "location_type": "mountain",
            "level_range": [20, 30],
            "connections": ["mountain_pass"],
            "enemies": ["young_dragon", "drake", "ancient_dragon"],
            "resources": ["dragon_scale", "dragon_bone"],
            "features": ["dragon_nest", "treasure_hoard", "peak_shrine"],
            "hidden": False
        },
        "mystic_sanctuary": {
            "name": "Mystic Sanctuary",
            "description": "A hidden sanctuary of magical learning.",
            "location_type": "temple",
            "level_range": [10, 20],
            "connections": ["capital_city"],
            "enemies": ["magical_guardian"],
            "resources": ["spell_tomes", "mana_crystals"],
            "features": ["library", "meditation_chambers", "portal_room"],
            "hidden": True,
            "requirements": {"magic_level": 5}
        }
    }
```

### Location Property Reference

| Property | Type | Description |
|----------|------|-------------|
| `name` | str | Display name |
| `description` | str | Location description |
| `location_type` | str | town, forest, cave, dungeon, temple, mountain, special |
| `level_range` | list | [min_level, max_level] for enemies |
| `connections` | list | Connected location IDs |
| `enemies` | list | Enemy IDs that spawn here |
| `resources` | list | Gatherable resources |
| `features` | list | Special location features |
| `hidden` | bool | Whether location is hidden |
| `requirements` | dict | Requirements to access |

### Registering NPCs

```python
def get_new_npcs(self) -> Dict[str, Dict]:
    """
    Return new NPCs added by this plugin.
    
    Returns:
        Dict mapping NPC IDs to NPC data
    """
    return {
        "master_blacksmith_bjorn": {
            "name": "Master Blacksmith Bjorn",
            "description": "A legendary dwarven blacksmith. His forge has crafted weapons for kings.",
            "npc_type": "blacksmith",
            "location": "capital_city",
            "services": ["craft", "repair", "enchant"],
            "can_train": ["Crafting", "Swordsmanship"],
            "training_cost": 300,
            "dialogue": {
                "greeting": {
                    "low_friendship": "\"State your business.\"",
                    "medium_friendship": "\"Back again?\"",
                    "high_friendship": "\"My friend!\""
                }
            }
        },
        "fairy_princess_aurora": {
            "name": "Princess Aurora of the Fae",
            "description": "A radiant fairy with wings like stained glass.",
            "npc_type": "quest_giver",
            "location": "fairy_grove",
            "services": ["fairy_blessing", "enchant"],
            "dialogue": {
                "greeting": {
                    "low_friendship": "\"A mortal! How delightful!\""
                }
            }
        }
    }
```

### NPC Property Reference

| Property | Type | Description |
|----------|------|-------------|
| `name` | str | Display name |
| `description` | str | NPC description |
| `npc_type` | str | blacksmith, trainer, merchant, quest_giver, mysterious |
| `location` | str | Location ID where NPC appears |
| `services` | list | Services offered |
| `can_train` | list | Skills this NPC can train |
| `training_cost` | int | Gold cost for training |
| `friendship_max` | int | Maximum friendship level |
| `requirements` | dict | Requirements to interact |

### Registering Quests

```python
def get_new_quests(self) -> Dict[str, Dict]:
    """
    Return new quests added by this plugin.
    
    Returns:
        Dict mapping quest IDs to quest data
    """
    return {
        "dragon_preparation": {
            "name": "Preparing for the Dragon",
            "description": "Prepare for battle with the Ancient Dragon.",
            "quest_type": "boss",
            "giver": "dragon_scholar_ignis",
            "location": "dragon_peak",
            "level_required": 20,
            "objectives": [
                {"type": "collect", "target": "dragon_scale", "required": 5,
                 "description": "Collect dragon scales"}
            ],
            "rewards": {
                "experience": 2000,
                "gold": 1500,
                "stat_bonus": {"strength": 2, "constitution": 2}
            }
        },
        "artifact_recovery": {
            "name": "The Arcane Artifact",
            "description": "Recover a powerful artifact from the Ancient Temple.",
            "quest_type": "side",
            "giver": "grand_magister_elara",
            "location": "capital_city",
            "level_required": 10,
            "objectives": [
                {"type": "reach", "target": "ancient_temple", "required": 1,
                 "description": "Reach the Ancient Temple"},
                {"type": "defeat_boss", "target": "forgotten_priest", "required": 1,
                 "description": "Defeat the Forgotten Priest"}
            ],
            "rewards": {
                "experience": 1500,
                "gold": 800,
                "items": ["magic_crystal"]
            }
        }
    }
```

### Quest Property Reference

| Property | Type | Description |
|----------|------|-------------|
| `name` | str | Quest display name |
| `description` | str | Quest description |
| `quest_type` | str | main, side, boss, daily |
| `giver` | str | NPC ID that gives the quest |
| `location` | str | Location where quest is available |
| `level_required` | int | Minimum level to accept |
| `objectives` | list | List of objective dictionaries |
| `rewards` | dict | Quest rewards |

### Objective Types

| Type | Target | Description |
|------|--------|-------------|
| `kill` | enemy_id | Defeat enemies |
| `collect` | item_id | Collect items |
| `reach` | location_id | Reach a location |
| `talk` | npc_id | Talk to an NPC |
| `defeat_boss` | boss_id | Defeat a boss |
| `use_item` | item_id | Use an item |

### Registering Crafting Recipes

```python
def register_recipes(self, crafting_manager) -> Dict[str, Dict]:
    """
    Register crafting recipes provided by this plugin.
    
    Returns:
        Dict mapping recipe IDs to recipe data
    """
    return {
        "thunder_hammer_recipe": {
            "name": "Thunder Hammer Recipe",
            "category": "weapons",
            "result": "thunder_hammer",
            "result_quantity": 1,
            "ingredients": {"iron_ingot": 5, "magic_crystal": 3, "enchanted_essence": 1},
            "skill_required": "Crafting",
            "skill_level": 15,
            "time": 4,
            "gold_cost": 500,
            "experience": 100
        },
        "mega_potion_recipe": {
            "name": "Mega Potion Recipe",
            "category": "alchemy",
            "result": "mega_potion",
            "result_quantity": 2,
            "ingredients": {"magic_crystal": 1, "enchanted_essence": 1},
            "skill_required": "Alchemy",
            "skill_level": 8,
            "time": 1,
            "gold_cost": 100,
            "experience": 40
        }
    }
```

### Recipe Property Reference

| Property | Type | Description |
|----------|------|-------------|
| `name` | str | Recipe display name |
| `category` | str | weapons, armor, alchemy, jewelry |
| `result` | str | Item ID produced |
| `result_quantity` | int | Number of items produced |
| `ingredients` | dict | Required materials with quantities |
| `skill_required` | str | Required crafting skill |
| `skill_level` | int | Required skill level |
| `time` | int | Crafting time in turns |
| `gold_cost` | int | Gold cost to craft |
| `experience` | int | Experience gained |

---

## Plugin Dependencies

### Dependency Types

| Type | Description | Behavior |
|------|-------------|----------|
| `dependencies` | Required plugins | Plugin fails to load if missing |
| `soft_dependencies` | Optional plugins | Load order adjusted if present |
| `conflicts` | Incompatible plugins | Plugin fails to load if conflict present |

### Declaring Dependencies

```python
info = PluginInfo(
    id="dragon_expansion",
    name="Dragon Expansion",
    
    # These plugins MUST be loaded before this one
    dependencies=["extended_world"],
    
    # These plugins will be loaded before if available
    soft_dependencies=["enhanced_combat", "extended_items"],
    
    # This plugin cannot run at the same time
    conflicts=["dragon_nerf"]
)
```

### Dependency Resolution

The plugin manager automatically:

1. Detects all plugins in the `plugins/` directory
2. Reads metadata from each plugin
3. Builds a dependency graph
4. Sorts plugins by priority and dependencies
5. Loads in the correct order
6. Reports errors for missing dependencies or conflicts

### Dependency Loading Order Example

```
Loading plugins with dependencies:

1. [SYSTEM] core_plugin         (priority: 0)
2. [CORE]   extended_world      (priority: 25)
3. [HIGH]   enhanced_combat     (priority: 50)
4. [NORMAL] extended_items      (priority: 100, soft-depends on enhanced_combat)
5. [NORMAL] extended_npcs       (priority: 100, depends on extended_world)
6. [NORMAL] dragon_expansion    (priority: 100, depends on extended_world)
```

---

## Plugin Styles

### Style 1: Class-Based (Recommended)

The class-based approach is recommended for complex plugins with lots of functionality:

```python
class MyComplexPlugin(Plugin):
    """A full-featured plugin using class inheritance."""
    
    def __init__(self):
        info = PluginInfo(
            id="my_complex_plugin",
            name="My Complex Plugin",
            version="1.0.0"
        )
        super().__init__(info)
        self._state = {}
        self._config = {}
    
    def on_load(self, game) -> bool:
        # Initialize state
        return True
    
    def on_unload(self, game) -> bool:
        # Cleanup
        return True
    
    def on_enable(self, game) -> bool:
        # Enable
        return True
    
    def on_disable(self, game) -> bool:
        # Disable
        return True
    
    def register_hooks(self, event_system):
        return {
            EventType.COMBAT_START: self._on_combat_start,
        }
    
    def register_commands(self, command_system):
        return {
            "my_command": {
                "handler": self._cmd_my_command,
                "help": "My command description"
            }
        }
    
    def register_items(self, item_registry):
        return {"my_item": {...}}

# Create instance
plugin = MyComplexPlugin()
```

### Style 2: Functional (PluginBuilder)

The functional approach using `PluginBuilder` is good for simple plugins:

```python
from systems.plugins import PluginBuilder, PluginPriority

def create_functional_plugin():
    """Create a plugin using the fluent builder API."""
    
    def on_load(game):
        print("Plugin loaded!")
        return True
    
    def on_combat_end(game, data):
        if data.get("result") == "victory":
            print("Victory!")
    
    def cmd_hello(game, args, context):
        return "Hello from functional plugin!"
    
    return (PluginBuilder("functional_plugin")
        .name("Functional Plugin")
        .version("1.0.0")
        .author("Developer")
        .description("A plugin built with the fluent API")
        .priority(PluginPriority.LOW)
        .tags("functional", "example")
        .on_load(on_load)
        .hook(EventType.COMBAT_END, on_combat_end)
        .command("hello", cmd_hello, "Say hello")
        .build())

plugin = create_functional_plugin()
```

### Style 3: Minimal

For the simplest possible plugin:

```python
class MinimalPlugin(Plugin):
    """The simplest possible plugin."""
    
    def __init__(self):
        super().__init__(PluginInfo(
            id="minimal",
            name="Minimal Plugin",
            version="1.0.0"
        ))
    
    def on_load(self, game) -> bool:
        return True
    
    def on_unload(self, game) -> bool:
        return True
    
    def on_enable(self, game) -> bool:
        return True
    
    def on_disable(self, game) -> bool:
        return True

plugin = MinimalPlugin()
```

---

## API Reference

### PluginInfo

```python
@dataclass
class PluginInfo:
    id: str
    name: str
    version: str = "1.0.0"
    author: str = "Unknown"
    description: str = ""
    dependencies: List[str] = field(default_factory=list)
    soft_dependencies: List[str] = field(default_factory=list)
    conflicts: List[str] = field(default_factory=list)
    priority: PluginPriority = PluginPriority.NORMAL
    tags: List[str] = field(default_factory=list)
    min_game_version: str = "1.0.0"
    max_game_version: str = ""
    
    def to_dict(self) -> Dict: ...
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'PluginInfo': ...
```

### Plugin (Abstract Base Class)

```python
class Plugin(ABC):
    def __init__(self, info: PluginInfo):
        self.info = info
        self.state = PluginState.DISCOVERED
        self._enabled = False
        self._config: Dict[str, Any] = {}
        self._hooks: Dict[EventType, List[Callable]] = defaultdict(list)
        self._commands: Dict[str, Callable] = {}
    
    @property
    def id(self) -> str: ...
    
    @property
    def enabled(self) -> bool: ...
    
    @abstractmethod
    def on_load(self, game: Any) -> bool: ...
    
    @abstractmethod
    def on_unload(self, game: Any) -> bool: ...
    
    @abstractmethod
    def on_enable(self, game: Any) -> bool: ...
    
    @abstractmethod
    def on_disable(self, game: Any) -> bool: ...
    
    def register_hook(self, event_type: EventType, callback: Callable): ...
    
    def register_command(self, name: str, callback: Callable): ...
    
    def get_config(self, key: str, default: Any = None) -> Any: ...
    
    def set_config(self, key: str, value: Any): ...
```

### PluginManager

```python
class PluginManager:
    def __init__(self, game: Any): ...
    
    def load_all_plugins(self) -> Tuple[int, int]:
        """Load all plugins from the plugins directory."""
    
    def unload_plugin(self, plugin_id: str) -> bool:
        """Unload a specific plugin."""
    
    def get_plugin(self, plugin_id: str) -> Optional[Plugin]:
        """Get a plugin by ID."""
    
    def emit_event(self, event_type: EventType, data: Dict):
        """Emit an event to all registered handlers."""
    
    def execute_command(self, command: str, *args, **kwargs) -> Tuple[bool, Any]:
        """Execute a registered command."""
    
    def register_content(self, content_type: str, content_id: str, content: Any):
        """Register content from a plugin."""
    
    def get_content(self, content_type: str, content_id: str) -> Optional[Any]:
        """Get registered content."""
    
    def get_all_content(self, content_type: str) -> Dict[str, Any]:
        """Get all content of a type."""
```

### PluginBuilder

```python
class PluginBuilder:
    def __init__(self, plugin_id: str): ...
    
    def name(self, name: str) -> 'PluginBuilder': ...
    def version(self, version: str) -> 'PluginBuilder': ...
    def author(self, author: str) -> 'PluginBuilder': ...
    def description(self, description: str) -> 'PluginBuilder': ...
    def depends(self, *plugin_ids: str) -> 'PluginBuilder': ...
    def conflicts_with(self, *plugin_ids: str) -> 'PluginBuilder': ...
    def priority(self, priority: PluginPriority) -> 'PluginBuilder': ...
    def tags(self, *tags: str) -> 'PluginBuilder': ...
    def on_load(self, callback: Callable) -> 'PluginBuilder': ...
    def on_unload(self, callback: Callable) -> 'PluginBuilder': ...
    def on_enable(self, callback: Callable) -> 'PluginBuilder': ...
    def on_disable(self, callback: Callable) -> 'PluginBuilder': ...
    def hook(self, event_type: EventType, callback: Callable) -> 'PluginBuilder': ...
    def command(self, name: str, callback: Callable, help_text: str = "") -> 'PluginBuilder': ...
    def content(self, content_type: str, content: Dict) -> 'PluginBuilder': ...
    
    def build(self) -> FunctionalPlugin:
        """Build and return the plugin."""
```

### PluginPriority

```python
class PluginPriority(Enum):
    SYSTEM = 0
    CORE = 25
    HIGH = 50
    NORMAL = 100
    LOW = 150
    OPTIONAL = 200
```

### PluginState

```python
class PluginState(Enum):
    UNDISCOVERED = auto()
    DISCOVERED = auto()
    LOADING = auto()
    RESOLVING = auto()
    INITIALIZING = auto()
    ENABLED = auto()
    DISABLED = auto()
    ERROR = auto()
    UNLOADING = auto()
    PENDING_RELOAD = auto()
    HOT_RELOADING = auto()
```

---

## Best Practices

### 1. Plugin Structure

- Keep plugins focused on a single purpose
- Use descriptive IDs and names
- Include comprehensive metadata
- Document your plugin with docstrings

### 2. Error Handling

```python
def on_load(self, game) -> bool:
    try:
        # Initialize resources
        self._initialize_data()
        return True
    except Exception as e:
        print(f"[{self.info.name}] Error loading: {e}")
        return False
```

### 3. Configuration Management

```python
def on_load(self, game) -> bool:
    # Set sensible defaults
    self._config = {
        "enabled": True,
        "bonus_amount": 100,
        "debug_mode": False
    }
    
    # Load saved config if available
    if hasattr(game, 'get_plugin_config'):
        saved = game.get_plugin_config(self.id)
        if saved:
            self._config.update(saved)
    
    return True
```

### 4. Resource Cleanup

```python
def on_unload(self, game) -> bool:
    # Save state before unloading
    if hasattr(game, 'save_plugin_config'):
        game.save_plugin_config(self.id, self._config)
    
    # Release resources
    self._state.clear()
    
    return True
```

### 5. Event Handler Efficiency

```python
def _on_combat_turn(self, game, data):
    # Check if we need to process
    if not self._config.get("enabled", True):
        return
    
    # Do minimal work in frequent events
    turn = data.get("turn_number", 0)
    
    # Only process every 3 turns
    if turn % 3 != 0:
        return
    
    # Process the event
    self._process_turn(game, data)
```

### 6. Command Design

- Provide clear help text
- Use consistent argument parsing
- Return helpful error messages
- Include usage examples

```python
def _cmd_my_command(self, game, args, context) -> str:
    """A well-designed command handler."""
    if not args:
        return (
            "My Command Help:\n"
            "Usage: /my_command <action> [value]\n"
            "Actions: enable, disable, show\n"
            "Example: /my_command enable 100"
        )
    
    action = args[0].lower()
    
    if action == "enable":
        if len(args) < 2:
            return "Error: Missing value. Usage: /my_command enable <value>"
        try:
            value = int(args[1])
            self._config["value"] = value
            return f"Enabled with value: {value}"
        except ValueError:
            return f"Error: Invalid number '{args[1]}'"
    
    elif action == "disable":
        self._config["enabled"] = False
        return "Disabled."
    
    elif action == "show":
        return f"Current config: {self._config}"
    
    return f"Unknown action: {action}"
```

### 7. Content Registration

- Use consistent naming conventions
- Provide complete data structures
- Balance content appropriately
- Consider progression curves

### 8. Dependency Management

- Only require dependencies that are truly necessary
- Use soft dependencies for optional integration
- Document dependency requirements clearly
- Test with and without soft dependencies

### 9. Testing Your Plugin

```python
def on_enable(self, game) -> bool:
    # Test game state
    if not hasattr(game, 'player'):
        print(f"[{self.info.name}] Warning: Player system not available")
    
    if not hasattr(game, 'plugin_manager'):
        print(f"[{self.info.name}] Error: Plugin manager not available")
        return False
    
    # Test dependencies
    for dep_id in self.info.dependencies:
        if not game.plugin_manager.get_plugin(dep_id):
            print(f"[{self.info.name}] Error: Missing dependency {dep_id}")
            return False
    
    return True
```

---

## Examples

### Complete Combat Enhancement Plugin

```python
"""
Enhanced Combat Plugin - Advanced Combat Features
Demonstrates event priorities, combat mechanics, abilities, and content provision.
"""

from systems.plugins import Plugin, PluginInfo, PluginPriority, EventType
from typing import Dict, Any


class EnhancedCombatPlugin(Plugin):
    """Enhanced combat plugin with advanced features."""
    
    def __init__(self):
        info = PluginInfo(
            id="enhanced_combat",
            name="Enhanced Combat",
            version="2.0.0",
            author="YSNRFD",
            description="Advanced combat mechanics including combo systems, "
                       "variety bonuses, and milestone abilities.",
            priority=PluginPriority.HIGH,
            tags=["combat", "mechanics", "abilities"]
        )
        super().__init__(info)
        self._combat_stats: Dict[str, Any] = {}
        self._config: Dict[str, Any] = {}
    
    def on_load(self, game) -> bool:
        print("[Enhanced Combat] Loading combat enhancements...")
        
        self._config = {
            "variety_bonus_percent": 10,
            "combo_multiplier": 1.1,
            "enable_combo_system": True
        }
        
        self._combat_stats = {
            "combats_started": 0,
            "combats_won": 0,
            "critical_hits": 0,
            "max_combo": 0
        }
        
        return True
    
    def on_unload(self, game) -> bool:
        print("[Enhanced Combat] Unloading...")
        return True
    
    def on_enable(self, game) -> bool:
        print("[Enhanced Combat] Enabled!")
        return True
    
    def on_disable(self, game) -> bool:
        return True
    
    def register_hooks(self, event_system):
        return {
            EventType.COMBAT_START: self._on_combat_start,
            EventType.COMBAT_END: self._on_combat_end,
            EventType.COMBAT_TURN: self._on_combat_turn,
            EventType.PLAYER_LEVEL_UP: self._on_level_up,
        }
    
    def _on_combat_start(self, game, data):
        self._combat_stats["combats_started"] += 1
        player = data.get("player")
        enemies = data.get("enemies", [])
        
        if self._config.get("enable_combo_system") and player:
            player._enhanced_combo = 0
        
        if enemies:
            unique_types = len(set(e.name for e in enemies))
            if unique_types >= 3:
                print(f"⚔️ Variety Bonus: +{self._config['variety_bonus_percent']}% experience!")
    
    def _on_combat_end(self, game, data):
        result = data.get("result")
        if result == "victory":
            self._combat_stats["combats_won"] += 1
    
    def _on_combat_turn(self, game, data):
        player = data.get("player")
        if not player or not self._config.get("enable_combo_system"):
            return
        
        current_combo = getattr(player, '_enhanced_combo', 0) + 1
        player._enhanced_combo = current_combo
        
        if current_combo > 0 and current_combo % 3 == 0:
            print(f"🔥 {current_combo}-hit combo!")
    
    def _on_level_up(self, game, data):
        level = data.get("level", 1)
        if level % 5 == 0:
            print(f"🎯 Milestone Level {level}!")
    
    def register_commands(self, command_system):
        return {
            "combat_stats": {
                "handler": self._cmd_stats,
                "help": "Show enhanced combat statistics",
                "category": "stats"
            }
        }
    
    def _cmd_stats(self, game, args, context) -> str:
        stats = self._combat_stats
        return (
            "Enhanced Combat Statistics:\n"
            f"  Combats Started: {stats.get('combats_started', 0)}\n"
            f"  Victories: {stats.get('combats_won', 0)}\n"
            f"  Max Combo: {stats.get('max_combo', 0)}"
        )


plugin = EnhancedCombatPlugin()
```

---

## Troubleshooting

### Plugin Not Loading

**Symptoms**: Plugin file exists but doesn't appear in game

**Solutions**:
1. Check that the file is in the correct `plugins/` directory
2. Ensure the file doesn't start with underscore (`_plugin.py`)
3. Verify the `plugin` variable is defined at module level
4. Check for Python syntax errors in the file
5. Look for error messages in the game console

### Missing Dependencies Error

**Error**: `Missing dependency: plugin_id requires other_plugin`

**Solutions**:
1. Install the required plugin
2. Move the dependency to `soft_dependencies` if optional
3. Check plugin IDs match exactly (case-sensitive)

### Plugin Conflicts

**Error**: `Plugin conflict: plugin_a conflicts with plugin_b`

**Solutions**:
1. Remove one of the conflicting plugins
2. Contact plugin authors for compatibility patches
3. Check if plugins provide similar functionality

### Commands Not Working

**Symptoms**: Commands registered but don't respond

**Solutions**:
1. Verify command format: `/command_name` (with slash)
2. Check command handler signature: `def handler(self, game, args, context)`
3. Ensure commands are returned from `register_commands()`
4. Test with `/help` to see if command is listed

### Events Not Firing

**Symptoms**: Event hooks registered but never called

**Solutions**:
1. Verify event types match exactly
2. Check that `register_hooks()` returns the correct dictionary
3. Ensure event is being emitted by the game
4. Test with print statements in handlers

### Content Not Appearing

**Symptoms**: Items/NPCs/locations registered but not in game

**Solutions**:
1. Verify registration method returns correct dictionary
2. Check content IDs are unique
3. Ensure game systems are accessing registered content
4. Test with debug commands to list content

### Performance Issues

**Symptoms**: Game slows down after plugin install

**Solutions**:
1. Optimize event handlers (reduce work in frequent events)
2. Cache computed values
3. Use configuration to disable expensive features
4. Profile plugin code to find bottlenecks

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2026-01-05 | Initial plugin system release |
| 1.1.0 | 2026-01-09 | Added PluginBuilder fluent API |
| 1.2.0 | 2026-01-13 | Added soft dependencies support |
| 2.0.0 | 2026-02-20 | Complete rewrite with async support |

---

## Contributing

To contribute plugins to the Legends of Eldoria ecosystem:

1. Follow the naming conventions
2. Include comprehensive metadata
3. Test with various game configurations
4. Document all commands and features
5. Provide example configurations
6. Handle errors gracefully

---

## Support

For questions or issues with plugin development:

1. Check this documentation
2. Review existing plugin examples
3. Examine the base_plugin_template.py
4. Test with minimal plugins first

---

**This documentation covers the complete plugin development experience for Legends of Eldoria. Happy modding!**

---

<div align="center">

**Legends of Eldoria Plugin System** 🔌

Made with ❤️ by [YSNRFD](https://github.com/ysnrfd)

*Happy Plugin Development!*

</div>

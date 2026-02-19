# Legends of Eldoria - Plugin Development Guide

## Table of Contents

1. [Overview](#overview)
2. [Installation](#installation)
3. [Quick Start](#quick-start)
4. [Plugin Styles](#plugin-styles)
5. [Plugin Structure](#plugin-structure)
6. [Plugin Interfaces](#plugin-interfaces)
7. [Plugin Metadata](#plugin-metadata)
8. [Lifecycle Management](#lifecycle-management)
9. [Configuration System](#configuration-system)
10. [Hot Reload Support](#hot-reload-support)
11. [Event System](#event-system)
12. [Command System](#command-system)
13. [Content Registry](#content-registry)
14. [Event Types Reference](#event-types-reference)
15. [Content Types Reference](#content-types-reference)
16. [Enum Values Reference](#enum-values-reference)
17. [Advanced Features](#advanced-features)
18. [Plugin Builder API](#plugin-builder-api)
19. [Decorator-Based Plugins](#decorator-based-plugins)
20. [JSON/YAML Plugins](#jsonyaml-plugins)
21. [Debug Commands](#debug-commands)
22. [Best Practices](#best-practices)
23. [Examples](#examples)
24. [Troubleshooting](#troubleshooting)
25. [File Structure](#file-structure)
26. [API Reference](#api-reference)
27. [Contributing](#contributing)
28. [Changelog](#changelog)

---

## Overview

The Legends of Eldoria plugin system is a **fully dynamic, extensible architecture** supporting multiple plugin styles and formats. This comprehensive system allows you to extend the game with new content, features, and mechanics without modifying the core game code.

### What Plugins Can Add

- **Items**: Weapons, armor, consumables, accessories, materials
- **Enemies**: New enemy types with custom abilities and drops
- **Locations**: Towns, dungeons, forests, temples, and special areas
- **NPCs**: Merchants, trainers, quest givers, and special characters
- **Quests**: Main story, side quests, boss fights, daily quests
- **Crafting Recipes**: New crafting formulas
- **Custom Commands**: Slash commands for players
- **Event Hooks**: React to game events in real-time
- **World Events**: Dynamic events that affect gameplay
- **Custom Content Types**: Any content type you define

### Key Features

| Feature | Description |
|---------|-------------|
| **Multiple Plugin Styles** | Class-based, Functional, Decorator-based, Data-only |
| **Protocol Interfaces** | Duck typing support for maximum flexibility |
| **Hot Reload** | Live plugin updates without game restart |
| **Configuration System** | Schema validation, type checking, runtime changes |
| **Event Priorities** | Control handler execution order |
| **Command Categories** | Organized commands with permissions |
| **Dynamic Content Registry** | Register any content type at runtime |
| **Dependency Management** | Automatic dependency resolution |
| **Plugin Discovery** | Auto-discovery from multiple sources |

---

## Installation

### Creating a New Plugin

1. Navigate to the `plugins/` directory
2. Create a new Python file (e.g., `my_plugin.py`)
3. Copy the structure from `base_plugin_template.py` or start from scratch
4. Implement the required methods
5. Place the file in the plugins folder - it will auto-load on game start

### Plugin Loading Order

Plugins load in order of their `priority` value (lower = earlier):

| Priority Range | Type | Description |
|----------------|------|-------------|
| 0-25 | SYSTEM/CORE | Core system plugins |
| 26-50 | HIGH | High priority content |
| 51-100 | NORMAL | Standard plugins (default) |
| 101-150 | LOW | Low priority additions |
| 151+ | OPTIONAL | Optional extras |

```python
from systems.plugins import PluginPriority

PluginInfo(
    priority=PluginPriority.NORMAL.value  # 100
)
```

---

## Quick Start

### Minimal Plugin Example

```python
from systems.plugins import PluginBase, PluginInfo

class MyFirstPlugin(PluginBase):
    @property
    def info(self) -> PluginInfo:
        return PluginInfo(
            id="my_first_plugin",
            name="My First Plugin",
            version="1.0.0",
            author="Your Name",
            description="My first plugin for Legends of Eldoria!"
        )
    
    def on_load(self, game):
        print("My First Plugin loaded successfully!")
    
    def on_unload(self, game):
        print("My First Plugin unloaded.")

# Required: Create the plugin instance
plugin = MyFirstPlugin()
```

### Plugin with Content

```python
from systems.plugins import (
    PluginBase, PluginInfo, PluginType, PluginPriority,
    IContentProvider, IHotReloadablePlugin
)

class ContentPlugin(PluginBase, IContentProvider, IHotReloadablePlugin):
    
    @property
    def info(self) -> PluginInfo:
        return PluginInfo(
            id="content_plugin",
            name="Content Plugin",
            version="1.0.0",
            author="Your Name",
            description="A plugin with custom content",
            priority=PluginPriority.NORMAL.value,
            plugin_type=PluginType.CLASS,
            supports_hot_reload=True,
            tags=["content", "items"]
        )
    
    def on_load(self, game):
        print("Content Plugin loading...")
        self._config = {}
    
    def on_unload(self, game):
        print("Content Plugin unloading...")
    
    # IContentProvider implementation
    def get_content_types(self) -> list:
        return ["items", "locations"]
    
    def get_content(self, content_type: str) -> dict:
        if content_type == "items":
            return self._get_items()
        elif content_type == "locations":
            return self._get_locations()
        return {}
    
    def _get_items(self) -> dict:
        return {
            "my_sword": {
                "name": "Blade of Power",
                "item_type": "weapon",
                "rarity": "Epic",
                "damage_min": 20,
                "damage_max": 35
            }
        }
    
    def _get_locations(self) -> dict:
        return {
            "my_dungeon": {
                "name": "Dark Cavern",
                "location_type": "dungeon",
                "level_range": [10, 20]
            }
        }
    
    # IHotReloadablePlugin implementation
    def on_before_reload(self, game) -> dict:
        return {"config": self._config}
    
    def on_after_reload(self, game, state: dict) -> None:
        self._config = state.get("config", {})

plugin = ContentPlugin()
```

---

## Plugin Styles

The dynamic plugin system supports multiple development styles:

### Style 1: Class-Based (Recommended for Complex Plugins)

```python
from systems.plugins import PluginBase, PluginInfo

class ComplexPlugin(PluginBase):
    @property
    def info(self) -> PluginInfo:
        return PluginInfo(
            id="complex_plugin",
            name="Complex Plugin",
            version="1.0.0",
            author="Developer",
            description="A complex plugin with full features"
        )
    
    def on_load(self, game):
        # Initialize state
        self._state = {"counter": 0}
    
    def on_unload(self, game):
        # Cleanup
        pass
    
    def register_hooks(self, event_system):
        return {
            EventType.COMBAT_END: self._on_combat_end
        }
    
    def register_commands(self, command_system):
        return {
            "mycommand": {
                "handler": self._cmd_handler,
                "help": "My custom command",
                "category": "custom"
            }
        }

plugin = ComplexPlugin()
```

### Style 2: Functional (Recommended for Simple Plugins)

```python
from systems.plugins import PluginBuilder, PluginPriority, EventType

def on_load(game):
    print("Functional plugin loaded!")

def on_combat_end(data):
    if data.get("result") == "victory":
        print("Victory!")

def cmd_hello(game, args, context):
    return "Hello from functional plugin!"

plugin = (PluginBuilder("functional_plugin")
    .name("Functional Plugin")
    .version("1.0.0")
    .author("Developer")
    .description("A plugin built with fluent API")
    .priority(PluginPriority.LOW.value)
    .tags("functional", "example")
    .supports_hot_reload(True)
    .on_load(on_load)
    .hook(EventType.COMBAT_END, on_combat_end)
    .command("hello", cmd_hello, "Say hello")
    .content("items", {"my_item": {"name": "My Item"}})
    .build())
```

### Style 3: Decorator-Based (Recommended for Handlers)

```python
from systems.plugins import plugin, hook, command, define_plugin

@plugin({
    "id": "decorator_plugin",
    "name": "Decorator Plugin",
    "version": "1.0.0",
    "author": "Developer",
    "description": "Plugin using decorators"
})
class DecoratorPlugin:
    
    @hook(EventType.COMBAT_START)
    def on_combat_start(self, data):
        print("Combat starting!")
    
    @command("dec_test", "Test command")
    def test_command(self, game, args):
        return "Decorator plugin test!"
```

### Style 4: Data-Only (JSON/YAML)

```json
{
    "info": {
        "id": "data_plugin",
        "name": "Data Plugin",
        "version": "1.0.0",
        "author": "Developer",
        "description": "Data-only plugin",
        "plugin_type": "data"
    },
    "items": {
        "my_sword": {
            "name": "Data Sword",
            "item_type": "weapon",
            "rarity": "Rare"
        }
    }
}
```

---

## Plugin Structure

### Required Components

Every plugin **must** implement:

```python
from systems.plugins import PluginBase, PluginInfo

class MyPlugin(PluginBase):
    @property
    def info(self) -> PluginInfo:
        """Return plugin metadata - REQUIRED"""
        return PluginInfo(
            id="unique_plugin_id",    # Lowercase, underscores only
            name="Display Name",      # Human-readable name
            version="1.0.0",          # Semantic versioning
            author="Author Name",     # Your name or organization
            description="What your plugin does"
        )
    
    def on_load(self, game):
        """Called when plugin is loaded - REQUIRED"""
        pass
    
    def on_unload(self, game):
        """Called when plugin is unloaded - REQUIRED"""
        pass

# REQUIRED: Create the plugin instance
plugin = MyPlugin()
```

### Optional Methods

| Method | Purpose | Return Type |
|--------|---------|-------------|
| `on_enable(game)` | Called when plugin is enabled | None |
| `on_disable(game)` | Called when plugin is disabled | None |
| `on_config_changed(game, key, value)` | Called when config changes | None |
| `register_hooks(event_system)` | Register event callbacks | `Dict[EventType, Callable]` |
| `register_commands(command_system)` | Register slash commands | `Dict[str, Callable]` |
| `register_content(content_registry)` | Register custom content | `Dict[str, Dict]` |
| `get_content_types()` | Return supported content types | `List[str]` |
| `get_content(content_type)` | Return content for type | `Dict[str, Any]` |
| `get_config()` | Get current configuration | `Dict[str, Any]` |
| `set_config(config)` | Set configuration | None |
| `validate_config(config)` | Validate configuration | `Tuple[bool, str]` |
| `on_before_reload(game)` | Save state before reload | `Dict[str, Any]` |
| `on_after_reload(game, state)` | Restore state after reload | None |

---

## Plugin Interfaces

The dynamic plugin system uses **Protocol interfaces** for duck typing. You can implement any combination of these interfaces:

### IPlugin (Base Interface)

```python
from systems.plugins import IPlugin

class MyPlugin(IPlugin):
    @property
    def info(self) -> PluginInfo:
        return PluginInfo(...)
    
    def on_load(self, game):
        pass
    
    def on_unload(self, game):
        pass
```

### IContentProvider

For plugins that provide game content:

```python
from systems.plugins import IContentProvider

class ContentPlugin(IContentProvider):
    def get_content_types(self) -> List[str]:
        return ["items", "enemies", "locations"]
    
    def get_content(self, content_type: str) -> Dict[str, Any]:
        if content_type == "items":
            return {"item_1": {"name": "Item One"}}
        return {}
```

### IHotReloadablePlugin

For plugins that support hot reload:

```python
from systems.plugins import IHotReloadablePlugin

class HotReloadPlugin(IHotReloadablePlugin):
    def on_before_reload(self, game) -> Dict[str, Any]:
        # Save state before reload
        return {"counter": self._counter}
    
    def on_after_reload(self, game, state: Dict[str, Any]) -> None:
        # Restore state after reload
        self._counter = state.get("counter", 0)
```

### IConfigurablePlugin

For plugins with configuration:

```python
from systems.plugins import IConfigurablePlugin

class ConfigurablePlugin(IConfigurablePlugin):
    def get_config(self) -> Dict[str, Any]:
        return self._config.copy()
    
    def set_config(self, config: Dict[str, Any]) -> None:
        self._config = config.copy()
    
    def validate_config(self, config: Dict[str, Any]) -> Tuple[bool, str]:
        if "max_value" in config and config["max_value"] < 0:
            return False, "max_value must be positive"
        return True, ""
```

### IEventSubscriber

For plugins that subscribe to events:

```python
from systems.plugins import IEventSubscriber, EventType

class EventPlugin(IEventSubscriber):
    def get_event_subscriptions(self) -> Dict[EventType, Callable]:
        return {
            EventType.COMBAT_END: self._on_combat_end,
            EventType.PLAYER_LEVEL_UP: self._on_level_up
        }
```

### ICommandProvider

For plugins that provide commands:

```python
from systems.plugins import ICommandProvider

class CommandPlugin(ICommandProvider):
    def get_commands(self) -> Dict[str, Callable]:
        return {
            "mycommand": self._cmd_handler
        }
```

---

## Plugin Metadata

### Complete PluginInfo Fields

```python
from systems.plugins import PluginInfo, PluginType, PluginPriority

PluginInfo(
    # === Required Fields ===
    id="plugin_id",              # Unique identifier (lowercase, underscores)
    name="Plugin Name",          # Display name
    version="1.0.0",             # Semantic version
    author="Author",             # Author name
    description="Description",   # Brief description
    
    # === Dependencies ===
    dependencies=["required_plugin"],    # Required dependencies
    soft_dependencies=["optional_plugin"], # Optional dependencies
    conflicts=["incompatible_plugin"],   # Incompatible plugins
    provides=["feature_1", "feature_2"], # Features this plugin provides
    
    # === Loading Configuration ===
    priority=PluginPriority.NORMAL.value,  # Load order priority
    plugin_type=PluginType.CLASS,          # Plugin type
    
    # === Version Compatibility ===
    min_game_version="1.0.0",    # Minimum game version
    max_game_version="2.0.0",    # Maximum game version (empty = any)
    api_version="2.0",           # Plugin API version
    
    # === Configuration ===
    configurable=True,           # Has configuration
    config_schema={              # Configuration schema
        "max_items": {
            "type": "integer",
            "default": 100,
            "min": 1,
            "max": 1000
        },
        "debug_mode": {
            "type": "boolean",
            "default": False
        },
        "welcome_message": {
            "type": "string",
            "default": "Welcome!"
        }
    },
    default_config={             # Default configuration values
        "max_items": 100,
        "debug_mode": False,
        "welcome_message": "Welcome!"
    },
    
    # === Hot Reload ===
    supports_hot_reload=True,    # Support live reloading
    reload_priority=50,          # Priority for reload order
    
    # === Metadata ===
    tags=["content", "items"],   # Tags for categorization
    homepage="https://...",      # Plugin homepage
    license="MIT",               # License
    repository="https://...",    # Source repository
    custom={                     # Custom metadata
        "category": "content",
        "min_level": 5
    }
)
```

### Plugin Types

| Type | Description | Use Case |
|------|-------------|----------|
| `CLASS` | Python class-based plugin | Complex plugins with state |
| `FUNCTIONAL` | Function-based plugin | Simple plugins without classes |
| `DATA` | JSON/YAML data plugin | Content-only plugins |
| `HYBRID` | Mixed structure | Complex data + logic |
| `MODULE` | Full Python module | Package-style plugins |
| `ARCHIVE` | Zip/package plugin | Distributed plugins |

---

## Lifecycle Management

### Plugin States

```
UNDISCOVERED → DISCOVERED → LOADING → RESOLVING → INITIALIZING → ENABLED
                                    ↓                              ↓
                                  ERROR ← ← ← ← ← ← ← ← ← DISABLED
                                    ↓
                              UNLOADING → PENDING_RELOAD → HOT_RELOADING
```

### Lifecycle Methods

```python
class LifecyclePlugin(PluginBase):
    
    def on_load(self, game):
        """Called when plugin is first loaded into memory."""
        print("Plugin loading...")
        self._state = {}
    
    def on_enable(self, game):
        """Called when plugin is enabled (after load or after disable)."""
        print("Plugin enabled!")
    
    def on_disable(self, game):
        """Called when plugin is disabled (before unload or manual disable)."""
        print("Plugin disabled.")
    
    def on_unload(self, game):
        """Called when plugin is being unloaded from memory."""
        print("Plugin unloading...")
        # Cleanup resources
    
    def on_config_changed(self, game, key: str, value: Any):
        """Called when a configuration value changes."""
        print(f"Config changed: {key} = {value}")
```

---

## Configuration System

### Defining Configuration Schema

```python
PluginInfo(
    configurable=True,
    config_schema={
        # Integer with bounds
        "max_enemies": {
            "type": "integer",
            "default": 10,
            "min": 1,
            "max": 50
        },
        
        # Float with bounds
        "damage_multiplier": {
            "type": "number",
            "default": 1.0,
            "min": 0.1,
            "max": 5.0
        },
        
        # Boolean
        "debug_mode": {
            "type": "boolean",
            "default": False
        },
        
        # String
        "welcome_message": {
            "type": "string",
            "default": "Welcome, adventurer!"
        },
        
        # Enumeration
        "difficulty": {
            "type": "enum",
            "default": "normal",
            "values": ["easy", "normal", "hard", "nightmare"]
        }
    },
    default_config={
        "max_enemies": 10,
        "damage_multiplier": 1.0,
        "debug_mode": False,
        "welcome_message": "Welcome, adventurer!",
        "difficulty": "normal"
    }
)
```

### Using Configuration

```python
class ConfigurablePlugin(PluginBase):
    
    def on_load(self, game):
        self._config = self.info.default_config.copy()
    
    def get_config(self) -> Dict[str, Any]:
        return self._config.copy()
    
    def set_config(self, config: Dict[str, Any]) -> None:
        valid, msg = self.validate_config(config)
        if valid:
            self._config = {**self._config, **config}
    
    def validate_config(self, config: Dict[str, Any]) -> Tuple[bool, str]:
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
            
            elif spec["type"] == "number":
                if not isinstance(value, (int, float)):
                    return False, f"{key} must be a number"
            
            elif spec["type"] == "boolean":
                if not isinstance(value, bool):
                    return False, f"{key} must be a boolean"
            
            elif spec["type"] == "string":
                if not isinstance(value, str):
                    return False, f"{key} must be a string"
        
        return True, ""
    
    def on_config_changed(self, game, key: str, value: Any):
        print(f"Configuration updated: {key} = {value}")
        # React to config change
```

---

## Hot Reload Support

### Implementing Hot Reload

```python
from systems.plugins import PluginBase, PluginInfo, IHotReloadablePlugin

class HotReloadPlugin(PluginBase, IHotReloadablePlugin):
    
    _state: Dict[str, Any] = {}
    
    @property
    def info(self) -> PluginInfo:
        return PluginInfo(
            id="hot_reload_plugin",
            name="Hot Reload Plugin",
            version="1.0.0",
            author="Developer",
            description="Plugin with hot reload support",
            supports_hot_reload=True
        )
    
    def on_load(self, game):
        print("Plugin loaded!")
        self._state = {"counter": 0, "events_processed": 0}
    
    def on_before_reload(self, game) -> Dict[str, Any]:
        """Save state before hot reload."""
        print("Saving state before reload...")
        return {
            "state": self._state.copy(),
            "timestamp": time.time()
        }
    
    def on_after_reload(self, game, state: Dict[str, Any]) -> None:
        """Restore state after hot reload."""
        print("Restoring state after reload...")
        self._state = state.get("state", {})
        self._state["reloads"] = self._state.get("reloads", 0) + 1
        print(f"Reload count: {self._state['reloads']}")
```

### Hot Reload Commands

```
/reload <plugin_id>     # Reload a specific plugin
/hot_reload             # Toggle hot reload monitoring
```

---

## Event System

### Event Priorities

Events handlers execute in priority order (lower value = executes first):

| Priority | Value | Description |
|----------|-------|-------------|
| `HIGHEST` | 0 | First to execute |
| `HIGH` | 25 | High priority |
| `NORMAL` | 50 | Default priority |
| `LOW` | 75 | Low priority |
| `LOWEST` | 100 | Last normal handler |
| `MONITOR` | 200 | For monitoring only |

### Registering Event Hooks

```python
from systems.plugins import EventType, EventPriority

def register_hooks(self, event_system):
    return {
        # Simple handler
        EventType.COMBAT_START: self._on_combat_start,
        
        # With priority (tuple format)
        EventType.COMBAT_END: (self._on_combat_end, EventPriority.HIGH),
        
        # Multiple handlers for same event
        EventType.PLAYER_LEVEL_UP: (self._on_level_up, EventPriority.NORMAL),
    }

def _on_combat_start(self, data):
    player = data.get("player")
    enemies = data.get("enemies", [])
    print(f"Combat started with {len(enemies)} enemies!")

def _on_combat_end(self, data):
    result = data.get("result")
    if result == "victory":
        print("Victory!")
```

### Event Handler Signature

```python
def event_handler(self, data: Dict[str, Any]) -> Optional[Any]:
    """
    Event handler signature.
    
    Args:
        data: Event data dictionary (varies by event type)
    
    Returns:
        Optional result (can modify event propagation)
    """
    player = data.get("player")
    return None  # Return value collected by event system
```

### Event Middleware

```python
def setup_event_middleware(self, event_system):
    # Add middleware that processes all events
    event_system.add_middleware(self._event_middleware)

def _event_middleware(self, event_type, data):
    """Process all events before handlers."""
    print(f"Event: {event_type}")
    # Can modify data
    data["timestamp"] = time.time()
    return data  # Return modified data
```

### Stopping Event Propagation

```python
def _on_combat_start(self, data):
    # Stop other handlers from processing
    # self.event_system.stop_propagation()
    pass
```

---

## Command System

### Registering Commands

```python
def register_commands(self, command_system):
    return {
        # Simple format
        "mycommand": self._cmd_simple,
        
        # Full format with metadata
        "advanced": {
            "handler": self._cmd_advanced,
            "help": "Advanced command with options",
            "usage": "/advanced <option> [value]",
            "category": "custom",
            "aliases": ["adv", "a"]
        }
    }

def _cmd_simple(self, game, args, context):
    """Simple command handler."""
    return "Simple command executed!"

def _cmd_advanced(self, game, args, context):
    """Advanced command with arguments."""
    if not args:
        return "Usage: /advanced <option> [value]"
    
    option = args[0]
    value = args[1] if len(args) > 1 else None
    
    return f"Option: {option}, Value: {value}"
```

### Command Categories

| Category | Description |
|----------|-------------|
| `system` | System commands |
| `debug` | Debug/cheat commands |
| `info` | Information commands |
| `stats` | Statistics commands |
| `custom` | Custom commands |

### Command Registration Format

```python
{
    "handler": Callable,        # Required: Command handler
    "help": str,               # Help text
    "usage": str,              # Usage string
    "category": str,           # Command category
    "aliases": List[str],      # Command aliases
    "min_args": int,           # Minimum arguments
    "max_args": int,           # Maximum arguments (-1 = unlimited)
    "permissions": List[str]   # Required permissions
}
```

---

## Content Registry

### Dynamic Content Types

The content registry allows registering any content type:

```python
def register_content(self, content_registry):
    return {
        "items": {
            "my_item": {"name": "My Item"}
        },
        "enemies": {
            "my_enemy": {"name": "My Enemy"}
        },
        # Custom content type
        "custom_type": {
            "custom_1": {"data": "value"}
        }
    }
```

### Content Registry API

```python
# Register a single content item
content_registry.register("items", "sword_1", {"name": "Sword"})

# Register multiple items
content_registry.register_batch("items", {
    "sword_1": {"name": "Sword"},
    "axe_1": {"name": "Axe"}
})

# Get content
item = content_registry.get("items", "sword_1")
all_items = content_registry.get_all("items")

# Query with filter
rare_items = content_registry.query("items", 
    lambda k, v: v.get("rarity") == "Rare")

# Get statistics
stats = content_registry.get_stats()
# {"items": 10, "enemies": 5, ...}

# Register new content type with validation
content_registry.register_type(
    "custom_content",
    validator=lambda data: "name" in data,
    factory=lambda id, **kw: {"id": id, **kw}
)
```

---

## Event Types Reference

### Combat Events

| Event | When It Fires | Data Dictionary |
|-------|---------------|-----------------|
| `COMBAT_START` | Combat begins | `{"player": Character, "enemies": List[Enemy]}` |
| `COMBAT_END` | Combat ends | `{"player": Character, "result": str, "enemies": List[Enemy]}` |
| `COMBAT_TURN` | Each combat turn | `{"player": Character, "enemy": Enemy, "turn_number": int}` |

### Player Events

| Event | When It Fires | Data Dictionary |
|-------|---------------|-----------------|
| `PLAYER_LEVEL_UP` | Player levels up | `{"player": Character, "level": int}` |
| `PLAYER_DEATH` | Player dies | `{"player": Character, "killer": Optional[Enemy]}` |

### Item Events

| Event | When It Fires | Data Dictionary |
|-------|---------------|-----------------|
| `ITEM_PICKUP` | Item picked up | `{"player": Character, "item": Item}` |
| `ITEM_EQUIP` | Item equipped | `{"player": Character, "item": Item, "slot": str}` |
| `ITEM_USE` | Item used | `{"player": Character, "item": Item, "target": Any}` |

### World Events

| Event | When It Fires | Data Dictionary |
|-------|---------------|-----------------|
| `LOCATION_ENTER` | Enter location | `{"player": Character, "location_id": str}` |
| `LOCATION_EXIT` | Exit location | `{"player": Character, "location_id": str}` |
| `TIME_CHANGE` | Time changes | `{"old_time": TimeOfDay, "new_time": TimeOfDay, "hour": int, "day": int}` |
| `WEATHER_CHANGE` | Weather changes | `{"old_weather": Weather, "new_weather": Weather}` |

### NPC/Quest Events

| Event | When It Fires | Data Dictionary |
|-------|---------------|-----------------|
| `NPC_INTERACT` | NPC interaction | `{"player": Character, "npc_id": str, "friendship": int}` |
| `QUEST_START` | Quest started | `{"player": Character, "quest_id": str}` |
| `QUEST_COMPLETE` | Quest completed | `{"player": Character, "quest_id": str, "rewards": Dict}` |

### System Events

| Event | When It Fires | Data Dictionary |
|-------|---------------|-----------------|
| `PLUGIN_LOAD` | Plugin loaded | `{"plugin_id": str}` |
| `PLUGIN_UNLOAD` | Plugin unloaded | `{"plugin_id": str}` |
| `GAME_START` | Game starts | `{"player": Character}` |
| `GAME_SAVE` | Game saved | `{"player": Character}` |
| `GAME_LOAD` | Game loaded | `{"player": Character}` |

---

## Content Types Reference

### Items

#### Weapon Item

```python
"weapon_id": {
    "name": "Sword of Power",
    "item_type": "weapon",
    "rarity": "Epic",
    "value": 2500,
    "weight": 3.5,
    "description": "A legendary blade forged in dragon fire.",
    
    # Weapon Properties
    "damage_min": 25,
    "damage_max": 40,
    "damage_type": "fire",
    "attack_speed": 1.2,
    "critical_chance": 0.15,
    "critical_damage": 2.0,
    "range": 1,
    "two_handed": False,
    
    # Requirements
    "level_required": 15,
    "stat_requirements": {"strength": 18, "dexterity": 12},
    
    # Bonuses
    "stat_bonuses": {"strength": 3},
    "special_effects": ["Burns enemies for 5 damage over 3 turns"]
}
```

#### Armor Item

```python
"armor_id": {
    "name": "Dragon Scale Plate",
    "item_type": "armor",
    "rarity": "Legendary",
    "value": 10000,
    "weight": 25.0,
    "description": "Armor crafted from dragon scales.",
    
    # Armor Properties
    "slot": "chest",  # head, chest, legs, feet, hands
    "defense": 45,
    "magic_defense": 20,
    "resistances": {"fire": 0.5, "physical": 0.2},
    
    # Requirements
    "level_required": 25,
    "stat_requirements": {"constitution": 15},
    
    # Bonuses
    "stat_bonuses": {"constitution": 5, "strength": 2}
}
```

#### Consumable Item

```python
"potion_id": {
    "name": "Greater Healing Potion",
    "item_type": "consumable",
    "rarity": "Rare",
    "value": 150,
    "weight": 0.3,
    "description": "A powerful healing potion.",
    
    # Effects
    "hp_restore": 100,
    "mp_restore": 50,
    "temporary_effects": [
        ("defense_buff", 10, 5),  # +10 defense for 5 turns
        ("regeneration", 5, 3)   # +5 HP per turn for 3 turns
    ],
    "use_message": "You feel rejuvenated!"
}
```

#### Accessory Item

```python
"ring_id": {
    "name": "Ring of Wisdom",
    "item_type": "accessory",
    "rarity": "Epic",
    "value": 3000,
    "weight": 0.1,
    "description": "A ring that enhances magical abilities.",
    
    # Bonuses
    "stat_bonuses": {"intelligence": 5, "wisdom": 3},
    "special_effects": [
        "MP Regeneration +5",
        "Spell Power +15%",
        "Cooldown Reduction -10%"
    ],
    
    # Requirements
    "level_required": 12
}
```

### Enemies

```python
"enemy_id": {
    "name": "Dragon Guardian",
    "description": "An ancient dragon tasked with protecting the treasury.",
    "base_hp": 500,
    "base_mp": 100,
    "base_damage": 75,
    "rarity": "Legendary",
    "faction": "dragon",
    
    # Combat Properties
    "abilities": ["fire_breath", "tail_sweep", "wing_buffet"],
    "resistances": {"fire": 0.8, "physical": 0.3},
    "weaknesses": {"ice": 1.5, "lightning": 1.3},
    
    # Drops
    "drops": {
        "gold": [100, 500],
        "items": ["dragon_scale", "dragon_heart", "legendary_weapon"],
        "drop_chances": {"dragon_heart": 0.1}
    },
    
    # Rewards
    "experience_mult": 3.0
}
```

### Locations

```python
"location_id": {
    "id": "dragon_lair",
    "name": "Dragon's Lair",
    "description": "A cavernous lair where an ancient dragon slumbers upon its hoard...",
    "location_type": "dungeon",
    "level_range": [20, 30],
    "connections": ["mountain_pass", "treasure_vault"],
    
    # Content
    "enemies": ["dragon_wyrmling", "dragon_guardian", "drake"],
    "items": ["dragon_scale", "gold_vein", "ancient_artifact"],
    "npcs": ["dragon_scholar"],
    "shops": [],
    
    # Properties
    "danger_level": 5,
    "discovery_exp": 500,
    "hidden": False,
    
    # Special Features
    "special_features": {
        "boss": "ancient_dragon",
        "legendary_treasure": True,
        "fire_hazard": 10,
        "requires_item": "dragon_key"
    },
    
    # Requirements
    "requirements": {
        "level": 20,
        "quest": "dragon_preparation"
    }
}
```

### NPCs

```python
"npc_id": {
    "id": "master_blacksmith",
    "name": "Master Smith Bjorn",
    "description": "A legendary blacksmith with arms like tree trunks...",
    "npc_type": "blacksmith",
    "location": "capital_city",
    
    # Shop (for merchants/blacksmiths)
    "shop_id": "master_forge",
    "shop_items": ["steel_sword", "plate_armor", "dragon_scale_armor"],
    "buy_multiplier": 1.2,   # 20% markup when buying
    "sell_multiplier": 0.5,  # 50% of value when selling
    
    # Services
    "services": ["craft", "repair", "enchant", "identify"],
    
    # Training (for trainers)
    "can_train": ["Swordsmanship", "Crafting"],
    "training_cost": 300,
    
    # Friendship System
    "friendship_max": 200,
    "friendship_rewards": {
        50: "10% discount on all services",
        100: "Access to legendary recipes",
        150: "Free weapon sharpening",
        200: "Masterwork enhancement service"
    },
    
    # Dialogue
    "dialogue": {
        "greeting": {
            "low_friendship": "\"State your business. I've got work to do.\"",
            "medium_friendship": "\"Ah, back again? Let me see what you need.\"",
            "high_friendship": "\"My friend! Come, let me show you my latest work!\""
        }
    }
}
```

### Quests

```python
"quest_id": {
    "id": "dragon_slayer",
    "name": "The Dragon's Bane",
    "description": "An ancient dragon threatens the realm. Gather allies and defeat it.",
    "quest_type": "boss",
    "giver": "king_aldric",
    "location": "royal_castle",
    "level_required": 20,
    
    # Objectives
    "objectives": [
        {
            "type": "talk",
            "target": "dragon_scholar",
            "required": 1,
            "description": "Consult the Dragon Scholar"
        },
        {
            "type": "collect",
            "target": "dragon_artifact",
            "required": 3,
            "description": "Collect Dragon Artifacts"
        },
        {
            "type": "defeat_boss",
            "target": "ancient_dragon",
            "required": 1,
            "description": "Defeat the Ancient Dragon"
        }
    ],
    
    # Rewards
    "rewards": {
        "experience": 5000,
        "gold": 10000,
        "items": ["dragon_scale_armor", "excalibur"],
        "stat_bonus": {"strength": 3, "constitution": 2},
        "skill_exp": {"Swordsmanship": 200}
    }
}
```

### Crafting Recipes

```python
"recipe_id": {
    "name": "Dragon Scale Armor Recipe",
    "category": "armor",
    "result": "dragon_scale_armor",
    "result_quantity": 1,
    
    # Ingredients
    "ingredients": {
        "dragon_scale": 10,
        "enchanted_steel": 5,
        "arcane_essence": 3
    },
    
    # Requirements
    "skill_required": "Crafting",
    "skill_level": 25,
    
    # Costs
    "time": 8,          # Hours to craft
    "gold_cost": 2000,
    
    # Rewards
    "experience": 200
}
```

---

## Enum Values Reference

### Rarity

```
Common, Uncommon, Rare, Epic, Legendary, Mythic
```

### DamageType

```
physical, fire, ice, lightning, holy, dark, poison, true
```

### StatType

```
strength, dexterity, constitution, intelligence, wisdom, charisma, luck
```

### ItemType

```
weapon, armor, consumable, accessory, material, quest
```

### LocationType

```
town, city, village, dungeon, forest, mountain, desert, swamp, 
cave, ruins, castle, temple, shop, inn, wilderness, special
```

### NPCType

```
merchant, trainer, quest_giver, blacksmith, healer, innkeeper,
guard, villager, noble, mysterious, enemy
```

### QuestType

```
main, side, daily, repeatable, boss, exploration, collection,
escort, delivery, hunt, puzzle
```

### ObjectiveType

```
kill, collect, talk, reach, use_item, craft, escort, survive,
defeat_boss, discover, custom
```

### Weather

```
Clear, Cloudy, Rain, Storm, Snow, Fog, Sandstorm, BloodMoon, Aurora
```

### TimeOfDay

```
Dawn, Morning, Noon, Afternoon, Dusk, Evening, Night, Midnight
```

### StatusEffectType

```
poison, burn, freeze, stun, blind, silence, slow, haste,
regeneration, protection, shield, strength_buff, weakness,
defense_buff, defense_debuff, magic_buff, magic_debuff
```

---

## Advanced Features

### Creating Custom Abilities

```python
from core.engine import Ability, AbilityType, TargetType, DamageType

def on_player_level_up(self, data):
    player = data.get("player")
    level = data.get("level")
    
    if level == 10:
        # Create a custom ability
        custom_ability = Ability(
            name="Dragon's Wrath",
            description="Unleash dragon fire upon your enemies.",
            ability_type=AbilityType.ACTIVE,
            target_type=TargetType.ALL_ENEMIES,
            mp_cost=50,
            cooldown=5,
            damage=100 + player.level * 5,
            damage_type=DamageType.FIRE,
            effects=[("burn", 10, 3)]  # Burn for 10 damage over 3 turns
        )
        player.abilities.append(custom_ability)
        print("New ability unlocked: Dragon's Wrath!")
```

### Dynamic World Events

```python
def register_hooks(self, event_system):
    return {
        EventType.TIME_CHANGE: self.on_time_change,
        EventType.WEATHER_CHANGE: self.on_weather_change
    }

def on_time_change(self, data):
    new_time = data.get("new_time")
    hour = data.get("hour")
    
    # Trigger special events at midnight
    if new_time == TimeOfDay.MIDNIGHT:
        print("The witching hour has arrived...")
        # Could spawn special enemies, unlock secret areas, etc.

def on_weather_change(self, data):
    new_weather = data.get("new_weather")
    
    if new_weather == Weather.BLOOD_MOON:
        print("The blood moon rises! Dark forces grow stronger!")
    elif new_weather == Weather.AURORA:
        print("The aurora fills the sky with magic!")
```

### Location-Specific Effects

```python
def on_location_enter(self, data):
    location_id = data.get("location_id")
    player = data.get("player")
    
    # Apply location-specific buffs/debuffs
    if location_id == "cursed_swamp":
        player.apply_status_effect("poison", 1, 0)  # Constant poison
        print("The swamp's toxic air poisons you!")
    
    elif location_id == "sacred_grove":
        player.apply_status_effect("regeneration", 5, 0)  # Constant regen
        print("The sacred grove's magic heals you!")
```

### Secret Discovery System

```python
class SecretPlugin(PluginBase):
    _discovered_secrets: set = set()
    
    def get_content_types(self) -> List[str]:
        return ["world_secrets"]
    
    def get_content(self, content_type: str) -> Dict[str, Any]:
        if content_type == "world_secrets":
            return {
                "ancient_cache": {
                    "name": "Forgotten Cache",
                    "description": "A hidden cache of supplies.",
                    "location": "forest_path",
                    "discovery_method": "explore",
                    "requirements": {"exploration_count": 10},
                    "rewards": {"gold": 500, "exp": 100}
                },
                "fairy_ring": {
                    "name": "Secret Fairy Ring",
                    "description": "A hidden fairy circle.",
                    "location": "deep_forest",
                    "discovery_method": "skill_check",
                    "requirements": {"luck": 15, "time": "midnight"},
                    "rewards": {"effect": "fairy_blessing", "exp": 200}
                }
            }
        return {}
    
    def on_location_enter(self, data):
        location_id = data.get("location_id")
        player = data.get("player")
        
        secrets = self.get_content("world_secrets")
        for secret_id, secret in secrets.items():
            if secret["location"] == location_id:
                if secret_id not in self._discovered_secrets:
                    if self._check_requirements(secret, player):
                        self._trigger_secret(secret_id, secret, player)
    
    def _check_requirements(self, secret, player) -> bool:
        reqs = secret.get("requirements", {})
        for key, value in reqs.items():
            if key == "level" and player.level < value:
                return False
            if key in ["strength", "dexterity", "intelligence", "luck"]:
                if getattr(player, key.lower(), 0) < value:
                    return False
        return True
    
    def _trigger_secret(self, secret_id, secret, player):
        self._discovered_secrets.add(secret_id)
        print(f"\n🔍 SECRET DISCOVERED: {secret['name']}")
        print(f"   {secret['description']}")
```

---

## Plugin Builder API

The `PluginBuilder` class provides a fluent API for creating plugins:

### Basic Usage

```python
from systems.plugins import PluginBuilder, PluginPriority

plugin = (PluginBuilder("my_plugin")
    .name("My Plugin")
    .version("1.0.0")
    .author("Developer")
    .description("A plugin built with fluent API")
    .priority(PluginPriority.NORMAL.value)
    .tags("example", "demo")
    .supports_hot_reload(True)
    .build())
```

### With Lifecycle Hooks

```python
def on_load(game):
    print("Loaded!")

def on_unload(game):
    print("Unloaded!")

plugin = (PluginBuilder("lifecycle_plugin")
    .name("Lifecycle Plugin")
    .version("1.0.0")
    .author("Developer")
    .description("Plugin with lifecycle hooks")
    .on_load(on_load)
    .on_unload(on_unload)
    .build())
```

### With Events and Commands

```python
def on_combat(data):
    print("Combat event!")

def cmd_test(game, args, context):
    return "Test command executed!"

plugin = (PluginBuilder("full_plugin")
    .name("Full Plugin")
    .version("1.0.0")
    .author("Developer")
    .description("Plugin with all features")
    .hook(EventType.COMBAT_END, on_combat)
    .command("test", cmd_test, "Test command")
    .build())
```

### With Content

```python
plugin = (PluginBuilder("content_plugin")
    .name("Content Plugin")
    .version("1.0.0")
    .author("Developer")
    .description("Plugin with content")
    .content("items", {
        "builder_sword": {
            "name": "Builder Sword",
            "item_type": "weapon",
            "rarity": "Rare"
        }
    })
    .content("locations", {
        "builder_tower": {
            "name": "Builder Tower",
            "location_type": "dungeon"
        }
    })
    .build())
```

### Using define_plugin Helper

```python
from systems.plugins import define_plugin

plugin = define_plugin({
    "id": "defined_plugin",
    "name": "Defined Plugin",
    "version": "1.0.0",
    "author": "Developer",
    "description": "Plugin defined with dict"
}).build()
```

---

## Decorator-Based Plugins

### @plugin Decorator

```python
from systems.plugins import plugin, hook, command

@plugin({
    "id": "decorator_plugin",
    "name": "Decorator Plugin",
    "version": "1.0.0",
    "author": "Developer",
    "description": "Plugin using decorators"
})
class DecoratorPlugin:
    
    @hook(EventType.COMBAT_START)
    def on_combat_start(self, data):
        print("Combat starting!")
    
    @hook(EventType.COMBAT_END, priority=EventPriority.HIGH)
    def on_combat_end(self, data):
        if data.get("result") == "victory":
            print("Victory!")
    
    @command("test_cmd", "Test command from decorator plugin")
    def test_command(self, game, args):
        return "Decorator plugin test!"
```

### @hook Decorator

```python
from systems.plugins import hook, EventPriority

@hook(EventType.PLAYER_LEVEL_UP, priority=EventPriority.HIGH)
def on_level_up(data):
    level = data.get("level")
    print(f"Level up! Now level {level}")
```

### @command Decorator

```python
from systems.plugins import command

@command("mycommand", "My custom command", aliases=["mycmd", "mc"])
def my_command(game, args):
    return f"Command executed with args: {args}"
```

---

## JSON/YAML Plugins

### JSON Plugin Format

```json
{
    "info": {
        "id": "json_plugin",
        "name": "JSON Plugin",
        "version": "1.0.0",
        "author": "Developer",
        "description": "Data-only JSON plugin",
        "plugin_type": "data",
        "tags": ["content", "json"]
    },
    
    "items": {
        "json_sword": {
            "name": "JSON Blade",
            "item_type": "weapon",
            "rarity": "Rare",
            "value": 500,
            "damage_min": 10,
            "damage_max": 20
        }
    },
    
    "enemies": {
        "json_golem": {
            "name": "JSON Golem",
            "base_hp": 100,
            "base_damage": 15,
            "rarity": "Uncommon"
        }
    },
    
    "locations": {
        "json_tower": {
            "name": "JSON Tower",
            "location_type": "dungeon",
            "level_range": [5, 15]
        }
    },
    
    "npcs": {
        "json_merchant": {
            "name": "JSON Merchant",
            "npc_type": "merchant",
            "location": "json_tower"
        }
    },
    
    "quests": {
        "json_quest": {
            "name": "The JSON Mystery",
            "quest_type": "side",
            "level_required": 5
        }
    },
    
    "recipes": {
        "json_recipe": {
            "name": "JSON Recipe",
            "category": "weapons",
            "result": "json_sword"
        }
    }
}
```

### YAML Plugin Format

```yaml
info:
  id: yaml_plugin
  name: YAML Plugin
  version: 1.0.0
  author: Developer
  description: Data-only YAML plugin
  plugin_type: data
  tags:
    - content
    - yaml

items:
  yaml_sword:
    name: YAML Blade
    item_type: weapon
    rarity: Rare
    damage_min: 10
    damage_max: 20

locations:
  yaml_cave:
    name: YAML Cave
    location_type: dungeon
    level_range:
      - 5
      - 15
```

---

## Debug Commands

The plugin system provides built-in debug commands:

### Plugin Management

| Command | Description | Usage |
|---------|-------------|-------|
| `/help` | Show available commands | `/help [command]` |
| `/plugins` | List loaded plugins | `/plugins` |
| `/plugin_info` | Show plugin details | `/plugin_info <plugin_id>` |
| `/reload` | Reload a plugin | `/reload <plugin_id>` |
| `/enable` | Enable a plugin | `/enable <plugin_id>` |
| `/disable` | Disable a plugin | `/disable <plugin_id>` |
| `/hot_reload` | Toggle hot reload monitoring | `/hot_reload` |
| `/content` | Show content registry stats | `/content` |

### Player Commands

| Command | Description | Usage |
|---------|-------------|-------|
| `/give` | Give item to player | `/give <item_id> [quantity]` |
| `/teleport` | Teleport to location | `/teleport <location_id>` |
| `/spawn` | Spawn and fight enemy | `/spawn <enemy_type> [level]` |
| `/setlevel` | Set player level | `/setlevel <level>` |
| `/god` | Toggle god mode | `/god` |
| `/heal` | Fully heal player | `/heal` |
| `/gold` | Add gold | `/gold <amount>` |

---

## Best Practices

### 1. Unique IDs

Use a consistent prefix for all your content IDs:

```python
# Good
"myplugin_sword_of_power"
"myplugin_dragon_boss"
"myplugin_secret_location"

# Bad - might conflict with other plugins
"sword_of_power"
"dragon_boss"
"secret_location"
```

### 2. Dependencies

Declare dependencies explicitly:

```python
PluginInfo(
    id="expansion_pack",
    dependencies=["core_items", "core_quests"],  # Required
    soft_dependencies=["extended_world"],         # Optional
    conflicts=["old_expansion"]                   # Incompatible
)
```

### 3. Balance

Keep content appropriate for level ranges:

```python
# Weapon balanced for level 10
{
    "damage_min": 15,
    "damage_max": 25,
    "level_required": 10
}

# Weapon balanced for level 20
{
    "damage_min": 35,
    "damage_max": 50,
    "level_required": 20
}
```

### 4. Error Handling

```python
def on_combat_end(self, data):
    try:
        player = data.get("player")
        if not player:
            return
        
        # Your logic here
        player.inventory.gold += 10
        
    except Exception as e:
        print(f"[MyPlugin] Error in on_combat_end: {e}")
```

### 5. Cleanup

```python
def on_unload(self, game):
    # Remove any applied effects
    # Save plugin state if needed
    # Clean up references
    print("My Plugin cleaned up and unloaded.")
```

### 6. Documentation

```python
def register_hooks(self, event_system):
    """
    Register event hooks for the plugin.
    
    Hooks registered:
    - COMBAT_END: Awards bonus gold on victory
    - PLAYER_LEVEL_UP: Unlocks abilities at milestones
    """
    return {
        EventType.COMBAT_END: self.on_combat_end,
        EventType.PLAYER_LEVEL_UP: self.on_level_up
    }
```

### 7. Configuration Validation

```python
def validate_config(self, config: Dict[str, Any]) -> Tuple[bool, str]:
    """Validate configuration against schema."""
    schema = self.info.config_schema
    
    for key, value in config.items():
        if key not in schema:
            return False, f"Unknown config key: {key}"
        
        spec = schema[key]
        
        # Type validation
        if spec["type"] == "integer" and not isinstance(value, int):
            return False, f"{key} must be an integer"
        
        # Range validation
        if "min" in spec and value < spec["min"]:
            return False, f"{key} must be >= {spec['min']}"
        if "max" in spec and value > spec["max"]:
            return False, f"{key} must be <= {spec['max']}"
    
    return True, ""
```

---

## Examples

### Complete Plugin: New Dungeon with Boss

```python
"""
Dark Cavern Plugin - Adds a new dungeon with boss encounter
"""

from __future__ import annotations
from systems.plugins import (
    PluginBase, PluginInfo, PluginType, PluginPriority,
    IContentProvider, IHotReloadablePlugin, EventType, EventPriority
)
from typing import Dict, Any, List


class DarkCavernPlugin(PluginBase, IContentProvider, IHotReloadablePlugin):
    
    _state: Dict[str, Any] = {}
    
    @property
    def info(self) -> PluginInfo:
        return PluginInfo(
            id="dark_cavern",
            name="Dark Cavern",
            version="1.0.0",
            author="Dungeon Master",
            description="Adds a mysterious cavern with a powerful boss.",
            priority=PluginPriority.NORMAL.value,
            plugin_type=PluginType.CLASS,
            supports_hot_reload=True,
            tags=["dungeon", "boss", "content"]
        )
    
    # Lifecycle
    def on_load(self, game):
        print("Dark Cavern Plugin loaded!")
        self._state = {"boss_defeated": False}
    
    def on_unload(self, game):
        print("Dark Cavern Plugin unloaded!")
    
    # Hot Reload
    def on_before_reload(self, game) -> Dict[str, Any]:
        return {"state": self._state.copy()}
    
    def on_after_reload(self, game, state: Dict[str, Any]) -> None:
        self._state = state.get("state", {})
    
    # Content Provider
    def get_content_types(self) -> List[str]:
        return ["items", "enemies", "locations", "npcs", "quests"]
    
    def get_content(self, content_type: str) -> Dict[str, Any]:
        content = {
            "items": self._get_items,
            "enemies": self._get_enemies,
            "locations": self._get_locations,
            "npcs": self._get_npcs,
            "quests": self._get_quests
        }
        return content.get(content_type, lambda: {})()
    
    def _get_items(self) -> Dict[str, Any]:
        return {
            "shadow_cloak": {
                "name": "Shadow Cloak",
                "item_type": "armor",
                "rarity": "Legendary",
                "value": 8000,
                "weight": 1.0,
                "description": "A cloak woven from shadow essence.",
                "slot": "chest",
                "defense": 20,
                "magic_defense": 35,
                "stat_bonuses": {"dexterity": 5, "luck": 3},
                "level_required": 20
            }
        }
    
    def _get_enemies(self) -> Dict[str, Any]:
        return {
            "shadow_lord": {
                "name": "Shadow Lord",
                "description": "A being of pure darkness.",
                "base_hp": 800,
                "base_mp": 300,
                "base_damage": 60,
                "rarity": "Legendary",
                "faction": "shadow",
                "abilities": ["dark_bolt", "shadow_clone", "void_embrace"],
                "resistances": {"physical": 0.5, "dark": 0.9},
                "weaknesses": {"holy": 2.0, "lightning": 1.3}
            }
        }
    
    def _get_locations(self) -> Dict[str, Any]:
        return {
            "dark_cavern": {
                "name": "Dark Cavern",
                "description": "A pitch-black cavern filled with danger.",
                "location_type": "cave",
                "level_range": [15, 25],
                "connections": ["forest_path"],
                "enemies": ["shadow_bat", "cave_spider", "dark_elemental"],
                "danger_level": 4,
                "special_features": {"boss": "shadow_lord"},
                "discovery_exp": 300
            }
        }
    
    def _get_npcs(self) -> Dict[str, Any]:
        return {
            "cavern_hermit": {
                "name": "Crazy Hermit",
                "description": "An old hermit living in the cavern.",
                "npc_type": "mysterious",
                "location": "dark_cavern",
                "services": ["information", "healing"]
            }
        }
    
    def _get_quests(self) -> Dict[str, Any]:
        return {
            "dark_cavern_quest": {
                "name": "Shadows of the Cavern",
                "description": "Defeat the Shadow Lord.",
                "quest_type": "boss",
                "giver": "cavern_hermit",
                "location": "dark_cavern",
                "level_required": 15,
                "objectives": [
                    {"type": "reach", "target": "dark_cavern", "required": 1},
                    {"type": "defeat_boss", "target": "shadow_lord", "required": 1}
                ],
                "rewards": {
                    "experience": 2000,
                    "gold": 1500,
                    "items": ["shadow_cloak"]
                }
            }
        }
    
    # Event Hooks
    def register_hooks(self, event_system) -> Dict:
        return {
            EventType.LOCATION_ENTER: (self._on_location_enter, EventPriority.NORMAL),
            EventType.COMBAT_END: self._on_combat_end
        }
    
    def _on_location_enter(self, data):
        location_id = data.get("location_id")
        if location_id == "dark_cavern":
            print("\nThe darkness envelops you...")
    
    def _on_combat_end(self, data):
        if data.get("result") == "victory":
            # Check if shadow lord was defeated
            pass

# Plugin instance
plugin = DarkCavernPlugin()
```

---

## Troubleshooting

### Common Issues and Solutions

| Issue | Solution |
|-------|----------|
| Plugin not loading | Check syntax: `python3 -c "import plugins.my_plugin"` |
| `'X' is not a valid EnumType` | Check valid enum values in Enum Reference section |
| Content not appearing | Verify IDs are unique and methods return correct types |
| Events not firing | Ensure hook is registered and callback signature matches |
| Import errors | Add `from __future__ import annotations` at top |
| Plugin conflicts | Add conflicting IDs to `conflicts` list in PluginInfo |
| Hot reload not working | Implement `on_before_reload` and `on_after_reload` |
| Command not found | Check command is registered and uses correct format |

### Debug Checklist

1. ✅ File is in the `plugins/` directory
2. ✅ File ends with `.py` (or `.json`/`.yaml`)
3. ✅ Class inherits from `PluginBase` (or uses PluginBuilder)
4. ✅ `info` property returns `PluginInfo` object
5. ✅ `on_load` and `on_unload` methods exist
6. ✅ `plugin = YourPluginClass()` line exists at bottom
7. ✅ No syntax errors (test with Python)
8. ✅ All enum values are valid
9. ✅ Dependencies are satisfied
10. ✅ No conflicts with other plugins

### Testing Your Plugin

```python
# test_plugin.py
import sys
sys.path.insert(0, '.')

from systems.plugins import PluginManager, PluginState

class MockPlayer:
    level = 10
    inventory = type('obj', (object,), {'gold': 0})()

class MockGame:
    def __init__(self):
        self.player = MockPlayer()

game = MockGame()
pm = PluginManager(game)

# Load your plugin
result = pm.load_plugin('my_plugin')

if result and pm._plugin_states.get('my_plugin') == PluginState.ENABLED:
    print("✅ Plugin loaded successfully!")
    
    # Check content
    stats = pm.content_registry.get_stats()
    print(f"Content: {stats}")
else:
    print("❌ Plugin failed to load")
```

---

## File Structure

```
rpg_game/
├── main.py                      # Game entry point
├── core/
│   ├── __init__.py
│   ├── engine.py                # Core engine classes, enums, utilities
│   ├── character.py             # Character system, skills, equipment
│   └── items.py                 # Item system, factories, database
├── systems/
│   ├── __init__.py
│   ├── plugins.py               # Dynamic plugin system (2500+ lines)
│   ├── world.py                 # World map, locations, travel, time
│   ├── combat.py                # Combat system, enemies, encounters
│   ├── quests.py                # Quest system, objectives, rewards
│   ├── npc.py                   # NPC system, dialogue, shops
│   ├── crafting.py              # Crafting system, recipes
│   └── save_load.py             # Save/load system
└── plugins/
    ├── README.md                # This documentation
    ├── base_plugin_template.py  # Complete Python template (850 lines)
    ├── json_plugin_template.json # JSON template
    ├── enhanced_combat.py       # Example: Combat enhancements
    ├── extended_items.py        # Example: New items
    ├── extended_npcs.py         # Example: New NPCs
    ├── extended_world.py        # Example: New locations
    └── my_plugin.py             # Your plugin here!
```

---

## API Reference

### PluginManager

```python
class PluginManager:
    def __init__(self, game: Any = None): ...
    
    # Path Management
    def add_plugin_path(self, path: str): ...
    def remove_plugin_path(self, path: str): ...
    
    # Discovery
    def discover_plugins(self, force: bool = False) -> List[str]: ...
    
    # Loading
    def load_plugin(self, plugin_id: str) -> bool: ...
    def unload_plugin(self, plugin_id: str) -> bool: ...
    def reload_plugin(self, plugin_id: str) -> str: ...
    
    # State Management
    def enable_plugin(self, plugin_id: str) -> bool: ...
    def disable_plugin(self, plugin_id: str) -> bool: ...
    def get_plugin_state(self, plugin_id: str) -> Optional[PluginState]: ...
    
    # Information
    def get_plugin(self, plugin_id: str) -> Optional[Any]: ...
    def get_plugin_info(self, plugin_id: str) -> Optional[PluginInfo]: ...
    
    # Dependency Resolution
    def resolve_dependencies(self, plugin_ids: List[str]) -> Tuple[List[str], List[str]]: ...
    def check_conflicts(self, plugin_id: str) -> List[str]: ...
    
    # Hot Reload
    def start_hot_reload(self): ...
    def stop_hot_reload(self): ...
```

### PluginBase

```python
class PluginBase(ABC):
    @property
    @abstractmethod
    def info(self) -> PluginInfo: ...
    
    @abstractmethod
    def on_load(self, game): ...
    
    @abstractmethod
    def on_unload(self, game): ...
    
    def on_enable(self, game): ...
    def on_disable(self, game): ...
    def on_config_changed(self, game, key: str, value: Any): ...
    
    def register_hooks(self, event_system) -> Dict[Any, Callable]: ...
    def register_commands(self, command_system) -> Dict[str, Callable]: ...
    def register_content(self, content_registry) -> Dict[str, Dict]: ...
    
    def get_config(self) -> Dict[str, Any]: ...
    def set_config(self, config: Dict[str, Any]): ...
    def validate_config(self, config: Dict[str, Any]) -> Tuple[bool, str]: ...
    
    def on_before_reload(self, game) -> Dict[str, Any]: ...
    def on_after_reload(self, game, state: Dict[str, Any]): ...
```

### PluginInfo

```python
@dataclass
class PluginInfo:
    # Required
    id: str
    name: str
    version: str
    author: str
    description: str
    
    # Dependencies
    dependencies: List[str] = field(default_factory=list)
    soft_dependencies: List[str] = field(default_factory=list)
    conflicts: List[str] = field(default_factory=list)
    provides: List[str] = field(default_factory=list)
    
    # Loading
    priority: int = 100
    plugin_type: PluginType = PluginType.CLASS
    
    # Version Compatibility
    min_game_version: str = "1.0.0"
    max_game_version: str = ""
    api_version: str = "1.0"
    
    # Configuration
    configurable: bool = False
    config_schema: Dict[str, Any] = field(default_factory=dict)
    default_config: Dict[str, Any] = field(default_factory=dict)
    
    # Hot Reload
    supports_hot_reload: bool = False
    reload_priority: int = 100
    
    # Metadata
    tags: List[str] = field(default_factory=list)
    homepage: str = ""
    license: str = ""
    repository: str = ""
    custom: Dict[str, Any] = field(default_factory=dict)
```

### EventSystem

```python
class EventSystem:
    def subscribe(self, event_type: Any, handler: Callable,
                  priority: EventPriority = EventPriority.NORMAL,
                  plugin_id: str = "", once: bool = False): ...
    
    def subscribe_async(self, event_type: Any, handler: Callable,
                        priority: EventPriority = EventPriority.NORMAL): ...
    
    def unsubscribe(self, event_type: Any, handler: Callable) -> bool: ...
    def unsubscribe_plugin(self, plugin_id: str) -> int: ...
    
    def emit(self, event_type: Any, data: Dict = None,
             allow_async: bool = False) -> List[Any]: ...
    
    def add_middleware(self, middleware: Callable): ...
    def stop_propagation(self): ...
```

### CommandSystem

```python
class CommandSystem:
    def register(self, name: str, handler: Callable,
                 help_text: str = "", aliases: List[str] = None,
                 plugin_id: str = "", permissions: List[str] = None,
                 min_args: int = 0, max_args: int = -1,
                 usage: str = "", category: str = "general"): ...
    
    def unregister(self, name: str) -> bool: ...
    def unregister_plugin(self, plugin_id: str) -> int: ...
    
    def execute(self, name: str, game: Any,
                args: List[str] = None, context: Dict = None) -> Tuple[bool, str]: ...
    
    def get_help(self, name: str = None, category: str = None) -> str: ...
    def get_commands(self) -> List[str]: ...
    def get_categories(self) -> List[str]: ...
```

### ContentRegistry

```python
class ContentRegistry:
    def register_type(self, content_type: str, factory: Callable = None,
                      validator: Callable = None, loader: Callable = None): ...
    
    def register(self, content_type: str, content_id: str,
                 content_data: Any, plugin_id: str = None) -> bool: ...
    
    def register_batch(self, content_type: str, content: Dict[str, Any],
                       plugin_id: str = None) -> int: ...
    
    def unregister(self, content_type: str, content_id: str) -> bool: ...
    def unregister_plugin(self, plugin_id: str) -> int: ...
    
    def get(self, content_type: str, content_id: str) -> Optional[Any]: ...
    def get_all(self, content_type: str) -> Dict[str, Any]: ...
    def get_types(self) -> List[str]: ...
    
    def query(self, content_type: str, filter_func: Callable = None) -> List: ...
    def get_stats(self) -> Dict[str, int]: ...
```

### PluginBuilder

```python
class PluginBuilder:
    def __init__(self, plugin_id: str): ...
    
    def name(self, name: str) -> 'PluginBuilder': ...
    def version(self, version: str) -> 'PluginBuilder': ...
    def author(self, author: str) -> 'PluginBuilder': ...
    def description(self, description: str) -> 'PluginBuilder': ...
    def priority(self, priority: int) -> 'PluginBuilder': ...
    def tags(self, *tags: str) -> 'PluginBuilder': ...
    def supports_hot_reload(self, supports: bool) -> 'PluginBuilder': ...
    
    def on_load(self, func: Callable) -> 'PluginBuilder': ...
    def on_unload(self, func: Callable) -> 'PluginBuilder': ...
    
    def hook(self, event_type: Any, callback: Callable) -> 'PluginBuilder': ...
    def command(self, name: str, callback: Callable, help_text: str = "") -> 'PluginBuilder': ...
    def content(self, content_type: str, data: Dict) -> 'PluginBuilder': ...
    
    def build(self) -> FunctionalPlugin: ...
```

---

## Contributing

### Plugin Submission Guidelines

1. **Test thoroughly** - Ensure your plugin loads without errors
2. **Use unique IDs** - Prefix all content IDs with your plugin name
3. **Document your code** - Add docstrings and comments
4. **Balance content** - Match the intended level ranges
5. **Handle errors** - Use try-except blocks for risky operations
6. **No breaking changes** - Don't modify core game behavior unexpectedly
7. **Implement interfaces** - Use appropriate protocols for your plugin type

### Code Style

```python
# Use type hints
def on_combat_end(self, data: Dict[str, Any]) -> None:
    player: Character = data.get("player")

# Use descriptive names
def register_shadow_enemies(self) -> Dict[str, Dict]:
    ...

# Document your methods
def get_new_locations(self) -> Dict[str, Dict[str, Any]]:
    """
    Return new locations added by this plugin.
    
    Returns:
        Dict mapping location IDs to location data dictionaries
    """
    return {...}
```

---

## Changelog

### Version 2.0.0 (Current - Dynamic Plugin System)

**Major Features:**
- Complete rewrite with dynamic plugin architecture
- Multiple plugin styles (Class, Functional, Decorator, Data-only)
- Protocol-based interfaces for duck typing
- Hot reload support with state preservation
- Configuration system with schema validation
- Event priorities and middleware
- Command categories and permissions
- Dynamic content registry
- PluginBuilder fluent API
- Decorator-based plugin creation

**New Classes:**
- `PluginManager` - Full plugin lifecycle management
- `PluginBuilder` - Fluent API for plugin creation
- `ContentRegistry` - Dynamic content type registration
- `EventSystem` - Priority-based event handling
- `CommandSystem` - Categorized command management
- `PluginDiscovery` - Multi-format plugin discovery
- `FunctionalPlugin` - Function-based plugin support

**New Protocols:**
- `IPlugin` - Base plugin interface
- `IContentProvider` - Content provision interface
- `IHotReloadablePlugin` - Hot reload interface
- `IConfigurablePlugin` - Configuration interface
- `IEventSubscriber` - Event subscription interface
- `ICommandProvider` - Command provision interface

**New Enums:**
- `PluginState` - 11 plugin states
- `PluginType` - 6 plugin types
- `PluginPriority` - 6 priority levels
- `EventPriority` - 6 handler priorities

### Version 1.0.0

- Initial plugin system release
- Basic Python plugin support
- JSON plugin template
- Event hook system with 18 event types
- Custom command registration
- Content registration for items, enemies, locations, NPCs, quests, recipes
- Built-in debug commands

### Included Plugins

| Plugin | Version | Description |
|--------|---------|-------------|
| Base Plugin Template | 2.0.0 | Complete reference plugin with all features |
| JSON Plugin Template | 2.0.0 | Data-only JSON plugin template |
| Enhanced Combat | 1.0.0 | Combat abilities and bonuses |
| Extended Items | 1.0.0 | New weapons, armor, consumables |
| Extended NPCs | 1.0.0 | 14 new NPCs across 9 locations |
| Extended World | 2.0.0 | 13 new locations, events, secrets |

---

## Support

For issues, questions, or contributions:
- Check the troubleshooting section above
- Review the example plugins in the `plugins/` directory
- Consult `base_plugin_template.py` for comprehensive examples
- Test with the provided test scripts

---

*Legends of Eldoria Plugin System v2.0.0 | Dynamic Plugin Architecture | © 2026 YSNRFD*

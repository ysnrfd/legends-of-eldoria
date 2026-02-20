# Legends of Eldoria - Plugin Development Guide

## Overview

The Legends of Eldoria plugin system allows you to extend the game with new content, features, and mechanics without modifying the core game code.

### What Plugins Can Add

- **Items**: Weapons, armor, consumables, accessories, materials
- **Enemies**: New enemy types with custom abilities and drops
- **Locations**: Towns, dungeons, forests, temples, and special areas
- **NPCs**: Merchants, trainers, quest givers, and special characters
- **Quests**: Main story, side quests, boss fights, daily quests
- **Crafting Recipes**: New crafting formulas
- **Custom Commands**: Slash commands for players
- **Event Hooks**: React to game events in real-time

### Key Features

| Feature | Description |
|---------|-------------|
| **Class-based Plugins** | Inherit from `Plugin` base class |
| **Event System** | Hook into game events |
| **Command System** | Register custom commands |
| **Content Registry** | Register items, enemies, locations, NPCs, quests, recipes |
| **Configuration** | Per-plugin configuration support |
| **Dependencies** | Declare plugin dependencies |

---

## Quick Start

### 1. Create a Simple Plugin

```python
from systems.plugins import Plugin, PluginInfo, PluginPriority, EventType

class MyPlugin(Plugin):
    def __init__(self):
        info = PluginInfo(
            id="my_plugin",
            name="My Plugin",
            version="1.0.0",
            author="Your Name",
            description="My first plugin",
            dependencies=[],
            conflicts=[],
            priority=PluginPriority.NORMAL,
            tags=["example"]
        )
        super().__init__(info)
    
    def on_load(self, game) -> bool:
        print("My plugin loaded!")
        return True
    
    def on_unload(self, game) -> bool:
        print("My plugin unloaded!")
        return True
    
    def on_enable(self, game) -> bool:
        return True
    
    def on_disable(self, game) -> bool:
        return True

# Required: Create plugin instance
plugin = MyPlugin()
```

### 2. Add Event Hooks

```python
def register_hooks(self, event_system) -> Dict[EventType, Any]:
    return {
        EventType.COMBAT_START: self._on_combat_start,
        EventType.PLAYER_LEVEL_UP: self._on_level_up,
    }

def _on_combat_start(self, game, data):
    print("Combat started!")
    
def _on_level_up(self, game, data):
    level = data.get("level")
    print(f"Player reached level {level}!")
```

### 3. Add Commands

```python
def register_commands(self, command_system) -> Dict[str, Any]:
    return {
        "mycommand": {
            "handler": self._cmd_mycommand,
            "help": "Description of my command",
            "usage": "/mycommand [args]",
            "category": "general"
        }
    }

def _cmd_mycommand(self, game, args, context):
    return "Hello from my plugin!"
```

### 4. Add Content

```python
def register_items(self, item_registry) -> Dict[str, Dict]:
    return {
        "my_sword": {
            "name": "My Custom Sword",
            "item_type": "weapon",
            "rarity": "Rare",
            "damage_min": 10,
            "damage_max": 20
        }
    }

def register_enemies(self, enemy_registry) -> Dict[str, Dict]:
    return {
        "my_enemy": {
            "name": "My Custom Enemy",
            "base_hp": 100,
            "base_damage": 15
        }
    }

def register_recipes(self, crafting_manager) -> Dict[str, Dict]:
    return {
        "my_recipe": {
            "name": "My Recipe",
            "result": "my_sword",
            "ingredients": {"iron": 2}
        }
    }

def get_new_locations(self) -> Dict[str, Dict]:
    return {
        "my_location": {
            "name": "My Location",
            "description": "A custom location",
            "location_type": "dungeon"
        }
    }

def get_new_npcs(self) -> Dict[str, Dict]:
    return {
        "my_npc": {
            "name": "My NPC",
            "npc_type": "merchant",
            "services": ["trade"]
        }
    }

def get_new_quests(self) -> Dict[str, Dict]:
    return {
        "my_quest": {
            "name": "My Quest",
            "description": "A custom quest",
            "objectives": [{"type": "kill", "target": "my_enemy", "required": 5}]
        }
    }
```

---

## Plugin Lifecycle

1. **Discovery** - Plugin files found in `plugins/` directory
2. **Load** - `on_load(game)` called
3. **Enable** - `on_enable(game)` called
4. **Running** - Plugin is active, hooks and commands registered
5. **Disable** - `on_disable(game)` called
6. **Unload** - `on_unload(game)` called

---

## Event Types

Available event types from `core.engine.EventType`:

| Event | Description |
|-------|-------------|
| `COMBAT_START` | Combat begins |
| `COMBAT_END` | Combat ends |
| `COMBAT_TURN` | New combat turn |
| `PLAYER_LEVEL_UP` | Player gains a level |
| `PLAYER_DEATH` | Player dies |
| `ITEM_PICKUP` | Item picked up |
| `ITEM_EQUIP` | Item equipped |
| `ITEM_USE` | Item used |
| `NPC_INTERACT` | NPC interaction |
| `LOCATION_ENTER` | Enter a location |
| `LOCATION_LEAVE` | Leave a location |
| `QUEST_START` | Quest started |
| `QUEST_COMPLETE` | Quest completed |
| `WEATHER_CHANGE` | Weather changes |
| `TIME_CHANGE` | Time of day changes |
| `PLAYER_MOVE` | Player moves |

---

## Content Types

### Items

```python
{
    "item_id": {
        "name": "Item Name",
        "item_type": "weapon|armor|consumable|accessory|material",
        "rarity": "Common|Uncommon|Rare|Epic|Legendary",
        "value": 100,
        "weight": 1.0,
        "description": "Item description",
        # Weapon-specific
        "damage_min": 10,
        "damage_max": 20,
        "damage_type": "physical|fire|ice|lightning|holy|dark|poison",
        "attack_speed": 1.0,
        "critical_chance": 0.1,
        # Armor-specific
        "defense": 10,
        "magic_defense": 5,
        "slot": "head|chest|legs|hands|feet",
        # Consumable-specific
        "hp_restore": 50,
        "mp_restore": 25,
        "use_message": "You use the item.",
        # All items
        "stat_bonuses": {"strength": 2, "dexterity": 1},
        "level_required": 5,
        "special_effects": ["Effect 1", "Effect 2"]
    }
}
```

### Enemies

```python
{
    "enemy_id": {
        "name": "Enemy Name",
        "description": "Enemy description",
        "base_hp": 100,
        "base_mp": 50,
        "base_damage": 15,
        "rarity": "Common|Uncommon|Rare|Epic|Legendary",
        "faction": "goblin|undead|beast|etc",
        "abilities": ["ability1", "ability2"],
        "resistances": {"fire": 0.5, "ice": 0.3},
        "weaknesses": {"holy": 1.5},
        "drops": {
            "gold": [10, 50],
            "items": ["item_id"]
        }
    }
}
```

### Locations

```python
{
    "location_id": {
        "name": "Location Name",
        "description": "Location description",
        "location_type": "town|dungeon|forest|mountain|etc",
        "level_range": [1, 10],
        "connections": ["other_location"],
        "enemies": ["enemy_id"],
        "resources": ["resource_id"],
        "features": ["feature1", "feature2"],
        "hidden": False,
        "requirements": {"level": 5, "quest": "quest_id"}
    }
}
```

### NPCs

```python
{
    "npc_id": {
        "name": "NPC Name",
        "description": "NPC description",
        "npc_type": "merchant|trainer|quest_giver|blacksmith|mysterious",
        "location": "location_id",
        "shop_items": ["item_id"],
        "services": ["trade", "train", "repair"],
        "can_train": ["Skill1", "Skill2"],
        "training_cost": 100,
        "dialogue": {
            "greeting": {
                "low_friendship": "Hello...",
                "medium_friendship": "Good to see you!",
                "high_friendship": "My friend!"
            }
        }
    }
}
```

### Quests

```python
{
    "quest_id": {
        "name": "Quest Name",
        "description": "Quest description",
        "quest_type": "main|side|boss|daily",
        "giver": "npc_id",
        "location": "location_id",
        "level_required": 5,
        "objectives": [
            {"type": "kill|collect|reach|talk|defeat_boss", 
             "target": "target_id", 
             "required": 5,
             "description": "Objective description"}
        ],
        "rewards": {
            "experience": 1000,
            "gold": 500,
            "items": ["item_id"],
            "stat_bonus": {"strength": 2}
        }
    }
}
```

### Recipes

```python
{
    "recipe_id": {
        "name": "Recipe Name",
        "category": "weapons|armor|alchemy|jewelry",
        "result": "item_id",
        "result_quantity": 1,
        "ingredients": {"material_id": 2, "other_material": 1},
        "skill_required": "Crafting|Alchemy",
        "skill_level": 5,
        "time": 2,
        "gold_cost": 100,
        "experience": 25
    }
}
```

---

## JSON Plugins

For simple content-only plugins, you can use JSON format:

```json
{
    "info": {
        "id": "my_json_plugin",
        "name": "My JSON Plugin",
        "version": "1.0.0",
        "author": "Your Name",
        "description": "A JSON plugin",
        "dependencies": [],
        "priority": 100,
        "tags": ["content"]
    },
    "items": {
        "my_item": {
            "name": "My Item",
            "item_type": "weapon",
            "rarity": "Rare"
        }
    },
    "enemies": {},
    "locations": {},
    "npcs": {},
    "quests": {},
    "recipes": {}
}
```

---

## Best Practices

1. **Always create the plugin instance**: End your file with `plugin = YourPlugin()`
2. **Return True from lifecycle methods**: Indicates successful operation
3. **Use proper type hints**: Helps with IDE support and debugging
4. **Handle errors gracefully**: Don't let your plugin crash the game
5. **Document your commands**: Provide clear help text
6. **Test thoroughly**: Ensure all features work as expected
7. **Use unique IDs**: Avoid conflicts with other plugins
8. **Declare dependencies**: Help the plugin manager load order

---

## Example Plugins

| Plugin | Description |
|--------|-------------|
| `base_plugin_template.py` | Complete reference with all features |
| `help_plugin.py` | Command help system |
| `enhanced_combat.py` | Combat mechanics and abilities |
| `extended_items.py` | Weapons, armor, consumables, recipes |
| `extended_npcs.py` | NPCs with dialogue and quests |
| `extended_world.py` | Locations, events, secrets |
| `json_plugin_template.json` | JSON-only content plugin |

---

## Troubleshooting

### Plugin not loading?
- Check that you created the plugin instance: `plugin = YourPlugin()`
- Verify the file is in the `plugins/` directory
- Check for syntax errors in your Python code

### Commands not working?
- Ensure `register_commands` returns a properly formatted dict
- Check that handler functions accept `(game, args, context)` parameters
- Verify command names are unique

### Events not firing?
- Make sure `register_hooks` returns `{EventType: handler_function}`
- Check that handler functions accept `(game, data)` parameters
- Verify you're using the correct EventType from `core.engine`

---

*Legends of Eldoria Plugin System | © 2026 YSNRFD*

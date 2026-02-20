# LEGENDS OF ELDORIA - Game Documentation

![Version](https://img.shields.io/badge/version-1.0.0-blue)
![Python](https://img.shields.io/badge/python-3.8%2B-green)
![License](https://img.shields.io/badge/license-Open%20Development-green)

**Creator:** YSNRFD | **GitHub:** [github.com/ysnrfd](https://github.com/ysnrfd) | **Email:** rfdysn@gmail.com

A fully-featured, open-world text-based RPG game with a powerful dynamic plugin architecture.

> **No ownership claims allowed** | **Free for development and expansion**

📚 For project overview and contribution guidelines, see the [root README.md](../README.md)

---

## 📑 Table of Contents

- [Features](#features)
- [Installation](#installation)
- [How to Play](#how-to-play)
- [Character Classes](#character-classes)
- [World Locations](#world-locations)
- [Plugin System](#plugin-system)
- [Game Structure](#game-structure)
- [Game Tips](#game-tips)

---

## Features

### 🎮 Core Gameplay
- **Open World Exploration**: Travel through diverse locations including villages, cities, forests, mountains, dungeons, and more
- **Turn-Based Combat**: Strategic combat system with abilities, status effects, and critical hits
- **Character Progression**: 10 unique classes, leveling system, and skill development
- **Quest System**: Main storyline, side quests, and daily quests with multiple objectives

### ⚔️ Combat System
- Multiple attack types (Physical, Magical, Fire, Ice, Lightning, etc.)
- Status effects (Poison, Burn, Freeze, Stun, etc.)
- Critical hits and evasion
- Enemy AI with varying difficulty
- Boss battles with unique mechanics

### 🎒 Equipment & Items
- 100+ items including weapons, armor, accessories, consumables
- 7 rarity tiers (Common → Uncommon → Rare → Epic → Legendary → Mythic → Divine)
- Equipment slots for full customization
- Inventory management with weight system

### 🌍 World Features
- Day/Night cycle affecting gameplay and encounters
- Dynamic weather system
- Multiple biomes and regions with unique challenges
- Random events and encounters
- NPCs with dialogue trees and quests

### 🛠️ Crafting System
- Blacksmithing, Alchemy, Enchanting
- Cooking, Jewelcrafting, Leatherworking
- Skill-based success rates with quality tiers
- Recipe discovery and mastery

### 🔌 Dynamic Plugin System
The game features a powerful, production-ready plugin architecture:

- **6 Plugin Types**: CLASS, FUNCTIONAL, DATA, HYBRID, MODULE, ARCHIVE
- **Interface Protocols**: IPlugin, IConfigurablePlugin, IHotReloadablePlugin, IContentProvider, IEventSubscriber, ICommandProvider
- **Dynamic Content Registry**: Factory/Validator/Loader per content type
- **Event System**: Priority-based event handling (HIGHEST → HIGH → NORMAL → LOW → LOWEST → MONITOR)
- **Command System**: Categories, permissions, middleware support
- **Hot Reload**: State preservation across reloads
- **Fluent API**: PluginBuilder for elegant plugin creation
- **Decorators**: @plugin, @hook, @command for quick setup
- **Multiple Formats**: .py, .json, .yaml, .zip plugin support

### 💾 Save System
- Multiple save slots
- Auto-save functionality
- Quick save/load with hotkeys
- Cross-platform save file compatibility

---

## Installation

### Requirements
- Python 3.8 or higher
- No external dependencies required!

### Quick Start

```bash
# Clone or download the repository
git clone https://github.com/ysnrfd/legends-of-eldoria.git

# Navigate to game directory
cd rpg_game

# Run the game
python main.py
```

---

## How to Play

### Main Commands
| Command | Action |
|---------|--------|
| `E` | Explore current location |
| `T` | Travel to another location |
| `I` | Open inventory |
| `C` | View character sheet |
| `Q` | View quest log |
| `M` | View world map |
| `R` | Rest (restore HP/MP) |
| `S` | Save game |
| `L` | Load game |
| `H` | Show help |
| `X` | Return to main menu |

### Combat Commands
| Key | Action |
|-----|--------|
| `1` | Basic Attack |
| `2` | Use Ability |
| `3` | Use Item |
| `4` | Defend |
| `5` | Flee |

### Plugin Commands
| Command | Action |
|---------|--------|
| `/help` | Show all plugin commands |
| `/plugins` | List loaded plugins |
| `/events` | Show event subscriptions |
| `/reload <plugin>` | Hot reload a plugin |
| `/unload <plugin>` | Unload a plugin |

---

## Character Classes

| Class | Description | Primary Stats | Playstyle |
|-------|-------------|---------------|-----------|
| Warrior | Melee combat specialist | STR, CON | Tank/DPS |
| Mage | Powerful spellcaster | INT, WIS | Ranged DPS |
| Rogue | Stealth and critical hits | DEX, LCK | Assassin |
| Ranger | Ranged combat and tracking | DEX, WIS | Scout/DPS |
| Paladin | Holy warrior with healing | STR, CHA | Tank/Support |
| Necromancer | Dark magic user | INT, WIS | Summoner |
| Monk | Martial artist | DEX, WIS | DPS/Healer |
| Bard | Support and debuffs | CHA, DEX | Support |
| Druid | Nature magic | WIS, INT | Hybrid |
| Warlock | Dark pact magic | CHA, INT | DPS |

---

## World Locations

### Starting Area
- **Willowbrook Village**: Peaceful starting village with trainers and shops
- **Whispering Woods**: Beginning forest area with low-level creatures
- **King's Highway**: Main road connecting regions

### Major Cities
- **Aurelia**: The capital city with advanced shops and quests
- **Irondeep**: Mining town with blacksmiths and crafting
- **Four Ways Crossroads**: Central hub connecting all regions

### Dangerous Areas
- **Temple of the Forgotten God**: Ancient dungeon with undead enemies
- **Dragon's Peak**: Legendary dragon lair with epic loot
- **Endless Dungeon**: Infinite procedurally generated floors
- **Murkmire Swamp**: Poisonous wetlands with challenging creatures

---

## Plugin System

### Quick Start - Using Decorators

The easiest way to create a plugin is using decorators:

```python
from systems.plugins import plugin, hook, command

@plugin(
    id="my_plugin",
    name="My Plugin",
    version="1.0.0",
    author="Your Name"
)
class MyPlugin:
    """A simple plugin using decorators."""
    
    @hook("player_level_up")
    def on_level_up(self, data):
        player = data.get("player")
        print(f"🎉 Level up! Now level {player.level}")
    
    @command("greet", help_text="Greet the player")
    def cmd_greet(self, args, game):
        return "Hello, brave adventurer!"
```

### Plugin Types

The system supports 6 different plugin types:

| Type | Description | Best For |
|------|-------------|----------|
| **CLASS** | Traditional class-based plugins | Complex plugins with state |
| **FUNCTIONAL** | Function-based plugins | Simple, stateless plugins |
| **DATA** | JSON/YAML data plugins | Content additions (items, enemies) |
| **HYBRID** | Combination of code and data | Full-featured content plugins |
| **MODULE** | Python module packages | Large plugin distributions |
| **ARCHIVE** | ZIP-based plugin bundles | Complete plugin packages |

### Using the Fluent API (PluginBuilder)

For more control, use the PluginBuilder fluent API:

```python
from systems.plugins import PluginBuilder, PluginType

plugin = (PluginBuilder("advanced_plugin")
    .with_name("Advanced Plugin")
    .with_version("2.0.0")
    .with_author("Developer")
    .with_type(PluginType.HYBRID)
    .with_description("An advanced plugin example")
    .with_dependencies(["core_plugin"])
    .on_event("combat_start", self.on_combat_start, priority=10)
    .on_event("combat_end", self.on_combat_end)
    .with_command("heal", self.cmd_heal, 
                  help_text="Heal yourself", 
                  category="combat")
    .with_content_factory("enemy", self.create_enemy)
    .with_content_validator("item", self.validate_item)
    .build()
)
```

### Creating Custom Content

Register content factories to add new game content:

```python
def create_enemy(data):
    """Factory function to create custom enemies."""
    from core.engine import Enemy
    return Enemy(
        name=data["name"],
        level=data["level"],
        hp=data["hp"],
        attack=data["attack"],
        defense=data["defense"]
    )

# Register in plugin
def on_load(self, game):
    game.plugins.content_registry.register_factory("enemy", create_enemy)
```

### Event System

Subscribe to events with priority-based handling:

```python
from systems.plugins import EventPriority

# Higher priority = executed first
@hook("player_death", priority=EventPriority.HIGHEST)
def prevent_death(self, data):
    player = data["player"]
    if player.has_item("phoenix_feather"):
        player.hp = player.max_hp // 2
        player.remove_item("phoenix_feather")
        return {"cancelled": True, "message": "Phoenix Feather saved you!"}

@hook("player_death", priority=EventPriority.MONITOR)
def log_death(self, data):
    # This runs last, after all other handlers
    print(f"Death event processed for {data['player'].name}")
```

**Available Event Priorities:**
| Priority | Value | Use Case |
|----------|-------|----------|
| HIGHEST | 100 | Override/cancel events |
| HIGH | 75 | Important processing |
| NORMAL | 50 | Default handling |
| LOW | 25 | Secondary effects |
| LOWEST | 1 | Cleanup/logging |
| MONITOR | 0 | Read-only observation |

### Command System

Register commands with categories and permissions:

```python
@command(
    "teleport",
    help_text="Teleport to a location",
    category="admin",
    permission="admin.teleport"
)
def cmd_teleport(self, args, game):
    if not args:
        return "Usage: /teleport <location_id>"
    location_id = args[0]
    game.world.travel_to(location_id)
    return f"Teleported to {location_id}!"
```

### Hot Reload

Enable hot reload for development:

```python
from systems.plugins import IHotReloadablePlugin

class DevPlugin(IHotReloadablePlugin):
    def get_state(self):
        """Return state to preserve across reloads."""
        return {"counter": self.counter}
    
    def restore_state(self, state):
        """Restore state after reload."""
        self.counter = state.get("counter", 0)
    
    def on_reload(self, game):
        """Called after hot reload."""
        print(f"Plugin reloaded! Counter: {self.counter}")
```

### JSON Plugin Format

For data-only plugins, use JSON:

```json
{
    "plugin_info": {
        "id": "legendary_weapons",
        "name": "Legendary Weapons Pack",
        "version": "1.0.0",
        "author": "YSNRFD"
    },
    "content": {
        "items": [
            {
                "id": "excalibur",
                "name": "Excalibur",
                "type": "weapon",
                "rarity": "divine",
                "stats": {"attack": 150, "strength": 50}
            }
        ]
    }
}
```

### Available Event Hooks

| Event | Description | Data |
|-------|-------------|------|
| `game_start` | Game initialized | `{game}` |
| `game_end` | Game shutting down | `{game}` |
| `player_create` | New character created | `{player}` |
| `player_level_up` | Player leveled up | `{player, old_level, new_level}` |
| `player_death` | Player died | `{player, killer}` |
| `combat_start` | Combat initiated | `{player, enemies}` |
| `combat_end` | Combat finished | `{player, enemies, victory}` |
| `combat_turn` | Combat turn processed | `{player, enemy, action}` |
| `item_pickup` | Item picked up | `{player, item}` |
| `item_use` | Item used | `{player, item, target}` |
| `item_equip` | Item equipped | `{player, item, slot}` |
| `quest_start` | Quest accepted | `{player, quest}` |
| `quest_complete` | Quest completed | `{player, quest, rewards}` |
| `location_enter` | Entered location | `{player, location}` |
| `location_exit` | Left location | `{player, location}` |

For detailed plugin documentation, see [plugins/README.md](plugins/README.md).

---

## Project Structure

```
legends-of-eldoria/
├── README.md                    # This file - Project overview
├── LICENSE.md                   # License file
├── LICENSE.txt                  # Plain text license
│
└── rpg_game/                    # Game directory
    ├── README.md                # Game documentation
    ├── main.py                  # Main game entry point
    ├── LICENSE.md               # License file
    ├── LICENSE.txt              # Plain text license
    │
    ├── core/                    # Core game systems
    │   ├── engine.py            # Game engine and base classes
    │   ├── character.py         # Character system
    │   └── items.py             # Item definitions
    │
    ├── systems/                 # Game systems
    │   ├── combat.py            # Combat system
    │   ├── world.py             # World and locations
    │   ├── quests.py            # Quest management
    │   ├── npc.py               # NPC system
    │   ├── crafting.py          # Crafting system
    │   ├── save_load.py         # Save/Load functionality
    │   └── plugins.py           # Plugin architecture
    │
    ├── plugins/                 # Plugin directory
    │   ├── README.md            # Plugin development guide
    │   ├── base_plugin_template.py
    │   ├── json_plugin_template.json
    │   └── *.py                 # Sample plugins
    │
    └── saves/                   # Save files directory
```

---

## Game Tips

1. **Start with Quests**: Talk to Elder Thorne in Willowbrook Village to begin your adventure
2. **Manage Resources**: Keep health potions for emergencies - you never know when a boss appears
3. **Explore Carefully**: Higher danger areas have better rewards but stronger enemies
4. **Rest When Needed**: Find inns in towns to fully restore HP and MP
5. **Upgrade Equipment**: Visit blacksmiths and shops regularly for better gear
6. **Level Up Skills**: Training improves your crafting success rates and combat abilities
7. **Use Plugins**: Extend the game with community plugins or create your own

---

## Contributing

Contributions are welcome! Here's how to help:

1. **Fork the repository** on GitHub
2. **Create a feature branch** (`git checkout -b feature/amazing-feature`)
3. **Commit your changes** (`git commit -m 'Add amazing feature'`)
4. **Push to the branch** (`git push origin feature/amazing-feature`)
5. **Open a Pull Request**

### Code Style
- Follow PEP 8 guidelines
- Add docstrings to all public functions and classes
- Write tests for new features
- Update documentation as needed

---

## License

This project is licensed under the **Open Development License**.

### Key Points:
- ✅ Free for personal and commercial use
- ✅ Modification and distribution allowed
- ✅ Plugin development encouraged
- 📋 Attribution to YSNRFD required
- ❌ No ownership claims allowed
- ❌ No liability

See [LICENSE.md](LICENSE.md) or [LICENSE.txt](LICENSE.txt) for full license text.

---

## Acknowledgments

- Inspired by classic text-based RPGs and MUDs
- Built with Python for maximum compatibility
- Designed for extensibility through the plugin system
- Community-driven development and improvement

---

<div align="center">

**Enjoy your adventure in Legends of Eldoria!** 🎮⚔️🐉

Made with ❤️ by [YSNRFD](https://github.com/ysnrfd)

[GitHub](https://github.com/ysnrfd/legends-of-eldoria) · [Report Bug](https://github.com/ysnrfd/legends-of-eldoria/issues) · [Request Feature](https://github.com/ysnrfd/legends-of-eldoria/issues)

</div>

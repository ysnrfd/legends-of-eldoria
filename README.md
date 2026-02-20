# LEGENDS OF ELDORIA - Open Source Text-Based RPG

![Version](https://img.shields.io/badge/version-1.0.0-blue)
![Python](https://img.shields.io/badge/python-3.8%2B-green)
![License](https://img.shields.io/badge/license-Open%20Development-green)

**Creator:** YSNRFD | **GitHub:** [github.com/ysnrfd](https://github.com/ysnrfd) | **Email:** rfdysn@gmail.com

A fully-featured, open-world text-based RPG game with a powerful dynamic plugin architecture.

> **No ownership claims allowed**
> |
> **Free for development and expansion**

## 📚 Documentation

| Document | Description |
|----------|-------------|
| [rpg_game/README.md](rpg_game/README.md) | Game features, installation, and how to play |
| [rpg_game/plugins/README.md](rpg_game/plugins/README.md) | Plugin development guide |

---

## 📑 Table of Contents

- [LEGENDS OF ELDORIA - Open Source Text-Based RPG](#legends-of-eldoria---open-source-text-based-rpg)
  - [📚 Documentation](#-documentation)
  - [📑 Table of Contents](#-table-of-contents)
  - [Overview](#overview)
  - [Features](#features)
  - [Quick Start](#quick-start)
    - [Requirements](#requirements)
    - [Installation](#installation)
  - [Repository Structure](#repository-structure)
  - [Contributing](#contributing)
    - [Code Style](#code-style)
  - [License](#license)
    - [Key Points:](#key-points)
  - [Acknowledgments](#acknowledgments)

---

## Overview

Legends of Eldoria is a fully-featured, open-world text-based RPG built in Python. The game features a powerful dynamic plugin architecture that allows developers to extend the game without modifying core code.

## Features

- **🎮 Open World Exploration** - Travel through diverse locations including villages, cities, forests, mountains, dungeons, and more
- **⚔️ Turn-Based Combat** - Strategic combat system with abilities, status effects, and critical hits
- **🎒 Equipment & Items** - 100+ items with 7 rarity tiers and full equipment customization
- **🛠️ Crafting System** - Blacksmithing, Alchemy, Enchanting, Cooking, Jewelcrafting, and Leatherworking
- **🔌 Dynamic Plugin System** - Production-ready plugin architecture with 6 plugin types, event system, and hot reload
- **💾 Save System** - Multiple save slots with auto-save and cross-platform compatibility

See [rpg_game/README.md](rpg_game/README.md) for detailed feature documentation.


---

## Quick Start

### Requirements
- Python 3.8 or higher
- No external dependencies required!

### Installation

```bash
# Clone the repository
git clone https://github.com/ysnrfd/legends-of-eldoria.git

# Navigate to game directory
cd rpg_game

# Run the game
python main.py
```

For detailed installation and gameplay instructions, see [rpg_game/README.md](rpg_game/README.md).


---

## Repository Structure

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

For plugin development, see [rpg_game/plugins/README.md](rpg_game/plugins/README.md).


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

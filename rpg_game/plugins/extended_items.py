"""
Extended Items Plugin - New Weapons, Armor, and Consumables
Demonstrates comprehensive item system with content provider pattern
"""

from __future__ import annotations
from systems.plugins import (
    PluginBase, PluginInfo, PluginType, PluginPriority,
    IContentProvider, IHotReloadablePlugin
)
from core.engine import Rarity, DamageType, StatType, EventType
from typing import Dict, List, Any


class ExtendedItemsPlugin(PluginBase, IContentProvider, IHotReloadablePlugin):
    """
    Extended Items plugin with comprehensive item additions.
    
    Features:
    - New weapon types
    - New armor sets
    - New consumables
    - New accessories
    - Crafting materials
    """
    
    @property
    def info(self) -> PluginInfo:
        return PluginInfo(
            id="extended_items",
            name="Extended Items",
            version="2.0.0",
            author="YSNRFD",
            description="Adds new weapons, armor, consumables, accessories, and materials "
                       "to expand the game's item system.",
            
            dependencies=[],
            soft_dependencies=["enhanced_combat"],
            conflicts=[],
            provides=["extended_items"],
            
            priority=PluginPriority.NORMAL.value,
            plugin_type=PluginType.CLASS,
            
            configurable=True,
            config_schema={
                "legendary_drop_rate": {
                    "type": "number", "default": 0.01, "min": 0, "max": 1
                },
                "enable_custom_items": {
                    "type": "boolean", "default": True
                }
            },
            default_config={
                "legendary_drop_rate": 0.01,
                "enable_custom_items": True
            },
            
            supports_hot_reload=True,
            tags=["items", "equipment", "loot"],
            custom={"item_count": 12}
        )
    
    # =========================================================================
    # Lifecycle
    # =========================================================================
    
    def on_load(self, game):
        print("[Extended Items] Loading extended item collection...")
        self._config = self.info.default_config.copy()
    
    def on_unload(self, game):
        print("[Extended Items] Unloading...")
    
    def on_before_reload(self, game) -> Dict[str, Any]:
        return {"config": self._config.copy()}
    
    def on_after_reload(self, game, state: Dict[str, Any]) -> None:
        self._config = state.get("config", self.info.default_config)
    
    # =========================================================================
    # Content Provider Implementation
    # =========================================================================
    
    def get_content_types(self) -> List[str]:
        return ["items"]
    
    def get_content(self, content_type: str) -> Dict[str, Any]:
        if content_type == "items":
            return self.get_all_items()
        return {}
    
    def register_content(self, content_registry) -> Dict[str, Dict]:
        return {"items": self.get_all_items()}
    
    def get_all_items(self) -> Dict[str, Dict]:
        """Get all items from this plugin"""
        items = {}
        items.update(self._get_weapons())
        items.update(self._get_armor())
        items.update(self._get_consumables())
        items.update(self._get_accessories())
        items.update(self._get_materials())
        return items
    
    # =========================================================================
    # Item Definitions
    # =========================================================================
    
    def _get_weapons(self) -> Dict[str, Dict]:
        """New weapons"""
        return {
            # Epic Weapons
            "thunder_hammer": {
                "name": "Thunder Hammer",
                "item_type": "weapon",
                "rarity": "Epic",
                "value": 3500,
                "weight": 8.0,
                "description": "A massive hammer that crackles with lightning. "
                             "Each strike echoes with thunder.",
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
            
            "void_dagger": {
                "name": "Void Dagger",
                "item_type": "weapon",
                "rarity": "Legendary",
                "value": 8000,
                "weight": 0.3,
                "description": "A dagger forged from pure darkness. "
                             "It seems to absorb light around it.",
                "damage_min": 12,
                "damage_max": 24,
                "damage_type": "dark",
                "attack_speed": 1.8,
                "critical_chance": 0.25,
                "critical_damage": 3.0,
                "level_required": 18,
                "stat_requirements": {"dexterity": 18},
                "special_effects": ["Shadow Step on kill", "Life Steal 10%"]
            },
            
            "holy_lance": {
                "name": "Holy Lance",
                "item_type": "weapon",
                "rarity": "Epic",
                "value": 4000,
                "weight": 4.0,
                "description": "A blessed lance that glows with divine light. "
                             "Effective against unholy creatures.",
                "damage_min": 15,
                "damage_max": 28,
                "damage_type": "holy",
                "attack_speed": 1.0,
                "critical_chance": 0.12,
                "range": 2,
                "level_required": 14,
                "stat_requirements": {"strength": 14, "charisma": 12},
                "special_effects": ["+50% damage to undead", "Divine Smite ability"]
            },
            
            "frost_staff": {
                "name": "Staff of the Frozen North",
                "item_type": "weapon",
                "rarity": "Epic",
                "value": 4500,
                "weight": 2.5,
                "description": "A staff carved from eternal ice. "
                             "Frost crystals form wherever it touches.",
                "damage_min": 8,
                "damage_max": 18,
                "damage_type": "ice",
                "attack_speed": 0.9,
                "critical_chance": 0.08,
                "stat_bonuses": {"intelligence": 5, "wisdom": 3},
                "level_required": 15,
                "stat_requirements": {"intelligence": 16},
                "special_effects": ["Freeze chance 15%", "Ice Armor spell"]
            },
            
            # Rare Weapons
            "steel_katana": {
                "name": "Steel Katana",
                "item_type": "weapon",
                "rarity": "Rare",
                "value": 800,
                "weight": 2.0,
                "description": "A finely crafted katana with a razor-sharp edge.",
                "damage_min": 10,
                "damage_max": 18,
                "damage_type": "physical",
                "attack_speed": 1.4,
                "critical_chance": 0.15,
                "level_required": 8
            }
        }
    
    def _get_armor(self) -> Dict[str, Dict]:
        """New armor"""
        return {
            # Legendary Armor
            "dragon_plate": {
                "name": "Dragon Plate Armor",
                "item_type": "armor",
                "rarity": "Legendary",
                "value": 30000,
                "weight": 25.0,
                "description": "Armor forged from the scales of an ancient dragon. "
                             "Even dragonfire cannot pierce it.",
                "slot": "chest",
                "defense": 50,
                "magic_defense": 30,
                "resistances": {"fire": 0.7, "physical": 0.3},
                "stat_bonuses": {"strength": 5, "constitution": 5},
                "level_required": 25,
                "stat_requirements": {"strength": 18},
                "special_effects": ["Dragon's Fury on hit", "Fire immunity"]
            },
            
            # Epic Armor
            "shadow_cloak": {
                "name": "Shadow Cloak",
                "item_type": "armor",
                "rarity": "Epic",
                "value": 2500,
                "weight": 1.0,
                "description": "A cloak woven from shadows. "
                             "Makes the wearer harder to detect.",
                "slot": "chest",
                "defense": 8,
                "magic_defense": 15,
                "stat_bonuses": {"dexterity": 3, "luck": 2},
                "level_required": 10,
                "special_effects": ["Stealth +20%", "Shadow Meld ability"]
            },
            
            "crown_of_wisdom": {
                "name": "Crown of Wisdom",
                "item_type": "armor",
                "rarity": "Epic",
                "value": 5000,
                "weight": 0.5,
                "description": "A mystical crown that enhances mental capabilities.",
                "slot": "head",
                "defense": 5,
                "magic_defense": 20,
                "stat_bonuses": {"intelligence": 5, "wisdom": 5},
                "level_required": 15,
                "special_effects": ["MP Regeneration +5", "Spell Power +15%"]
            },
            
            # Rare Armor
            "leather_vest": {
                "name": "Reinforced Leather Vest",
                "item_type": "armor",
                "rarity": "Rare",
                "value": 400,
                "weight": 3.0,
                "description": "Sturdy leather armor with metal reinforcement.",
                "slot": "chest",
                "defense": 12,
                "magic_defense": 5,
                "level_required": 5
            }
        }
    
    def _get_consumables(self) -> Dict[str, Dict]:
        """New consumables"""
        return {
            # Epic Consumables
            "elixir_of_power": {
                "name": "Elixir of Power",
                "item_type": "consumable",
                "rarity": "Epic",
                "value": 500,
                "weight": 0.3,
                "description": "A powerful elixir that temporarily increases strength.",
                "temporary_effects": [("strength_buff", 10, 5)],
                "use_message": "You feel immense power flowing through you!"
            },
            
            "phoenix_feather": {
                "name": "Phoenix Feather",
                "item_type": "consumable",
                "rarity": "Legendary",
                "value": 2000,
                "weight": 0.1,
                "description": "A feather from a phoenix. "
                             "Automatically revives you upon death once.",
                "use_message": "The phoenix feather burns with eternal flame.",
                "special_effects": ["Auto-revive on death"]
            },
            
            # Rare Consumables
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
            
            "antidote_plus": {
                "name": "Greater Antidote",
                "item_type": "consumable",
                "rarity": "Uncommon",
                "value": 75,
                "weight": 0.1,
                "description": "Cures poison and provides resistance.",
                "effects": ["cure_poison", "poison_resistance_5_turns"],
                "use_message": "The antidote cleanses your system."
            },
            
            # Common Consumables
            "ration": {
                "name": "Travel Ration",
                "item_type": "consumable",
                "rarity": "Common",
                "value": 10,
                "weight": 0.5,
                "description": "Dried meat and bread for traveling.",
                "hp_restore": 15,
                "use_message": "You eat the travel ration."
            }
        }
    
    def _get_accessories(self) -> Dict[str, Dict]:
        """New accessories"""
        return {
            # Epic Accessories
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
            
            "amulet_of_the_mage": {
                "name": "Amulet of the Mage",
                "item_type": "accessory",
                "rarity": "Epic",
                "value": 3000,
                "weight": 0.2,
                "description": "An amulet that greatly enhances magical abilities.",
                "stat_bonuses": {"intelligence": 6, "wisdom": 4},
                "special_effects": ["Magic Power +25%", "MP Regeneration +5"],
                "level_required": 10
            },
            
            # Rare Accessories
            "warrior_pendant": {
                "name": "Warrior's Pendant",
                "item_type": "accessory",
                "rarity": "Rare",
                "value": 800,
                "weight": 0.1,
                "description": "A pendant blessed by warriors of old.",
                "stat_bonuses": {"strength": 3, "constitution": 2},
                "level_required": 5
            },
            
            "lucky_coin": {
                "name": "Lucky Coin",
                "item_type": "accessory",
                "rarity": "Rare",
                "value": 500,
                "weight": 0.05,
                "description": "A coin said to bring good fortune.",
                "stat_bonuses": {"luck": 5},
                "special_effects": ["Gold Find +20%", "Item Find +10%"],
                "level_required": 1
            }
        }
    
    def _get_materials(self) -> Dict[str, Dict]:
        """New crafting materials"""
        return {
            "dragon_scale": {
                "name": "Dragon Scale",
                "item_type": "material",
                "rarity": "Epic",
                "value": 500,
                "weight": 0.5,
                "description": "A scale from a dragon. Used in legendary crafting."
            },
            
            "magic_crystal": {
                "name": "Magic Crystal",
                "item_type": "material",
                "rarity": "Rare",
                "value": 100,
                "weight": 0.1,
                "description": "A crystal infused with magical energy."
            },
            
            "enchanted_essence": {
                "name": "Enchanted Essence",
                "item_type": "material",
                "rarity": "Epic",
                "value": 300,
                "weight": 0.1,
                "description": "Pure magical essence extracted from powerful items."
            }
        }
    
    # =========================================================================
    # Legacy Support
    # =========================================================================
    
    def register_items(self, item_registry) -> Dict[str, Any]:
        return self.get_all_items()
    
    # =========================================================================
    # Event Hooks
    # =========================================================================
    
    def register_hooks(self, event_system) -> Dict:
        return {
            EventType.ITEM_PICKUP: self._on_item_pickup,
            EventType.ITEM_EQUIP: self._on_item_equip
        }
    
    def _on_item_pickup(self, data):
        item = data.get("item")
        player = data.get("player")
        
        if item and hasattr(item, 'rarity'):
            if item.rarity == Rarity.LEGENDARY:
                print(f"🌟 LEGENDARY item found: {item.name}!")
            elif item.rarity == Rarity.EPIC:
                print(f"✨ Epic item discovered: {item.name}!")
        
        return None
    
    def _on_item_equip(self, data):
        item = data.get("item")
        player = data.get("player")
        
        if item and hasattr(item, 'special_effects'):
            effects = item.special_effects
            if effects:
                print(f"  Special effects: {', '.join(effects)}")
        
        return None
    
    # =========================================================================
    # Commands
    # =========================================================================
    
    def register_commands(self, command_system) -> Dict:
        return {
            "item_list": {
                "handler": self._cmd_list,
                "help": "List extended items",
                "category": "info"
            }
        }
    
    def _cmd_list(self, game, args, context):
        items = self.get_all_items()
        
        # Group by type
        by_type = {}
        for item_id, item_data in items.items():
            item_type = item_data.get("item_type", "unknown")
            if item_type not in by_type:
                by_type[item_type] = []
            by_type[item_type].append((item_id, item_data))
        
        lines = ["Extended Items:", "=" * 50]
        for item_type, items_list in sorted(by_type.items()):
            lines.append(f"\n[{item_type.upper()}]")
            for item_id, item_data in items_list:
                rarity = item_data.get("rarity", "Common")
                name = item_data.get("name", item_id)
                lines.append(f"  • {name} ({rarity})")
        
        lines.append(f"\nTotal: {len(items)} items")
        return "\n".join(lines)


# Plugin instance
plugin = ExtendedItemsPlugin()

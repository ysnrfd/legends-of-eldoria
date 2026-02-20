"""
Extended Items Plugin - New Weapons, Armor, and Consumables
Demonstrates comprehensive item system with content provider pattern.
"""

from __future__ import annotations
from systems.plugins import Plugin, PluginInfo, PluginPriority, EventType
from core.engine import Rarity
from typing import Dict, List, Any


class ExtendedItemsPlugin(Plugin):
    """
    Extended Items plugin with comprehensive item additions.
    
    Features:
    - New weapon types (elemental, legendary)
    - New armor sets (dragon, shadow, mage)
    - New consumables (potions, elixirs)
    - New accessories (rings, amulets)
    - Crafting materials
    - Crafting recipes
    - Drop rate configuration
    """
    
    def __init__(self):
        info = PluginInfo(
            id="extended_items",
            name="Extended Items",
            version="2.0.0",
            author="YSNRFD",
            description="Adds new weapons, armor, consumables, accessories, materials, "
                       "and crafting recipes to expand the game's item system.",
            dependencies=[],
            soft_dependencies=["enhanced_combat"],
            conflicts=[],
            priority=PluginPriority.NORMAL,
            tags=["items", "equipment", "loot", "crafting"]
        )
        super().__init__(info)
        self._config: Dict[str, Any] = {}
    
    def on_load(self, game) -> bool:
        """Initialize extended items"""
        print("[Extended Items] Loading extended item collection...")
        
        self._config = {
            "legendary_drop_rate": 0.01,
            "epic_drop_rate": 0.05,
            "rare_drop_rate": 0.15,
            "enable_custom_items": True,
            "crafting_bonus": 1.0
        }
        
        return True
    
    def on_unload(self, game) -> bool:
        """Cleanup"""
        print("[Extended Items] Unloading...")
        return True
    
    def on_enable(self, game) -> bool:
        """Enable items"""
        print("[Extended Items] Enabled!")
        return True
    
    def on_disable(self, game) -> bool:
        """Disable items"""
        return True
    
    def register_hooks(self, event_system) -> Dict[EventType, Any]:
        """
        Register item-related event hooks.
        
        Returns:
            Dict mapping EventType to handler functions
        """
        return {
            EventType.ITEM_PICKUP: self._on_item_pickup,
            EventType.ITEM_EQUIP: self._on_item_equip,
            EventType.ITEM_USE: self._on_item_use,
        }
    
    def _on_item_pickup(self, game, data):
        """Handle rare item discoveries"""
        item = data.get("item")
        player = data.get("player")
        
        if not item or not hasattr(item, 'rarity'):
            return
        
        # Announce legendary/epic finds
        if item.rarity == Rarity.LEGENDARY:
            print(f"🌟 LEGENDARY item found: {item.name}!")
            if player:
                print(f"   This will serve you well, {player.name}!")
        elif item.rarity == Rarity.EPIC:
            print(f"✨ Epic item discovered: {item.name}!")
    
    def _on_item_equip(self, game, data):
        """Handle item equips"""
        item = data.get("item")
        
        if item and hasattr(item, 'special_effects'):
            effects = item.special_effects
            if effects:
                print(f"  Special effects active: {', '.join(effects)}")
    
    def _on_item_use(self, game, data):
        """Handle item usage"""
        item = data.get("item")
        
        if item and hasattr(item, 'use_message'):
            print(f"  {item.use_message}")
    
    def register_commands(self, command_system) -> Dict[str, Any]:
        """
        Register item-related commands.
        
        Returns:
            Dict mapping command names to handler info
        """
        return {
            "item_list": {
                "handler": self._cmd_list,
                "help": "List all extended items by category",
                "category": "info"
            },
            "item_config": {
                "handler": self._cmd_config,
                "help": "Configure item drop rates",
                "usage": "/item_config [key] [value]",
                "category": "config"
            },
            "item_search": {
                "handler": self._cmd_search,
                "help": "Search for items by name or type",
                "usage": "/item_search <query>",
                "category": "info"
            },
            "recipes": {
                "handler": self._cmd_recipes,
                "help": "List all crafting recipes",
                "category": "info"
            }
        }
    
    def _cmd_list(self, game, args, context) -> str:
        """List all extended items"""
        items = self._get_all_items()
        
        # Group by type
        by_type: Dict[str, List] = {}
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
                level = item_data.get("level_required", 1)
                lines.append(f"  • {name} ({rarity}) - Lv.{level}")
        
        lines.append(f"\nTotal: {len(items)} items")
        return "\n".join(lines)
    
    def _cmd_config(self, game, args, context) -> str:
        """Configure item settings"""
        if not args:
            return f"Item Config: {self._config}"
        
        if len(args) == 1:
            key = args[0]
            return f"{key} = {self._config.get(key, 'Not found')}"
        
        key, value = args[0], args[1]
        
        # Parse value
        if value.lower() in ("true", "yes", "1", "on"):
            value = True
        elif value.lower() in ("false", "no", "0", "off"):
            value = False
        else:
            try:
                value = float(value)
            except ValueError:
                pass
        
        old_value = self._config.get(key)
        self._config[key] = value
        
        return f"Set {key}: {old_value} -> {value}"
    
    def _cmd_search(self, game, args, context) -> str:
        """Search for items"""
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
    
    def _cmd_recipes(self, game, args, context) -> str:
        """List all crafting recipes"""
        recipes = self._get_recipes()
        
        lines = ["Crafting Recipes:", "=" * 50]
        for recipe_id, recipe in recipes.items():
            result = recipe.get("result", "unknown")
            result_qty = recipe.get("result_quantity", 1)
            skill = recipe.get("skill_required", "None")
            level = recipe.get("skill_level", 0)
            
            lines.append(f"\n{recipe.get('name', recipe_id)}:")
            lines.append(f"  Result: {result} x{result_qty}")
            lines.append(f"  Skill: {skill} (Lv.{level})")
            lines.append(f"  Ingredients: {recipe.get('ingredients', {})}")
        
        return "\n".join(lines)
    
    def _get_all_items(self) -> Dict[str, Dict]:
        """Get all items from this plugin"""
        items = {}
        items.update(self._get_weapons())
        items.update(self._get_armor())
        items.update(self._get_consumables())
        items.update(self._get_accessories())
        items.update(self._get_materials())
        return items
    
    def register_items(self, item_registry) -> Dict[str, Dict]:
        """
        Register items provided by this plugin.
        
        Returns:
            Dict mapping item IDs to item data
        """
        return self._get_all_items()
    
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
            "void_dagger": {
                "name": "Void Dagger",
                "item_type": "weapon",
                "rarity": "Legendary",
                "value": 8000,
                "weight": 0.3,
                "description": "A dagger forged from pure darkness.",
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
                "description": "A blessed lance that glows with divine light.",
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
                "description": "A staff carved from eternal ice.",
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
            },
            "flame_sword": {
                "name": "Flame Tongue",
                "item_type": "weapon",
                "rarity": "Epic",
                "value": 3200,
                "weight": 3.0,
                "description": "A blade that burns with eternal flame.",
                "damage_min": 14,
                "damage_max": 26,
                "damage_type": "fire",
                "attack_speed": 1.0,
                "critical_chance": 0.12,
                "level_required": 12,
                "special_effects": ["Burn damage over time", "Fire resistance +20%"]
            }
        }
    
    def _get_armor(self) -> Dict[str, Dict]:
        """New armor"""
        return {
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
                "stat_requirements": {"strength": 18},
                "special_effects": ["Dragon's Fury on hit", "Fire immunity"]
            },
            "shadow_cloak": {
                "name": "Shadow Cloak",
                "item_type": "armor",
                "rarity": "Epic",
                "value": 2500,
                "weight": 1.0,
                "description": "A cloak woven from shadows.",
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
            },
            "mage_robes": {
                "name": "Archmage Robes",
                "item_type": "armor",
                "rarity": "Epic",
                "value": 2800,
                "weight": 1.0,
                "description": "Robes worn by master spellcasters.",
                "slot": "chest",
                "defense": 6,
                "magic_defense": 25,
                "stat_bonuses": {"intelligence": 4, "wisdom": 4},
                "level_required": 12,
                "special_effects": ["Spell cost reduction -15%", "Magic find +10%"]
            }
        }
    
    def _get_consumables(self) -> Dict[str, Dict]:
        """New consumables"""
        return {
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
                "description": "A feather from a phoenix. Automatically revives you once.",
                "use_message": "The phoenix feather burns with eternal flame.",
                "special_effects": ["Auto-revive on death"]
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
            "ration": {
                "name": "Travel Ration",
                "item_type": "consumable",
                "rarity": "Common",
                "value": 10,
                "weight": 0.5,
                "description": "Dried meat and bread for traveling.",
                "hp_restore": 15,
                "use_message": "You eat the travel ration."
            },
            "mana_crystal": {
                "name": "Mana Crystal",
                "item_type": "consumable",
                "rarity": "Rare",
                "value": 250,
                "weight": 0.1,
                "description": "A crystal that restores magical energy.",
                "mp_restore": 100,
                "use_message": "The crystal dissolves, flooding you with mana!"
            }
        }
    
    def _get_accessories(self) -> Dict[str, Dict]:
        """New accessories"""
        return {
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
            },
            "elemental_ring": {
                "name": "Ring of Elements",
                "item_type": "accessory",
                "rarity": "Epic",
                "value": 3500,
                "weight": 0.1,
                "description": "A ring that channels elemental power.",
                "stat_bonuses": {"intelligence": 3, "wisdom": 3},
                "special_effects": ["Elemental damage +15%", "Elemental resistance +10%"],
                "level_required": 15
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
            },
            "iron_ingot": {
                "name": "Iron Ingot",
                "item_type": "material",
                "rarity": "Common",
                "value": 20,
                "weight": 1.0,
                "description": "A refined iron ingot for crafting."
            },
            "leather_hide": {
                "name": "Leather Hide",
                "item_type": "material",
                "rarity": "Common",
                "value": 15,
                "weight": 0.5,
                "description": "Treated leather for armor crafting."
            }
        }
    
    def _get_recipes(self) -> Dict[str, Dict]:
        """Crafting recipes"""
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
            "shadow_cloak_recipe": {
                "name": "Shadow Cloak Recipe",
                "category": "armor",
                "result": "shadow_cloak",
                "result_quantity": 1,
                "ingredients": {"leather_hide": 4, "magic_crystal": 2, "enchanted_essence": 1},
                "skill_required": "Crafting",
                "skill_level": 12,
                "time": 3,
                "gold_cost": 400,
                "experience": 80
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
            },
            "ring_of_shadows_recipe": {
                "name": "Ring of Shadows Recipe",
                "category": "jewelry",
                "result": "ring_of_shadows",
                "result_quantity": 1,
                "ingredients": {"iron_ingot": 2, "magic_crystal": 3, "enchanted_essence": 2},
                "skill_required": "Crafting",
                "skill_level": 14,
                "time": 3,
                "gold_cost": 600,
                "experience": 90
            },
            "steel_katana_recipe": {
                "name": "Steel Katana Recipe",
                "category": "weapons",
                "result": "steel_katana",
                "result_quantity": 1,
                "ingredients": {"iron_ingot": 3, "leather_hide": 1},
                "skill_required": "Crafting",
                "skill_level": 6,
                "time": 2,
                "gold_cost": 150,
                "experience": 35
            }
        }
    
    def register_recipes(self, crafting_manager) -> Dict[str, Dict]:
        """
        Register crafting recipes provided by this plugin.
        
        Returns:
            Dict mapping recipe IDs to recipe data
        """
        return self._get_recipes()


# Plugin instance - REQUIRED
plugin = ExtendedItemsPlugin()

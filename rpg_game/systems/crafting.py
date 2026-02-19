"""
Crafting System - Create Items, Equipment, and Consumables
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any, TYPE_CHECKING
from enum import Enum
import sys
import os
import random
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.engine import Rarity, StatType
from core.items import Item, Weapon, Armor, Consumable, Material, get_item, ItemFactory

if TYPE_CHECKING:
    from core.character import Character


class CraftingCategory(Enum):
    BLACKSMITH = "blacksmith"
    ALCHEMY = "alchemy"
    ENCHANTING = "enchanting"
    COOKING = "cooking"
    JEWELCRAFTING = "jewelcrafting"
    LEATHERWORKING = "leatherworking"
    TAILORING = "tailoring"


@dataclass
class CraftingRecipe:
    """A crafting recipe"""
    id: str
    name: str
    category: CraftingCategory
    result_item: str
    result_quantity: int = 1
    materials: Dict[str, int] = field(default_factory=dict)
    skill_required: str = "Crafting"
    skill_level: int = 1
    tools_required: List[str] = field(default_factory=list)
    success_rate: float = 0.9
    quality_range: Tuple[int, int] = (1, 3)
    experience_gained: int = 10
    description: str = ""
    
    def can_craft(self, player: 'Character') -> Tuple[bool, str]:
        """Check if player can craft this recipe"""
        # Check skill level
        skill = player.skills.get(self.skill_required)
        if not skill or skill.current_level < self.skill_level:
            return False, f"Requires {self.skill_required} level {self.skill_level}"
        
        # Check materials
        for material_id, quantity in self.materials.items():
            if not player.inventory.has_item(material_id.replace("_", " ").title(), quantity):
                return False, f"Missing materials"
        
        # Check tools
        for tool in self.tools_required:
            if not player.inventory.has_item(tool):
                return False, f"Missing tool: {tool}"
        
        return True, "Can craft"
    
    def get_materials_display(self) -> str:
        """Get materials needed display"""
        lines = []
        for material_id, quantity in self.materials.items():
            lines.append(f"  • {material_id.replace('_', ' ').title()}: {quantity}")
        return "\n".join(lines)
    
    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "name": self.name,
            "category": self.category.value,
            "result_item": self.result_item,
            "result_quantity": self.result_quantity,
            "materials": self.materials,
            "skill_required": self.skill_required,
            "skill_level": self.skill_level,
            "tools_required": self.tools_required,
            "success_rate": self.success_rate,
            "quality_range": self.quality_range,
            "experience_gained": self.experience_gained,
            "description": self.description
        }


class CraftingManager:
    """Manages crafting recipes and processes"""
    
    def __init__(self):
        self.recipes: Dict[str, CraftingRecipe] = {}
        self._init_recipes()
    
    def _init_recipes(self):
        """Initialize crafting recipes"""
        recipes_data = [
            # Blacksmith Recipes
            {
                "id": "craft_iron_sword",
                "name": "Iron Sword",
                "category": CraftingCategory.BLACKSMITH,
                "result_item": "iron_sword",
                "materials": {"iron_ore": 3, "coal": 1},
                "skill_required": "Crafting",
                "skill_level": 1,
                "tools_required": ["hammer"],
                "success_rate": 0.85,
                "experience_gained": 15,
                "description": "Forge a basic iron sword."
            },
            {
                "id": "craft_steel_sword",
                "name": "Steel Sword",
                "category": CraftingCategory.BLACKSMITH,
                "result_item": "steel_greatsword",
                "materials": {"steel_ingot": 3, "iron_ore": 2, "coal": 2},
                "skill_required": "Crafting",
                "skill_level": 3,
                "tools_required": ["hammer", "anvil"],
                "success_rate": 0.75,
                "experience_gained": 30,
                "description": "Forge a quality steel sword."
            },
            {
                "id": "craft_leather_armor",
                "name": "Leather Armor",
                "category": CraftingCategory.LEATHERWORKING,
                "result_item": "leather_armor",
                "materials": {"leather": 5, "thread": 2},
                "skill_required": "Crafting",
                "skill_level": 1,
                "tools_required": ["needle"],
                "success_rate": 0.9,
                "experience_gained": 20,
                "description": "Craft basic leather armor."
            },
            {
                "id": "craft_chainmail",
                "name": "Chainmail",
                "category": CraftingCategory.BLACKSMITH,
                "result_item": "chainmail",
                "materials": {"iron_ore": 5, "steel_ingot": 2},
                "skill_required": "Crafting",
                "skill_level": 4,
                "tools_required": ["hammer", "anvil", "pliers"],
                "success_rate": 0.7,
                "experience_gained": 40,
                "description": "Forge chainmail armor."
            },
            {
                "id": "craft_plate_armor",
                "name": "Plate Armor",
                "category": CraftingCategory.BLACKSMITH,
                "result_item": "plate_armor",
                "materials": {"steel_ingot": 8, "iron_ore": 4, "leather": 2},
                "skill_required": "Crafting",
                "skill_level": 7,
                "tools_required": ["hammer", "anvil", "forge"],
                "success_rate": 0.6,
                "experience_gained": 75,
                "description": "Forge heavy plate armor."
            },
            
            # Alchemy Recipes
            {
                "id": "craft_health_potion",
                "name": "Health Potion",
                "category": CraftingCategory.ALCHEMY,
                "result_item": "health_potion",
                "materials": {"herb": 3, "crystal_vial": 1},
                "skill_required": "Crafting",
                "skill_level": 1,
                "tools_required": ["mortar_pestle"],
                "success_rate": 0.95,
                "experience_gained": 10,
                "description": "Brew a healing potion."
            },
            {
                "id": "craft_greater_health_potion",
                "name": "Greater Health Potion",
                "category": CraftingCategory.ALCHEMY,
                "result_item": "health_potion_greater",
                "materials": {"herb": 6, "magic_crystal": 1, "crystal_vial": 1},
                "skill_required": "Crafting",
                "skill_level": 4,
                "tools_required": ["mortar_pestle", "alchemy_table"],
                "success_rate": 0.8,
                "experience_gained": 25,
                "description": "Brew a powerful healing potion."
            },
            {
                "id": "craft_mana_potion",
                "name": "Mana Potion",
                "category": CraftingCategory.ALCHEMY,
                "result_item": "mana_potion",
                "materials": {"magic_crystal": 2, "crystal_vial": 1},
                "skill_required": "Crafting",
                "skill_level": 2,
                "tools_required": ["mortar_pestle"],
                "success_rate": 0.9,
                "experience_gained": 15,
                "description": "Brew a mana restoration potion."
            },
            {
                "id": "craft_antidote",
                "name": "Antidote",
                "category": CraftingCategory.ALCHEMY,
                "result_item": "antidote",
                "materials": {"herb": 2, "purifying_powder": 1},
                "skill_required": "Crafting",
                "skill_level": 1,
                "tools_required": ["mortar_pestle"],
                "success_rate": 0.95,
                "experience_gained": 8,
                "description": "Create a cure for poison."
            },
            
            # Enchanting Recipes
            {
                "id": "enchant_weapon_fire",
                "name": "Fire Enchant Weapon",
                "category": CraftingCategory.ENCHANTING,
                "result_item": "flame_blade",
                "materials": {"weapon": 1, "fire_essence": 2, "magic_crystal": 3},
                "skill_required": "Crafting",
                "skill_level": 5,
                "tools_required": ["enchanting_table"],
                "success_rate": 0.6,
                "experience_gained": 50,
                "description": "Enchant a weapon with fire damage."
            },
            {
                "id": "enchant_armor_protection",
                "name": "Protective Enchant",
                "category": CraftingCategory.ENCHANTING,
                "result_item": "mage_robes",
                "materials": {"armor": 1, "protection_rune": 1, "magic_crystal": 2},
                "skill_required": "Crafting",
                "skill_level": 4,
                "tools_required": ["enchanting_table"],
                "success_rate": 0.7,
                "experience_gained": 40,
                "description": "Enchant armor with magical protection."
            },
            
            # Cooking Recipes
            {
                "id": "cook_rations",
                "name": "Travel Rations",
                "category": CraftingCategory.COOKING,
                "result_item": "rations",
                "materials": {"raw_meat": 2, "herb": 1},
                "skill_required": "Crafting",
                "skill_level": 1,
                "tools_required": [],
                "success_rate": 0.95,
                "experience_gained": 5,
                "description": "Prepare travel rations."
            },
            
            # Jewelcrafting Recipes
            {
                "id": "craft_silver_ring",
                "name": "Silver Ring",
                "category": CraftingCategory.JEWELCRAFTING,
                "result_item": "silver_ring",
                "materials": {"silver_ingot": 1, "gem": 1},
                "skill_required": "Crafting",
                "skill_level": 2,
                "tools_required": ["jewelers_kit"],
                "success_rate": 0.85,
                "experience_gained": 20,
                "description": "Craft a silver ring."
            },
            {
                "id": "craft_ruby_amulet",
                "name": "Ruby Amulet",
                "category": CraftingCategory.JEWELCRAFTING,
                "result_item": "ruby_amulet",
                "materials": {"gold_ingot": 1, "ruby": 1, "magic_crystal": 1},
                "skill_required": "Crafting",
                "skill_level": 5,
                "tools_required": ["jewelers_kit"],
                "success_rate": 0.7,
                "experience_gained": 45,
                "description": "Craft a powerful ruby amulet."
            }
        ]
        
        for recipe_data in recipes_data:
            recipe = CraftingRecipe(
                id=recipe_data["id"],
                name=recipe_data["name"],
                category=CraftingCategory(recipe_data["category"]),
                result_item=recipe_data["result_item"],
                result_quantity=recipe_data.get("result_quantity", 1),
                materials=recipe_data.get("materials", {}),
                skill_required=recipe_data.get("skill_required", "Crafting"),
                skill_level=recipe_data.get("skill_level", 1),
                tools_required=recipe_data.get("tools_required", []),
                success_rate=recipe_data.get("success_rate", 0.9),
                quality_range=recipe_data.get("quality_range", (1, 3)),
                experience_gained=recipe_data.get("experience_gained", 10),
                description=recipe_data.get("description", "")
            )
            self.recipes[recipe.id] = recipe
    
    def get_recipes_by_category(self, category: CraftingCategory) -> List[CraftingRecipe]:
        """Get all recipes in a category"""
        return [r for r in self.recipes.values() if r.category == category]
    
    def get_available_recipes(self, player: 'Character') -> List[CraftingRecipe]:
        """Get recipes the player can potentially craft"""
        return [
            r for r in self.recipes.values()
            if player.skills.get(r.skill_required, None) and
            player.skills[r.skill_required].current_level >= r.skill_level
        ]
    
    def craft(self, recipe_id: str, player: 'Character') -> Tuple[bool, str, Optional[Item]]:
        """Attempt to craft an item"""
        recipe = self.recipes.get(recipe_id)
        if not recipe:
            return False, "Recipe not found.", None
        
        # Check if can craft
        can_craft, message = recipe.can_craft(player)
        if not can_craft:
            return False, message, None
        
        # Remove materials
        for material_id, quantity in recipe.materials.items():
            player.inventory.remove_item(material_id.replace("_", " ").title(), quantity)
        
        # Determine success
        success_roll = random.random()
        skill = player.skills.get(recipe.skill_required)
        skill_bonus = (skill.current_level * 0.02) if skill else 0
        
        success = success_roll <= (recipe.success_rate + skill_bonus)
        
        if success:
            # Create item
            item = get_item(recipe.result_item, recipe.result_quantity)
            if item:
                # Add skill experience
                if skill:
                    skill.add_experience(recipe.experience_gained)
                
                player.items_crafted += 1
                return True, f"Successfully crafted {item.name}!", item
            else:
                return False, "Failed to create item.", None
        else:
            # Failure - materials are lost
            if skill:
                skill.add_experience(recipe.experience_gained // 4)
            return False, "Crafting failed! Materials were lost.", None
    
    def get_crafting_menu(self, player: 'Character') -> str:
        """Get crafting menu display"""
        lines = [
            f"\n{'='*60}",
            "CRAFTING",
            f"{'='*60}"
        ]
        
        for category in CraftingCategory:
            recipes = self.get_recipes_by_category(category)
            available = [
                r for r in recipes
                if player.skills.get(r.skill_required, None) and
                player.skills[r.skill_required].current_level >= r.skill_level
            ]
            
            if available:
                lines.append(f"\n{category.value.title()}:")
                for recipe in available:
                    can_craft, _ = recipe.can_craft(player)
                    status = "✓" if can_craft else "✗"
                    lines.append(f"  [{status}] {recipe.name} (Lv.{recipe.skill_level})")
        
        return "\n".join(lines)
    
    def to_dict(self) -> Dict:
        return {
            "recipes": {k: v.to_dict() for k, v in self.recipes.items()}
        }


print("Crafting system loaded successfully!")

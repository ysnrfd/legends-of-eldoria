"""
Crafting System - Create Items, Equipment, and Consumables

Author: YSNRFD
Version: 1.0.0
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, TYPE_CHECKING
from enum import Enum
import sys
import os
import random
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.items import Item, get_item

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
        
        # Check materials - use item IDs instead of display names
        for material_id, quantity in self.materials.items():
            # Try to find item by ID first, then by name
            has_item = False
            for item in player.inventory.items:
                item_id = item.name.lower().replace(" ", "_")
                if item_id == material_id and item.quantity >= quantity:
                    has_item = True
                    break
            
            if not has_item:
                return False, f"Missing materials: {material_id.replace('_', ' ').title()}"
        
        # Check tools
        for tool in self.tools_required:
            has_tool = False
            for item in player.inventory.items:
                if item.name.lower() == tool.lower():
                    has_tool = True
                    break
            if not has_tool:
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
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'CraftingRecipe':
        return cls(
            id=data["id"],
            name=data["name"],
            category=CraftingCategory(data["category"]),
            result_item=data["result_item"],
            result_quantity=data.get("result_quantity", 1),
            materials=data.get("materials", {}),
            skill_required=data.get("skill_required", "Crafting"),
            skill_level=data.get("skill_level", 1),
            tools_required=data.get("tools_required", []),
            success_rate=data.get("success_rate", 0.9),
            quality_range=tuple(data.get("quality_range", [1, 3])),
            experience_gained=data.get("experience_gained", 10),
            description=data.get("description", "")
        )


class CraftingManager:
    """Manages crafting recipes and operations"""
    
    def __init__(self):
        self.recipes: Dict[str, CraftingRecipe] = {}
        self._init_recipes()
    
    def _init_recipes(self):
        """Initialize default recipes"""
        default_recipes = {
            # Blacksmithing
            "iron_sword": CraftingRecipe(
                id="iron_sword",
                name="Iron Sword",
                category=CraftingCategory.BLACKSMITH,
                result_item="iron_sword",
                materials={"iron_ore": 3, "leather": 1},
                skill_required="Crafting",
                skill_level=2,
                success_rate=0.85,
                experience_gained=25,
                description="Forge a basic iron sword."
            ),
            "steel_sword": CraftingRecipe(
                id="steel_sword",
                name="Steel Sword",
                category=CraftingCategory.BLACKSMITH,
                result_item="steel_sword",
                materials={"iron_ore": 5, "magic_essence": 1},
                skill_required="Crafting",
                skill_level=5,
                success_rate=0.75,
                experience_gained=50,
                description="Forge a quality steel sword."
            ),
            "iron_armor": CraftingRecipe(
                id="iron_armor",
                name="Iron Armor",
                category=CraftingCategory.BLACKSMITH,
                result_item="iron_armor",
                materials={"iron_ore": 8, "leather": 2},
                skill_required="Crafting",
                skill_level=3,
                success_rate=0.80,
                experience_gained=40,
                description="Forge protective iron armor."
            ),
            
            # Alchemy
            "health_potion": CraftingRecipe(
                id="health_potion",
                name="Health Potion",
                category=CraftingCategory.ALCHEMY,
                result_item="health_potion",
                materials={"herb": 2},
                skill_required="Magic",
                skill_level=1,
                success_rate=0.90,
                experience_gained=15,
                description="Brew a healing potion."
            ),
            "mana_potion": CraftingRecipe(
                id="mana_potion",
                name="Mana Potion",
                category=CraftingCategory.ALCHEMY,
                result_item="mana_potion",
                materials={"herb": 1, "magic_essence": 1},
                skill_required="Magic",
                skill_level=3,
                success_rate=0.85,
                experience_gained=20,
                description="Brew a mana restoration potion."
            ),
            "elixir": CraftingRecipe(
                id="elixir",
                name="Elixir",
                category=CraftingCategory.ALCHEMY,
                result_item="elixir",
                materials={"health_potion": 1, "mana_potion": 1, "magic_essence": 2},
                skill_required="Magic",
                skill_level=5,
                success_rate=0.70,
                experience_gained=50,
                description="Brew a powerful elixir."
            ),
            
            # Enchanting
            "enchanted_ring": CraftingRecipe(
                id="enchanted_ring",
                name="Enchanted Ring",
                category=CraftingCategory.ENCHANTING,
                result_item="silver_ring",
                materials={"silver_ring": 1, "magic_essence": 2},
                skill_required="Magic",
                skill_level=4,
                success_rate=0.75,
                experience_gained=35,
                description="Enchant a ring with magical properties."
            ),
            
            # Cooking
            "traveler_meal": CraftingRecipe(
                id="traveler_meal",
                name="Traveler's Meal",
                category=CraftingCategory.COOKING,
                result_item="traveler_meal",
                materials={"herb": 1},
                skill_required="Survival",
                skill_level=1,
                success_rate=0.95,
                experience_gained=10,
                description="Prepare a simple but nourishing meal."
            )
        }
        
        for recipe_id, recipe in default_recipes.items():
            self.recipes[recipe_id] = recipe
    
    def get_recipe(self, recipe_id: str) -> Optional[CraftingRecipe]:
        """Get a recipe by ID"""
        return self.recipes.get(recipe_id)
    
    def get_recipes_by_category(self, category: CraftingCategory) -> List[CraftingRecipe]:
        """Get all recipes in a category"""
        return [r for r in self.recipes.values() if r.category == category]
    
    def get_available_recipes(self, player: 'Character') -> List[CraftingRecipe]:
        """Get recipes the player can craft"""
        available = []
        for recipe in self.recipes.values():
            can_craft, _ = recipe.can_craft(player)
            if can_craft:
                available.append(recipe)
        return available
    
    def craft(self, recipe_id: str, player: 'Character') -> Tuple[bool, str, Optional[Item]]:
        """Attempt to craft an item"""
        recipe = self.get_recipe(recipe_id)
        if not recipe:
            return False, "Recipe not found.", None
        
        # Check if can craft
        can_craft, message = recipe.can_craft(player)
        if not can_craft:
            return False, message, None
        
        # Remove materials - use item IDs
        for material_id, quantity in recipe.materials.items():
            # Find item by ID
            removed = False
            for item in player.inventory.items:
                item_id = item.name.lower().replace(" ", "_")
                if item_id == material_id:
                    if item.quantity <= quantity:
                        player.inventory.items.remove(item)
                    else:
                        item.quantity -= quantity
                    removed = True
                    break
            
            if not removed:
                return False, f"Failed to remove material: {material_id}", None
        
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

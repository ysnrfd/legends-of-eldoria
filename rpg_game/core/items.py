"""
Item System - Weapons, Armor, Consumables, and Materials

Author: YSNRFD
Version: 1.0.0
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any, TYPE_CHECKING
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.engine import (
    Item, ItemType, Rarity, DamageType, StatType, EquipmentSlot,
    Entity, StatusEffectType
)

if TYPE_CHECKING:
    from core.character import Character


# =============================================================================
# WEAPONS
# =============================================================================

@dataclass
class Weapon(Item):
    """Weapon item with damage and combat properties"""
    damage_min: int = 1
    damage_max: int = 5
    damage_type: DamageType = DamageType.PHYSICAL
    attack_speed: float = 1.0
    critical_chance: float = 0.05
    critical_damage: float = 2.0
    range: int = 1
    two_handed: bool = False
    stat_requirements: Dict[str, int] = field(default_factory=dict)
    
    def __post_init__(self):
        self.item_type = ItemType.WEAPON
        self.equippable = True
        self.stackable = False
    
    def get_damage(self) -> int:
        """Get random damage value"""
        import random
        return random.randint(self.damage_min, self.damage_max)
    
    def can_equip(self, character: 'Character') -> Tuple[bool, str]:
        """Check if character can equip this weapon"""
        if character.level < self.level_required:
            return False, f"Required level: {self.level_required}"
        
        for stat_name, required in self.stat_requirements.items():
            stat_type = StatType(stat_name)
            if character.get_stat(stat_type) < required:
                return False, f"Required {stat_name}: {required}"
        
        return True, "Can equip"
    
    def get_display_stats(self) -> str:
        """Get weapon stats display"""
        lines = [
            f"Damage: {self.damage_min}-{self.damage_max}",
            f"Damage Type: {self.damage_type.value.title()}",
            f"Attack Speed: {self.attack_speed:.1f}",
            f"Crit Chance: {self.critical_chance * 100:.1f}%",
            f"Crit Damage: {self.critical_damage:.1f}x"
        ]
        if self.two_handed:
            lines.append("Two-Handed")
        if self.range > 1:
            lines.append(f"Range: {self.range}")
        return "\n".join(lines)
    
    def to_dict(self) -> Dict:
        data = super().to_dict()
        data.update({
            "damage_min": self.damage_min,
            "damage_max": self.damage_max,
            "damage_type": self.damage_type.value,
            "attack_speed": self.attack_speed,
            "critical_chance": self.critical_chance,
            "critical_damage": self.critical_damage,
            "range": self.range,
            "two_handed": self.two_handed,
            "stat_requirements": self.stat_requirements
        })
        return data


# =============================================================================
# ARMOR
# =============================================================================

@dataclass
class Armor(Item):
    """Armor item with defense properties"""
    slot: EquipmentSlot = EquipmentSlot.CHEST
    defense: int = 1
    magic_defense: int = 0
    resistances: Dict[str, float] = field(default_factory=dict)
    stat_bonuses: Dict[str, int] = field(default_factory=dict)
    
    def __post_init__(self):
        self.item_type = ItemType.ARMOR
        self.equippable = True
        self.stackable = False
    
    def get_total_defense(self) -> int:
        """Get total defense value"""
        return self.defense + self.magic_defense
    
    def get_display_stats(self) -> str:
        """Get armor stats display"""
        lines = [
            f"Slot: {self.slot.value.replace('_', ' ').title()}",
            f"Defense: {self.defense}",
            f"Magic Defense: {self.magic_defense}"
        ]
        if self.resistances:
            lines.append("Resistances:")
            for dtype, value in self.resistances.items():
                lines.append(f"  {dtype}: {value*100:.0f}%")
        if self.stat_bonuses:
            lines.append("Stat Bonuses:")
            for stat, bonus in self.stat_bonuses.items():
                lines.append(f"  {stat}: +{bonus}")
        return "\n".join(lines)
    
    def to_dict(self) -> Dict:
        data = super().to_dict()
        data.update({
            "slot": self.slot.value,
            "defense": self.defense,
            "magic_defense": self.magic_defense,
            "resistances": self.resistances,
            "stat_bonuses": self.stat_bonuses
        })
        return data


# =============================================================================
# CONSUMABLES
# =============================================================================

@dataclass
class Consumable(Item):
    """Consumable item with effects"""
    hp_restore: int = 0
    mp_restore: int = 0
    stamina_restore: int = 0
    temporary_effects: List[Tuple[StatusEffectType, int, int]] = field(default_factory=list)
    cooldown: int = 0
    use_message: str = "You use the item."
    
    def __post_init__(self):
        self.item_type = ItemType.CONSUMABLE
        self.usable = True
        self.stackable = True
    
    def use(self, target: Entity) -> Tuple[bool, str]:
        """Use the consumable on a target"""
        messages = [self.use_message]
        
        # Restore HP
        if self.hp_restore > 0:
            old_hp = target.current_hp
            target.heal(self.hp_restore)
            actual_heal = target.current_hp - old_hp
            messages.append(f"Restored {actual_heal} HP!")
        
        # Restore MP
        if self.mp_restore > 0:
            old_mp = target.current_mp
            target.restore_mp(self.mp_restore)
            actual_restore = target.current_mp - old_mp
            messages.append(f"Restored {actual_restore} MP!")
        
        # Restore Stamina
        if self.stamina_restore > 0:
            old_stamina = target.current_stamina
            target.restore_stamina(self.stamina_restore)
            actual_restore = target.current_stamina - old_stamina
            messages.append(f"Restored {actual_restore} Stamina!")
        
        # Apply temporary effects
        for effect_type, duration, strength in self.temporary_effects:
            target.apply_status_effect(effect_type, duration, strength)
            messages.append(f"Applied {effect_type.value} for {duration} turns!")
        
        return True, "\n".join(messages)
    
    def to_dict(self) -> Dict:
        data = super().to_dict()
        data.update({
            "hp_restore": self.hp_restore,
            "mp_restore": self.mp_restore,
            "stamina_restore": self.stamina_restore,
            "temporary_effects": [(e.value, d, s) for e, d, s in self.temporary_effects],
            "cooldown": self.cooldown,
            "use_message": self.use_message
        })
        return data


# =============================================================================
# MATERIALS
# =============================================================================

@dataclass
class Material(Item):
    """Crafting material"""
    material_type: str = "generic"
    quality: int = 1
    crafting_value: int = 1
    
    def __post_init__(self):
        self.item_type = ItemType.MATERIAL
        self.stackable = True
    
    def to_dict(self) -> Dict:
        data = super().to_dict()
        data.update({
            "material_type": self.material_type,
            "quality": self.quality,
            "crafting_value": self.crafting_value
        })
        return data


# =============================================================================
# ITEM FACTORY
# =============================================================================

class ItemFactory:
    """Factory for creating items from data"""
    
    @staticmethod
    def create_item(data: Dict[str, Any]) -> Optional[Item]:
        """Create an item from dictionary data"""
        item_type = data.get("item_type", "material")
        
        if item_type == "weapon":
            return ItemFactory._create_weapon(data)
        elif item_type == "armor":
            return ItemFactory._create_armor(data)
        elif item_type == "consumable":
            return ItemFactory._create_consumable(data)
        elif item_type == "material":
            return ItemFactory._create_material(data)
        elif item_type == "accessory":
            return ItemFactory._create_accessory(data)
        else:
            # Generic item
            return Item(
                name=data.get("name", "Unknown Item"),
                description=data.get("description", ""),
                item_type=ItemType(item_type) if item_type in [t.value for t in ItemType] else ItemType.MATERIAL,
                rarity=Rarity(data.get("rarity", "Common")) if data.get("rarity") in [r.value for r in Rarity] else Rarity.COMMON,
                value=data.get("value", 0),
                weight=data.get("weight", 0.0),
                quantity=data.get("quantity", 1),
                level_required=data.get("level_required", 1)
            )
    
    @staticmethod
    def _create_weapon(data: Dict) -> Optional[Weapon]:
        try:
            return Weapon(
                name=data.get("name", "Unknown Weapon"),
                description=data.get("description", ""),
                rarity=Rarity(data.get("rarity", "Common")) if data.get("rarity") in [r.value for r in Rarity] else Rarity.COMMON,
                value=data.get("value", 0),
                weight=data.get("weight", 1.0),
                quantity=data.get("quantity", 1),
                level_required=data.get("level_required", 1),
                damage_min=data.get("damage_min", 1),
                damage_max=data.get("damage_max", 5),
                damage_type=DamageType(data.get("damage_type", "physical")) if data.get("damage_type") in [d.value for d in DamageType] else DamageType.PHYSICAL,
                attack_speed=data.get("attack_speed", 1.0),
                critical_chance=data.get("critical_chance", 0.05),
                critical_damage=data.get("critical_damage", 2.0),
                two_handed=data.get("two_handed", False),
                stat_requirements=data.get("stat_requirements", {})
            )
        except (ValueError, KeyError) as e:
            print(f"Error creating weapon: {e}")
            return None
    
    @staticmethod
    def _create_armor(data: Dict) -> Optional[Armor]:
        try:
            slot_value = data.get("slot", "chest")
            slot = EquipmentSlot(slot_value) if slot_value in [s.value for s in EquipmentSlot] else EquipmentSlot.CHEST
            
            return Armor(
                name=data.get("name", "Unknown Armor"),
                description=data.get("description", ""),
                rarity=Rarity(data.get("rarity", "Common")) if data.get("rarity") in [r.value for r in Rarity] else Rarity.COMMON,
                value=data.get("value", 0),
                weight=data.get("weight", 2.0),
                quantity=data.get("quantity", 1),
                level_required=data.get("level_required", 1),
                slot=slot,
                defense=data.get("defense", 1),
                magic_defense=data.get("magic_defense", 0),
                resistances=data.get("resistances", {}),
                stat_bonuses=data.get("stat_bonuses", {})
            )
        except (ValueError, KeyError) as e:
            print(f"Error creating armor: {e}")
            return None
    
    @staticmethod
    def _create_consumable(data: Dict) -> Optional[Consumable]:
        try:
            effects = []
            for effect_data in data.get("temporary_effects", []):
                if isinstance(effect_data, tuple) and len(effect_data) == 3:
                    effects.append(effect_data)
                elif isinstance(effect_data, list) and len(effect_data) == 3:
                    effect_type, duration, strength = effect_data
                    effects.append((StatusEffectType(effect_type), duration, strength))
            
            return Consumable(
                name=data.get("name", "Unknown Consumable"),
                description=data.get("description", ""),
                rarity=Rarity(data.get("rarity", "Common")) if data.get("rarity") in [r.value for r in Rarity] else Rarity.COMMON,
                value=data.get("value", 0),
                weight=data.get("weight", 0.1),
                quantity=data.get("quantity", 1),
                level_required=data.get("level_required", 1),
                hp_restore=data.get("hp_restore", 0),
                mp_restore=data.get("mp_restore", 0),
                stamina_restore=data.get("stamina_restore", 0),
                temporary_effects=effects,
                cooldown=data.get("cooldown", 0),
                use_message=data.get("use_message", "You use the item.")
            )
        except (ValueError, KeyError) as e:
            print(f"Error creating consumable: {e}")
            return None
    
    @staticmethod
    def _create_material(data: Dict) -> Optional[Material]:
        try:
            return Material(
                name=data.get("name", "Unknown Material"),
                description=data.get("description", ""),
                rarity=Rarity(data.get("rarity", "Common")) if data.get("rarity") in [r.value for r in Rarity] else Rarity.COMMON,
                value=data.get("value", 0),
                weight=data.get("weight", 0.1),
                quantity=data.get("quantity", 1),
                level_required=data.get("level_required", 1),
                material_type=data.get("material_type", "generic"),
                quality=data.get("quality", 1),
                crafting_value=data.get("crafting_value", 1)
            )
        except (ValueError, KeyError) as e:
            print(f"Error creating material: {e}")
            return None
    
    @staticmethod
    def _create_accessory(data: Dict) -> Optional[Item]:
        """Create accessory item"""
        try:
            return Item(
                name=data.get("name", "Unknown Accessory"),
                description=data.get("description", ""),
                item_type=ItemType.ACCESSORY,
                rarity=Rarity(data.get("rarity", "Common")) if data.get("rarity") in [r.value for r in Rarity] else Rarity.COMMON,
                value=data.get("value", 0),
                weight=data.get("weight", 0.1),
                quantity=data.get("quantity", 1),
                level_required=data.get("level_required", 1),
                equippable=True,
                stackable=False
            )
        except (ValueError, KeyError) as e:
            print(f"Error creating accessory: {e}")
            return None


# =============================================================================
# ITEM DATABASE
# =============================================================================

ITEM_DATABASE = {
    # WEAPONS
    "rusty_sword": {
        "name": "Rusty Sword",
        "item_type": "weapon",
        "rarity": "Common",
        "value": 10,
        "weight": 2.0,
        "description": "An old, rusty sword. Better than nothing.",
        "damage_min": 2,
        "damage_max": 5,
        "damage_type": "physical",
        "attack_speed": 1.0,
        "critical_chance": 0.05,
        "critical_damage": 1.5
    },
    "iron_sword": {
        "name": "Iron Sword",
        "item_type": "weapon",
        "rarity": "Common",
        "value": 50,
        "weight": 2.5,
        "description": "A standard iron sword.",
        "damage_min": 4,
        "damage_max": 8,
        "damage_type": "physical",
        "attack_speed": 1.0,
        "critical_chance": 0.05,
        "critical_damage": 1.5,
        "level_required": 2
    },
    "steel_sword": {
        "name": "Steel Sword",
        "item_type": "weapon",
        "rarity": "Uncommon",
        "value": 150,
        "weight": 2.5,
        "description": "A well-crafted steel sword.",
        "damage_min": 6,
        "damage_max": 12,
        "damage_type": "physical",
        "attack_speed": 1.1,
        "critical_chance": 0.08,
        "critical_damage": 1.6,
        "level_required": 5
    },
    "shadow_dagger": {
        "name": "Shadow Dagger",
        "item_type": "weapon",
        "rarity": "Rare",
        "value": 300,
        "weight": 1.0,
        "description": "A dagger that seems to blend with shadows.",
        "damage_min": 5,
        "damage_max": 10,
        "damage_type": "dark",
        "attack_speed": 1.5,
        "critical_chance": 0.15,
        "critical_damage": 2.0,
        "level_required": 8
    },
    "frost_staff": {
        "name": "Frost Staff",
        "item_type": "weapon",
        "rarity": "Rare",
        "value": 400,
        "weight": 2.0,
        "description": "A staff that radiates cold energy.",
        "damage_min": 8,
        "damage_max": 15,
        "damage_type": "ice",
        "attack_speed": 1.0,
        "critical_chance": 0.05,
        "critical_damage": 1.5,
        "level_required": 10
    },
    "flame_blade": {
        "name": "Flame Blade",
        "item_type": "weapon",
        "rarity": "Epic",
        "value": 1000,
        "weight": 3.0,
        "description": "A sword wreathed in eternal flames.",
        "damage_min": 15,
        "damage_max": 25,
        "damage_type": "fire",
        "attack_speed": 1.0,
        "critical_chance": 0.10,
        "critical_damage": 2.0,
        "level_required": 15
    },
    "legendary_blade": {
        "name": "Blade of Legends",
        "item_type": "weapon",
        "rarity": "Legendary",
        "value": 5000,
        "weight": 3.5,
        "description": "A weapon of immense power, spoken of in ancient tales.",
        "damage_min": 30,
        "damage_max": 50,
        "damage_type": "holy",
        "attack_speed": 1.2,
        "critical_chance": 0.20,
        "critical_damage": 2.5,
        "level_required": 25
    },
    
    # ARMOR
    "cloth_shirt": {
        "name": "Cloth Shirt",
        "item_type": "armor",
        "rarity": "Common",
        "value": 5,
        "weight": 1.0,
        "description": "Simple cloth clothing.",
        "slot": "chest",
        "defense": 1,
        "magic_defense": 0
    },
    "leather_armor": {
        "name": "Leather Armor",
        "item_type": "armor",
        "rarity": "Common",
        "value": 30,
        "weight": 3.0,
        "description": "Basic leather protection.",
        "slot": "chest",
        "defense": 3,
        "magic_defense": 1,
        "level_required": 2
    },
    "iron_armor": {
        "name": "Iron Armor",
        "item_type": "armor",
        "rarity": "Uncommon",
        "value": 100,
        "weight": 8.0,
        "description": "Sturdy iron plate armor.",
        "slot": "chest",
        "defense": 8,
        "magic_defense": 2,
        "resistances": {"physical": 0.1},
        "level_required": 5
    },
    "steel_armor": {
        "name": "Steel Armor",
        "item_type": "armor",
        "rarity": "Rare",
        "value": 300,
        "weight": 10.0,
        "description": "High-quality steel armor.",
        "slot": "chest",
        "defense": 12,
        "magic_defense": 4,
        "resistances": {"physical": 0.15},
        "level_required": 10
    },
    "mage_robes": {
        "name": "Mage Robes",
        "item_type": "armor",
        "rarity": "Uncommon",
        "value": 80,
        "weight": 1.5,
        "description": "Robes enchanted for magical protection.",
        "slot": "chest",
        "defense": 2,
        "magic_defense": 8,
        "stat_bonuses": {"intelligence": 2, "wisdom": 1},
        "level_required": 5
    },
    "dragon_scale_armor": {
        "name": "Dragon Scale Armor",
        "item_type": "armor",
        "rarity": "Legendary",
        "value": 3000,
        "weight": 12.0,
        "description": "Armor forged from dragon scales.",
        "slot": "chest",
        "defense": 25,
        "magic_defense": 15,
        "resistances": {"fire": 0.5, "physical": 0.2},
        "stat_bonuses": {"constitution": 5},
        "level_required": 25
    },
    
    # CONSUMABLES
    "health_potion_minor": {
        "name": "Minor Health Potion",
        "item_type": "consumable",
        "rarity": "Common",
        "value": 15,
        "weight": 0.5,
        "description": "Restores a small amount of health.",
        "hp_restore": 25,
        "use_message": "You drink the potion and feel refreshed."
    },
    "health_potion": {
        "name": "Health Potion",
        "item_type": "consumable",
        "rarity": "Common",
        "value": 40,
        "weight": 0.5,
        "description": "Restores health.",
        "hp_restore": 50,
        "use_message": "You drink the potion and feel much better."
    },
    "health_potion_major": {
        "name": "Major Health Potion",
        "item_type": "consumable",
        "rarity": "Uncommon",
        "value": 100,
        "weight": 0.5,
        "description": "Restores a large amount of health.",
        "hp_restore": 100,
        "use_message": "You drink the potion and feel revitalized."
    },
    "mana_potion": {
        "name": "Mana Potion",
        "item_type": "consumable",
        "rarity": "Common",
        "value": 35,
        "weight": 0.5,
        "description": "Restores magical energy.",
        "mp_restore": 30,
        "use_message": "You drink the potion and feel magical energy return."
    },
    "stamina_potion": {
        "name": "Stamina Potion",
        "item_type": "consumable",
        "rarity": "Common",
        "value": 25,
        "weight": 0.5,
        "description": "Restores stamina.",
        "stamina_restore": 30,
        "use_message": "You drink the potion and feel energized."
    },
    "elixir": {
        "name": "Elixir",
        "item_type": "consumable",
        "rarity": "Rare",
        "value": 200,
        "weight": 0.5,
        "description": "Restores health, mana, and stamina.",
        "hp_restore": 50,
        "mp_restore": 50,
        "stamina_restore": 50,
        "use_message": "You drink the elixir and feel completely restored."
    },
    
    # MATERIALS
    "iron_ore": {
        "name": "Iron Ore",
        "item_type": "material",
        "rarity": "Common",
        "value": 5,
        "weight": 2.0,
        "description": "Raw iron ore that can be smelted.",
        "material_type": "ore",
        "quality": 1,
        "crafting_value": 5
    },
    "leather": {
        "name": "Leather",
        "item_type": "material",
        "rarity": "Common",
        "value": 3,
        "weight": 0.5,
        "description": "Treated animal hide.",
        "material_type": "leather",
        "quality": 1,
        "crafting_value": 3
    },
    "magic_essence": {
        "name": "Magic Essence",
        "item_type": "material",
        "rarity": "Uncommon",
        "value": 50,
        "weight": 0.1,
        "description": "Concentrated magical energy.",
        "material_type": "magic",
        "quality": 2,
        "crafting_value": 25
    },
    "dragon_bone": {
        "name": "Dragon Bone",
        "item_type": "material",
        "rarity": "Epic",
        "value": 500,
        "weight": 3.0,
        "description": "The bone of an ancient dragon.",
        "material_type": "bone",
        "quality": 5,
        "crafting_value": 100
    },
    "herb": {
        "name": "Healing Herb",
        "item_type": "material",
        "rarity": "Common",
        "value": 3,
        "weight": 0.1,
        "description": "A common herb with healing properties.",
        "material_type": "herb",
        "quality": 1,
        "crafting_value": 5
    },
    "magic_crystal": {
        "name": "Magic Crystal",
        "item_type": "material",
        "rarity": "Rare",
        "value": 100,
        "weight": 0.2,
        "description": "A crystal pulsing with magical energy.",
        "material_type": "magic",
        "quality": 3,
        "crafting_value": 50
    },
    
    # ACCESSORIES
    "silver_ring": {
        "name": "Silver Ring",
        "item_type": "accessory",
        "rarity": "Common",
        "value": 50,
        "weight": 0.1,
        "description": "A simple silver ring.",
        "stat_bonuses": {"charisma": 1}
    },
    "ruby_amulet": {
        "name": "Ruby Amulet",
        "item_type": "accessory",
        "rarity": "Rare",
        "value": 500,
        "weight": 0.2,
        "description": "An amulet set with a glowing ruby.",
        "stat_bonuses": {"strength": 3, "constitution": 2}
    },
    "ring_of_power": {
        "name": "Ring of Power",
        "item_type": "accessory",
        "rarity": "Epic",
        "value": 3000,
        "weight": 0.1,
        "description": "A ring that greatly enhances magical abilities.",
        "stat_bonuses": {"intelligence": 5, "wisdom": 5},
        "special_effects": ["Magic Power +20%"],
        "level_required": 15
    }
}


def get_item(item_id: str, quantity: int = 1) -> Optional[Item]:
    """Get an item from the database by ID"""
    if item_id not in ITEM_DATABASE:
        return None
    
    data = ITEM_DATABASE[item_id].copy()
    data["quantity"] = quantity
    return ItemFactory.create_item(data)


def get_random_item(rarity: Optional[Rarity] = None, item_type: Optional[ItemType] = None) -> Optional[Item]:
    """Get a random item from the database"""
    import random
    
    candidates = []
    for item_id, data in ITEM_DATABASE.items():
        if rarity and Rarity(data.get("rarity", "Common")) != rarity:
            continue
        if item_type and ItemType(data.get("item_type", "material")) != item_type:
            continue
        candidates.append(item_id)
    
    if not candidates:
        return None
    
    return get_item(random.choice(candidates))


print("Item system loaded successfully!")

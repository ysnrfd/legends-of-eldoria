"""
Item System - Weapons, Armor, Consumables, and Materials
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any, Union, TYPE_CHECKING
from enum import Enum
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.engine import (
    Item, ItemType, Rarity, DamageType, StatType, EquipmentSlot,
    Entity, StatusEffectType, clamp
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
        super().__post_init__()
    
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
            "stat_requirements": self.stat_requirements,
            "item_type": "weapon"
        })
        return data


# =============================================================================
# ARMOR
# =============================================================================

@dataclass
class Armor(Item):
    """Armor item with defense and resistances"""
    slot: EquipmentSlot = EquipmentSlot.CHEST
    defense: int = 0
    magic_defense: int = 0
    resistances: Dict[str, float] = field(default_factory=dict)
    stat_bonuses: Dict[str, int] = field(default_factory=dict)
    
    def __post_init__(self):
        self.item_type = ItemType.ARMOR
        super().__post_init__()
    
    def get_total_defense(self) -> int:
        """Get combined defense"""
        return self.defense + self.magic_defense
    
    def get_display_stats(self) -> str:
        """Get armor stats display"""
        lines = [f"Slot: {self.slot.value.replace('_', ' ').title()}"]
        if self.defense > 0:
            lines.append(f"Physical Defense: {self.defense}")
        if self.magic_defense > 0:
            lines.append(f"Magic Defense: {self.magic_defense}")
        for dtype, res in self.resistances.items():
            lines.append(f"{dtype.title()} Resistance: {res * 100:.0f}%")
        for stat, bonus in self.stat_bonuses.items():
            lines.append(f"+{bonus} {stat.title()}")
        return "\n".join(lines)
    
    def to_dict(self) -> Dict:
        data = super().to_dict()
        data.update({
            "slot": self.slot.value,
            "defense": self.defense,
            "magic_defense": self.magic_defense,
            "resistances": self.resistances,
            "stat_bonuses": self.stat_bonuses,
            "item_type": "armor"
        })
        return data


# =============================================================================
# CONSUMABLES
# =============================================================================

@dataclass
class Consumable(Item):
    """Consumable item with restoration and temporary effects"""
    hp_restore: int = 0
    mp_restore: int = 0
    stamina_restore: int = 0
    temporary_effects: List[Tuple[str, int, int]] = field(default_factory=list)
    cooldown: int = 0
    use_message: str = ""
    
    def __post_init__(self):
        self.item_type = ItemType.CONSUMABLE
        self.stackable = True
        super().__post_init__()
    
    def use(self, user: Entity) -> Tuple[bool, str]:
        """Use the consumable on an entity"""
        messages = []
        
        if self.hp_restore > 0:
            healed = user.heal(self.hp_restore)
            messages.append(f"+{healed} HP")
        
        if self.mp_restore > 0:
            mp = user.restore_mp(self.mp_restore)
            messages.append(f"+{mp} MP")
        
        if self.stamina_restore > 0:
            stamina = user.restore_stamina(self.stamina_restore)
            messages.append(f"+{stamina} Stamina")
        
        for effect_name, duration, strength in self.temporary_effects:
            effect_type = StatusEffectType(effect_name)
            user.apply_status_effect(effect_type, duration, strength)
            messages.append(f"Applied {effect_name} ({duration} turns)")
        
        if self.use_message:
            messages.append(self.use_message)
        
        return True, f"Used {self.name}: {', '.join(messages)}"
    
    def get_display_stats(self) -> str:
        """Get consumable stats display"""
        lines = []
        if self.hp_restore > 0:
            lines.append(f"Restores {self.hp_restore} HP")
        if self.mp_restore > 0:
            lines.append(f"Restores {self.mp_restore} MP")
        if self.stamina_restore > 0:
            lines.append(f"Restores {self.stamina_restore} Stamina")
        for effect, duration, strength in self.temporary_effects:
            lines.append(f"Grants {effect} for {duration} turns")
        return "\n".join(lines) if lines else "No special effects"
    
    def to_dict(self) -> Dict:
        data = super().to_dict()
        data.update({
            "hp_restore": self.hp_restore,
            "mp_restore": self.mp_restore,
            "stamina_restore": self.stamina_restore,
            "temporary_effects": self.temporary_effects,
            "cooldown": self.cooldown,
            "use_message": self.use_message,
            "item_type": "consumable"
        })
        return data


# =============================================================================
# MATERIALS
# =============================================================================

@dataclass
class Material(Item):
    """Crafting material item"""
    material_type: str = "generic"
    quality: int = 1
    crafting_value: int = 1
    
    def __post_init__(self):
        self.item_type = ItemType.MATERIAL
        self.stackable = True
        super().__post_init__()
    
    def to_dict(self) -> Dict:
        data = super().to_dict()
        data.update({
            "material_type": self.material_type,
            "quality": self.quality,
            "crafting_value": self.crafting_value,
            "item_type": "material"
        })
        return data


# =============================================================================
# ACCESSORIES
# =============================================================================

@dataclass
class Accessory(Item):
    """Accessory item (rings, amulets, etc.)"""
    stat_bonuses: Dict[str, int] = field(default_factory=dict)
    special_effects: List[str] = field(default_factory=list)
    
    def __post_init__(self):
        self.item_type = ItemType.ACCESSORY
        super().__post_init__()
    
    def to_dict(self) -> Dict:
        data = super().to_dict()
        data.update({
            "stat_bonuses": self.stat_bonuses,
            "special_effects": self.special_effects,
            "item_type": "accessory"
        })
        return data


# =============================================================================
# ITEM FACTORY
# =============================================================================

class ItemFactory:
    """Factory for creating items from data"""
    
    @staticmethod
    def _get_rarity(rarity_str: str) -> Rarity:
        """Convert rarity string to Rarity enum"""
        rarity_map = {
            "Common": Rarity.COMMON,
            "Uncommon": Rarity.UNCOMMON,
            "Rare": Rarity.RARE,
            "Epic": Rarity.EPIC,
            "Legendary": Rarity.LEGENDARY,
            "Mythic": Rarity.MYTHIC,
            "Divine": Rarity.DIVINE
        }
        return rarity_map.get(rarity_str, Rarity.COMMON)
    
    @staticmethod
    def create_item(data: Dict) -> Item:
        """Create appropriate item type from dictionary"""
        item_type = data.get("item_type", "item")
        
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
            return Item(
                name=data["name"],
                item_type=ItemType(data.get("item_type", "material")),
                rarity=ItemFactory._get_rarity(data.get("rarity", "Common")),
                value=data.get("value", 1),
                weight=data.get("weight", 0.1),
                stackable=data.get("stackable", False),
                max_stack=data.get("max_stack", 99),
                quantity=data.get("quantity", 1),
                description=data.get("description", ""),
                level_required=data.get("level_required", 1)
            )
    
    @staticmethod
    def _create_weapon(data: Dict) -> Weapon:
        return Weapon(
            name=data["name"],
            rarity=ItemFactory._get_rarity(data.get("rarity", "Common")),
            value=data.get("value", 1),
            weight=data.get("weight", 1.0),
            description=data.get("description", ""),
            level_required=data.get("level_required", 1),
            damage_min=data.get("damage_min", 1),
            damage_max=data.get("damage_max", 5),
            damage_type=DamageType(data.get("damage_type", "physical")),
            attack_speed=data.get("attack_speed", 1.0),
            critical_chance=data.get("critical_chance", 0.05),
            critical_damage=data.get("critical_damage", 2.0),
            range=data.get("range", 1),
            two_handed=data.get("two_handed", False),
            stat_requirements=data.get("stat_requirements", {})
        )
    
    @staticmethod
    def _create_armor(data: Dict) -> Armor:
        return Armor(
            name=data["name"],
            rarity=ItemFactory._get_rarity(data.get("rarity", "Common")),
            value=data.get("value", 1),
            weight=data.get("weight", 1.0),
            description=data.get("description", ""),
            level_required=data.get("level_required", 1),
            slot=EquipmentSlot(data.get("slot", "chest")),
            defense=data.get("defense", 0),
            magic_defense=data.get("magic_defense", 0),
            resistances=data.get("resistances", {}),
            stat_bonuses=data.get("stat_bonuses", {})
        )
    
    @staticmethod
    def _create_consumable(data: Dict) -> Consumable:
        return Consumable(
            name=data["name"],
            rarity=ItemFactory._get_rarity(data.get("rarity", "Common")),
            value=data.get("value", 1),
            weight=data.get("weight", 0.1),
            description=data.get("description", ""),
            quantity=data.get("quantity", 1),
            hp_restore=data.get("hp_restore", 0),
            mp_restore=data.get("mp_restore", 0),
            stamina_restore=data.get("stamina_restore", 0),
            temporary_effects=data.get("temporary_effects", []),
            cooldown=data.get("cooldown", 0),
            use_message=data.get("use_message", "")
        )
    
    @staticmethod
    def _create_material(data: Dict) -> Material:
        return Material(
            name=data["name"],
            rarity=ItemFactory._get_rarity(data.get("rarity", "Common")),
            value=data.get("value", 1),
            weight=data.get("weight", 0.1),
            description=data.get("description", ""),
            quantity=data.get("quantity", 1),
            material_type=data.get("material_type", "generic"),
            quality=data.get("quality", 1),
            crafting_value=data.get("crafting_value", 1)
        )
    
    @staticmethod
    def _create_accessory(data: Dict) -> Accessory:
        return Accessory(
            name=data["name"],
            rarity=ItemFactory._get_rarity(data.get("rarity", "Common")),
            value=data.get("value", 1),
            weight=data.get("weight", 0.1),
            description=data.get("description", ""),
            level_required=data.get("level_required", 1),
            stat_bonuses=data.get("stat_bonuses", {}),
            special_effects=data.get("special_effects", [])
        )


# =============================================================================
# PREDEFINED ITEMS DATABASE
# =============================================================================

ITEM_DATABASE = {
    # WEAPONS
    "rusty_sword": {
        "name": "Rusty Sword",
        "item_type": "weapon",
        "rarity": "Common",
        "value": 10,
        "weight": 2.0,
        "description": "An old, rusted blade. Still sharp enough to cut.",
        "damage_min": 2,
        "damage_max": 5,
        "damage_type": "physical",
        "attack_speed": 1.0,
        "critical_chance": 0.02
    },
    "iron_sword": {
        "name": "Iron Sword",
        "item_type": "weapon",
        "rarity": "Common",
        "value": 50,
        "weight": 2.5,
        "description": "A well-crafted iron sword.",
        "damage_min": 5,
        "damage_max": 10,
        "damage_type": "physical",
        "attack_speed": 1.0,
        "critical_chance": 0.03
    },
    "steel_greatsword": {
        "name": "Steel Greatsword",
        "item_type": "weapon",
        "rarity": "Uncommon",
        "value": 200,
        "weight": 5.0,
        "description": "A massive two-handed blade of quality steel.",
        "damage_min": 12,
        "damage_max": 20,
        "damage_type": "physical",
        "attack_speed": 0.8,
        "critical_chance": 0.05,
        "two_handed": True,
        "stat_requirements": {"strength": 12}
    },
    "flame_blade": {
        "name": "Flame Blade",
        "item_type": "weapon",
        "rarity": "Rare",
        "value": 1000,
        "weight": 2.5,
        "description": "A sword imbued with eternal flames.",
        "damage_min": 10,
        "damage_max": 15,
        "damage_type": "fire",
        "attack_speed": 1.1,
        "critical_chance": 0.08,
        "level_required": 10
    },
    "frost_staff": {
        "name": "Frost Staff",
        "item_type": "weapon",
        "rarity": "Rare",
        "value": 800,
        "weight": 2.0,
        "description": "A staff that channels the power of ice.",
        "damage_min": 8,
        "damage_max": 14,
        "damage_type": "ice",
        "attack_speed": 1.0,
        "critical_chance": 0.06,
        "level_required": 8,
        "stat_requirements": {"intelligence": 14}
    },
    "shadow_dagger": {
        "name": "Shadow Dagger",
        "item_type": "weapon",
        "rarity": "Epic",
        "value": 2500,
        "weight": 0.5,
        "description": "A dagger forged in darkness, it strikes unseen.",
        "damage_min": 8,
        "damage_max": 16,
        "damage_type": "dark",
        "attack_speed": 1.5,
        "critical_chance": 0.15,
        "critical_damage": 2.5,
        "level_required": 15,
        "stat_requirements": {"dexterity": 16}
    },
    "excalibur": {
        "name": "Excalibur",
        "item_type": "weapon",
        "rarity": "Legendary",
        "value": 50000,
        "weight": 3.0,
        "description": "The legendary sword of kings. Its holy light banishes evil.",
        "damage_min": 25,
        "damage_max": 40,
        "damage_type": "holy",
        "attack_speed": 1.2,
        "critical_chance": 0.12,
        "critical_damage": 3.0,
        "level_required": 30,
        "stat_requirements": {"strength": 18, "charisma": 15}
    },
    
    # ARMOR
    "cloth_shirt": {
        "name": "Cloth Shirt",
        "item_type": "armor",
        "rarity": "Common",
        "value": 5,
        "weight": 0.5,
        "description": "Simple cloth clothing. Offers minimal protection.",
        "slot": "chest",
        "defense": 1
    },
    "leather_armor": {
        "name": "Leather Armor",
        "item_type": "armor",
        "rarity": "Common",
        "value": 75,
        "weight": 4.0,
        "description": "Sturdy leather armor for basic protection.",
        "slot": "chest",
        "defense": 5,
        "stat_bonuses": {"dexterity": 1}
    },
    "chainmail": {
        "name": "Chainmail",
        "item_type": "armor",
        "rarity": "Uncommon",
        "value": 200,
        "weight": 10.0,
        "description": "Interlocking metal rings provide good protection.",
        "slot": "chest",
        "defense": 12,
        "magic_defense": 3,
        "stat_requirements": {"constitution": 12}
    },
    "plate_armor": {
        "name": "Plate Armor",
        "item_type": "armor",
        "rarity": "Rare",
        "value": 800,
        "weight": 20.0,
        "description": "Heavy plate armor for maximum protection.",
        "slot": "chest",
        "defense": 25,
        "magic_defense": 5,
        "stat_requirements": {"strength": 14, "constitution": 14}
    },
    "mage_robes": {
        "name": "Mage Robes",
        "item_type": "armor",
        "rarity": "Uncommon",
        "value": 150,
        "weight": 1.0,
        "description": "Enchanted robes that enhance magical abilities.",
        "slot": "chest",
        "defense": 3,
        "magic_defense": 10,
        "stat_bonuses": {"intelligence": 2, "wisdom": 1}
    },
    "dragon_scale_armor": {
        "name": "Dragon Scale Armor",
        "item_type": "armor",
        "rarity": "Legendary",
        "value": 25000,
        "weight": 15.0,
        "description": "Armor forged from dragon scales. Nearly impenetrable.",
        "slot": "chest",
        "defense": 40,
        "magic_defense": 20,
        "resistances": {"fire": 0.5, "physical": 0.2},
        "level_required": 25
    },
    "iron_helmet": {
        "name": "Iron Helmet",
        "item_type": "armor",
        "rarity": "Common",
        "value": 40,
        "weight": 2.0,
        "description": "A basic iron helmet.",
        "slot": "head",
        "defense": 3
    },
    "leather_boots": {
        "name": "Leather Boots",
        "item_type": "armor",
        "rarity": "Common",
        "value": 30,
        "weight": 1.0,
        "description": "Comfortable leather footwear.",
        "slot": "feet",
        "defense": 2,
        "stat_bonuses": {"dexterity": 1}
    },
    
    # CONSUMABLES
    "health_potion_minor": {
        "name": "Minor Health Potion",
        "item_type": "consumable",
        "rarity": "Common",
        "value": 25,
        "weight": 0.2,
        "description": "A small red potion that restores health.",
        "hp_restore": 30,
        "use_message": "You drink the health potion."
    },
    "health_potion": {
        "name": "Health Potion",
        "item_type": "consumable",
        "rarity": "Uncommon",
        "value": 75,
        "weight": 0.2,
        "description": "A standard health potion.",
        "hp_restore": 75,
        "use_message": "You drink the health potion."
    },
    "health_potion_greater": {
        "name": "Greater Health Potion",
        "item_type": "consumable",
        "rarity": "Rare",
        "value": 200,
        "weight": 0.2,
        "description": "A powerful health restoration potion.",
        "hp_restore": 150,
        "use_message": "You drink the greater health potion."
    },
    "mana_potion": {
        "name": "Mana Potion",
        "item_type": "consumable",
        "rarity": "Uncommon",
        "value": 60,
        "weight": 0.2,
        "description": "A blue potion that restores magical energy.",
        "mp_restore": 50,
        "use_message": "You drink the mana potion."
    },
    "stamina_potion": {
        "name": "Stamina Potion",
        "item_type": "consumable",
        "rarity": "Common",
        "value": 30,
        "weight": 0.2,
        "description": "Restores your stamina.",
        "stamina_restore": 50,
        "use_message": "You drink the stamina potion."
    },
    "antidote": {
        "name": "Antidote",
        "item_type": "consumable",
        "rarity": "Common",
        "value": 40,
        "weight": 0.1,
        "description": "Cures poison status.",
        "use_message": "The antidote neutralizes any poison in your system."
    },
    "strength_elixir": {
        "name": "Strength Elixir",
        "item_type": "consumable",
        "rarity": "Rare",
        "value": 150,
        "weight": 0.3,
        "description": "Temporarily increases your strength.",
        "temporary_effects": [("strength_buff", 5, 3)],
        "use_message": "You feel a surge of power!"
    },
    
    # MATERIALS
    "iron_ore": {
        "name": "Iron Ore",
        "item_type": "material",
        "rarity": "Common",
        "value": 5,
        "weight": 1.0,
        "description": "Raw iron ore for smelting.",
        "material_type": "metal",
        "quality": 1,
        "crafting_value": 10
    },
    "steel_ingot": {
        "name": "Steel Ingot",
        "item_type": "material",
        "rarity": "Uncommon",
        "value": 25,
        "weight": 1.0,
        "description": "Refined steel for crafting.",
        "material_type": "metal",
        "quality": 2,
        "crafting_value": 25
    },
    "dragon_scale": {
        "name": "Dragon Scale",
        "item_type": "material",
        "rarity": "Epic",
        "value": 500,
        "weight": 0.5,
        "description": "A scale from a dragon. Highly valuable for crafting.",
        "material_type": "special",
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

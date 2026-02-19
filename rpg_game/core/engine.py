"""
LEGENDS OF ELDORIA - Complete Text-Based RPG Engine
A fully-featured, open-world text-based RPG with plugin support.

Author: YSNRFD
Version: 1.0.0
"""

from __future__ import annotations
import json
import random
import time
import os
import sys
import math
import hashlib
import inspect
from abc import ABC, abstractmethod
from dataclasses import dataclass, field, asdict
from typing import (
    Dict, List, Optional, Any, Callable, Type, Union, Tuple,
    Set, ClassVar
)
from enum import Enum, auto
from datetime import datetime
from pathlib import Path
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# =============================================================================
# ENUMERATIONS
# =============================================================================

class StatType(Enum):
    """Character statistics types"""
    STRENGTH = "strength"
    DEXTERITY = "dexterity"
    CONSTITUTION = "constitution"
    INTELLIGENCE = "intelligence"
    WISDOM = "wisdom"
    CHARISMA = "charisma"
    LUCK = "luck"


class DamageType(Enum):
    """Types of damage"""
    PHYSICAL = "physical"
    MAGICAL = "magical"
    FIRE = "fire"
    ICE = "ice"
    LIGHTNING = "lightning"
    POISON = "poison"
    HOLY = "holy"
    DARK = "dark"
    TRUE = "true"


class ItemType(Enum):
    """Item categories"""
    WEAPON = "weapon"
    ARMOR = "armor"
    ACCESSORY = "accessory"
    CONSUMABLE = "consumable"
    MATERIAL = "material"
    QUEST_ITEM = "quest_item"
    KEY_ITEM = "key_item"
    TREASURE = "treasure"
    BOOK = "book"
    AMMUNITION = "ammunition"


class EquipmentSlot(Enum):
    """Equipment slots"""
    MAIN_HAND = "main_hand"
    OFF_HAND = "off_hand"
    HEAD = "head"
    CHEST = "chest"
    LEGS = "legs"
    FEET = "feet"
    HANDS = "hands"
    NECK = "neck"
    RING_1 = "ring_1"
    RING_2 = "ring_2"
    ACCESSORY = "accessory"


class Rarity(Enum):
    """Item/Entity rarity levels"""
    COMMON = ("Common", 1.0, "\033[90m")
    UNCOMMON = ("Uncommon", 1.2, "\033[92m")
    RARE = ("Rare", 1.5, "\033[94m")
    EPIC = ("Epic", 2.0, "\033[95m")
    LEGENDARY = ("Legendary", 3.0, "\033[93m")
    MYTHIC = ("Mythic", 5.0, "\033[91m")
    DIVINE = ("Divine", 10.0, "\033[97m")

    def __init__(self, display_name: str, multiplier: float, color: str):
        self.display_name = display_name
        self.multiplier = multiplier
        self.color = color


class CharacterClass(Enum):
    """Character classes"""
    WARRIOR = "Warrior"
    MAGE = "Mage"
    ROGUE = "Rogue"
    RANGER = "Ranger"
    PALADIN = "Paladin"
    NECROMANCER = "Necromancer"
    MONK = "Monk"
    BARD = "Bard"
    DRUID = "Druid"
    WARLOCK = "Warlock"


class StatusEffectType(Enum):
    """Status effect types"""
    POISON = "poison"
    BURN = "burn"
    FREEZE = "freeze"
    STUN = "stun"
    BLEED = "bleed"
    REGENERATION = "regeneration"
    BLESSING = "blessing"
    CURSE = "curse"
    HASTE = "haste"
    SLOW = "slow"
    STRENGTH_BUFF = "strength_buff"
    DEFENSE_BUFF = "defense_buff"
    INVISIBLE = "invisible"
    SILENCE = "silence"
    IMMOBILIZE = "immobilize"
    CHARM = "charm"
    FEAR = "fear"
    BLIND = "blind"
    REFLECT = "reflect"
    SHIELD = "shield"


class TimeOfDay(Enum):
    """Time of day"""
    DAWN = "Dawn"
    MORNING = "Morning"
    NOON = "Noon"
    AFTERNOON = "Afternoon"
    DUSK = "Dusk"
    EVENING = "Evening"
    NIGHT = "Night"
    MIDNIGHT = "Midnight"


class Weather(Enum):
    """Weather conditions"""
    CLEAR = "Clear"
    CLOUDY = "Cloudy"
    RAIN = "Rain"
    STORM = "Storm"
    SNOW = "Snow"
    FOG = "Fog"
    SANDSTORM = "Sandstorm"
    BLOOD_MOON = "Blood Moon"
    AURORA = "Aurora"


class QuestStatus(Enum):
    """Quest status states"""
    LOCKED = "locked"
    AVAILABLE = "available"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"


class EventType(Enum):
    """Game event types for plugin hooks"""
    GAME_START = "game_start"
    GAME_END = "game_end"
    GAME_LOAD = "game_load"
    GAME_SAVE = "game_save"
    PLAYER_CREATE = "player_create"
    PLAYER_LEVEL_UP = "player_level_up"
    PLAYER_DEATH = "player_death"
    PLAYER_RESPAWN = "player_respawn"
    COMBAT_START = "combat_start"
    COMBAT_END = "combat_end"
    COMBAT_TURN = "combat_turn"
    ENEMY_KILLED = "enemy_killed"
    ITEM_PICKUP = "item_pickup"
    ITEM_DROP = "item_drop"
    ITEM_USE = "item_use"
    ITEM_EQUIP = "item_equip"
    ITEM_UNEQUIP = "item_unequip"
    QUEST_START = "quest_start"
    QUEST_COMPLETE = "quest_complete"
    QUEST_FAIL = "quest_fail"
    LOCATION_ENTER = "location_enter"
    LOCATION_EXIT = "location_exit"
    NPC_INTERACT = "npc_interact"
    DIALOGUE_CHOICE = "dialogue_choice"
    SHOP_OPEN = "shop_open"
    SHOP_BUY = "shop_buy"
    SHOP_SELL = "shop_sell"
    CRAFT_SUCCESS = "craft_success"
    CRAFT_FAIL = "craft_fail"
    SKILL_USE = "skill_use"
    SKILL_LEARN = "skill_learn"
    SPELL_CAST = "spell_cast"
    EFFECT_APPLY = "effect_apply"
    EFFECT_REMOVE = "effect_remove"
    TIME_CHANGE = "time_change"
    WEATHER_CHANGE = "weather_change"
    ACHIEVEMENT_UNLOCK = "achievement_unlock"
    PLUGIN_LOAD = "plugin_load"
    PLUGIN_UNLOAD = "plugin_unload"
    CUSTOM = "custom"


# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================

def clear_screen():
    """Clear the terminal screen"""
    os.system('cls' if os.name == 'nt' else 'clear')


def colored_text(text: str, color: str) -> str:
    """Return colored text for terminal"""
    return f"{color}{text}\033[0m"


def print_border(char: str = "=", length: int = 80):
    """Print a border line"""
    print(char * length)


def print_boxed(text: str, char: str = "=", width: int = 80):
    """Print text in a bordered box"""
    lines = text.split('\n')
    print(char * width)
    for line in lines:
        padding = width - len(line) - 2
        left_pad = padding // 2
        right_pad = padding - left_pad
        print(f"{char}{' ' * left_pad}{line}{' ' * right_pad}{char}")
    print(char * width)


def roll_dice(sides: int = 20, count: int = 1, modifier: int = 0) -> int:
    """Roll dice and return result"""
    total = sum(random.randint(1, sides) for _ in range(count)) + modifier
    return total


def clamp(value: int, min_val: int, max_val: int) -> int:
    """Clamp value between min and max"""
    return max(min_val, min(value, max_val))


def format_number(num: int) -> str:
    """Format number with commas"""
    return f"{num:,}"


def generate_id() -> str:
    """Generate unique ID"""
    return hashlib.md5(f"{time.time()}{random.random()}".encode()).hexdigest()[:12]


def typewriter_effect(text: str, delay: float = 0.02):
    """Print text with typewriter effect"""
    for char in text:
        sys.stdout.write(char)
        sys.stdout.flush()
        time.sleep(delay)
    print()


def get_input(prompt: str, valid_choices: Optional[List[str]] = None) -> str:
    """Get user input with validation"""
    while True:
        try:
            user_input = input(prompt).strip().lower()
            if valid_choices is None or user_input in [c.lower() for c in valid_choices]:
                return user_input
            print(f"Invalid choice. Please enter one of: {', '.join(valid_choices)}")
        except EOFError:
            print("\nPlease enter a valid input.")
        except KeyboardInterrupt:
            print("\nOperation cancelled.")
            return ""


def pause(message: str = "Press Enter to continue..."):
    """Pause for user input"""
    try:
        input(message)
    except (EOFError, KeyboardInterrupt):
        pass


# =============================================================================
# CORE DATA CLASSES
# =============================================================================

@dataclass
class Stats:
    """Character statistics"""
    strength: int = 10
    dexterity: int = 10
    constitution: int = 10
    intelligence: int = 10
    wisdom: int = 10
    charisma: int = 10
    luck: int = 10

    def __getitem__(self, stat_type: StatType) -> int:
        return getattr(self, stat_type.value, 10)

    def __setitem__(self, stat_type: StatType, value: int):
        setattr(self, stat_type.value, clamp(value, 1, 100))

    def get_modifier(self, stat_type: StatType) -> int:
        """Get D&D style modifier for stat"""
        return (self[stat_type] - 10) // 2

    def to_dict(self) -> Dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict) -> 'Stats':
        return cls(**data)


@dataclass
class Damage:
    """Damage information"""
    amount: int
    damage_type: DamageType
    is_critical: bool = False
    source: str = ""
    bypass_resistance: bool = False


@dataclass
class HealInfo:
    """Healing information"""
    amount: int
    source: str = ""
    is_critical: bool = False


@dataclass
class CombatLog:
    """Combat log entry"""
    turn: int
    actor: str
    action: str
    result: str
    timestamp: float = field(default_factory=time.time)


# =============================================================================
# BASE CLASSES
# =============================================================================

class GameObject(ABC):
    """Base class for all game objects"""

    _id_counter: ClassVar[int] = 0

    def __init__(self, name: str, description: str = ""):
        self.id = self._generate_id()
        self.name = name
        self.description = description
        self.tags: Set[str] = set()
        self.custom_data: Dict[str, Any] = {}

    @classmethod
    def _generate_id(cls) -> str:
        cls._id_counter += 1
        return f"{cls.__name__}_{cls._id_counter}_{random.randint(1000, 9999)}"

    def add_tag(self, tag: str):
        self.tags.add(tag.lower())

    def remove_tag(self, tag: str):
        self.tags.discard(tag.lower())

    def has_tag(self, tag: str) -> bool:
        return tag.lower() in self.tags

    def set_data(self, key: str, value: Any):
        self.custom_data[key] = value

    def get_data(self, key: str, default: Any = None) -> Any:
        return self.custom_data.get(key, default)

    @abstractmethod
    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "tags": list(self.tags),
            "custom_data": self.custom_data
        }

    @classmethod
    @abstractmethod
    def from_dict(cls, data: Dict) -> 'GameObject':
        pass


class Entity(GameObject):
    """Base class for all entities (characters, enemies, NPCs)"""

    def __init__(
        self,
        name: str,
        level: int = 1,
        description: str = "",
        stats: Optional[Stats] = None
    ):
        super().__init__(name, description)
        self.level = level
        self.stats = stats or Stats()
        self.max_hp = self._calculate_max_hp()
        self.current_hp = self.max_hp
        self.max_mp = self._calculate_max_mp()
        self.current_mp = self.max_mp
        self.max_stamina = self._calculate_max_stamina()
        self.current_stamina = self.max_stamina
        self.experience = 0
        self.experience_to_level = self._calculate_exp_to_level()
        self.status_effects: Dict[StatusEffectType, Dict] = {}
        self.is_alive = True
        self.resistances: Dict[DamageType, float] = {dt: 0.0 for dt in DamageType}
        self.abilities: List['Ability'] = []
        self.position: Optional[str] = None
        self.faction: str = "neutral"
        self.hostility_range: int = 5

    def _calculate_max_hp(self) -> int:
        base = 100
        per_level = 20
        con_bonus = self.stats.get_modifier(StatType.CONSTITUTION) * 10
        return base + (self.level * per_level) + con_bonus

    def _calculate_max_mp(self) -> int:
        base = 50
        per_level = 10
        int_bonus = self.stats.get_modifier(StatType.INTELLIGENCE) * 5
        return base + (self.level * per_level) + int_bonus

    def _calculate_max_stamina(self) -> int:
        base = 100
        per_level = 5
        dex_bonus = self.stats.get_modifier(StatType.DEXTERITY) * 5
        con_bonus = self.stats.get_modifier(StatType.CONSTITUTION) * 3
        return base + (self.level * per_level) + dex_bonus + con_bonus

    def _calculate_exp_to_level(self) -> int:
        return int(100 * (1.5 ** (self.level - 1)))

    def take_damage(self, damage: Damage) -> int:
        """Apply damage to entity"""
        if damage.bypass_resistance:
            actual_damage = damage.amount
        else:
            resistance = self.resistances.get(damage.damage_type, 0)
            actual_damage = max(1, int(damage.amount * (1 - resistance)))

        self.current_hp = max(0, self.current_hp - actual_damage)

        if self.current_hp <= 0:
            self.is_alive = False

        return actual_damage

    def heal(self, amount: int) -> int:
        """Heal the entity"""
        old_hp = self.current_hp
        self.current_hp = min(self.max_hp, self.current_hp + amount)
        return self.current_hp - old_hp

    def restore_mp(self, amount: int) -> int:
        """Restore mana"""
        old_mp = self.current_mp
        self.current_mp = min(self.max_mp, self.current_mp + amount)
        return self.current_mp - old_mp

    def restore_stamina(self, amount: int) -> int:
        """Restore stamina"""
        old_stamina = self.current_stamina
        self.current_stamina = min(self.max_stamina, self.current_stamina + amount)
        return self.current_stamina - old_stamina

    def apply_status_effect(self, effect_type: StatusEffectType, duration: int, strength: int = 1):
        """Apply a status effect"""
        self.status_effects[effect_type] = {
            "duration": duration,
            "strength": strength,
            "turns_remaining": duration
        }

    def remove_status_effect(self, effect_type: StatusEffectType):
        """Remove a status effect"""
        self.status_effects.pop(effect_type, None)

    def has_status_effect(self, effect_type: StatusEffectType) -> bool:
        """Check if entity has a status effect"""
        return effect_type in self.status_effects

    def process_status_effects(self) -> List[str]:
        """Process status effects and return messages"""
        messages = []

        for effect_type, data in list(self.status_effects.items()):
            strength = data["strength"]

            if effect_type == StatusEffectType.POISON:
                damage = strength * 5
                self.take_damage(Damage(damage, DamageType.POISON))
                messages.append(f"Poison deals {damage} damage!")

            elif effect_type == StatusEffectType.BURN:
                damage = strength * 8
                self.take_damage(Damage(damage, DamageType.FIRE))
                messages.append(f"Burn deals {damage} damage!")

            elif effect_type == StatusEffectType.REGENERATION:
                heal = strength * 10
                self.heal(heal)
                messages.append(f"Regeneration heals {heal} HP!")

            elif effect_type == StatusEffectType.BLEED:
                damage = strength * 3
                self.take_damage(Damage(damage, DamageType.PHYSICAL))
                messages.append(f"Bleeding deals {damage} damage!")

            data["turns_remaining"] -= 1
            if data["turns_remaining"] <= 0:
                del self.status_effects[effect_type]
                messages.append(f"{effect_type.value.title()} has worn off.")

        return messages

    def get_stat(self, stat_type: StatType) -> int:
        """Get stat value including bonuses"""
        base = self.stats[stat_type]

        for effect_type, data in self.status_effects.items():
            if effect_type == StatusEffectType.STRENGTH_BUFF and stat_type == StatType.STRENGTH:
                base += data["strength"] * 5

        return base

    def get_accuracy(self) -> int:
        """Calculate accuracy"""
        base = 75
        dex_bonus = self.stats.get_modifier(StatType.DEXTERITY) * 2
        luck_bonus = self.stats.get_modifier(StatType.LUCK)
        return base + dex_bonus + luck_bonus

    def get_evasion(self) -> int:
        """Calculate evasion chance"""
        base = 10
        dex_bonus = self.stats.get_modifier(StatType.DEXTERITY) * 2
        return base + dex_bonus

    def get_critical_chance(self) -> float:
        """Calculate critical hit chance"""
        base = 5.0
        luck_bonus = self.stats.get_modifier(StatType.LUCK) * 0.5
        return base + luck_bonus

    def get_critical_damage(self) -> float:
        """Calculate critical damage multiplier"""
        return 2.0 + (self.stats.get_modifier(StatType.LUCK) * 0.1)

    def level_up(self) -> bool:
        """Level up if enough experience"""
        if self.experience >= self.experience_to_level:
            self.experience -= self.experience_to_level
            self.level += 1
            self.experience_to_level = self._calculate_exp_to_level()

            old_max_hp = self.max_hp
            old_max_mp = self.max_mp
            old_max_stamina = self.max_stamina

            self.max_hp = self._calculate_max_hp()
            self.max_mp = self._calculate_max_mp()
            self.max_stamina = self._calculate_max_stamina()

            self.current_hp += self.max_hp - old_max_hp
            self.current_mp += self.max_mp - old_max_mp
            self.current_stamina += self.max_stamina - old_max_stamina

            return True
        return False

    def get_attack_power(self) -> int:
        """Calculate physical attack power"""
        return 10 + self.level * 2 + self.stats.get_modifier(StatType.STRENGTH) * 3

    def get_magic_power(self) -> int:
        """Calculate magic attack power"""
        return 10 + self.level * 2 + self.stats.get_modifier(StatType.INTELLIGENCE) * 3

    def get_defense(self) -> int:
        """Calculate physical defense"""
        return 5 + self.level + self.stats.get_modifier(StatType.CONSTITUTION) * 2

    def get_magic_defense(self) -> int:
        """Calculate magic defense"""
        return 5 + self.level + self.stats.get_modifier(StatType.WISDOM) * 2

    def to_dict(self) -> Dict:
        data = super().to_dict()
        data.update({
            "level": self.level,
            "stats": self.stats.to_dict(),
            "max_hp": self.max_hp,
            "current_hp": self.current_hp,
            "max_mp": self.max_mp,
            "current_mp": self.current_mp,
            "max_stamina": self.max_stamina,
            "current_stamina": self.current_stamina,
            "experience": self.experience,
            "experience_to_level": self.experience_to_level,
            "status_effects": {k.value: v for k, v in self.status_effects.items()},
            "is_alive": self.is_alive,
            "resistances": {k.value: v for k, v in self.resistances.items()},
            "position": self.position,
            "faction": self.faction,
            "hostility_range": self.hostility_range
        })
        return data

    @classmethod
    def from_dict(cls, data: Dict) -> 'Entity':
        entity = cls(
            name=data["name"],
            level=data["level"],
            description=data["description"]
        )
        entity.id = data["id"]
        entity.stats = Stats.from_dict(data["stats"])
        entity.max_hp = data["max_hp"]
        entity.current_hp = data["current_hp"]
        entity.max_mp = data["max_mp"]
        entity.current_mp = data["current_mp"]
        entity.max_stamina = data["max_stamina"]
        entity.current_stamina = data["current_stamina"]
        entity.experience = data["experience"]
        entity.experience_to_level = data["experience_to_level"]
        entity.status_effects = {
            StatusEffectType(k): v for k, v in data.get("status_effects", {}).items()
        }
        entity.is_alive = data["is_alive"]
        entity.resistances = {
            DamageType(k): v for k, v in data.get("resistances", {}).items()
        }
        entity.position = data.get("position")
        entity.faction = data.get("faction", "neutral")
        entity.hostility_range = data.get("hostility_range", 5)
        entity.tags = set(data.get("tags", []))
        entity.custom_data = data.get("custom_data", {})
        return entity


# =============================================================================
# ITEM BASE CLASS
# =============================================================================

@dataclass
class Item(GameObject):
    """Base item class"""
    name: str = ""
    item_type: ItemType = ItemType.MATERIAL
    rarity: Rarity = Rarity.COMMON
    value: int = 1
    weight: float = 0.1
    stackable: bool = False
    max_stack: int = 99
    quantity: int = 1
    description: str = ""
    level_required: int = 1
    effects: List[Tuple[str, Any]] = field(default_factory=list)

    def __post_init__(self):
        super().__init__(self.name, self.description)

    def use(self, user: Entity) -> Tuple[bool, str]:
        """Use the item"""
        return False, "This item cannot be used."

    def get_display_name(self) -> str:
        """Get colored display name"""
        return f"{self.rarity.color}[{self.rarity.display_name}] {self.name}\033[0m"

    def examine(self) -> str:
        """Get detailed item description"""
        lines = [
            self.get_display_name(),
            f"Type: {self.item_type.value.title()}",
            f"Value: {value:,} gold" if (value := self.value) else "Value: 1 gold",
            f"Weight: {self.weight:.1f} kg",
            f"",
            f"{self.description}"
        ]
        if self.level_required > 1:
            lines.append(f"Required Level: {self.level_required}")
        return "\n".join(lines)

    def to_dict(self) -> Dict:
        data = super().to_dict()
        data.update({
            "name": self.name,
            "item_type": self.item_type.value,
            "rarity": self.rarity.value,
            "value": self.value,
            "weight": self.weight,
            "stackable": self.stackable,
            "max_stack": self.max_stack,
            "quantity": self.quantity,
            "description": self.description,
            "level_required": self.level_required,
            "effects": self.effects
        })
        return data

    @classmethod
    def from_dict(cls, data: Dict) -> 'Item':
        return cls(
            name=data["name"],
            item_type=ItemType(data["item_type"]),
            rarity=Rarity(data["rarity"]),
            value=data["value"],
            weight=data["weight"],
            stackable=data["stackable"],
            max_stack=data["max_stack"],
            quantity=data["quantity"],
            description=data["description"],
            level_required=data.get("level_required", 1),
            effects=data.get("effects", [])
        )


# =============================================================================
# ABILITY SYSTEM
# =============================================================================

class AbilityType(Enum):
    ACTIVE = "active"
    PASSIVE = "passive"
    TOGGLE = "toggle"


class TargetType(Enum):
    SELF = "self"
    SINGLE_ENEMY = "single_enemy"
    ALL_ENEMIES = "all_enemies"
    SINGLE_ALLY = "single_ally"
    ALL_ALLIES = "all_allies"
    AREA = "area"
    GROUND = "ground"
    ANY = "any"


@dataclass
class Ability:
    """Represents an ability or spell"""
    name: str
    description: str
    ability_type: AbilityType
    target_type: TargetType
    mp_cost: int = 0
    stamina_cost: int = 0
    hp_cost: int = 0
    cooldown: int = 0
    current_cooldown: int = 0
    damage: int = 0
    damage_type: Optional[DamageType] = None
    healing: int = 0
    effects: List[Tuple[StatusEffectType, int, int]] = field(default_factory=list)
    level_required: int = 1
    class_required: Optional[CharacterClass] = None
    range: int = 1
    accuracy_modifier: int = 0
    critical_modifier: float = 0.0
    requirements: Dict[str, Any] = field(default_factory=dict)

    def can_use(self, caster: Entity) -> Tuple[bool, str]:
        """Check if ability can be used"""
        if self.current_cooldown > 0:
            return False, f"Ability on cooldown: {self.current_cooldown} turns remaining"

        if caster.current_mp < self.mp_cost:
            return False, f"Not enough MP (need {self.mp_cost}, have {caster.current_mp})"

        if caster.current_stamina < self.stamina_cost:
            return False, f"Not enough stamina (need {self.stamina_cost}, have {caster.current_stamina})"

        if caster.current_hp <= self.hp_cost:
            return False, f"Not enough HP for sacrifice"

        if caster.level < self.level_required:
            return False, f"Required level: {self.level_required}"

        return True, "Can use"

    def use(self, caster: Entity, target: Entity) -> Dict[str, Any]:
        """Use the ability on a target"""
        result = {
            "success": False,
            "damage": 0,
            "healing": 0,
            "effects_applied": [],
            "messages": []
        }

        can_use, message = self.can_use(caster)
        if not can_use:
            result["messages"].append(message)
            return result

        # Apply costs
        caster.current_mp -= self.mp_cost
        caster.current_stamina -= self.stamina_cost
        caster.current_hp -= self.hp_cost

        result["success"] = True
        self.current_cooldown = self.cooldown

        # Calculate damage
        if self.damage > 0:
            is_critical = random.random() < (caster.get_critical_chance() + self.critical_modifier)
            damage_mult = caster.get_critical_damage() if is_critical else 1.0

            base_damage = self.damage + caster.get_magic_power() if self.damage_type != DamageType.PHYSICAL else self.damage + caster.get_attack_power()
            total_damage = int(base_damage * damage_mult)

            if self.damage_type:
                actual_damage = target.take_damage(Damage(
                    total_damage,
                    self.damage_type,
                    is_critical
                ))
                result["damage"] = actual_damage
                crit_text = " CRITICAL!" if is_critical else ""
                result["messages"].append(f"{caster.name}'s {self.name} deals {actual_damage} {self.damage_type.value} damage to {target.name}!{crit_text}")

        # Apply healing
        if self.healing > 0:
            heal_amount = target.heal(self.healing + caster.get_magic_power() // 2)
            result["healing"] = heal_amount
            result["messages"].append(f"{self.name} heals {target.name} for {heal_amount} HP!")

        # Apply status effects
        for effect_type, duration, strength in self.effects:
            target.apply_status_effect(effect_type, duration, strength)
            result["effects_applied"].append(effect_type.value)
            result["messages"].append(f"{target.name} is afflicted with {effect_type.value}!")

        return result

    def end_turn(self):
        """Reduce cooldown at end of turn"""
        if self.current_cooldown > 0:
            self.current_cooldown -= 1

    def to_dict(self) -> Dict:
        return {
            "name": self.name,
            "description": self.description,
            "ability_type": self.ability_type.value,
            "target_type": self.target_type.value,
            "mp_cost": self.mp_cost,
            "stamina_cost": self.stamina_cost,
            "hp_cost": self.hp_cost,
            "cooldown": self.cooldown,
            "current_cooldown": self.current_cooldown,
            "damage": self.damage,
            "damage_type": self.damage_type.value if self.damage_type else None,
            "healing": self.healing,
            "effects": [(e.value, d, s) for e, d, s in self.effects],
            "level_required": self.level_required,
            "class_required": self.class_required.value if self.class_required else None,
            "range": self.range,
            "accuracy_modifier": self.accuracy_modifier,
            "critical_modifier": self.critical_modifier,
            "requirements": self.requirements
        }

    @classmethod
    def from_dict(cls, data: Dict) -> 'Ability':
        return cls(
            name=data["name"],
            description=data["description"],
            ability_type=AbilityType(data["ability_type"]),
            target_type=TargetType(data["target_type"]),
            mp_cost=data["mp_cost"],
            stamina_cost=data["stamina_cost"],
            hp_cost=data.get("hp_cost", 0),
            cooldown=data["cooldown"],
            current_cooldown=data["current_cooldown"],
            damage=data["damage"],
            damage_type=DamageType(data["damage_type"]) if data.get("damage_type") else None,
            healing=data["healing"],
            effects=[(StatusEffectType(e), d, s) for e, d, s in data.get("effects", [])],
            level_required=data.get("level_required", 1),
            class_required=CharacterClass(data["class_required"]) if data.get("class_required") else None,
            range=data.get("range", 1),
            accuracy_modifier=data.get("accuracy_modifier", 0),
            critical_modifier=data.get("critical_modifier", 0.0),
            requirements=data.get("requirements", {})
        )


print("Core engine module loaded successfully!")

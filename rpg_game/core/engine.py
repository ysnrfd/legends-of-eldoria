"""
LEGENDS OF ELDORIA - Complete Text-Based RPG Engine
A fully-featured, open-world text-based RPG with plugin support.

Author: YSNRFD
Version: 1.0.0
"""

from __future__ import annotations
import random
import time
import os
import hashlib
from dataclasses import dataclass, field
from typing import (
    Dict, List, Optional, Any, Union, Tuple
)
from enum import Enum
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
    BLEED = "bleed"
    STUN = "stun"
    SLOW = "slow"
    HASTE = "haste"
    REGENERATION = "regeneration"
    SHIELD = "shield"
    BLESSING = "blessing"
    CURSE = "curse"
    FEAR = "fear"
    CHARM = "charm"
    INVISIBLE = "invisible"
    STRENGTH_BUFF = "strength_buff"
    DEFENSE_BUFF = "defense_buff"
    MAGIC_BUFF = "magic_buff"
    IMMOBILIZE = "immobilize"
    SILENCE = "silence"
    CONFUSION = "confusion"


class AbilityType(Enum):
    """Ability types"""
    ACTIVE = "active"
    PASSIVE = "passive"
    TOGGLE = "toggle"
    ULTIMATE = "ultimate"


class TargetType(Enum):
    """Target types for abilities"""
    SELF = "self"
    SINGLE_ENEMY = "single_enemy"
    ALL_ENEMIES = "all_enemies"
    SINGLE_ALLY = "single_ally"
    ALL_ALLIES = "all_allies"
    AREA = "area"


class EventType(Enum):
    """Game event types"""
    GAME_START = "game_start"
    GAME_END = "game_end"
    GAME_SAVE = "game_save"
    GAME_LOAD = "game_load"
    COMBAT_START = "combat_start"
    COMBAT_END = "combat_end"
    TURN_START = "turn_start"
    TURN_END = "turn_end"
    DAMAGE_DEALT = "damage_dealt"
    DAMAGE_TAKEN = "damage_taken"
    HEALING_RECEIVED = "healing_received"
    ITEM_ACQUIRED = "item_acquired"
    ITEM_USED = "item_used"
    QUEST_STARTED = "quest_started"
    QUEST_COMPLETED = "quest_completed"
    QUEST_OBJECTIVE_UPDATED = "quest_objective_updated"
    LEVEL_UP = "level_up"
    DEATH = "death"
    RESURRECTION = "resurrection"
    LOCATION_ENTER = "location_enter"
    LOCATION_LEAVE = "location_leave"
    NPC_INTERACTION = "npc_interaction"
    SHOP_OPEN = "shop_open"
    CRAFTING_SUCCESS = "crafting_success"
    CRAFTING_FAILURE = "crafting_failure"
    PLUGIN_LOADED = "plugin_loaded"
    PLUGIN_UNLOADED = "plugin_unloaded"


class TimeOfDay(Enum):
    """Time of day"""
    DAWN = "dawn"
    MORNING = "morning"
    NOON = "noon"
    AFTERNOON = "afternoon"
    DUSK = "dusk"
    NIGHT = "night"
    MIDNIGHT = "midnight"


class Weather(Enum):
    """Weather conditions"""
    CLEAR = "clear"
    CLOUDY = "cloudy"
    RAIN = "rain"
    STORM = "storm"
    SNOW = "snow"
    FOG = "fog"
    WINDY = "windy"


class QuestStatus(Enum):
    """Quest status"""
    AVAILABLE = "available"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    TURNED_IN = "turned_in"


# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================

def clamp(value: Union[int, float], min_val: Union[int, float], max_val: Union[int, float]) -> Union[int, float]:
    """Clamp value between min and max"""
    return max(min_val, min(value, max_val))


def roll_dice(sides: int = 20, count: int = 1) -> int:
    """Roll dice"""
    return sum(random.randint(1, sides) for _ in range(count))


def format_number(num: Union[int, float]) -> str:
    """Format large numbers"""
    if num >= 1_000_000:
        return f"{num/1_000_000:.1f}M"
    elif num >= 1_000:
        return f"{num/1_000:.1f}k"
    return str(int(num))


def colored_text(text: str, color_code: str) -> str:
    """Apply color to text"""
    return f"{color_code}{text}\033[0m"


def clear_screen():
    """Clear the terminal screen"""
    os.system('cls' if os.name == 'nt' else 'clear')


def print_border(width: int = 60, char: str = "="):
    """Print a border line"""
    print(char * width)


def print_boxed(text: str, width: int = 60):
    """Print text in a box"""
    print("=" * width)
    print(f"  {text}")
    print("=" * width)


def get_input(prompt: str, valid_options: Optional[List[str]] = None) -> str:
    """Get user input with optional validation"""
    while True:
        try:
            user_input = input(prompt).strip().lower()
            if valid_options is None or user_input in valid_options:
                return user_input
            print("Invalid option. Please try again.")
        except (EOFError, KeyboardInterrupt):
            return ""


def pause(message: str = "Press Enter to continue..."):
    """Pause for user input"""
    input(message)


def typewriter_effect(text: str, delay: float = 0.03):
    """Print text with typewriter effect"""
    for char in text:
        print(char, end='', flush=True)
        time.sleep(delay)
    print()


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
    
    def get_modifier(self, stat_type: StatType) -> int:
        """Get ability modifier for a stat"""
        value = getattr(self, stat_type.value, 10)
        return (value - 10) // 2
    
    def to_dict(self) -> Dict:
        return {
            "strength": self.strength,
            "dexterity": self.dexterity,
            "constitution": self.constitution,
            "intelligence": self.intelligence,
            "wisdom": self.wisdom,
            "charisma": self.charisma,
            "luck": self.luck
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Stats':
        return cls(
            strength=data.get("strength", 10),
            dexterity=data.get("dexterity", 10),
            constitution=data.get("constitution", 10),
            intelligence=data.get("intelligence", 10),
            wisdom=data.get("wisdom", 10),
            charisma=data.get("charisma", 10),
            luck=data.get("luck", 10)
        )


@dataclass
class Damage:
    """Represents damage dealt"""
    amount: int
    damage_type: DamageType
    is_critical: bool = False
    is_dodged: bool = False
    is_blocked: bool = False
    source: Optional[str] = None
    
    def apply(self, target: 'Entity') -> int:
        """Apply damage to target"""
        if self.is_dodged:
            return 0
        
        actual_damage = self.amount
        
        if self.is_blocked:
            actual_damage = actual_damage // 2
        
        # Apply resistances
        resistance = target.resistances.get(self.damage_type, 0)
        actual_damage = int(actual_damage * (1 - resistance))
        
        # Apply defense buff
        if StatusEffectType.DEFENSE_BUFF in target.status_effects:
            buff_data = target.status_effects[StatusEffectType.DEFENSE_BUFF]
            buff_value = buff_data.get("value", 0)
            actual_damage = max(1, actual_damage - buff_value)
        
        target.current_hp -= actual_damage
        if target.current_hp <= 0:
            target.is_alive = False
        
        return actual_damage


@dataclass
class CombatLog:
    """Log entry for combat"""
    turn: int
    actor: str
    action: str
    target: Optional[str] = None
    damage: int = 0
    healing: int = 0
    effects_applied: List[str] = field(default_factory=list)
    message: str = ""


@dataclass
class GameObject:
    """Base class for all game objects"""
    id: str = field(default_factory=lambda: hashlib.md5(str(time.time()).encode()).hexdigest()[:8])
    name: str = "Unknown"
    description: str = ""
    created_at: float = field(default_factory=time.time)
    
    def examine(self) -> str:
        """Get detailed description"""
        return f"{self.name}\n{'='*40}\n{self.description}"


@dataclass
class Item(GameObject):
    """Base item class"""
    item_type: ItemType = ItemType.MATERIAL
    rarity: Rarity = Rarity.COMMON
    value: int = 0
    weight: float = 0.0
    quantity: int = 1
    max_stack: int = 99
    stackable: bool = True
    level_required: int = 1
    usable: bool = False
    equippable: bool = False
    
    def __post_init__(self):
        if not self.id:
            self.id = hashlib.md5(f"{self.name}{time.time()}".encode()).hexdigest()[:8]
    
    def get_value(self) -> int:
        """Get total value including quantity"""
        return self.value * self.quantity
    
    def get_weight(self) -> float:
        """Get total weight including quantity"""
        return self.weight * self.quantity
    
    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "item_type": self.item_type.value,
            "rarity": self.rarity.name,
            "value": self.value,
            "weight": self.weight,
            "quantity": self.quantity,
            "max_stack": self.max_stack,
            "stackable": self.stackable,
            "level_required": self.level_required,
            "usable": self.usable,
            "equippable": self.equippable
        }


@dataclass
class Ability:
    """Character ability/skill"""
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
    effects: List[Tuple[StatusEffectType, int, int]] = field(default_factory=list)  # (type, duration, strength)
    level_required: int = 1
    class_required: Optional[CharacterClass] = None
    range: int = 1
    accuracy_modifier: int = 0
    critical_modifier: float = 0.0
    requirements: Dict[str, Any] = field(default_factory=dict)
    
    def can_use(self, user: 'Entity') -> Tuple[bool, str]:
        """Check if ability can be used"""
        if self.current_cooldown > 0:
            return False, f"On cooldown ({self.current_cooldown} turns remaining)"
        
        if user.current_mp < self.mp_cost:
            return False, f"Not enough MP (need {self.mp_cost})"
        
        if user.current_stamina < self.stamina_cost:
            return False, f"Not enough stamina (need {self.stamina_cost})"
        
        if user.current_hp <= self.hp_cost:
            return False, f"Not enough HP (need {self.hp_cost})"
        
        if user.level < self.level_required:
            return False, f"Requires level {self.level_required}"
        
        if self.class_required and hasattr(user, 'character_class'):
            if user.character_class != self.class_required:
                return False, f"Requires {self.class_required.value} class"
        
        return True, "Can use"
    
    def use(self, user: 'Entity', target: Optional['Entity'] = None) -> Dict[str, Any]:
        """Use the ability"""
        can_use, msg = self.can_use(user)
        if not can_use:
            return {"success": False, "message": msg}
        
        # Pay costs
        user.current_mp -= self.mp_cost
        user.current_stamina -= self.stamina_cost
        user.current_hp -= self.hp_cost
        self.current_cooldown = self.cooldown
        
        result = {
            "success": True,
            "message": f"{user.name} uses {self.name}!",
            "damage_dealt": 0,
            "healing_done": 0,
            "effects_applied": [],
            "messages": []
        }
        
        # Apply damage
        if self.damage > 0 and target:
            is_critical = random.random() < (user.get_critical_chance() + self.critical_modifier)
            damage_amount = self.damage
            
            if is_critical:
                damage_amount = int(damage_amount * 1.5)
            
            damage = Damage(
                amount=damage_amount,
                damage_type=self.damage_type or DamageType.PHYSICAL,
                is_critical=is_critical,
                source=self.name
            )
            
            actual_damage = damage.apply(target)
            result["damage_dealt"] = actual_damage
            result["messages"].append(f"Dealt {actual_damage} damage!")
            
            if is_critical:
                result["messages"].append("Critical hit!")
        
        # Apply healing
        if self.healing > 0:
            heal_amount = self.healing
            user.heal(heal_amount)
            result["healing_done"] = heal_amount
            result["messages"].append(f"Healed for {heal_amount} HP!")
        
        # Apply effects
        for effect_type, duration, strength in self.effects:
            if target:
                target.apply_status_effect(effect_type, duration, strength)
            else:
                user.apply_status_effect(effect_type, duration, strength)
            result["effects_applied"].append(effect_type.value)
            result["messages"].append(f"{target.name if target else user.name} is afflicted with {effect_type.value}!")
        
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


class Entity(GameObject):
    """Base entity class for characters and enemies"""
    
    def __init__(
        self,
        name: str,
        level: int = 1,
        description: str = "",
        stats: Optional[Stats] = None
    ):
        super().__init__(name=name, description=description)
        self.level = level
        self.stats = stats or Stats()
        
        # Combat stats
        self.max_hp = self._calculate_max_hp()
        self.current_hp = self.max_hp
        self.max_mp = self._calculate_max_mp()
        self.current_mp = self.max_mp
        self.max_stamina = self._calculate_max_stamina()
        self.current_stamina = self.max_stamina
        
        # Experience
        self.experience = 0
        self.experience_to_level = self._calculate_exp_to_level()
        
        # Status
        self.is_alive = True
        self.status_effects: Dict[StatusEffectType, Dict[str, Any]] = {}
        self.abilities: List[Ability] = []
        
        # Resistances
        self.resistances: Dict[DamageType, float] = {
            DamageType.PHYSICAL: 0.0,
            DamageType.MAGICAL: 0.0,
            DamageType.FIRE: 0.0,
            DamageType.ICE: 0.0,
            DamageType.LIGHTNING: 0.0,
            DamageType.POISON: 0.0,
            DamageType.HOLY: 0.0,
            DamageType.DARK: 0.0,
            DamageType.TRUE: 0.0
        }
        
        # Position
        self.position: Optional[str] = None
        self.faction: str = "neutral"
    
    def _calculate_max_hp(self) -> int:
        """Calculate maximum HP"""
        con_mod = self.stats.get_modifier(StatType.CONSTITUTION)
        return 50 + (self.level * 10) + (con_mod * 5)
    
    def _calculate_max_mp(self) -> int:
        """Calculate maximum MP"""
        int_mod = self.stats.get_modifier(StatType.INTELLIGENCE)
        wis_mod = self.stats.get_modifier(StatType.WISDOM)
        return 20 + (self.level * 5) + (int_mod * 3) + (wis_mod * 2)
    
    def _calculate_max_stamina(self) -> int:
        """Calculate maximum stamina"""
        con_mod = self.stats.get_modifier(StatType.CONSTITUTION)
        str_mod = self.stats.get_modifier(StatType.STRENGTH)
        return 30 + (self.level * 5) + (con_mod * 2) + (str_mod * 2)
    
    def _calculate_exp_to_level(self) -> int:
        """Calculate experience needed for next level"""
        return int(100 * (1.5 ** (self.level - 1)))
    
    def get_stat(self, stat_type: StatType) -> int:
        """Get stat value"""
        return getattr(self.stats, stat_type.value, 10)
    
    def get_attack_power(self) -> int:
        """Calculate attack power"""
        str_mod = self.stats.get_modifier(StatType.STRENGTH)
        return 10 + (self.level * 2) + (str_mod * 2)
    
    def get_defense(self) -> int:
        """Calculate defense"""
        con_mod = self.stats.get_modifier(StatType.CONSTITUTION)
        return 5 + (self.level) + con_mod
    
    def get_magic_power(self) -> int:
        """Calculate magic power"""
        int_mod = self.stats.get_modifier(StatType.INTELLIGENCE)
        return 10 + (self.level * 2) + (int_mod * 3)
    
    def get_accuracy(self) -> int:
        """Calculate accuracy percentage"""
        dex_mod = self.stats.get_modifier(StatType.DEXTERITY)
        return clamp(50 + (self.level * 2) + (dex_mod * 2), 5, 95)
    
    def get_evasion(self) -> int:
        """Calculate evasion percentage"""
        dex_mod = self.stats.get_modifier(StatType.DEXTERITY)
        return clamp(5 + (self.level) + dex_mod, 0, 50)
    
    def get_critical_chance(self) -> float:
        """Calculate critical hit chance"""
        luck_mod = self.stats.get_modifier(StatType.LUCK)
        return clamp(0.05 + (luck_mod * 0.01), 0.0, 0.5)
    
    def get_resistances(self) -> Dict[DamageType, float]:
        """Get damage resistances"""
        return self.resistances.copy()
    
    def heal(self, amount: int):
        """Heal the entity"""
        self.current_hp = min(self.max_hp, self.current_hp + amount)
    
    def restore_mp(self, amount: int):
        """Restore MP"""
        self.current_mp = min(self.max_mp, self.current_mp + amount)
    
    def restore_stamina(self, amount: int):
        """Restore stamina"""
        self.current_stamina = min(self.max_stamina, self.current_stamina + amount)
    
    def take_damage(self, damage: Damage) -> int:
        """Take damage"""
        return damage.apply(self)
    
    def apply_status_effect(self, effect_type: StatusEffectType, duration: int, strength: int = 1):
        """Apply a status effect"""
        self.status_effects[effect_type] = {
            "turns_remaining": duration,
            "strength": strength,
            "applied_at": time.time()
        }
    
    def remove_status_effect(self, effect_type: StatusEffectType):
        """Remove a status effect"""
        if effect_type in self.status_effects:
            del self.status_effects[effect_type]
    
    def process_status_effects(self) -> List[str]:
        """Process active status effects at turn end"""
        messages = []
        effects_to_remove = []
        
        for effect_type, data in self.status_effects.items():
            # Apply effect
            if effect_type == StatusEffectType.POISON:
                damage = data["strength"] * 5
                self.current_hp -= damage
                messages.append(f"{self.name} takes {damage} poison damage!")
            
            elif effect_type == StatusEffectType.BURN:
                damage = data["strength"] * 3
                self.current_hp -= damage
                messages.append(f"{self.name} takes {damage} burn damage!")
            
            elif effect_type == StatusEffectType.BLEED:
                damage = data["strength"] * 4
                self.current_hp -= damage
                messages.append(f"{self.name} takes {damage} bleed damage!")
            
            elif effect_type == StatusEffectType.REGENERATION:
                healing = data["strength"] * 5
                self.heal(healing)
                messages.append(f"{self.name} regenerates {healing} HP!")
            
            # Decrement duration
            data["turns_remaining"] -= 1
            if data["turns_remaining"] <= 0:
                effects_to_remove.append(effect_type)
                messages.append(f"{effect_type.value.title()} wore off!")
        
        # Remove expired effects
        for effect in effects_to_remove:
            del self.status_effects[effect]
        
        # Check death
        if self.current_hp <= 0:
            self.is_alive = False
            messages.append(f"{self.name} has fallen!")
        
        return messages
    
    def level_up(self) -> bool:
        """Attempt to level up"""
        if self.experience >= self.experience_to_level:
            self.level += 1
            self.experience -= self.experience_to_level
            self.experience_to_level = self._calculate_exp_to_level()
            
            # Increase stats
            self.max_hp = self._calculate_max_hp()
            self.max_mp = self._calculate_max_mp()
            self.max_stamina = self._calculate_max_stamina()
            
            # Restore resources
            self.current_hp = self.max_hp
            self.current_mp = self.max_mp
            self.current_stamina = self.max_stamina
            
            return True
        return False
    
    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
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
            "is_alive": self.is_alive,
            "status_effects": {
                k.value: v for k, v in self.status_effects.items()
            },
            "resistances": {k.value: v for k, v in self.resistances.items()},
            "position": self.position,
            "faction": self.faction
        }


print("Core engine module loaded successfully!")

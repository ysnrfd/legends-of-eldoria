"""
Mount System - Rideable creatures for travel and combat

Author: YSNRFD
Version: 1.0.0
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, TYPE_CHECKING
from enum import Enum
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.engine import GameObject, Rarity, colored_text

if TYPE_CHECKING:
    from core.character import Character


class MountType(Enum):
    """Types of mounts"""
    HORSE = "horse"
    WOLF = "wolf"
    DRAGON = "dragon"
    GRIFFIN = "griffin"
    SPIDER = "spider"
    GOLEM = "golem"
    MAGIC_CARPET = "magic_carpet"
    GIANT_TURTLE = "giant_turtle"
    PHOENIX = "phoenix"
    UNICORN = "unicorn"


class MountSpeed(Enum):
    """Mount speed tiers"""
    SLOW = 1.2      # 20% faster
    NORMAL = 1.5    # 50% faster
    FAST = 2.0      # 100% faster
    VERY_FAST = 3.0 # 200% faster


@dataclass
class Mount(GameObject):
    """A rideable mount"""
    mount_type: MountType = MountType.HORSE
    speed: MountSpeed = MountSpeed.NORMAL
    rarity: Rarity = Rarity.COMMON
    level_required: int = 1
    stamina_cost: int = 5  # Stamina cost per travel
    combat_bonus: Dict[str, Any] = field(default_factory=dict)
    is_summoned: bool = False
    hunger: int = 100  # 0-100, decreases over time
    happiness: int = 100  # 0-100, affects performance
    experience: int = 0  # Mount can level up too
    level: int = 1
    max_level: int = 10
    special_ability: Optional[str] = None
    value: int = 100
    can_fly: bool = False
    can_swim: bool = False
    can_climb: bool = False
    
    def __post_init__(self):
        if not self.id:
            import hashlib
            import time
            self.id = hashlib.md5(f"{self.name}{time.time()}".encode()).hexdigest()[:8]
    
    def get_speed_multiplier(self) -> float:
        """Calculate actual speed based on mount condition"""
        base_speed = self.speed.value
        
        # Happiness affects speed (50-100% efficiency)
        happiness_mod = 0.5 + (self.happiness / 200)
        
        # Hunger affects speed (starving mounts are slower)
        if self.hunger < 20:
            hunger_mod = 0.5
        elif self.hunger < 50:
            hunger_mod = 0.75
        else:
            hunger_mod = 1.0
        
        return base_speed * happiness_mod * hunger_mod
    
    def feed(self, food_value: int = 20) -> str:
        """Feed the mount to restore hunger"""
        old_hunger = self.hunger
        self.hunger = min(100, self.hunger + food_value)
        self.happiness = min(100, self.happiness + 5)
        
        if self.hunger == 100:
            return f"{self.name} is completely satisfied!"
        elif self.hunger > old_hunger:
            return f"{self.name} happily eats the food. Hunger: {old_hunger} -> {self.hunger}"
        else:
            return f"{self.name} is not hungry right now."
    
    def pet(self) -> str:
        """Pet the mount to increase happiness"""
        old_happiness = self.happiness
        self.happiness = min(100, self.happiness + 10)
        
        if self.happiness == 100:
            return f"{self.name} loves you! Happiness is maxed out."
        else:
            return f"You pet {self.name}. Happiness: {old_happiness} -> {self.happiness}"
    
    def travel(self, distance: int = 1) -> tuple[bool, str]:
        """Travel using this mount"""
        if self.hunger <= 0:
            return False, f"{self.name} is too hungry to travel! Feed them first."
        
        if self.stamina_cost > 0:
            self.hunger = max(0, self.hunger - self.stamina_cost)
        
        speed = self.get_speed_multiplier()
        return True, f"You travel on {self.name} at {speed:.1f}x speed!"
    
    def add_experience(self, amount: int) -> bool:
        """Add experience to mount and check for level up"""
        self.experience += amount
        
        exp_needed = self.get_exp_to_level()
        if self.experience >= exp_needed and self.level < self.max_level:
            self.experience -= exp_needed
            self.level += 1
            self._on_level_up()
            return True
        return False
    
    def get_exp_to_level(self) -> int:
        """Calculate experience needed for next level"""
        return int(100 * (1.5 ** (self.level - 1)))
    
    def _on_level_up(self):
        """Handle mount level up"""
        # Improve stats on level up
        self.happiness = 100
        self.hunger = 100
        
        # Increase speed tier if applicable
        if self.level == 5 and self.speed == MountSpeed.SLOW:
            self.speed = MountSpeed.NORMAL
        elif self.level == 10 and self.speed == MountSpeed.NORMAL:
            self.speed = MountSpeed.FAST
    
    def get_display(self) -> str:
        """Get formatted mount display"""
        speed_text = f"{self.get_speed_multiplier():.1f}x"
        rarity_color = self.rarity.color
        
        lines = [
            f"\n{'='*50}",
            f"{rarity_color}🐎 {self.name}\033[0m",
            f"{'='*50}",
            f"Type: {self.mount_type.value.title()}",
            f"Level: {self.level}/{self.max_level}",
            f"Speed: {speed_text}",
            f"Hunger: {self.hunger}/100",
            f"Happiness: {self.happiness}/100",
            f"Experience: {self.experience}/{self.get_exp_to_level()}",
        ]
        
        if self.special_ability:
            lines.append(f"Special Ability: {self.special_ability}")
        
        if self.can_fly:
            lines.append("✈️ Can Fly")
        if self.can_swim:
            lines.append("🌊 Can Swim")
        if self.can_climb:
            lines.append("⛰️ Can Climb Mountains")
        
        # Combat bonuses
        if self.combat_bonus:
            lines.append("\nCombat Bonuses:")
            for bonus, value in self.combat_bonus.items():
                lines.append(f"  • {bonus}: {value}")
        
        return "\n".join(lines)
    
    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "mount_type": self.mount_type.value,
            "speed": self.speed.value,
            "rarity": self.rarity.value,
            "level_required": self.level_required,
            "stamina_cost": self.stamina_cost,
            "combat_bonus": self.combat_bonus,
            "is_summoned": self.is_summoned,
            "hunger": self.hunger,
            "happiness": self.happiness,
            "experience": self.experience,
            "level": self.level,
            "max_level": self.max_level,
            "special_ability": self.special_ability,
            "value": self.value,
            "can_fly": self.can_fly,
            "can_swim": self.can_swim,
            "can_climb": self.can_climb
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Mount':
        return cls(
            id=data.get("id"),
            name=data["name"],
            description=data.get("description", ""),
            mount_type=MountType(data.get("mount_type", "horse")),
            speed=MountSpeed(data.get("speed", 1.5)),
            rarity=Rarity(data.get("rarity", "common")),
            level_required=data.get("level_required", 1),
            stamina_cost=data.get("stamina_cost", 5),
            combat_bonus=data.get("combat_bonus", {}),
            is_summoned=data.get("is_summoned", False),
            hunger=data.get("hunger", 100),
            happiness=data.get("happiness", 100),
            experience=data.get("experience", 0),
            level=data.get("level", 1),
            max_level=data.get("max_level", 10),
            special_ability=data.get("special_ability"),
            value=data.get("value", 100),
            can_fly=data.get("can_fly", False),
            can_swim=data.get("can_swim", False),
            can_climb=data.get("can_climb", False)
        )


# =============================================================================
# MOUNT DATABASE
# =============================================================================

MOUNT_DATABASE: Dict[str, Mount] = {
    # Common Mounts
    "brown_horse": Mount(
        name="Brown Horse",
        description="A reliable steed. Not fast, but dependable.",
        mount_type=MountType.HORSE,
        speed=MountSpeed.SLOW,
        rarity=Rarity.COMMON,
        level_required=1,
        value=100,
        stamina_cost=3
    ),
    "white_horse": Mount(
        name="White Horse",
        description="A swift and noble mount.",
        mount_type=MountType.HORSE,
        speed=MountSpeed.NORMAL,
        rarity=Rarity.UNCOMMON,
        level_required=5,
        value=300,
        stamina_cost=4
    ),
    "giant_wolf": Mount(
        name="Giant Wolf",
        description="A fierce wolf that has been tamed. Fast and agile.",
        mount_type=MountType.WOLF,
        speed=MountSpeed.NORMAL,
        rarity=Rarity.UNCOMMON,
        level_required=8,
        value=500,
        stamina_cost=5,
        combat_bonus={"attack_power": 5},
        can_climb=True
    ),
    
    # Rare Mounts
    "armored_warhorse": Mount(
        name="Armored Warhorse",
        description="A battle-trained horse in heavy armor.",
        mount_type=MountType.HORSE,
        speed=MountSpeed.NORMAL,
        rarity=Rarity.RARE,
        level_required=10,
        value=1000,
        stamina_cost=6,
        combat_bonus={"defense": 10, "attack_power": 3}
    ),
    "shadow_wolf": Mount(
        name="Shadow Wolf",
        description="A wolf from the shadow realm. Can move silently.",
        mount_type=MountType.WOLF,
        speed=MountSpeed.FAST,
        rarity=Rarity.RARE,
        level_required=12,
        value=1500,
        stamina_cost=6,
        combat_bonus={"stealth": 15, "attack_power": 8},
        special_ability="Shadow Step - Chance to avoid combat"
    ),
    
    # Epic Mounts
    "griffin": Mount(
        name="Griffin",
        description="A majestic creature with the body of a lion and wings of an eagle.",
        mount_type=MountType.GRIFFIN,
        speed=MountSpeed.FAST,
        rarity=Rarity.EPIC,
        level_required=15,
        value=5000,
        stamina_cost=8,
        can_fly=True,
        can_climb=True,
        combat_bonus={"attack_power": 15, "defense": 10},
        special_ability="Aerial Assault - Bonus damage when dismounting into combat"
    ),
    "young_dragon": Mount(
        name="Young Dragon",
        description="A young dragon that has bonded with you. Extremely rare.",
        mount_type=MountType.DRAGON,
        speed=MountSpeed.VERY_FAST,
        rarity=Rarity.EPIC,
        level_required=20,
        value=10000,
        stamina_cost=10,
        can_fly=True,
        can_climb=True,
        combat_bonus={"attack_power": 20, "magic_power": 15, "fire_resistance": 0.5},
        special_ability="Dragon's Breath - Fire damage to enemies when entering combat"
    ),
    
    # Legendary Mounts
    "phoenix": Mount(
        name="Phoenix",
        description="A mythical bird of fire that resurrects itself.",
        mount_type=MountType.PHOENIX,
        speed=MountSpeed.VERY_FAST,
        rarity=Rarity.LEGENDARY,
        level_required=25,
        value=50000,
        stamina_cost=12,
        can_fly=True,
        combat_bonus={"magic_power": 30, "fire_damage": 25, "regeneration": 5},
        special_ability="Rebirth - Once per day, survive a fatal blow with 25% HP"
    ),
    "ancient_dragon": Mount(
        name="Ancient Dragon",
        description="An ancient wyrm that has chosen you as its rider.",
        mount_type=MountType.DRAGON,
        speed=MountSpeed.VERY_FAST,
        rarity=Rarity.LEGENDARY,
        level_required=30,
        value=100000,
        stamina_cost=15,
        can_fly=True,
        can_swim=True,
        can_climb=True,
        combat_bonus={"attack_power": 50, "defense": 30, "magic_power": 40, "all_resistances": 0.2},
        special_ability="Dragon's Might - Massive stat boost while mounted"
    ),
    
    # Special Mounts
    "magic_carpet": Mount(
        name="Magic Carpet",
        description="A flying carpet that responds to your thoughts.",
        mount_type=MountType.MAGIC_CARPET,
        speed=MountSpeed.FAST,
        rarity=Rarity.RARE,
        level_required=10,
        value=3000,
        stamina_cost=4,
        can_fly=True,
        combat_bonus={"magic_power": 10}
    ),
    "giant_turtle": Mount(
        name="Giant Turtle",
        description="A massive turtle that carries you on its back. Slow but safe.",
        mount_type=MountType.GIANT_TURTLE,
        speed=MountSpeed.SLOW,
        rarity=Rarity.UNCOMMON,
        level_required=5,
        value=400,
        stamina_cost=2,
        can_swim=True,
        combat_bonus={"defense": 20, "hp_bonus": 50}
    ),
    "unicorn": Mount(
        name="Unicorn",
        description="A pure white unicorn that only bonds with the worthy.",
        mount_type=MountType.UNICORN,
        speed=MountSpeed.FAST,
        rarity=Rarity.EPIC,
        level_required=15,
        value=8000,
        stamina_cost=6,
        can_climb=True,
        combat_bonus={"magic_power": 20, "healing_bonus": 25, "blessing": True},
        special_ability="Purification - Immunity to poison and disease while mounted"
    ),
}


def get_mount(mount_id: str) -> Optional[Mount]:
    """Get a mount by ID"""
    mount = MOUNT_DATABASE.get(mount_id)
    if mount:
        # Return a copy so each player has their own instance
        return Mount.from_dict(mount.to_dict())
    return None


def get_mounts_by_rarity(rarity: Rarity) -> List[Mount]:
    """Get all mounts of a specific rarity"""
    return [m for m in MOUNT_DATABASE.values() if m.rarity == rarity]


def get_available_mounts(player_level: int) -> List[Mount]:
    """Get mounts available to player based on level"""
    return [m for m in MOUNT_DATABASE.values() if m.level_required <= player_level]


print("Mount system loaded successfully!")

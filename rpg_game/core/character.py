"""
Character System - Player Character with Skills, Equipment, and Progression

Author: YSNRFD
Version: 1.0.0
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any, Set, TYPE_CHECKING, Union
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.engine import (
    Entity, Stats, StatType, CharacterClass, DamageType,
    StatusEffectType, Ability, AbilityType, TargetType, EquipmentSlot, format_number
)
from core.items import Weapon, Armor, Consumable, Item, get_item

if TYPE_CHECKING:
    from systems.quests import Quest


# =============================================================================
# SKILL SYSTEM
# =============================================================================

@dataclass
class Skill:
    """Represents a learnable skill"""
    name: str
    description: str
    skill_type: str  # combat, magic, crafting, etc.
    max_level: int = 10
    current_level: int = 0
    experience: int = 0
    effects: Dict[str, Any] = field(default_factory=dict)
    
    def get_exp_to_next_level(self) -> int:
        """Calculate experience needed for next level"""
        if self.current_level >= self.max_level:
            return 0
        return int(100 * (1.5 ** self.current_level))
    
    def add_experience(self, amount: int) -> bool:
        """Add experience and check for level up"""
        if self.current_level >= self.max_level:
            return False
        
        self.experience += amount
        leveled_up = False
        
        while self.experience >= self.get_exp_to_next_level() and self.current_level < self.max_level:
            self.experience -= self.get_exp_to_next_level()
            self.current_level += 1
            leveled_up = True
        
        return leveled_up
    
    def get_effect_value(self, effect_name: str) -> float:
        """Get the current value of an effect based on level"""
        base = self.effects.get(effect_name, {}).get("base", 0)
        per_level = self.effects.get(effect_name, {}).get("per_level", 0)
        return base + (per_level * self.current_level)
    
    def to_dict(self) -> Dict:
        return {
            "name": self.name,
            "description": self.description,
            "skill_type": self.skill_type,
            "max_level": self.max_level,
            "current_level": self.current_level,
            "experience": self.experience,
            "effects": self.effects
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Skill':
        return cls(
            name=data["name"],
            description=data["description"],
            skill_type=data["skill_type"],
            max_level=data.get("max_level", 10),
            current_level=data.get("current_level", 0),
            experience=data.get("experience", 0),
            effects=data.get("effects", {})
        )


# =============================================================================
# CLASS ABILITIES DATABASE
# =============================================================================

CLASS_ABILITIES = {
    CharacterClass.WARRIOR: [
        Ability(
            name="Power Strike",
            description="A powerful melee attack that deals extra damage.",
            ability_type=AbilityType.ACTIVE,
            target_type=TargetType.SINGLE_ENEMY,
            mp_cost=0,
            stamina_cost=15,
            cooldown=2,
            damage=25,
            damage_type=DamageType.PHYSICAL,
            level_required=1
        ),
        Ability(
            name="Shield Bash",
            description="Stun your enemy with your shield.",
            ability_type=AbilityType.ACTIVE,
            target_type=TargetType.SINGLE_ENEMY,
            mp_cost=0,
            stamina_cost=20,
            cooldown=3,
            damage=15,
            damage_type=DamageType.PHYSICAL,
            effects=[(StatusEffectType.STUN, 1, 1)],
            level_required=3
        ),
        Ability(
            name="Battle Cry",
            description="Boost your attack power temporarily.",
            ability_type=AbilityType.ACTIVE,
            target_type=TargetType.SELF,
            mp_cost=10,
            stamina_cost=10,
            cooldown=5,
            effects=[(StatusEffectType.STRENGTH_BUFF, 3, 3)],
            level_required=5
        ),
        Ability(
            name="Whirlwind",
            description="Spin and attack all nearby enemies.",
            ability_type=AbilityType.ACTIVE,
            target_type=TargetType.ALL_ENEMIES,
            mp_cost=20,
            stamina_cost=30,
            cooldown=4,
            damage=20,
            damage_type=DamageType.PHYSICAL,
            level_required=10
        ),
    ],
    CharacterClass.MAGE: [
        Ability(
            name="Fireball",
            description="Launch a ball of fire at your enemy.",
            ability_type=AbilityType.ACTIVE,
            target_type=TargetType.SINGLE_ENEMY,
            mp_cost=15,
            cooldown=1,
            damage=30,
            damage_type=DamageType.FIRE,
            effects=[(StatusEffectType.BURN, 3, 1)],
            level_required=1
        ),
        Ability(
            name="Ice Bolt",
            description="A frozen projectile that slows enemies.",
            ability_type=AbilityType.ACTIVE,
            target_type=TargetType.SINGLE_ENEMY,
            mp_cost=12,
            cooldown=1,
            damage=25,
            damage_type=DamageType.ICE,
            effects=[(StatusEffectType.SLOW, 2, 1)],
            level_required=1
        ),
        Ability(
            name="Lightning Strike",
            description="Call down lightning on your foe.",
            ability_type=AbilityType.ACTIVE,
            target_type=TargetType.SINGLE_ENEMY,
            mp_cost=25,
            cooldown=3,
            damage=50,
            damage_type=DamageType.LIGHTNING,
            level_required=5
        ),
        Ability(
            name="Arcane Shield",
            description="Create a magical barrier for protection.",
            ability_type=AbilityType.ACTIVE,
            target_type=TargetType.SELF,
            mp_cost=20,
            cooldown=5,
            effects=[(StatusEffectType.SHIELD, 4, 3)],
            level_required=8
        ),
        Ability(
            name="Meteor Storm",
            description="Rain destruction upon all enemies.",
            ability_type=AbilityType.ACTIVE,
            target_type=TargetType.ALL_ENEMIES,
            mp_cost=50,
            cooldown=8,
            damage=60,
            damage_type=DamageType.FIRE,
            effects=[(StatusEffectType.BURN, 4, 2)],
            level_required=15
        ),
    ],
    CharacterClass.ROGUE: [
        Ability(
            name="Backstab",
            description="A deadly attack from the shadows.",
            ability_type=AbilityType.ACTIVE,
            target_type=TargetType.SINGLE_ENEMY,
            mp_cost=0,
            stamina_cost=20,
            cooldown=2,
            damage=35,
            damage_type=DamageType.PHYSICAL,
            critical_modifier=0.25,
            level_required=1
        ),
        Ability(
            name="Poison Blade",
            description="Coat your weapon with deadly poison.",
            ability_type=AbilityType.ACTIVE,
            target_type=TargetType.SINGLE_ENEMY,
            mp_cost=5,
            stamina_cost=10,
            cooldown=3,
            damage=15,
            damage_type=DamageType.PHYSICAL,
            effects=[(StatusEffectType.POISON, 5, 2)],
            level_required=3
        ),
        Ability(
            name="Vanish",
            description="Disappear into the shadows.",
            ability_type=AbilityType.ACTIVE,
            target_type=TargetType.SELF,
            mp_cost=15,
            stamina_cost=20,
            cooldown=6,
            effects=[(StatusEffectType.INVISIBLE, 3, 1)],
            level_required=5
        ),
        Ability(
            name="Eviscerate",
            description="A brutal finishing move.",
            ability_type=AbilityType.ACTIVE,
            target_type=TargetType.SINGLE_ENEMY,
            mp_cost=10,
            stamina_cost=35,
            cooldown=4,
            damage=50,
            damage_type=DamageType.PHYSICAL,
            critical_modifier=0.35,
            level_required=10
        ),
    ],
    CharacterClass.RANGER: [
        Ability(
            name="Precise Shot",
            description="A carefully aimed attack.",
            ability_type=AbilityType.ACTIVE,
            target_type=TargetType.SINGLE_ENEMY,
            mp_cost=5,
            stamina_cost=15,
            cooldown=1,
            damage=30,
            damage_type=DamageType.PHYSICAL,
            accuracy_modifier=20,
            level_required=1
        ),
        Ability(
            name="Multi-Shot",
            description="Fire arrows at multiple enemies.",
            ability_type=AbilityType.ACTIVE,
            target_type=TargetType.ALL_ENEMIES,
            mp_cost=15,
            stamina_cost=25,
            cooldown=3,
            damage=18,
            damage_type=DamageType.PHYSICAL,
            level_required=5
        ),
        Ability(
            name="Trap",
            description="Set a trap that damages and slows.",
            ability_type=AbilityType.ACTIVE,
            target_type=TargetType.SINGLE_ENEMY,
            mp_cost=10,
            stamina_cost=20,
            cooldown=4,
            damage=25,
            damage_type=DamageType.PHYSICAL,
            effects=[(StatusEffectType.IMMOBILIZE, 2, 1), (StatusEffectType.BLEED, 3, 1)],
            level_required=8
        ),
    ],
    CharacterClass.PALADIN: [
        Ability(
            name="Holy Smite",
            description="Strike with divine power.",
            ability_type=AbilityType.ACTIVE,
            target_type=TargetType.SINGLE_ENEMY,
            mp_cost=15,
            cooldown=2,
            damage=30,
            damage_type=DamageType.HOLY,
            level_required=1
        ),
        Ability(
            name="Divine Shield",
            description="Protect yourself with holy light.",
            ability_type=AbilityType.ACTIVE,
            target_type=TargetType.SELF,
            mp_cost=25,
            cooldown=6,
            effects=[(StatusEffectType.SHIELD, 4, 5), (StatusEffectType.BLESSING, 4, 2)],
            level_required=5
        ),
        Ability(
            name="Healing Light",
            description="Heal yourself with divine magic.",
            ability_type=AbilityType.ACTIVE,
            target_type=TargetType.SELF,
            mp_cost=20,
            cooldown=4,
            healing=50,
            level_required=3
        ),
        Ability(
            name="Judgment",
            description="Deal massive holy damage to evil.",
            ability_type=AbilityType.ACTIVE,
            target_type=TargetType.SINGLE_ENEMY,
            mp_cost=40,
            cooldown=5,
            damage=70,
            damage_type=DamageType.HOLY,
            level_required=12
        ),
    ],
    CharacterClass.NECROMANCER: [
        Ability(
            name="Drain Life",
            description="Steal life force from your enemy.",
            ability_type=AbilityType.ACTIVE,
            target_type=TargetType.SINGLE_ENEMY,
            mp_cost=15,
            cooldown=2,
            damage=25,
            damage_type=DamageType.DARK,
            healing=15,
            level_required=1
        ),
        Ability(
            name="Curse",
            description="Afflict your enemy with a curse.",
            ability_type=AbilityType.ACTIVE,
            target_type=TargetType.SINGLE_ENEMY,
            mp_cost=10,
            cooldown=3,
            effects=[(StatusEffectType.CURSE, 5, 2)],
            level_required=3
        ),
        Ability(
            name="Dark Bolt",
            description="A bolt of dark energy.",
            ability_type=AbilityType.ACTIVE,
            target_type=TargetType.SINGLE_ENEMY,
            mp_cost=20,
            cooldown=1,
            damage=35,
            damage_type=DamageType.DARK,
            level_required=5
        ),
        Ability(
            name="Death Coil",
            description="Powerful dark magic attack.",
            ability_type=AbilityType.ACTIVE,
            target_type=TargetType.SINGLE_ENEMY,
            mp_cost=35,
            cooldown=4,
            damage=60,
            damage_type=DamageType.DARK,
            healing=30,
            level_required=10
        ),
    ],
    CharacterClass.MONK: [
        Ability(
            name="Palm Strike",
            description="A quick martial arts attack.",
            ability_type=AbilityType.ACTIVE,
            target_type=TargetType.SINGLE_ENEMY,
            mp_cost=0,
            stamina_cost=15,
            cooldown=0,
            damage=20,
            damage_type=DamageType.PHYSICAL,
            level_required=1
        ),
        Ability(
            name="Meditation",
            description="Restore your spiritual energy.",
            ability_type=AbilityType.ACTIVE,
            target_type=TargetType.SELF,
            mp_cost=0,
            stamina_cost=0,
            cooldown=4,
            healing=30,
            effects=[(StatusEffectType.REGENERATION, 3, 2)],
            level_required=3
        ),
        Ability(
            name="Flying Kick",
            description="A devastating aerial attack.",
            ability_type=AbilityType.ACTIVE,
            target_type=TargetType.SINGLE_ENEMY,
            mp_cost=10,
            stamina_cost=30,
            cooldown=3,
            damage=45,
            damage_type=DamageType.PHYSICAL,
            level_required=7
        ),
        Ability(
            name="Inner Peace",
            description="Achieve perfect clarity.",
            ability_type=AbilityType.ACTIVE,
            target_type=TargetType.SELF,
            mp_cost=20,
            cooldown=5,
            effects=[
                (StatusEffectType.STRENGTH_BUFF, 4, 2),
                (StatusEffectType.DEFENSE_BUFF, 4, 2),
                (StatusEffectType.HASTE, 4, 1)
            ],
            level_required=12
        ),
    ],
    CharacterClass.BARD: [
        Ability(
            name="Inspiring Song",
            description="Boost ally morale with music.",
            ability_type=AbilityType.ACTIVE,
            target_type=TargetType.SELF,
            mp_cost=15,
            cooldown=4,
            effects=[(StatusEffectType.STRENGTH_BUFF, 3, 2), (StatusEffectType.BLESSING, 3, 1)],
            level_required=1
        ),
        Ability(
            name="Dissonance",
            description="Harm enemies with jarring music.",
            ability_type=AbilityType.ACTIVE,
            target_type=TargetType.ALL_ENEMIES,
            mp_cost=20,
            cooldown=3,
            damage=20,
            damage_type=DamageType.MAGICAL,
            effects=[(StatusEffectType.SLOW, 2, 1)],
            level_required=3
        ),
        Ability(
            name="Lullaby",
            description="Put an enemy to sleep.",
            ability_type=AbilityType.ACTIVE,
            target_type=TargetType.SINGLE_ENEMY,
            mp_cost=25,
            cooldown=5,
            effects=[(StatusEffectType.STUN, 2, 1)],
            level_required=7
        ),
    ],
    CharacterClass.DRUID: [
        Ability(
            name="Nature's Wrath",
            description="Attack with natural energy.",
            ability_type=AbilityType.ACTIVE,
            target_type=TargetType.SINGLE_ENEMY,
            mp_cost=12,
            cooldown=1,
            damage=28,
            damage_type=DamageType.MAGICAL,
            level_required=1
        ),
        Ability(
            name="Healing Touch",
            description="Restore health with nature's power.",
            ability_type=AbilityType.ACTIVE,
            target_type=TargetType.SELF,
            mp_cost=18,
            cooldown=3,
            healing=45,
            level_required=3
        ),
        Ability(
            name="Entangle",
            description="Root enemies with vines.",
            ability_type=AbilityType.ACTIVE,
            target_type=TargetType.SINGLE_ENEMY,
            mp_cost=15,
            cooldown=4,
            damage=15,
            damage_type=DamageType.PHYSICAL,
            effects=[(StatusEffectType.IMMOBILIZE, 3, 1)],
            level_required=5
        ),
        Ability(
            name="Storm Call",
            description="Summon a powerful storm.",
            ability_type=AbilityType.ACTIVE,
            target_type=TargetType.ALL_ENEMIES,
            mp_cost=40,
            cooldown=6,
            damage=45,
            damage_type=DamageType.LIGHTNING,
            effects=[(StatusEffectType.STUN, 1, 1)],
            level_required=10
        ),
    ],
    CharacterClass.WARLOCK: [
        Ability(
            name="Eldritch Blast",
            description="Dark energy projectile.",
            ability_type=AbilityType.ACTIVE,
            target_type=TargetType.SINGLE_ENEMY,
            mp_cost=10,
            cooldown=1,
            damage=30,
            damage_type=DamageType.DARK,
            level_required=1
        ),
        Ability(
            name="Life Tap",
            description="Sacrifice health for mana.",
            ability_type=AbilityType.ACTIVE,
            target_type=TargetType.SELF,
            hp_cost=20,
            cooldown=0,
            healing=0,
            level_required=1
        ),
        Ability(
            name="Fear",
            description="Terrify your enemy.",
            ability_type=AbilityType.ACTIVE,
            target_type=TargetType.SINGLE_ENEMY,
            mp_cost=20,
            cooldown=4,
            effects=[(StatusEffectType.FEAR, 3, 2)],
            level_required=5
        ),
        Ability(
            name="Soul Drain",
            description="Devastating attack that heals.",
            ability_type=AbilityType.ACTIVE,
            target_type=TargetType.SINGLE_ENEMY,
            mp_cost=30,
            cooldown=5,
            damage=55,
            damage_type=DamageType.DARK,
            healing=40,
            level_required=10
        ),
    ],
}


# =============================================================================
# CHARACTER CLASS
# =============================================================================

class Character(Entity):
    """Player character class"""
    
    def __init__(
        self,
        name: str,
        character_class: CharacterClass,
        level: int = 1,
        stats: Optional[Stats] = None
    ):
        super().__init__(name, level, "", stats)
        self.character_class = character_class
        self.inventory = Inventory()
        self.equipment = Equipment()
        self.skills: Dict[str, Skill] = {}
        self.quests: Dict[str, 'Quest'] = {}
        self.completed_quests: Set[str] = set()
        self.reputation: Dict[str, int] = {}
        self.achievements: Set[str] = set()
        self.play_time: int = 0
        self.monsters_killed: int = 0
        self.deaths: int = 0
        self.damage_dealt: int = 0
        self.damage_taken: int = 0
        self.gold_earned: int = 0
        self.gold_spent: int = 0
        self.items_crafted: int = 0
        self.quests_completed: int = 0
        
        # Initialize class-specific stats and abilities
        self._init_class()
    
    def _init_class(self):
        """Initialize class-specific attributes"""
        # Set base stats based on class
        base_stats = {
            CharacterClass.WARRIOR: Stats(strength=14, constitution=14, dexterity=10, intelligence=8, wisdom=10, charisma=10, luck=10),
            CharacterClass.MAGE: Stats(strength=8, constitution=10, dexterity=10, intelligence=16, wisdom=14, charisma=10, luck=10),
            CharacterClass.ROGUE: Stats(strength=10, constitution=10, dexterity=16, intelligence=10, wisdom=10, charisma=12, luck=12),
            CharacterClass.RANGER: Stats(strength=12, constitution=12, dexterity=14, intelligence=10, wisdom=12, charisma=10, luck=10),
            CharacterClass.PALADIN: Stats(strength=14, constitution=14, dexterity=10, intelligence=10, wisdom=12, charisma=12, luck=8),
            CharacterClass.NECROMANCER: Stats(strength=8, constitution=10, dexterity=10, intelligence=14, wisdom=14, charisma=10, luck=10),
            CharacterClass.MONK: Stats(strength=12, constitution=12, dexterity=14, intelligence=12, wisdom=14, charisma=8, luck=10),
            CharacterClass.BARD: Stats(strength=10, constitution=10, dexterity=12, intelligence=12, wisdom=10, charisma=16, luck=10),
            CharacterClass.DRUID: Stats(strength=10, constitution=12, dexterity=10, intelligence=14, wisdom=16, charisma=10, luck=8),
            CharacterClass.WARLOCK: Stats(strength=8, constitution=12, dexterity=10, intelligence=14, wisdom=12, charisma=14, luck=10),
        }
        
        self.stats = base_stats.get(self.character_class, Stats())
        self.max_hp = self._calculate_max_hp()
        self.current_hp = self.max_hp
        self.max_mp = self._calculate_max_mp()
        self.current_mp = self.max_mp
        self.max_stamina = self._calculate_max_stamina()
        self.current_stamina = self.max_stamina
        
        # Add class abilities
        if self.character_class in CLASS_ABILITIES:
            for ability in CLASS_ABILITIES[self.character_class]:
                if ability.level_required <= self.level:
                    self.abilities.append(ability)
        
        # Initialize default skills
        self._init_skills()
    
    def _init_skills(self):
        """Initialize default skills"""
        default_skills = [
            Skill(
                name="Swordsmanship",
                description="Proficiency with swords and blades.",
                skill_type="combat",
                effects={"damage_bonus": {"base": 0, "per_level": 2}}
            ),
            Skill(
                name="Magic",
                description="Mastery of magical arts.",
                skill_type="magic",
                effects={"magic_power": {"base": 0, "per_level": 3}}
            ),
            Skill(
                name="Stealth",
                description="The art of remaining unseen.",
                skill_type="rogue",
                effects={"evasion": {"base": 0, "per_level": 1}}
            ),
            Skill(
                name="Crafting",
                description="Ability to create items and equipment.",
                skill_type="crafting",
                effects={"quality": {"base": 0, "per_level": 5}}
            ),
            Skill(
                name="Survival",
                description="Knowledge of the wild.",
                skill_type="exploration",
                effects={"stamina_regen": {"base": 0, "per_level": 1}}
            ),
            Skill(
                name="Persuasion",
                description="The art of convincing others.",
                skill_type="social",
                effects={"prices": {"base": 0, "per_level": -2}}
            ),
        ]
        
        for skill in default_skills:
            self.skills[skill.name] = skill
    
    def get_stat(self, stat_type: StatType) -> int:
        """Get stat value with equipment bonuses"""
        base = super().get_stat(stat_type)
        
        # Add equipment bonuses
        for slot, item in self.equipment.slots.items():
            if item:
                if isinstance(item, Armor) and hasattr(item, 'stat_bonuses'):
                    if stat_type.value in item.stat_bonuses:
                        base += item.stat_bonuses[stat_type.value]
                elif hasattr(item, 'stat_bonuses') and stat_type.value in item.stat_bonuses:
                    base += item.stat_bonuses[stat_type.value]
        
        return base
    
    def get_attack_power(self) -> int:
        """Calculate total attack power with weapon"""
        base = super().get_attack_power()
        weapon = self.equipment.get_weapon()
        if weapon:
            base += (weapon.damage_min + weapon.damage_max) // 2
        return base
    
    def get_defense(self) -> int:
        """Calculate total defense with armor"""
        base = super().get_defense()
        base += self.equipment.get_total_defense()
        return base
    
    def get_resistances(self) -> Dict[DamageType, float]:
        """Get total resistances from equipment"""
        resistances = super().get_resistances()
        eq_resistances = self.equipment.get_resistances()
        for dtype, res in eq_resistances.items():
            resistances[dtype] = resistances.get(dtype, 0) + res
        return resistances
    
    def equip_item(self, item_name: str) -> Tuple[bool, str]:
        """Equip an item from inventory"""
        item = self.inventory.get_item(item_name)
        if not item:
            return False, f"Item '{item_name}' not found in inventory."
        
        # Check if already equipped
        for slot, equipped in self.equipment.slots.items():
            if equipped and equipped.name.lower() == item_name.lower():
                return False, f"{item.name} is already equipped."
        
        if isinstance(item, Weapon):
            can_equip, msg = item.can_equip(self)
            if not can_equip:
                return False, msg
            success, prev_item, msg = self.equipment.equip(item)
            if success:
                self.inventory.remove_item(item_name)
                if prev_item:
                    self.inventory.add_item(prev_item)
                return True, msg
            return False, msg
        
        elif isinstance(item, Armor):
            success, prev_item, msg = self.equipment.equip(item)
            if success:
                self.inventory.remove_item(item_name)
                if prev_item:
                    self.inventory.add_item(prev_item)
                return True, msg
            return False, msg
        
        return False, "This item cannot be equipped."
    
    def unequip_item(self, slot_name: str) -> Tuple[bool, str]:
        """Unequip item from a slot"""
        try:
            slot = EquipmentSlot(slot_name.lower())
        except ValueError:
            return False, f"Invalid equipment slot: {slot_name}"
        
        success, item, msg = self.equipment.unequip(slot)
        if success:
            added, _ = self.inventory.add_item(item)
            if not added:
                # Put it back
                self.equipment.equip(item, slot)
                return False, "Inventory is full!"
            return True, msg
        return False, msg
    
    def use_item(self, item_name: str) -> Tuple[bool, str]:
        """Use a consumable item"""
        item = self.inventory.get_item(item_name)
        if not item:
            return False, f"Item '{item_name}' not found."
        
        if isinstance(item, Consumable):
            success, msg = item.use(self)
            if success:
                if item.quantity <= 1:
                    self.inventory.remove_item(item_name)
                else:
                    item.quantity -= 1
            return success, msg
        
        return False, f"Cannot use {item.name}."
    
    def add_experience(self, amount: int) -> Tuple[bool, List[str]]:
        """Add experience and handle level ups"""
        messages = []
        self.experience += amount
        messages.append(f"Gained {amount} experience!")
        
        leveled_up = False
        while self.level_up():
            leveled_up = True
            messages.append(f"\n{'='*40}")
            messages.append(f"LEVEL UP! You are now level {self.level}!")
            messages.append(f"HP: {self.max_hp}, MP: {self.max_mp}, Stamina: {self.max_stamina}")
            
            # Check for new abilities
            if self.character_class in CLASS_ABILITIES:
                for ability in CLASS_ABILITIES[self.character_class]:
                    if ability.level_required == self.level:
                        # Check if ability already learned
                        if not any(a.name == ability.name for a in self.abilities):
                            self.abilities.append(ability)
                            messages.append(f"Learned new ability: {ability.name}!")
        
        return leveled_up, messages
    
    def add_gold(self, amount: int):
        """Add gold to inventory"""
        self.inventory.gold += amount
        self.gold_earned += amount
    
    def spend_gold(self, amount: int) -> bool:
        """Spend gold if enough available"""
        if self.inventory.gold >= amount:
            self.inventory.gold -= amount
            self.gold_spent += amount
            return True
        return False
    
    def get_hp_bar(self, width: int = 20) -> str:
        """Get HP bar string"""
        filled = int((self.current_hp / self.max_hp) * width)
        bar = "█" * filled + "░" * (width - filled)
        return f"[{bar}] {self.current_hp}/{self.max_hp}"
    
    def get_mp_bar(self, width: int = 20) -> str:
        """Get MP bar string"""
        filled = int((self.current_mp / self.max_mp) * width) if self.max_mp > 0 else 0
        bar = "█" * filled + "░" * (width - filled)
        return f"[{bar}] {self.current_mp}/{self.max_mp}"
    
    def get_stamina_bar(self, width: int = 20) -> str:
        """Get stamina bar string"""
        filled = int((self.current_stamina / self.max_stamina) * width)
        bar = "█" * filled + "░" * (width - filled)
        return f"[{bar}] {self.current_stamina}/{self.max_stamina}"
    
    def get_exp_bar(self, width: int = 20) -> str:
        """Get experience bar string"""
        percent = self.experience / self.experience_to_level if self.experience_to_level > 0 else 0
        filled = int(percent * width)
        bar = "█" * filled + "░" * (width - filled)
        return f"[{bar}] {self.experience}/{self.experience_to_level}"
    
    def get_status_display(self) -> str:
        """Get character status display"""
        lines = [
            f"\n{'='*50}",
            f"{self.name} - Level {self.level} {self.character_class.value}",
            f"{'='*50}",
            f"HP:     {self.get_hp_bar()}",
            f"MP:     {self.get_mp_bar()}",
            f"Stamina: {self.get_stamina_bar()}",
            f"EXP:    {self.get_exp_bar()}",
            f"",
            f"Gold: {format_number(self.inventory.gold)}",
            f"",
            f"Stats:",
            f"  STR: {self.get_stat(StatType.STRENGTH):2d} ({self.stats.get_modifier(StatType.STRENGTH):+d})",
            f"  DEX: {self.get_stat(StatType.DEXTERITY):2d} ({self.stats.get_modifier(StatType.DEXTERITY):+d})",
            f"  CON: {self.get_stat(StatType.CONSTITUTION):2d} ({self.stats.get_modifier(StatType.CONSTITUTION):+d})",
            f"  INT: {self.get_stat(StatType.INTELLIGENCE):2d} ({self.stats.get_modifier(StatType.INTELLIGENCE):+d})",
            f"  WIS: {self.get_stat(StatType.WISDOM):2d} ({self.stats.get_modifier(StatType.WISDOM):+d})",
            f"  CHA: {self.get_stat(StatType.CHARISMA):2d} ({self.stats.get_modifier(StatType.CHARISMA):+d})",
            f"  LCK: {self.get_stat(StatType.LUCK):2d} ({self.stats.get_modifier(StatType.LUCK):+d})",
            f"",
            f"Attack Power: {self.get_attack_power()}",
            f"Defense: {self.get_defense()}",
            f"Magic Power: {self.get_magic_power()}",
            f"Accuracy: {self.get_accuracy()}%",
            f"Evasion: {self.get_evasion()}%",
            f"Critical: {self.get_critical_chance():.1f}%",
        ]
        
        # Show status effects
        if self.status_effects:
            lines.append("")
            lines.append("Status Effects:")
            for effect_type, data in self.status_effects.items():
                lines.append(f"  • {effect_type.value.title()} ({data['turns_remaining']} turns)")
        
        return "\n".join(lines)
    
    def to_dict(self) -> Dict:
        data = super().to_dict()
        data.update({
            "character_class": self.character_class.value,
            "inventory": self.inventory.to_dict(),
            "equipment": self.equipment.to_dict(),
            "skills": {k: v.to_dict() for k, v in self.skills.items()},
            "quests": {k: v.to_dict() for k, v in self.quests.items()},
            "completed_quests": list(self.completed_quests),
            "reputation": self.reputation,
            "achievements": list(self.achievements),
            "play_time": self.play_time,
            "monsters_killed": self.monsters_killed,
            "deaths": self.deaths,
            "damage_dealt": self.damage_dealt,
            "damage_taken": self.damage_taken,
            "gold_earned": self.gold_earned,
            "gold_spent": self.gold_spent,
            "items_crafted": self.items_crafted,
            "quests_completed": self.quests_completed,
            "abilities": [a.to_dict() for a in self.abilities]
        })
        return data
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Character':
        from systems.quests import Quest
        
        char = cls(
            name=data["name"],
            character_class=CharacterClass(data["character_class"]),
            level=data["level"]
        )
        char.id = data["id"]
        char.stats = Stats.from_dict(data["stats"])
        char.max_hp = data["max_hp"]
        char.current_hp = data["current_hp"]
        char.max_mp = data["max_mp"]
        char.current_mp = data["current_mp"]
        char.max_stamina = data["max_stamina"]
        char.current_stamina = data["current_stamina"]
        char.experience = data["experience"]
        char.experience_to_level = data["experience_to_level"]
        char.status_effects = {
            StatusEffectType(k): v for k, v in data.get("status_effects", {}).items()
        }
        char.is_alive = data["is_alive"]
        char.position = data.get("position")
        char.inventory = Inventory.from_dict(data["inventory"])
        char.equipment = Equipment.from_dict(data["equipment"])
        char.skills = {k: Skill.from_dict(v) for k, v in data.get("skills", {}).items()}
        char.quests = {k: Quest.from_dict(v) for k, v in data.get("quests", {}).items()}
        char.completed_quests = set(data.get("completed_quests", []))
        char.reputation = data.get("reputation", {})
        char.achievements = set(data.get("achievements", []))
        char.play_time = data.get("play_time", 0)
        char.monsters_killed = data.get("monsters_killed", 0)
        char.deaths = data.get("deaths", 0)
        char.damage_dealt = data.get("damage_dealt", 0)
        char.damage_taken = data.get("damage_taken", 0)
        char.gold_earned = data.get("gold_earned", 0)
        char.gold_spent = data.get("gold_spent", 0)
        char.items_crafted = data.get("items_crafted", 0)
        char.quests_completed = data.get("quests_completed", 0)
        char.abilities = [Ability.from_dict(a) for a in data.get("abilities", [])]
        
        return char


# =============================================================================
# INVENTORY CLASS
# =============================================================================

class Inventory:
    """Inventory management system"""
    
    def __init__(self, max_slots: int = 50, max_weight: float = 100.0):
        self.max_slots = max_slots
        self.max_weight = max_weight
        self.items: List[Item] = []
        self.gold: int = 0
    
    def add_item(self, item: Item) -> Tuple[bool, str]:
        """Add an item to inventory"""
        if not item.stackable:
            if len(self.items) >= self.max_slots:
                return False, "Inventory is full!"
            self.items.append(item)
            return True, f"Added {item.name} to inventory."
        
        # Check for existing stack
        for existing in self.items:
            if existing.name == item.name and existing.stackable:
                if existing.quantity + item.quantity <= existing.max_stack:
                    existing.quantity += item.quantity
                    return True, f"Added {item.quantity}x {item.name}."
                else:
                    space = existing.max_stack - existing.quantity
                    existing.quantity = existing.max_stack
                    item.quantity -= space
                    if len(self.items) < self.max_slots:
                        self.items.append(item)
                        return True, f"Stack filled, added remaining {item.quantity}x {item.name}."
                    return False, "Inventory is full!"
        
        if len(self.items) >= self.max_slots:
            return False, "Inventory is full!"
        
        self.items.append(item)
        return True, f"Added {item.quantity}x {item.name}."
    
    def remove_item(self, item_name: str, quantity: int = 1) -> Tuple[bool, Optional[Item]]:
        """Remove an item from inventory"""
        for i, item in enumerate(self.items):
            if item.name.lower() == item_name.lower():
                if item.quantity <= quantity:
                    self.items.pop(i)
                    return True, item
                else:
                    item.quantity -= quantity
                    new_item = get_item(item.name.lower().replace(" ", "_"), quantity)
                    return True, new_item
        return False, None
    
    def get_item(self, item_name: str) -> Optional[Item]:
        """Get item by name"""
        for item in self.items:
            if item.name.lower() == item_name.lower():
                return item
        return None
    
    def has_item(self, item_name: str, quantity: int = 1) -> bool:
        """Check if inventory has an item"""
        item = self.get_item(item_name)
        return item is not None and item.quantity >= quantity
    
    def get_total_weight(self) -> float:
        """Calculate total weight"""
        return sum(item.weight * item.quantity for item in self.items)
    
    def get_total_value(self) -> int:
        """Calculate total value"""
        return sum(item.value * item.quantity for item in self.items)
    
    def get_display(self) -> str:
        """Get formatted inventory display"""
        lines = [
            f"\n{'='*50}",
            f"INVENTORY ({len(self.items)}/{self.max_slots})",
            f"{'='*50}"
        ]
        
        if not self.items:
            lines.append("Empty")
        else:
            for item in self.items:
                qty = f"x{item.quantity}" if item.quantity > 1 else ""
                rarity_color = item.rarity.color
                lines.append(f"  {rarity_color}{item.name}\033[0m {qty}")
        
        lines.append(f"\nGold: {format_number(self.gold)}")
        lines.append(f"Weight: {self.get_total_weight():.1f}/{self.max_weight} kg")
        lines.append(f"Total Value: {format_number(self.get_total_value())}")
        
        return "\n".join(lines)
    
    def to_dict(self) -> Dict:
        return {
            "max_slots": self.max_slots,
            "max_weight": self.max_weight,
            "items": [self._item_to_dict(item) for item in self.items],
            "gold": self.gold
        }
    
    def _item_to_dict(self, item: Item) -> Dict:
        """Convert item to dictionary"""
        from core.items import Weapon, Armor, Consumable, Material
        
        data = {
            "name": item.name,
            "item_type": item.item_type.value,
            "rarity": item.rarity.value,
            "value": item.value,
            "weight": item.weight,
            "quantity": item.quantity,
            "description": item.description,
            "level_required": item.level_required
        }
        
        # Add type-specific data
        if isinstance(item, Weapon):
            data.update({
                "damage_min": item.damage_min,
                "damage_max": item.damage_max,
                "damage_type": item.damage_type.value,
                "attack_speed": item.attack_speed,
                "critical_chance": item.critical_chance,
                "critical_damage": item.critical_damage,
                "two_handed": item.two_handed,
                "stat_requirements": item.stat_requirements
            })
        elif isinstance(item, Armor):
            data.update({
                "slot": item.slot.value,
                "defense": item.defense,
                "magic_defense": item.magic_defense,
                "resistances": item.resistances,
                "stat_bonuses": item.stat_bonuses
            })
        elif isinstance(item, Consumable):
            data.update({
                "hp_restore": item.hp_restore,
                "mp_restore": item.mp_restore,
                "stamina_restore": item.stamina_restore,
                "temporary_effects": item.temporary_effects,
                "cooldown": item.cooldown,
                "use_message": item.use_message
            })
        elif isinstance(item, Material):
            data.update({
                "material_type": item.material_type,
                "quality": item.quality,
                "crafting_value": item.crafting_value
            })
        
        return data
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Inventory':
        from core.items import ItemFactory
        
        inv = cls(
            max_slots=data.get("max_slots", 50),
            max_weight=data.get("max_weight", 100.0)
        )
        inv.gold = data.get("gold", 0)
        for item_data in data.get("items", []):
            item = ItemFactory.create_item(item_data)
            if item:
                inv.items.append(item)
        return inv


# =============================================================================
# EQUIPMENT CLASS
# =============================================================================

class Equipment:
    """Equipment management system"""
    
    def __init__(self):
        self.slots: Dict[EquipmentSlot, Optional[Union[Weapon, Armor]]] = {
            slot: None for slot in EquipmentSlot
        }
    
    def equip(self, item: Union[Weapon, Armor], slot: Optional[EquipmentSlot] = None) -> Tuple[bool, Optional[Union[Weapon, Armor]], str]:
        """Equip an item"""
        if isinstance(item, Weapon):
            if slot is None:
                slot = EquipmentSlot.MAIN_HAND
            
            if item.two_handed:
                offhand_item = self.slots[EquipmentSlot.OFF_HAND]
                if offhand_item:
                    return False, None, "Cannot equip two-handed weapon with off-hand item."
                
                previous = self.slots[slot]
                self.slots[slot] = item
                self.slots[EquipmentSlot.OFF_HAND] = None
                return True, previous, f"Equipped {item.name} (two-handed)."
        
        elif isinstance(item, Armor):
            slot = item.slot
        
        previous = self.slots.get(slot)
        self.slots[slot] = item
        
        return True, previous, f"Equipped {item.name} to {slot.value.replace('_', ' ')}."
    
    def unequip(self, slot: EquipmentSlot) -> Tuple[bool, Optional[Union[Weapon, Armor]], str]:
        """Unequip from a slot"""
        item = self.slots.get(slot)
        if item is None:
            return False, None, f"No item equipped in {slot.value.replace('_', ' ')}."
        
        self.slots[slot] = None
        return True, item, f"Unequipped {item.name}."
    
    def get_weapon(self) -> Optional[Weapon]:
        """Get main hand weapon"""
        item = self.slots.get(EquipmentSlot.MAIN_HAND)
        return item if isinstance(item, Weapon) else None
    
    def get_total_defense(self) -> int:
        """Calculate total defense"""
        return sum(item.defense for item in self.slots.values() if isinstance(item, Armor))
    
    def get_resistances(self) -> Dict[DamageType, float]:
        """Calculate total resistances"""
        resistances = {}
        for item in self.slots.values():
            if isinstance(item, Armor) and hasattr(item, 'resistances'):
                for dtype, res in item.resistances.items():
                    dt = DamageType(dtype) if isinstance(dtype, str) else dtype
                    resistances[dt] = resistances.get(dt, 0) + res
        return resistances
    
    def get_display(self) -> str:
        """Get equipment display"""
        lines = [f"\n{'='*50}", "EQUIPMENT", f"{'='*50}"]
        
        for slot, item in self.slots.items():
            slot_name = slot.value.replace('_', ' ').title()
            if item:
                rarity_color = item.rarity.color
                lines.append(f"{slot_name:12}: {rarity_color}{item.name}\033[0m")
            else:
                lines.append(f"{slot_name:12}: [Empty]")
        
        return "\n".join(lines)
    
    def to_dict(self) -> Dict:
        return {
            "slots": {
                slot.value: self._item_to_dict(item) if item else None
                for slot, item in self.slots.items()
            }
        }
    
    def _item_to_dict(self, item: Union[Weapon, Armor]) -> Dict:
        """Convert item to dictionary"""
        data = {
            "name": item.name,
            "item_type": "weapon" if isinstance(item, Weapon) else "armor",
            "rarity": item.rarity.value,
            "value": item.value,
            "weight": item.weight,
            "description": item.description,
            "level_required": item.level_required
        }
        
        if isinstance(item, Weapon):
            data.update({
                "damage_min": item.damage_min,
                "damage_max": item.damage_max,
                "damage_type": item.damage_type.value,
                "attack_speed": item.attack_speed,
                "critical_chance": item.critical_chance,
                "critical_damage": item.critical_damage,
                "two_handed": item.two_handed
            })
        elif isinstance(item, Armor):
            data.update({
                "slot": item.slot.value,
                "defense": item.defense,
                "magic_defense": item.magic_defense,
                "resistances": item.resistances,
                "stat_bonuses": item.stat_bonuses
            })
        
        return data
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Equipment':
        from core.items import ItemFactory
        eq = cls()
        for slot_name, item_data in data.get("slots", {}).items():
            if item_data:
                try:
                    slot = EquipmentSlot(slot_name)
                    item = ItemFactory.create_item(item_data)
                    if isinstance(item, (Weapon, Armor)):
                        eq.slots[slot] = item
                except (ValueError, KeyError):
                    continue
        return eq


print("Character system loaded successfully!")

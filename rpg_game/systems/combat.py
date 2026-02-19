"""
Combat System - Turn-based Combat with Skills and Abilities
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any, TYPE_CHECKING
from enum import Enum
import sys
import os
import random
import time
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.engine import (
    Entity, Damage, DamageType, StatusEffectType, Ability,
    AbilityType, TargetType,
    Rarity, StatType, CombatLog, EventType, roll_dice, clamp,
    colored_text, print_border, pause
)

if TYPE_CHECKING:
    from core.character import Character


class CombatState(Enum):
    INIT = "init"
    PLAYER_TURN = "player_turn"
    ENEMY_TURN = "enemy_turn"
    VICTORY = "victory"
    DEFEAT = "defeat"
    FLED = "fled"


@dataclass
class CombatResult:
    """Result of a combat encounter"""
    victory: bool
    fled: bool = False
    experience_gained: int = 0
    gold_gained: int = 0
    items_dropped: List[Any] = field(default_factory=list)
    turns_elapsed: int = 0
    damage_dealt: int = 0
    damage_taken: int = 0
    abilities_used: int = 0


class CombatEncounter:
    """Manages a combat encounter"""
    
    def __init__(self, player: 'Character', enemies: List[Entity], event_system=None):
        self.player = player
        self.enemies = enemies
        self.state = CombatState.INIT
        self.turn = 0
        self.logs: List[CombatLog] = []
        self.event_system = event_system
        
    def start(self) -> CombatResult:
        """Start the combat encounter"""
        self.state = CombatState.PLAYER_TURN
        self.turn = 1
        
        result = CombatResult(victory=False)
        
        # Combat introduction
        self._display_intro()
        
        if self.event_system:
            self.event_system.emit(EventType.COMBAT_START, {
                "player": self.player,
                "enemies": self.enemies
            })
        
        while self.state not in [CombatState.VICTORY, CombatState.DEFEAT, CombatState.FLED]:
            # Process turn
            if self.state == CombatState.PLAYER_TURN:
                fled = self._player_turn()
                if fled:
                    self.state = CombatState.FLED
                    result.fled = True
                    break
            elif self.state == CombatState.ENEMY_TURN:
                self._enemy_turn()
            
            # Check victory/defeat conditions
            if not self.player.is_alive:
                self.state = CombatState.DEFEAT
            elif all(not e.is_alive for e in self.enemies):
                self.state = CombatState.VICTORY
            
            # End turn processing
            self._end_turn_processing()
        
        # Generate result
        result.victory = self.state == CombatState.VICTORY
        result.turns_elapsed = self.turn
        
        if result.victory:
            result.experience_gained = sum(e.level * 25 for e in self.enemies)
            result.gold_gained = sum(e.level * random.randint(5, 15) for e in self.enemies)
            result.items_dropped = self._generate_loot()
            
            if self.event_system:
                self.event_system.emit(EventType.COMBAT_END, {
                    "result": "victory",
                    "player": self.player,
                    "experience": result.experience_gained,
                    "gold": result.gold_gained,
                    "items": result.items_dropped
                })
        
        return result
    
    def _display_intro(self):
        """Display combat introduction"""
        print("\n" + "="*60)
        print(colored_text("⚔️  COMBAT ENGAGED!  ⚔️", "\033[91m"))
        print("="*60)
        print(f"\n{self.player.name} VS")
        for enemy in self.enemies:
            hp_percent = (enemy.current_hp / enemy.max_hp) * 100
            print(f"  • {enemy.name} (Lv.{enemy.level}) - HP: {enemy.current_hp}/{enemy.max_hp}")
        print()
    
    def _player_turn(self) -> bool:
        """Execute player turn, returns True if fled"""
        print("\n" + "-"*40)
        print(f"Turn {self.turn} - Your Turn")
        print("-"*40)
        
        # Display status
        self._display_combat_status()
        
        while True:
            print("\nActions:")
            print("  [1] Attack")
            print("  [2] Abilities")
            print("  [3] Items")
            print("  [4] Defend")
            print("  [5] Flee")
            
            choice = input("\nChoose action: ").strip()
            
            if choice == "1":
                return self._player_attack()
            elif choice == "2":
                result = self._player_ability()
                if result:
                    return result
            elif choice == "3":
                result = self._player_item()
                if result:
                    return result
            elif choice == "4":
                return self._player_defend()
            elif choice == "5":
                if self._player_flee():
                    return True
            else:
                print("Invalid choice.")
        
        return False
    
    def _player_attack(self) -> bool:
        """Execute basic attack"""
        target = self._select_target()
        if target is None:
            return False
        
        # Calculate damage
        weapon = self.player.equipment.get_weapon()
        base_damage = self.player.get_attack_power()
        
        if weapon:
            base_damage = weapon.get_damage() + self.player.stats.get_modifier(StatType.STRENGTH) * 2
        
        # Check hit
        accuracy = self.player.get_accuracy()
        evasion = target.get_evasion()
        hit_chance = max(5, min(95, accuracy - evasion))
        
        if random.randint(1, 100) > hit_chance:
            print(f"\nYour attack missed {target.name}!")
            self._log_turn("attack", "missed")
            self.state = CombatState.ENEMY_TURN
            return False
        
        # Check critical
        is_critical = random.random() < self.player.get_critical_chance()
        if weapon and is_critical:
            crit_mult = weapon.critical_damage
        else:
            crit_mult = 1.5 if is_critical else 1.0
        
        damage = int(base_damage * crit_mult)
        actual_damage = target.take_damage(Damage(damage, DamageType.PHYSICAL, is_critical))
        
        crit_text = colored_text(" CRITICAL!", "\033[93m") if is_critical else ""
        print(f"\nYou attack {target.name} for {actual_damage} damage!{crit_text}")
        
        if not target.is_alive:
            print(colored_text(f"  {target.name} has been defeated!", "\033[92m"))
        
        self._log_turn("attack", f"dealt {actual_damage} damage")
        self.state = CombatState.ENEMY_TURN
        return False
    
    def _player_ability(self) -> bool:
        """Use an ability"""
        abilities = [a for a in self.player.abilities if a.ability_type.value == "active"]
        
        if not abilities:
            print("\nNo abilities available!")
            return False
        
        print("\nAbilities:")
        for i, ability in enumerate(abilities, 1):
            cooldown_text = f" (CD: {ability.current_cooldown})" if ability.current_cooldown > 0 else ""
            mp_text = f" MP:{ability.mp_cost}" if ability.mp_cost > 0 else ""
            stamina_text = f" SP:{ability.stamina_cost}" if ability.stamina_cost > 0 else ""
            print(f"  [{i}] {ability.name}{mp_text}{stamina_text}{cooldown_text}")
            print(f"      {ability.description}")
        
        print("  [0] Back")
        
        choice = input("\nSelect ability: ").strip()
        
        if choice == "0":
            return False
        
        try:
            idx = int(choice) - 1
            if 0 <= idx < len(abilities):
                ability = abilities[idx]
                return self._use_ability(ability)
        except ValueError:
            pass
        
        print("Invalid choice.")
        return False
    
    def _use_ability(self, ability: Ability) -> bool:
        """Use a specific ability"""
        can_use, msg = ability.can_use(self.player)
        if not can_use:
            print(f"\nCannot use ability: {msg}")
            return False
        
        # Select target based on ability type
        if ability.target_type.value in ["single_enemy", "any"]:
            target = self._select_target()
            if target is None:
                return False
        else:
            target = self.player
        
        result = ability.use(self.player, target)
        
        for msg in result["messages"]:
            print(f"\n{msg}")
        
        if result["success"]:
            self.state = CombatState.ENEMY_TURN
            return False
        
        return False
    
    def _player_item(self) -> bool:
        """Use an item in combat"""
        consumables = [item for item in self.player.inventory.items 
                       if hasattr(item, 'hp_restore') or hasattr(item, 'mp_restore')]
        
        if not consumables:
            print("\nNo usable items!")
            return False
        
        print("\nItems:")
        for i, item in enumerate(consumables, 1):
            print(f"  [{i}] {item.name} x{item.quantity}")
        
        print("  [0] Back")
        
        choice = input("\nSelect item: ").strip()
        
        if choice == "0":
            return False
        
        try:
            idx = int(choice) - 1
            if 0 <= idx < len(consumables):
                item = consumables[idx]
                success, msg = self.player.use_item(item.name)
                print(f"\n{msg}")
                if success:
                    self.state = CombatState.ENEMY_TURN
        except ValueError:
            print("Invalid choice.")
        
        return False
    
    def _player_defend(self) -> bool:
        """Defend to reduce incoming damage"""
        self.player.apply_status_effect(StatusEffectType.DEFENSE_BUFF, 1, 2)
        print("\nYou take a defensive stance!")
        self.state = CombatState.ENEMY_TURN
        return False
    
    def _player_flee(self) -> bool:
        """Attempt to flee from combat"""
        avg_enemy_level = sum(e.level for e in self.enemies if e.is_alive) / max(1, sum(1 for e in self.enemies if e.is_alive))
        flee_chance = max(10, min(90, 50 + (self.player.level - avg_enemy_level) * 5))
        
        if random.randint(1, 100) <= flee_chance:
            print("\nYou successfully fled from combat!")
            return True
        else:
            print("\nFailed to escape!")
            self.state = CombatState.ENEMY_TURN
            return False
    
    def _enemy_turn(self):
        """Execute enemy turns"""
        print("\n" + "-"*40)
        print(f"Turn {self.turn} - Enemy Turn")
        print("-"*40)
        
        for enemy in self.enemies:
            if not enemy.is_alive:
                continue
            
            # Simple AI: attack player or use abilities
            if enemy.abilities and random.random() < 0.3:
                ability = random.choice(enemy.abilities)
                can_use, _ = ability.can_use(enemy)
                if can_use:
                    result = ability.use(enemy, self.player)
                    for msg in result["messages"]:
                        print(f"\n{enemy.name}: {msg}")
                    continue
            
            # Basic attack
            base_damage = enemy.get_attack_power()
            is_critical = random.random() < enemy.get_critical_chance()
            damage = int(base_damage * (enemy.get_critical_damage() if is_critical else 1.0))
            
            # Check player evasion
            if random.randint(1, 100) <= self.player.get_evasion():
                print(f"\n{enemy.name} attacks but you dodge!")
                continue
            
            actual_damage = self.player.take_damage(Damage(damage, DamageType.PHYSICAL, is_critical))
            crit_text = colored_text(" CRITICAL!", "\033[93m") if is_critical else ""
            
            print(f"\n{enemy.name} attacks you for {actual_damage} damage!{crit_text}")
            
            if not self.player.is_alive:
                print(colored_text("\nYou have been defeated!", "\033[91m"))
                break
        
        self.turn += 1
        self.state = CombatState.PLAYER_TURN
    
    def _select_target(self) -> Optional[Entity]:
        """Select a target from living enemies"""
        living_enemies = [e for e in self.enemies if e.is_alive]
        
        if len(living_enemies) == 1:
            return living_enemies[0]
        
        print("\nSelect target:")
        for i, enemy in enumerate(living_enemies, 1):
            hp_bar = self._get_hp_bar(enemy)
            print(f"  [{i}] {enemy.name} - {hp_bar}")
        
        choice = input("\nTarget: ").strip()
        
        try:
            idx = int(choice) - 1
            if 0 <= idx < len(living_enemies):
                return living_enemies[idx]
        except ValueError:
            pass
        
        print("Invalid target.")
        return None
    
    def _display_combat_status(self):
        """Display current combat status"""
        print(f"\n{self.player.name}:")
        print(f"  HP: {self.player.get_hp_bar(15)}")
        print(f"  MP: {self.player.get_mp_bar(15)}")
        print(f"  Stamina: {self.player.get_stamina_bar(15)}")
        
        print("\nEnemies:")
        for enemy in self.enemies:
            if enemy.is_alive:
                hp_bar = self._get_hp_bar(enemy)
                print(f"  {enemy.name}: {hp_bar}")
            else:
                print(f"  {enemy.name}: [DEFEATED]")
    
    def _get_hp_bar(self, entity: Entity, width: int = 15) -> str:
        """Get HP bar for an entity"""
        percent = entity.current_hp / entity.max_hp
        filled = int(percent * width)
        bar = "█" * filled + "░" * (width - filled)
        return f"[{bar}] {entity.current_hp}/{entity.max_hp}"
    
    def _end_turn_processing(self):
        """Process end of turn effects"""
        # Process player status effects
        if self.player.is_alive:
            messages = self.player.process_status_effects()
            for msg in messages:
                print(f"\n{msg}")
        
        # Process enemy status effects
        for enemy in self.enemies:
            if enemy.is_alive:
                messages = enemy.process_status_effects()
                for msg in messages:
                    print(f"\n{enemy.name}: {msg}")
        
        # Reduce ability cooldowns
        for ability in self.player.abilities:
            ability.end_turn()
    
    def _generate_loot(self) -> List[Any]:
        """Generate loot from defeated enemies"""
        from core.items import get_random_item
        
        loot = []
        for enemy in self.enemies:
            # Gold drop already calculated
            # Chance for item drop
            if random.random() < 0.3:  # 30% chance
                item = get_random_item()
                if item:
                    loot.append(item)
        
        return loot
    
    def _log_turn(self, action: str, result: str):
        """Log a combat action"""
        self.logs.append(CombatLog(
            turn=self.turn,
            actor=self.player.name,
            action=action,
            result=result
        ))


# =============================================================================
# ENEMY FACTORY
# =============================================================================

class EnemyFactory:
    """Factory for creating enemies"""
    
    ENEMY_TEMPLATES = {
        "goblin": {
            "name": "Goblin",
            "description": "A small, green-skinned creature.",
            "base_hp": 30,
            "base_mp": 10,
            "base_damage": 5,
            "rarity": "Common",
            "faction": "monster"
        },
        "wolf": {
            "name": "Wolf",
            "description": "A fierce predatory wolf.",
            "base_hp": 40,
            "base_mp": 0,
            "base_damage": 8,
            "rarity": "Common",
            "faction": "beast"
        },
        "skeleton": {
            "name": "Skeleton",
            "description": "Animated bones of the dead.",
            "base_hp": 35,
            "base_mp": 20,
            "base_damage": 10,
            "rarity": "Common",
            "faction": "undead"
        },
        "orc_warrior": {
            "name": "Orc Warrior",
            "description": "A brutish orc soldier.",
            "base_hp": 80,
            "base_mp": 15,
            "base_damage": 15,
            "rarity": "Uncommon",
            "faction": "monster"
        },
        "dark_mage": {
            "name": "Dark Mage",
            "description": "A corrupted spellcaster.",
            "base_hp": 50,
            "base_mp": 100,
            "base_damage": 20,
            "rarity": "Uncommon",
            "faction": "evil"
        },
        "troll": {
            "name": "Troll",
            "description": "A massive, regenerating beast.",
            "base_hp": 150,
            "base_mp": 0,
            "base_damage": 25,
            "rarity": "Rare",
            "faction": "monster"
        },
        "dragon_wyrmling": {
            "name": "Dragon Wyrmling",
            "description": "A young dragon, still dangerous.",
            "base_hp": 200,
            "base_mp": 50,
            "base_damage": 35,
            "rarity": "Rare",
            "faction": "dragon"
        },
        "vampire": {
            "name": "Vampire",
            "description": "An undead noble with dark powers.",
            "base_hp": 120,
            "base_mp": 80,
            "base_damage": 30,
            "rarity": "Epic",
            "faction": "undead"
        },
        "demon": {
            "name": "Demon",
            "description": "A creature from the abyss.",
            "base_hp": 300,
            "base_mp": 100,
            "base_damage": 50,
            "rarity": "Epic",
            "faction": "demon"
        },
        "ancient_dragon": {
            "name": "Ancient Dragon",
            "description": "A mighty dragon of legend.",
            "base_hp": 1000,
            "base_mp": 500,
            "base_damage": 100,
            "rarity": "Legendary",
            "faction": "dragon"
        }
    }
    
    @staticmethod
    def create_enemy(template_id: str, level: int = 1) -> Optional[Entity]:
        """Create an enemy from a template"""
        if template_id not in EnemyFactory.ENEMY_TEMPLATES:
            return None
        
        template = EnemyFactory.ENEMY_TEMPLATES[template_id]
        
        enemy = Entity(
            name=template["name"],
            level=level,
            description=template["description"]
        )
        
        # Scale stats based on level
        level_mult = 1 + (level - 1) * 0.2
        enemy.max_hp = int(template["base_hp"] * level_mult)
        enemy.current_hp = enemy.max_hp
        enemy.max_mp = int(template["base_mp"] * level_mult)
        enemy.current_mp = enemy.max_mp
        
        enemy.faction = template.get("faction", "monster")
        enemy.resistances[DamageType.PHYSICAL] = 0.1 if template["rarity"] in ["Epic", "Legendary"] else 0
        
        # Add abilities for higher level enemies
        if level >= 5 and template["rarity"] in ["Uncommon", "Rare", "Epic", "Legendary"]:
            enemy.abilities.append(Ability(
                name="Power Strike",
                description="A powerful attack.",
                ability_type=AbilityType.ACTIVE,
                target_type=TargetType.SINGLE_ENEMY,
                mp_cost=10,
                cooldown=2,
                damage=int(template["base_damage"] * 1.5)
            ))
        
        return enemy
    
    @staticmethod
    def get_random_enemy(min_level: int = 1, max_level: int = 10, difficulty: str = "normal") -> Entity:
        """Get a random enemy appropriate for the level range"""
        templates_by_difficulty = {
            "easy": ["goblin", "wolf", "skeleton"],
            "normal": ["goblin", "wolf", "skeleton", "orc_warrior", "dark_mage"],
            "hard": ["orc_warrior", "dark_mage", "troll", "dragon_wyrmling"],
            "boss": ["vampire", "demon", "ancient_dragon"]
        }
        
        candidates = templates_by_difficulty.get(difficulty, templates_by_difficulty["normal"])
        template_id = random.choice(candidates)
        level = random.randint(min_level, max_level)
        
        return EnemyFactory.create_enemy(template_id, level)


print("Combat system loaded successfully!")

"""
Combat System - Turn-based Combat with Skills and Abilities

Author: YSNRFD
Version: 1.0.0
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Optional, Any, TYPE_CHECKING
from enum import Enum
import sys
import os
import random
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.engine import (
    Entity, Damage, DamageType, StatusEffectType, Ability,
    AbilityType, TargetType,
    StatType, CombatLog, EventType, clamp,
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
                break
            
            alive_enemies = [e for e in self.enemies if e.is_alive]
            if not alive_enemies:
                self.state = CombatState.VICTORY
                break
            
            # Switch turns
            if self.state == CombatState.PLAYER_TURN:
                self.state = CombatState.ENEMY_TURN
            else:
                self.state = CombatState.PLAYER_TURN
                self.turn += 1
            
            # Process status effects
            self._process_status_effects()
        
        # Calculate results
        if self.state == CombatState.VICTORY:
            result.victory = True
            result.experience_gained = self._calculate_experience()
            result.gold_gained = self._calculate_gold()
            result.items_dropped = self._generate_loot()
            result.turns_elapsed = self.turn
        
        if self.event_system:
            self.event_system.emit(EventType.COMBAT_END, {
                "player": self.player,
                "enemies": self.enemies,
                "result": result,
                "victory": result.victory
            })
        
        return result
    
    def _display_intro(self):
        """Display combat introduction"""
        print_border()
        print(colored_text("COMBAT ENCOUNTER!", "\033[91m"))
        print_border()
        print(f"\nYou face {len(self.enemies)} enemy(s):")
        for enemy in self.enemies:
            print(f"  • {enemy.name} (Level {enemy.level})")
        print()
        pause()
    
    def _player_turn(self) -> bool:
        """Process player turn"""
        print(f"\n{'='*60}")
        print(f"TURN {self.turn} - YOUR TURN")
        print(f"{'='*60}")
        print(f"HP: {self.player.current_hp}/{self.player.max_hp}")
        print(f"MP: {self.player.current_mp}/{self.player.max_mp}")
        print(f"Stamina: {self.player.current_stamina}/{self.player.max_stamina}")
        
        # Show enemies
        print("\nEnemies:")
        for i, enemy in enumerate(self.enemies, 1):
            if enemy.is_alive:
                status = ""
                if enemy.status_effects:
                    status = f" [{', '.join(e.value for e in enemy.status_effects.keys())}]"
                print(f"  [{i}] {enemy.name} - HP: {enemy.current_hp}/{enemy.max_hp}{status}")
        
        # Get player action
        print("\nActions:")
        print("  [1] Attack")
        print("  [2] Ability")
        print("  [3] Item")
        print("  [4] Defend")
        print("  [5] Flee")
        
        choice = input("\nChoose action (1-5): ").strip()
        
        if choice == "1":
            self._player_attack()
        elif choice == "2":
            self._player_ability()
        elif choice == "3":
            self._player_item()
        elif choice == "4":
            self._player_defend()
        elif choice == "5":
            return self._player_flee()
        else:
            print("Invalid choice!")
        
        return False
    
    def _player_attack(self):
        """Player basic attack"""
        # Select target
        alive_enemies = [e for e in self.enemies if e.is_alive]
        if not alive_enemies:
            return
        
        print("\nSelect target:")
        for i, enemy in enumerate(alive_enemies, 1):
            print(f"  [{i}] {enemy.name}")
        
        try:
            target_idx = int(input("Target: ").strip()) - 1
            if 0 <= target_idx < len(alive_enemies):
                target = alive_enemies[target_idx]
                
                # Calculate hit chance
                hit_chance = self.player.get_accuracy() - target.get_evasion()
                hit_chance = clamp(hit_chance, 5, 95)
                
                if random.randint(1, 100) <= hit_chance:
                    # Hit!
                    is_critical = random.random() < self.player.get_critical_chance()
                    damage = self.player.get_attack_power()
                    
                    if is_critical:
                        damage = int(damage * 1.5)
                        print(colored_text("CRITICAL HIT!", "\033[93m"))
                    
                    # Apply damage
                    dmg = Damage(
                        amount=damage,
                        damage_type=DamageType.PHYSICAL,
                        is_critical=is_critical
                    )
                    actual_damage = target.take_damage(dmg)
                    
                    print(f"You attack {target.name} for {actual_damage} damage!")
                    
                    if not target.is_alive:
                        print(colored_text(f"{target.name} has been defeated!", "\033[92m"))
                else:
                    print(f"You missed {target.name}!")
                    
        except ValueError:
            print("Invalid target!")
    
    def _player_ability(self):
        """Player use ability"""
        if not self.player.abilities:
            print("You have no abilities!")
            return
        
        # Show available abilities
        print("\nAbilities:")
        available_abilities = []
        for i, ability in enumerate(self.player.abilities, 1):
            can_use, reason = ability.can_use(self.player)
            status = "✓" if can_use else f"✗ ({reason})"
            print(f"  [{i}] {ability.name} - {status}")
            if can_use:
                available_abilities.append((i, ability))
        
        if not available_abilities:
            print("No abilities available to use!")
            return
        
        try:
            choice = int(input("\nSelect ability (0 to cancel): ").strip())
            if choice == 0:
                return
            
            selected = None
            for idx, ability in available_abilities:
                if idx == choice:
                    selected = ability
                    break
            
            if selected:
                # Select target if needed
                target = None
                if selected.target_type == TargetType.SINGLE_ENEMY:
                    alive_enemies = [e for e in self.enemies if e.is_alive]
                    print("\nSelect target:")
                    for i, enemy in enumerate(alive_enemies, 1):
                        print(f"  [{i}] {enemy.name}")
                    try:
                        target_idx = int(input("Target: ").strip()) - 1
                        if 0 <= target_idx < len(alive_enemies):
                            target = alive_enemies[target_idx]
                    except ValueError:
                        print("Invalid target!")
                        return
                
                # Use ability
                result = selected.use(self.player, target)
                print(f"\n{result['message']}")
                for msg in result.get('messages', []):
                    print(f"  {msg}")
                
                # Check if target died
                if target and not target.is_alive:
                    print(colored_text(f"{target.name} has been defeated!", "\033[92m"))
                    
        except ValueError:
            print("Invalid choice!")
    
    def _player_item(self):
        """Player use item"""
        # Get consumable items
        from core.items import Consumable
        consumables = [
            item for item in self.player.inventory.items 
            if isinstance(item, Consumable) and item.usable
        ]
        
        if not consumables:
            print("No usable items!")
            return
        
        print("\nItems:")
        for i, item in enumerate(consumables, 1):
            print(f"  [{i}] {item.name} x{item.quantity}")
        
        try:
            choice = int(input("\nSelect item (0 to cancel): ").strip())
            if choice == 0:
                return
            
            if 1 <= choice <= len(consumables):
                item = consumables[choice - 1]
                success, msg = item.use(self.player)
                print(f"\n{msg}")
                
                # Remove or decrement item
                if item.quantity <= 1:
                    self.player.inventory.remove_item(item.name)
                else:
                    item.quantity -= 1
                    
        except ValueError:
            print("Invalid choice!")
    
    def _player_defend(self):
        """Player defends"""
        print("You take a defensive stance!")
        self.player.apply_status_effect(StatusEffectType.DEFENSE_BUFF, 1, 5)
    
    def _player_flee(self) -> bool:
        """Attempt to flee"""
        flee_chance = 50 + (self.player.get_stat(StatType.DEXTERITY) - 10) * 2
        flee_chance = clamp(flee_chance, 10, 90)
        
        if random.randint(1, 100) <= flee_chance:
            print(colored_text("You successfully fled!", "\033[92m"))
            return True
        else:
            print(colored_text("Failed to flee!", "\033[91m"))
            return False
    
    def _enemy_turn(self):
        """Process enemy turns"""
        print(f"\n{'='*60}")
        print("ENEMY TURN")
        print(f"{'='*60}")
        
        for enemy in self.enemies:
            if not enemy.is_alive:
                continue
            
            # Simple AI: attack player
            if enemy.abilities:
                # Try to use ability if available
                usable_abilities = [
                    ability for ability in enemy.abilities 
                    if ability.can_use(enemy)[0]
                ]
                if usable_abilities and random.random() < 0.3:
                    ability = random.choice(usable_abilities)
                    result = ability.use(enemy, self.player)
                    print(f"\n{enemy.name} uses {ability.name}!")
                    for msg in result.get('messages', []):
                        print(f"  {msg}")
                    continue
            
            # Basic attack
            hit_chance = 80 - self.player.get_evasion()
            hit_chance = clamp(hit_chance, 10, 95)
            
            if random.randint(1, 100) <= hit_chance:
                damage = enemy.get_attack_power()
                is_critical = random.random() < 0.05
                
                if is_critical:
                    damage = int(damage * 1.5)
                    print(colored_text("Enemy critical hit!", "\033[91m"))
                
                dmg = Damage(
                    amount=damage,
                    damage_type=DamageType.PHYSICAL,
                    is_critical=is_critical
                )
                actual_damage = self.player.take_damage(dmg)
                
                print(f"\n{enemy.name} attacks you for {actual_damage} damage!")
                
                if not self.player.is_alive:
                    print(colored_text("You have been defeated!", "\033[91m"))
                    break
            else:
                print(f"\n{enemy.name} missed!")
    
    def _process_status_effects(self):
        """Process status effects for all combatants"""
        # Process player effects
        messages = self.player.process_status_effects()
        for msg in messages:
            print(f"  {msg}")
        
        # Process enemy effects
        for enemy in self.enemies:
            messages = enemy.process_status_effects()
            for msg in messages:
                print(f"  {msg}")
    
    def _calculate_experience(self) -> int:
        """Calculate experience gained"""
        total_exp = 0
        for enemy in self.enemies:
            if not enemy.is_alive:
                base_exp = enemy.level * 10
                total_exp += base_exp
        return total_exp
    
    def _calculate_gold(self) -> int:
        """Calculate gold gained"""
        total_gold = 0
        for enemy in self.enemies:
            if not enemy.is_alive:
                base_gold = enemy.level * 5
                total_gold += base_gold
        return total_gold
    
    def _generate_loot(self) -> List[Any]:
        """Generate loot from defeated enemies"""
        from core.items import get_random_item, Rarity, ItemType
        
        loot = []
        for enemy in self.enemies:
            if not enemy.is_alive:
                # Chance for item drop based on enemy rarity
                drop_chance = 0.3  # 30% base chance
                
                # Higher level enemies have better drop rates
                if enemy.level >= 10:
                    drop_chance = 0.5
                if enemy.level >= 20:
                    drop_chance = 0.7
                
                if random.random() < drop_chance:
                    # Determine rarity based on enemy level
                    rarity_roll = random.random()
                    if enemy.level >= 20 and rarity_roll < 0.1:
                        rarity = Rarity.LEGENDARY
                    elif enemy.level >= 15 and rarity_roll < 0.2:
                        rarity = Rarity.EPIC
                    elif enemy.level >= 10 and rarity_roll < 0.3:
                        rarity = Rarity.RARE
                    elif enemy.level >= 5 and rarity_roll < 0.5:
                        rarity = Rarity.UNCOMMON
                    else:
                        rarity = Rarity.COMMON
                    
                    item = get_random_item(rarity=rarity)
                    if item:
                        loot.append(item)
        
        return loot


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
            "faction": "goblin"
        },
        "wolf": {
            "name": "Wolf",
            "description": "A wild, hungry wolf.",
            "base_hp": 40,
            "base_mp": 0,
            "base_damage": 8,
            "rarity": "Common",
            "faction": "beast"
        },
        "skeleton": {
            "name": "Skeleton",
            "description": "An undead skeleton warrior.",
            "base_hp": 35,
            "base_mp": 0,
            "base_damage": 6,
            "rarity": "Common",
            "faction": "undead"
        },
        "orc_warrior": {
            "name": "Orc Warrior",
            "description": "A strong orc fighter.",
            "base_hp": 60,
            "base_mp": 20,
            "base_damage": 12,
            "rarity": "Uncommon",
            "faction": "orc"
        },
        "dark_mage": {
            "name": "Dark Mage",
            "description": "A practitioner of dark magic.",
            "base_hp": 45,
            "base_mp": 80,
            "base_damage": 15,
            "rarity": "Uncommon",
            "faction": "cultist"
        },
        "troll": {
            "name": "Troll",
            "description": "A large, regenerating troll.",
            "base_hp": 100,
            "base_mp": 30,
            "base_damage": 18,
            "rarity": "Rare",
            "faction": "troll"
        },
        "dragon_wyrmling": {
            "name": "Dragon Wyrmling",
            "description": "A young dragon.",
            "base_hp": 150,
            "base_mp": 100,
            "base_damage": 25,
            "rarity": "Rare",
            "faction": "dragon"
        },
        "vampire": {
            "name": "Vampire",
            "description": "A powerful vampire lord.",
            "base_hp": 200,
            "base_mp": 150,
            "base_damage": 30,
            "rarity": "Epic",
            "faction": "vampire"
        },
        "demon": {
            "name": "Demon",
            "description": "A creature from the abyss.",
            "base_hp": 250,
            "base_mp": 200,
            "base_damage": 40,
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

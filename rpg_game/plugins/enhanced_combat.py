"""
Enhanced Combat Plugin - Advanced Combat Features
Demonstrates event priorities, combat mechanics, abilities, and content provision.
"""

from __future__ import annotations
from systems.plugins import Plugin, PluginInfo, PluginPriority, EventType
from core.engine import Rarity
from typing import Dict, List, Any, Optional


class EnhancedCombatPlugin(Plugin):
    """
    Enhanced combat plugin with advanced features.
    
    Features:
    - Combat variety bonuses
    - Milestone ability unlocks
    - Combo system
    - Critical hit enhancements
    - Damage tracking
    - New enemies and combat items
    """
    
    def __init__(self):
        info = PluginInfo(
            id="enhanced_combat",
            name="Enhanced Combat",
            version="2.0.0",
            author="YSNRFD",
            description="Advanced combat mechanics including combo systems, "
                       "variety bonuses, milestone abilities, and enhanced criticals.",
            dependencies=[],
            soft_dependencies=["extended_items"],
            conflicts=[],
            priority=PluginPriority.HIGH,
            tags=["combat", "mechanics", "abilities", "enemies"]
        )
        super().__init__(info)
        
        # Plugin state
        self._combat_stats: Dict[str, Any] = {}
        self._config: Dict[str, Any] = {}
    
    def on_load(self, game) -> bool:
        """Initialize combat enhancements"""
        print("[Enhanced Combat] Loading combat enhancements...")
        
        self._config = {
            "variety_bonus_percent": 10,
            "combo_multiplier": 1.1,
            "milestone_level_interval": 5,
            "enable_combo_system": True,
            "critical_damage_bonus": 0.2
        }
        
        self._combat_stats = {
            "combats_started": 0,
            "combats_won": 0,
            "combats_lost": 0,
            "total_damage_dealt": 0,
            "total_damage_taken": 0,
            "critical_hits": 0,
            "max_combo": 0,
            "variety_bonuses": 0
        }
        
        return True
    
    def on_unload(self, game) -> bool:
        """Cleanup combat enhancements"""
        print("[Enhanced Combat] Unloading...")
        print(f"  Final Stats: {self._combat_stats['combats_won']} wins, "
              f"{self._combat_stats['combats_lost']} losses")
        return True
    
    def on_enable(self, game) -> bool:
        """Enable combat enhancements"""
        print("[Enhanced Combat] Enabled!")
        return True
    
    def on_disable(self, game) -> bool:
        """Disable combat enhancements"""
        print("[Enhanced Combat] Disabled")
        return True
    
    def register_hooks(self, event_system) -> Dict[EventType, Any]:
        """
        Register combat event hooks.
        
        Returns:
            Dict mapping EventType to handler functions
        """
        return {
            EventType.COMBAT_START: self._on_combat_start,
            EventType.COMBAT_END: self._on_combat_end,
            EventType.COMBAT_TURN: self._on_combat_turn,
            EventType.PLAYER_LEVEL_UP: self._on_level_up,
            EventType.ITEM_PICKUP: self._on_item_pickup,
            EventType.ITEM_EQUIP: self._on_item_equip,
        }
    
    def _on_combat_start(self, game, data):
        """Initialize combat with variety bonus detection"""
        self._combat_stats["combats_started"] += 1
        
        player = data.get("player")
        enemies = data.get("enemies", [])
        
        # Initialize combo state
        if self._config.get("enable_combo_system") and player:
            player._enhanced_combo = 0
        
        # Variety bonus for fighting diverse enemies
        if enemies:
            unique_types = len(set(e.name for e in enemies))
            if unique_types >= 3:
                bonus_percent = self._config.get("variety_bonus_percent", 10)
                print(f"⚔️ Variety Bonus: +{bonus_percent}% experience!")
                self._combat_stats["variety_bonuses"] += 1
                
                # Store for end of combat
                if player:
                    player._variety_bonus = bonus_percent / 100
    
    def _on_combat_end(self, game, data):
        """Process combat results and apply bonuses"""
        player = data.get("player")
        result = data.get("result")
        
        if result == "victory":
            self._combat_stats["combats_won"] += 1
            
            # Apply variety bonus
            if player and hasattr(player, '_variety_bonus'):
                bonus = player._variety_bonus
                if bonus > 0:
                    print(f"  Variety bonus applied: +{int(bonus * 100)}%")
                delattr(player, '_variety_bonus')
            
            # Reset combo
            if hasattr(player, '_enhanced_combo'):
                max_combo = player._enhanced_combo
                if max_combo > self._combat_stats["max_combo"]:
                    self._combat_stats["max_combo"] = max_combo
                delattr(player, '_enhanced_combo')
        else:
            self._combat_stats["combats_lost"] += 1
    
    def _on_combat_turn(self, game, data):
        """Track combos and provide combat enhancements"""
        player = data.get("player")
        
        if not player or not self._config.get("enable_combo_system"):
            return
        
        # Increment combo
        current_combo = getattr(player, '_enhanced_combo', 0) + 1
        player._enhanced_combo = current_combo
        
        # Combo bonuses every 3 hits
        if current_combo > 0 and current_combo % 3 == 0:
            combo_mult = self._config.get("combo_multiplier", 1.1)
            print(f"🔥 {current_combo}-hit combo! Damage x{combo_mult:.1f}!")
    
    def _on_level_up(self, game, data):
        """Grant milestone abilities"""
        player = data.get("player")
        level = data.get("level", 1)
        
        if not player:
            return
        
        interval = self._config.get("milestone_level_interval", 5)
        
        if level % interval == 0:
            print(f"🎯 Milestone Level {level}! Combat prowess increased!")
            
            # Add passive combat bonus
            if not hasattr(player, '_combat_bonuses'):
                player._combat_bonuses = {}
            
            player._combat_bonuses[f"milestone_{level}"] = {
                "critical_chance": 0.02,
                "damage_bonus": level // 2
            }
    
    def _on_item_pickup(self, game, data):
        """Track rare item discoveries"""
        item = data.get("item")
        
        if item and hasattr(item, 'rarity'):
            if item.rarity == Rarity.LEGENDARY:
                print(f"🌟 LEGENDARY item found: {item.name}!")
    
    def _on_item_equip(self, game, data):
        """Handle combat item equips"""
        item = data.get("item")
        
        if item and hasattr(item, 'special_effects'):
            effects = item.special_effects
            if effects:
                print(f"  Combat effects: {', '.join(effects)}")
    
    def register_commands(self, command_system) -> Dict[str, Any]:
        """
        Register combat-related commands.
        
        Returns:
            Dict mapping command names to handler info
        """
        return {
            "combat_stats": {
                "handler": self._cmd_stats,
                "help": "Show enhanced combat statistics",
                "category": "stats"
            },
            "combat_config": {
                "handler": self._cmd_config,
                "help": "Configure combat enhancements",
                "usage": "/combat_config [key] [value]",
                "category": "config"
            },
            "combo_reset": {
                "handler": self._cmd_combo_reset,
                "help": "Reset combo counter",
                "category": "debug"
            },
            "combat_test": {
                "handler": self._cmd_test,
                "help": "Test combat calculations",
                "category": "debug"
            }
        }
    
    def _cmd_stats(self, game, args, context) -> str:
        """Display combat statistics"""
        stats = self._combat_stats
        
        total = stats.get("combats_won", 0) + stats.get("combats_lost", 0)
        win_rate = (stats.get("combats_won", 0) / total * 100) if total > 0 else 0
        
        return (
            "Enhanced Combat Statistics:\n"
            f"  Combats Started: {stats.get('combats_started', 0)}\n"
            f"  Victories: {stats.get('combats_won', 0)}\n"
            f"  Defeats: {stats.get('combats_lost', 0)}\n"
            f"  Win Rate: {win_rate:.1f}%\n"
            f"  Critical Hits: {stats.get('critical_hits', 0)}\n"
            f"  Max Combo: {stats.get('max_combo', 0)}\n"
            f"  Variety Bonuses: {stats.get('variety_bonuses', 0)}\n"
            f"\nConfiguration:\n"
            f"  Combo System: {'On' if self._config.get('enable_combo_system') else 'Off'}\n"
            f"  Variety Bonus: {self._config.get('variety_bonus_percent')}%\n"
            f"  Combo Multiplier: {self._config.get('combo_multiplier')}x"
        )
    
    def _cmd_config(self, game, args, context) -> str:
        """Configure combat settings"""
        if not args:
            return f"Combat Config: {self._config}"
        
        if len(args) == 1:
            key = args[0]
            return f"{key} = {self._config.get(key, 'Not found')}"
        
        key, value = args[0], args[1]
        
        # Parse value
        if value.lower() in ("true", "yes", "1", "on"):
            value = True
        elif value.lower() in ("false", "no", "0", "off"):
            value = False
        else:
            try:
                value = int(value)
            except ValueError:
                try:
                    value = float(value)
                except ValueError:
                    pass
        
        old_value = self._config.get(key)
        self._config[key] = value
        
        return f"Set {key}: {old_value} -> {value}"
    
    def _cmd_combo_reset(self, game, args, context) -> str:
        """Reset combo counter"""
        self._combat_stats["max_combo"] = 0
        if game and hasattr(game, 'player') and game.player:
            if hasattr(game.player, '_enhanced_combo'):
                game.player._enhanced_combo = 0
        return "Combo counter reset!"
    
    def _cmd_test(self, game, args, context) -> str:
        """Test combat calculations"""
        if not args:
            return "Usage: /combat_test <base_damage> [combo_count]"
        
        try:
            base_damage = int(args[0])
            combo = int(args[1]) if len(args) > 1 else 0
        except ValueError:
            return "Invalid numbers provided"
        
        # Calculate with combo multiplier
        if combo > 0 and self._config.get("enable_combo_system"):
            multiplier = self._config.get("combo_multiplier", 1.1) ** (combo // 3)
            final_damage = int(base_damage * multiplier)
            return (
                f"Combat Test:\n"
                f"  Base Damage: {base_damage}\n"
                f"  Combo: {combo}\n"
                f"  Multiplier: {multiplier:.2f}x\n"
                f"  Final Damage: {final_damage}"
            )
        
        return f"Combat Test: Base damage {base_damage} (no combo bonus)"
    
    def register_enemies(self, enemy_registry) -> Dict[str, Dict]:
        """
        Register enhanced combat enemies.
        
        Returns:
            Dict mapping enemy IDs to enemy data
        """
        return {
            "elite_knight": {
                "name": "Elite Knight",
                "description": "A highly trained warrior in gleaming armor.",
                "base_hp": 200,
                "base_mp": 50,
                "base_damage": 30,
                "rarity": "Rare",
                "faction": "human",
                "abilities": ["shield_bash", "power_strike"],
                "resistances": {"physical": 0.3},
                "drops": {"gold": [50, 150], "items": ["knight_armor"]}
            },
            "shadow_assassin": {
                "name": "Shadow Assassin",
                "description": "A deadly killer emerging from darkness.",
                "base_hp": 100,
                "base_mp": 80,
                "base_damage": 40,
                "rarity": "Epic",
                "faction": "assassin",
                "abilities": ["backstab", "shadow_step", "poison_blade"],
                "resistances": {"physical": 0.2, "dark": 0.5},
                "weaknesses": {"holy": 1.5},
                "drops": {"gold": [100, 300], "items": ["assassin_dagger"]}
            },
            "combat_trainer": {
                "name": "Combat Trainer",
                "description": "An experienced warrior who tests adventurers.",
                "base_hp": 300,
                "base_mp": 100,
                "base_damage": 35,
                "rarity": "Rare",
                "faction": "human",
                "abilities": ["teaching_strike", "defensive_stance"],
                "resistances": {"physical": 0.4},
                "drops": {"gold": [80, 200]}
            },
            "berserker": {
                "name": "Berserker",
                "description": "A warrior consumed by battle rage.",
                "base_hp": 250,
                "base_mp": 30,
                "base_damage": 50,
                "rarity": "Epic",
                "faction": "barbarian",
                "abilities": ["berserker_rage", "wild_swing"],
                "resistances": {"physical": 0.1},
                "weaknesses": {"ice": 1.3},
                "drops": {"gold": [150, 400], "items": ["berserker_axe"]}
            },
            "duelist": {
                "name": "Master Duelist",
                "description": "A master of one-on-one combat.",
                "base_hp": 180,
                "base_mp": 60,
                "base_damage": 35,
                "rarity": "Rare",
                "faction": "human",
                "abilities": ["riposte", "precise_thrust", "disarm"],
                "resistances": {"physical": 0.2},
                "drops": {"gold": [100, 250], "items": ["duelist_rapier"]}
            }
        }
    
    def register_items(self, item_registry) -> Dict[str, Dict]:
        """
        Register combat-related items.
        
        Returns:
            Dict mapping item IDs to item data
        """
        return {
            "knight_armor": {
                "name": "Knight's Plate",
                "item_type": "armor",
                "rarity": "Rare",
                "value": 800,
                "weight": 20.0,
                "description": "Sturdy armor worn by elite knights.",
                "slot": "chest",
                "defense": 25,
                "magic_defense": 10,
                "level_required": 8
            },
            "assassin_dagger": {
                "name": "Assassin's Blade",
                "item_type": "weapon",
                "rarity": "Epic",
                "value": 1200,
                "weight": 0.5,
                "description": "A dagger designed for quick, lethal strikes.",
                "damage_min": 8,
                "damage_max": 16,
                "damage_type": "physical",
                "attack_speed": 1.6,
                "critical_chance": 0.20,
                "critical_damage": 2.5,
                "level_required": 10
            },
            "berserker_axe": {
                "name": "Berserker's Axe",
                "item_type": "weapon",
                "rarity": "Epic",
                "value": 1500,
                "weight": 6.0,
                "description": "A heavy axe that grows stronger with each hit.",
                "damage_min": 15,
                "damage_max": 30,
                "damage_type": "physical",
                "attack_speed": 0.8,
                "critical_chance": 0.15,
                "special_effects": ["Damage increases with consecutive hits"],
                "level_required": 12
            },
            "duelist_rapier": {
                "name": "Duelist's Rapier",
                "item_type": "weapon",
                "rarity": "Rare",
                "value": 900,
                "weight": 1.5,
                "description": "A precise weapon for skilled fighters.",
                "damage_min": 10,
                "damage_max": 18,
                "damage_type": "physical",
                "attack_speed": 1.4,
                "critical_chance": 0.18,
                "level_required": 8
            },
            "combat_stimulant": {
                "name": "Combat Stimulant",
                "item_type": "consumable",
                "rarity": "Uncommon",
                "value": 75,
                "weight": 0.1,
                "description": "Temporarily increases combat abilities.",
                "temporary_effects": [("strength_buff", 5, 5), ("haste", 0, 5)],
                "use_message": "You feel your combat abilities surge!"
            }
        }


# Plugin instance - REQUIRED
plugin = EnhancedCombatPlugin()

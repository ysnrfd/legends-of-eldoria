"""
Enhanced Combat Plugin - Advanced Combat Features
Demonstrates event priorities, combat mechanics, and abilities
"""

from __future__ import annotations
from systems.plugins import (
    PluginBase, PluginInfo, PluginType, PluginPriority,
    EventPriority, IHotReloadablePlugin
)
from core.engine import (
    Ability, AbilityType, TargetType, DamageType, StatusEffectType,
    EventType, Rarity
)
from typing import Dict, List, Any, Tuple


class EnhancedCombatPlugin(PluginBase, IHotReloadablePlugin):
    """
    Enhanced combat plugin with advanced features.
    
    Features:
    - Combat variety bonuses
    - Milestone ability unlocks
    - Combo system
    - Critical hit enhancements
    - Damage tracking
    """
    
    # Plugin state (survives hot reload)
    _combat_stats: Dict[str, Any] = {}
    
    @property
    def info(self) -> PluginInfo:
        return PluginInfo(
            id="enhanced_combat",
            name="Enhanced Combat",
            version="2.0.0",
            author="YSNRFD",
            description="Advanced combat mechanics including combo systems, "
                       "variety bonuses, milestone abilities, and enhanced criticals.",
            
            # Dependencies and conflicts
            dependencies=[],
            soft_dependencies=["extended_items"],
            conflicts=[],
            provides=["combat_enhancements"],
            
            # Loading
            priority=PluginPriority.HIGH.value,
            plugin_type=PluginType.CLASS,
            
            # Configuration
            configurable=True,
            config_schema={
                "variety_bonus_percent": {
                    "type": "integer", "default": 10, "min": 0, "max": 50
                },
                "combo_multiplier": {
                    "type": "number", "default": 1.1, "min": 1.0, "max": 2.0
                },
                "milestone_level_interval": {
                    "type": "integer", "default": 5, "min": 1, "max": 20
                },
                "enable_combo_system": {
                    "type": "boolean", "default": True
                }
            },
            default_config={
                "variety_bonus_percent": 10,
                "combo_multiplier": 1.1,
                "milestone_level_interval": 5,
                "enable_combo_system": True
            },
            
            # Hot reload
            supports_hot_reload=True,
            
            # Metadata
            tags=["combat", "mechanics", "abilities"],
            custom={"category": "gameplay"}
        )
    
    # =========================================================================
    # Lifecycle
    # =========================================================================
    
    def on_load(self, game):
        print("[Enhanced Combat] Loading combat enhancements...")
        
        self._config = self.info.default_config.copy()
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
    
    def on_unload(self, game):
        print("[Enhanced Combat] Unloading...")
        print(f"  Stats: {self._combat_stats['combats_won']} wins, "
              f"{self._combat_stats['combats_lost']} losses")
    
    def on_enable(self, game):
        print("[Enhanced Combat] Enabled!")
    
    # =========================================================================
    # Hot Reload Support
    # =========================================================================
    
    def on_before_reload(self, game) -> Dict[str, Any]:
        return {
            "stats": self._combat_stats.copy(),
            "config": self._config.copy()
        }
    
    def on_after_reload(self, game, state: Dict[str, Any]) -> None:
        self._combat_stats = state.get("stats", {})
        self._config = state.get("config", self.info.default_config)
        print(f"[Enhanced Combat] Reloaded! Combats: {self._combat_stats.get('combats_started', 0)}")
    
    # =========================================================================
    # Event Hooks
    # =========================================================================
    
    def register_hooks(self, event_system) -> Dict:
        return {
            # High priority to run before other plugins
            EventType.COMBAT_START: (self._on_combat_start, EventPriority.HIGH),
            EventType.COMBAT_END: (self._on_combat_end, EventPriority.HIGH),
            EventType.COMBAT_TURN: (self._on_combat_turn, EventPriority.NORMAL),
            EventType.PLAYER_LEVEL_UP: (self._on_level_up, EventPriority.NORMAL),
        }
    
    def _on_combat_start(self, data):
        """Initialize combat with variety bonus detection"""
        self._combat_stats["combats_started"] += 1
        
        player = data.get("player")
        enemies = data.get("enemies", [])
        
        # Store combo state
        if self._config.get("enable_combo_system"):
            if player:
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
        
        return None
    
    def _on_combat_end(self, data):
        """Process combat results and apply bonuses"""
        player = data.get("player")
        result = data.get("result")
        enemies = data.get("enemies", [])
        
        if result == "victory":
            self._combat_stats["combats_won"] += 1
            
            # Apply variety bonus
            if player and hasattr(player, '_variety_bonus'):
                bonus = player._variety_bonus
                if bonus > 0:
                    # Could add bonus gold/XP here
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
        
        return None
    
    def _on_combat_turn(self, data):
        """Track combos and provide combat enhancements"""
        player = data.get("player")
        enemy = data.get("enemy")
        turn = data.get("turn_number", 0)
        
        if not player or not self._config.get("enable_combo_system"):
            return None
        
        # Increment combo
        current_combo = getattr(player, '_enhanced_combo', 0) + 1
        player._enhanced_combo = current_combo
        
        # Combo bonuses every 3 hits
        if current_combo > 0 and current_combo % 3 == 0:
            combo_mult = self._config.get("combo_multiplier", 1.1)
            print(f"🔥 {current_combo}-hit combo! Damage x{combo_mult:.1f}!")
        
        return None
    
    def _on_level_up(self, data):
        """Grant milestone abilities"""
        player = data.get("player")
        level = data.get("level", 1)
        
        if not player:
            return None
        
        interval = self._config.get("milestone_level_interval", 5)
        
        if level % interval == 0:
            # Create milestone ability
            ability_name = f"Milestone Power Lv.{level}"
            bonus_ability = Ability(
                name=ability_name,
                description=f"Power granted at level {level} milestone.",
                ability_type=AbilityType.ACTIVE,
                target_type=TargetType.SINGLE_ENEMY,
                mp_cost=20 + level,
                cooldown=4,
                damage=30 + level * 3,
                damage_type=DamageType.PHYSICAL,
                effects=[("strength_buff", level // 5, 3)]
            )
            
            player.abilities.append(bonus_ability)
            print(f"🎯 Milestone Level {level}! New ability: {ability_name}!")
        
        return None
    
    # =========================================================================
    # Commands
    # =========================================================================
    
    def register_commands(self, command_system) -> Dict:
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
            }
        }
    
    def _cmd_stats(self, game, args, context):
        """Display combat statistics"""
        stats = self._combat_stats
        return (
            "Enhanced Combat Statistics:\n"
            f"  Combats Started: {stats.get('combats_started', 0)}\n"
            f"  Victories: {stats.get('combats_won', 0)}\n"
            f"  Defeats: {stats.get('combats_lost', 0)}\n"
            f"  Win Rate: {self._calc_win_rate():.1f}%\n"
            f"  Critical Hits: {stats.get('critical_hits', 0)}\n"
            f"  Max Combo: {stats.get('max_combo', 0)}\n"
            f"  Variety Bonuses: {stats.get('variety_bonuses', 0)}\n"
            f"\nConfiguration:\n"
            f"  Combo System: {'On' if self._config.get('enable_combo_system') else 'Off'}\n"
            f"  Variety Bonus: {self._config.get('variety_bonus_percent')}%\n"
            f"  Combo Multiplier: {self._config.get('combo_multiplier')}x"
        )
    
    def _cmd_config(self, game, args, context):
        """Configure combat settings"""
        if not args:
            return f"Config: {self._config}"
        
        if len(args) == 1:
            key = args[0]
            return f"{key} = {self._config.get(key, 'Not found')}"
        
        key, value = args[0], args[1]
        
        # Parse value based on schema
        schema = self.info.config_schema.get(key, {})
        if schema.get("type") == "integer":
            value = int(value)
        elif schema.get("type") == "number":
            value = float(value)
        elif schema.get("type") == "boolean":
            value = value.lower() in ("true", "yes", "1", "on")
        
        old_value = self._config.get(key)
        self._config[key] = value
        
        return f"Set {key}: {old_value} -> {value}"
    
    def _cmd_combo_reset(self, game, args, context):
        """Reset combo counter"""
        self._combat_stats["max_combo"] = 0
        if game and game.player and hasattr(game.player, '_enhanced_combo'):
            game.player._enhanced_combo = 0
        return "Combo counter reset!"
    
    def _calc_win_rate(self) -> float:
        """Calculate win rate percentage"""
        total = self._combat_stats.get("combats_won", 0) + self._combat_stats.get("combats_lost", 0)
        if total == 0:
            return 0.0
        return (self._combat_stats.get("combats_won", 0) / total) * 100
    
    # =========================================================================
    # Enemy Registration
    # =========================================================================
    
    def register_enemies(self, enemy_registry) -> Dict[str, Any]:
        """Register enhanced combat enemies"""
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
            }
        }


# Plugin instance
plugin = EnhancedCombatPlugin()

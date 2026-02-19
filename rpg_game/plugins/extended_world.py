"""
Extended World Plugin - New Locations, Events, and Secrets
Demonstrates comprehensive world building with dynamic features
"""

from __future__ import annotations
from systems.plugins import (
    PluginBase, PluginInfo, PluginType, PluginPriority,
    IContentProvider, IHotReloadablePlugin, EventPriority
)
from core.engine import Rarity, DamageType, StatType, Weather, TimeOfDay, EventType
from typing import Dict, List, Any, Tuple
from dataclasses import dataclass, field
import random


@dataclass
class WorldSecret:
    """A hidden secret in the world"""
    id: str
    name: str
    description: str
    location: str
    discovery_method: str
    requirements: Dict[str, Any] = field(default_factory=dict)
    rewards: Dict[str, Any] = field(default_factory=dict)


@dataclass
class WorldEvent:
    """A dynamic world event"""
    id: str
    name: str
    description: str
    event_type: str
    duration: int
    effects: Dict[str, Any] = field(default_factory=dict)
    locations: List[str] = field(default_factory=list)
    conditions: Dict[str, Any] = field(default_factory=dict)


class ExtendedWorldPlugin(PluginBase, IContentProvider, IHotReloadablePlugin):
    """
    Extended World plugin with new locations and features.
    
    Features:
    - 14 new locations (underground, magical, dark, special)
    - World secrets for discovery
    - Dynamic world events
    - Weather effects
    - Exploration rewards
    - Time-based features
    """
    
    _discovered_secrets: set = set()
    _active_events: Dict[str, Any] = {}
    
    @property
    def info(self) -> PluginInfo:
        return PluginInfo(
            id="extended_world",
            name="Extended World",
            version="2.0.0",
            author="YSNRFD",
            description="Expands the world with 14 new locations, dynamic events, "
                       "secrets, weather effects, and exploration features.",
            
            dependencies=[],
            soft_dependencies=["extended_npcs"],
            conflicts=[],
            provides=["extended_locations", "world_events", "world_secrets"],
            
            priority=PluginPriority.NORMAL.value,
            plugin_type=PluginType.CLASS,
            
            configurable=True,
            config_schema={
                "event_frequency": {
                    "type": "integer", "default": 5, "min": 1, "max": 20
                },
                "secret_discovery_chance": {
                    "type": "number", "default": 0.1, "min": 0, "max": 1
                }
            },
            default_config={
                "event_frequency": 5,
                "secret_discovery_chance": 0.1
            },
            
            supports_hot_reload=True,
            tags=["world", "locations", "exploration", "events"],
            custom={"location_count": 14, "secret_count": 8}
        )
    
    # =========================================================================
    # Lifecycle
    # =========================================================================
    
    def on_load(self, game):
        print("[Extended World] Loading extended world content...")
        self._config = self.info.default_config.copy()
        self._discovered_secrets = set()
        self._active_events = {}
    
    def on_unload(self, game):
        print("[Extended World] Unloading...")
    
    def on_before_reload(self, game) -> Dict[str, Any]:
        return {
            "discovered_secrets": list(self._discovered_secrets),
            "active_events": self._active_events.copy(),
            "config": self._config.copy()
        }
    
    def on_after_reload(self, game, state: Dict[str, Any]) -> None:
        self._discovered_secrets = set(state.get("discovered_secrets", []))
        self._active_events = state.get("active_events", {})
        self._config = state.get("config", self.info.default_config)
        print(f"[Extended World] Reloaded! {len(self._discovered_secrets)} secrets discovered")
    
    # =========================================================================
    # Content Provider
    # =========================================================================
    
    def get_content_types(self) -> List[str]:
        return ["locations", "world_events", "world_secrets"]
    
    def get_content(self, content_type: str) -> Dict[str, Any]:
        if content_type == "locations":
            return self._get_locations()
        elif content_type == "world_events":
            return self._get_world_events()
        elif content_type == "world_secrets":
            return self._get_world_secrets()
        return {}
    
    # =========================================================================
    # Location Definitions
    # =========================================================================
    
    def _get_locations(self) -> Dict[str, Dict]:
        return {
            # =========================================================================
            # UNDERGROUND AREAS
            # =========================================================================
            
            "crystal_caverns": {
                "name": "Crystal Caverns",
                "description": "A breathtaking underground cave system where massive crystals pulse "
                             "with magical energy. The walls shimmer with every color imaginable.",
                "location_type": "cave",
                "level_range": [8, 15],
                "connections": ["mining_town"],
                "enemies": ["crystal_golem", "cave_spider", "rock_elemental"],
                "items": ["magic_crystal", "crystal_shard", "rare_gem"],
                "danger_level": 4,
                "special_features": {
                    "crystal_harvesting": True,
                    "magic_recharge": {"mp_per_turn": 5},
                    "hidden_passages": 3,
                    "boss": "crystal_colossus"
                },
                "discovery_exp": 200
            },
            
            "underground_lake": {
                "name": "Mirror Lake",
                "description": "An enormous underground lake so still it perfectly reflects "
                             "the cavern ceiling. Strange lights dance beneath its surface.",
                "location_type": "cave",
                "level_range": [12, 20],
                "connections": ["crystal_caverns"],
                "enemies": ["water_elemental", "lake_monster", "drowned_spirit"],
                "items": ["ancient_coin", "water_crystal"],
                "danger_level": 5,
                "special_features": {
                    "boat_travel": True,
                    "underwater_sections": True,
                    "boss": "ancient_hydra"
                },
                "discovery_exp": 350
            },
            
            # =========================================================================
            # MAGICAL LOCATIONS
            # =========================================================================
            
            "floating_islands": {
                "name": "Sky Sanctuary",
                "description": "A chain of floating islands high above the clouds, connected by "
                             "magical bridges. Ancient ruins lie scattered across the islands.",
                "location_type": "special",
                "level_range": [15, 25],
                "connections": ["mountain_pass"],
                "enemies": ["sky_elemental", "cloud_dragon", "wind_spirit"],
                "items": ["sky_crystal", "feather_fall_potion"],
                "danger_level": 5,
                "special_features": {
                    "flight_mechanics": True,
                    "falling_hazard": True,
                    "boss": "storm_lord"
                },
                "discovery_exp": 400,
                "requirements": {"level": 15}
            },
            
            "enchanted_garden": {
                "name": "Garden of Eternal Bloom",
                "description": "A hidden garden where flowers bloom eternally and plants "
                             "grow to impossible sizes. A dryad protects the garden's heart.",
                "location_type": "special",
                "level_range": [5, 12],
                "connections": ["deep_forest"],
                "enemies": ["enraged_plant", "giant_bee", "dryad"],
                "items": ["rare_herb", "golden_apple"],
                "danger_level": 3,
                "special_features": {
                    "herb_gathering": {"bonus": 2.0},
                    "boss": "guardian_dryad",
                    "healing_aura": 5
                },
                "discovery_exp": 150
            },
            
            "mage_tower": {
                "name": "Tower of the Arcane",
                "description": "A spiraling tower that seems to touch the stars. Each floor "
                             "contains different magical challenges and creatures.",
                "location_type": "dungeon",
                "level_range": [10, 30],
                "connections": ["capital_city"],
                "enemies": ["enchanted_armor", "magical_construct", "phantom_mage"],
                "items": ["spell_scroll", "magic_crystal"],
                "danger_level": 4,
                "special_features": {
                    "floor_system": {"total_floors": 10},
                    "boss_every_floor": True,
                    "final_boss": "archmage_ghost"
                },
                "discovery_exp": 300
            },
            
            # =========================================================================
            # DARK LOCATIONS
            # =========================================================================
            
            "cursed_village": {
                "name": "Hollow's End",
                "description": "A village consumed by an ancient curse. The buildings stand empty, "
                             "but shadows move in the windows. Ghostly figures reenact their deaths.",
                "location_type": "village",
                "level_range": [10, 18],
                "connections": ["swamp_lands", "ruined_kingdom"],
                "enemies": ["restless_spirit", "cursed_villager", "shadow_beast"],
                "items": ["cursed_relic", "purified_water"],
                "danger_level": 4,
                "special_features": {
                    "time_loop": True,
                    "curse_mechanic": True,
                    "boss": "curse_bearer",
                    "night_danger_multiplier": 2.0
                },
                "discovery_exp": 250,
                "time_variants": {
                    "day": "The village appears peaceful but empty.",
                    "night": "Ghostly lights flicker in windows."
                }
            },
            
            "demon_portal": {
                "name": "Hellgate Rift",
                "description": "A massive tear in reality where demons pour into the world. "
                             "The ground is scorched and the sky above burns red.",
                "location_type": "special",
                "level_range": [25, 35],
                "connections": ["ruined_kingdom"],
                "enemies": ["demon", "hell_hound", "pit_lord"],
                "items": ["demon_heart", "hellfire_orb"],
                "danger_level": 5,
                "special_features": {
                    "demonic_influence": {"stat_reduction": -2},
                    "boss": "demon_lord",
                    "legendary_drops": True
                },
                "discovery_exp": 750,
                "requirements": {"level": 25}
            },
            
            "shadow_realm": {
                "name": "Realm of Shadows",
                "description": "A twisted reflection of the world where light is foreign. "
                             "Shadow creatures hunt endlessly in the darkness.",
                "location_type": "special",
                "level_range": [20, 30],
                "connections": [],
                "enemies": ["shadow_self", "darkness_elemental", "void_walker"],
                "items": ["shadow_essence", "void_crystal"],
                "danger_level": 5,
                "special_features": {
                    "mirror_world": True,
                    "light_mechanic": True,
                    "boss": "shadow_king"
                },
                "discovery_exp": 600
            },
            
            # =========================================================================
            # SPECIAL LOCATIONS
            # =========================================================================
            
            "arena_of_champions": {
                "name": "Grand Arena",
                "description": "A massive colosseum that has hosted legendary battles for millennia. "
                             "The crowd's roar echoes even when the stands are empty.",
                "location_type": "special",
                "level_range": [1, 50],
                "connections": ["capital_city"],
                "danger_level": 0,
                "special_features": {
                    "arena_battles": True,
                    "betting_system": True,
                    "ranked_matches": True
                },
                "discovery_exp": 100
            },
            
            "treasure_vault": {
                "name": "Dragon's Hoard",
                "description": "A cavern filled with mountains of gold and gems. "
                             "This was once a dragon's lair, and its cursed treasure remains.",
                "location_type": "cave",
                "level_range": [20, 30],
                "connections": ["dragon_peak"],
                "items": ["ancient_gold", "dragon_gem"],
                "danger_level": 4,
                "special_features": {
                    "gold_curse": True,
                    "traps": 10,
                    "boss": "treasure_guardian"
                },
                "discovery_exp": 500
            },
            
            "celestial_observatory": {
                "name": "Starfall Observatory",
                "description": "An ancient observatory perched on the highest peak. "
                             "During meteor showers, wishes made here may come true.",
                "location_type": "special",
                "level_range": [1, 30],
                "connections": ["mountain_pass"],
                "danger_level": 1,
                "special_features": {
                    "star_reading": True,
                    "wish_mechanic": {"chance": 0.1},
                    "meteor_events": True
                },
                "discovery_exp": 200
            },
            
            # =========================================================================
            # HIDDEN LOCATIONS
            # =========================================================================
            
            "hidden_waterfall": {
                "name": "Cascading Secrets",
                "description": "Behind a magnificent waterfall lies a hidden cave with "
                             "ancient murals and a natural healing spring.",
                "location_type": "cave",
                "level_range": [5, 12],
                "connections": ["forest_path"],
                "enemies": ["water_sprite", "cave_fisher"],
                "items": ["healing_water", "ancient_relic"],
                "danger_level": 2,
                "special_features": {
                    "healing_spring": True,
                    "hidden_entrance": True
                },
                "discovery_exp": 100,
                "hidden": True,
                "discovery_method": "skill_check"
            },
            
            "goblin_kingdom": {
                "name": "Goblin Underground",
                "description": "A sprawling city built by goblins beneath the earth. "
                             "The Goblin King rules with an iron fist.",
                "location_type": "dungeon",
                "level_range": [3, 10],
                "connections": ["forest_path"],
                "enemies": ["goblin", "goblin_warrior", "goblin_shaman"],
                "items": ["goblin_treasure", "stolen_goods"],
                "danger_level": 3,
                "special_features": {
                    "goblin_market": True,
                    "boss": "goblin_king",
                    "stealth_infiltration": True
                },
                "discovery_exp": 150,
                "hidden": True
            }
        }
    
    # =========================================================================
    # World Secrets
    # =========================================================================
    
    def _get_world_secrets(self) -> Dict[str, Dict]:
        """Secrets for discovery"""
        return {
            "ancient_cache_1": {
                "name": "Forgotten Adventurer's Cache",
                "description": "A hidden cache of supplies left by an ancient adventurer.",
                "location": "forest_path",
                "discovery_method": "explore",
                "requirements": {"exploration_count": 10},
                "rewards": {"gold": 500, "items": ["health_potion"], "exp": 100}
            },
            
            "fairy_ring": {
                "name": "Secret Fairy Ring",
                "description": "A hidden fairy circle that grants blessings.",
                "location": "deep_forest",
                "discovery_method": "skill_check",
                "requirements": {"luck": 15, "time": "midnight"},
                "rewards": {"effect": "fairy_blessing", "stat_bonus": {"luck": 3}, "exp": 200}
            },
            
            "dragon_treasure": {
                "name": "Hidden Dragon Hoard",
                "description": "A small stash of dragon treasure overlooked by adventurers.",
                "location": "dragon_peak",
                "discovery_method": "explore",
                "requirements": {"level": 20},
                "rewards": {"gold": 5000, "items": ["dragon_scale"], "exp": 500}
            },
            
            "sunken_ship": {
                "name": "Shipwreck Treasure",
                "description": "An ancient shipwreck with valuable cargo.",
                "location": "underground_lake",
                "discovery_method": "skill_check",
                "requirements": {"dexterity": 15},
                "rewards": {"gold": 3000, "items": ["ancient_weapon"], "exp": 300}
            },
            
            "mage_library": {
                "name": "Secret Library Section",
                "description": "A hidden section of the mage tower library.",
                "location": "mage_tower",
                "discovery_method": "item_use",
                "requirements": {"item": "mage_key"},
                "rewards": {"items": ["ancient_spell_tome"], "skill_exp": {"Magic": 100}, "exp": 400}
            },
            
            "crystal_heart": {
                "name": "Heart of the Caverns",
                "description": "The central crystal that powers the entire cavern.",
                "location": "crystal_caverns",
                "discovery_method": "explore",
                "requirements": {"explore_depth": 10},
                "rewards": {"effect": "crystal_empowerment", "stat_bonus": {"intelligence": 5}, "exp": 400}
            },
            
            "shadow_mirror": {
                "name": "Mirror of Truth",
                "description": "An ancient mirror that shows your true self.",
                "location": "shadow_realm",
                "discovery_method": "time_based",
                "requirements": {"time": "midnight"},
                "rewards": {"effect": "true_sight", "special_ability": "shadow_walk", "exp": 600}
            },
            
            "celestial_wish": {
                "name": "Falling Star",
                "description": "A meteor has fallen here during a shower.",
                "location": "celestial_observatory",
                "discovery_method": "time_based",
                "requirements": {"event": "meteor_shower"},
                "rewards": {"wish": True, "exp": 1000}
            }
        }
    
    # =========================================================================
    # World Events
    # =========================================================================
    
    def _get_world_events(self) -> Dict[str, Dict]:
        """Dynamic world events"""
        return {
            "blood_moon": {
                "name": "Blood Moon Rising",
                "description": "A crimson moon hangs in the sky. Dark creatures grow stronger.",
                "event_type": "global",
                "duration": -1,
                "effects": {
                    "enemy_damage_mult": 1.5,
                    "dark_creature_spawn_mult": 2.0,
                    "drop_rate_mult": 1.3
                },
                "conditions": {"weather": "Blood Moon"}
            },
            
            "merchant_caravan": {
                "name": "Traveling Merchants",
                "description": "A caravan of rare merchants has set up shop.",
                "event_type": "location",
                "duration": 5,
                "effects": {
                    "special_shop": True,
                    "discount": 0.8
                },
                "locations": ["capital_city", "crossroads"]
            },
            
            "goblin_invasion": {
                "name": "Goblin Invasion",
                "description": "Goblins are attacking the area! Defend or flee!",
                "event_type": "location",
                "duration": 3,
                "effects": {
                    "enemy_spawn_mult": 3.0,
                    "enemy_type": "goblin",
                    "gold_reward_mult": 2.0
                },
                "locations": ["start_village", "forest_path"]
            },
            
            "aurora_borealis": {
                "name": "Northern Lights",
                "description": "Magical lights dance across the sky, empowering all.",
                "event_type": "global",
                "duration": 5,
                "effects": {
                    "mp_regen_mult": 2.0,
                    "magic_power_bonus": 10
                }
            },
            
            "harvest_festival": {
                "name": "Harvest Festival",
                "description": "The annual harvest festival brings joy and celebration.",
                "event_type": "global",
                "duration": 7,
                "effects": {
                    "shop_discount": 0.75,
                    "rest_heal_mult": 2.0,
                    "friendship_gain_mult": 2.0
                },
                "conditions": {"day": [180, 200]}
            },
            
            "dragon_migration": {
                "name": "Dragon Migration",
                "description": "Dragons are migrating through the area. Danger and opportunity!",
                "event_type": "location",
                "duration": 3,
                "effects": {
                    "dragon_spawn": True,
                    "dragon_scale_drop": 0.5
                },
                "locations": ["mountain_pass", "dragon_peak"]
            },
            
            "magical_storm": {
                "name": "Arcane Storm",
                "description": "Raw magic crackles through the air. Spells are more powerful.",
                "event_type": "global",
                "duration": 4,
                "effects": {
                    "magic_damage_mult": 1.5,
                    "magic_misfire_chance": 0.15
                },
                "conditions": {"weather": "Storm"}
            },
            
            "undead_rising": {
                "name": "Night of the Undead",
                "description": "The dead rise from their graves. The living must be vigilant.",
                "event_type": "location",
                "duration": 2,
                "effects": {
                    "undead_spawn_mult": 3.0,
                    "holy_damage_mult": 2.0
                },
                "locations": ["ruined_kingdom", "cursed_village", "ancient_temple"],
                "conditions": {"time": "night"}
            }
        }
    
    # =========================================================================
    # Exploration Rewards
    # =========================================================================
    
    def get_exploration_rewards(self) -> Dict[int, Dict]:
        """Milestone rewards for exploration"""
        return {
            5: {
                "title": "Novice Explorer",
                "exp_bonus": 5,
                "gold_reward": 100,
                "items": ["compass"]
            },
            10: {
                "title": "Wanderer",
                "exp_bonus": 10,
                "stat_bonus": {"luck": 1}
            },
            25: {
                "title": "Pathfinder",
                "exp_bonus": 15,
                "ability": "quick_travel",
                "gold_reward": 500
            },
            50: {
                "title": "Cartographer",
                "exp_bonus": 20,
                "stat_bonus": {"wisdom": 2},
                "items": ["master_map"]
            },
            100: {
                "title": "World Traveler",
                "exp_bonus": 25,
                "stat_bonus": {"luck": 2, "wisdom": 2},
                "ability": "danger_sense"
            },
            200: {
                "title": "Legendary Explorer",
                "exp_bonus": 50,
                "stat_bonus": {"luck": 5, "wisdom": 5, "charisma": 2}
            }
        }
    
    # =========================================================================
    # Legacy Support
    # =========================================================================
    
    def get_new_locations(self) -> Dict[str, Dict]:
        return self._get_locations()
    
    # =========================================================================
    # Event Hooks
    # =========================================================================
    
    def register_hooks(self, event_system) -> Dict:
        return {
            EventType.LOCATION_ENTER: (self._on_location_enter, EventPriority.NORMAL),
            EventType.TIME_CHANGE: self._on_time_change,
            EventType.WEATHER_CHANGE: self._on_weather_change,
            EventType.PLAYER_LEVEL_UP: self._on_level_up
        }
    
    def _on_location_enter(self, data):
        location_id = data.get("location_id")
        player = data.get("player")
        
        # Check for secrets
        secrets = self._get_world_secrets()
        for secret_id, secret in secrets.items():
            if secret["location"] == location_id and secret_id not in self._discovered_secrets:
                if self._check_secret_requirements(secret, player):
                    self._trigger_secret(secret_id, secret, player)
        
        return None
    
    def _check_secret_requirements(self, secret: Dict, player) -> bool:
        """Check if player meets secret discovery requirements"""
        reqs = secret.get("requirements", {})
        
        # Level check
        if "level" in reqs:
            if not player or player.level < reqs["level"]:
                return False
        
        # Stat check
        for stat, value in reqs.items():
            if stat in ["strength", "dexterity", "intelligence", "luck"]:
                if not player or getattr(player, stat.lower(), 0) < value:
                    return False
        
        return True
    
    def _trigger_secret(self, secret_id: str, secret: Dict, player):
        """Trigger secret discovery"""
        self._discovered_secrets.add(secret_id)
        print(f"\n🔍 SECRET DISCOVERED: {secret['name']}")
        print(f"   {secret['description']}")
        
        rewards = secret.get("rewards", {})
        if rewards.get("gold"):
            print(f"   💰 Found {rewards['gold']} gold!")
        if rewards.get("items"):
            print(f"   📦 Found: {', '.join(rewards['items'])}")
    
    def _on_time_change(self, data):
        new_time = data.get("new_time")
        
        # Trigger time-based events
        if new_time == TimeOfDay.MIDNIGHT:
            # Random secret discovery chance
            if random.random() < 0.1:
                print("\n🌙 The witching hour... secrets may reveal themselves...")
        
        return None
    
    def _on_weather_change(self, data):
        new_weather = data.get("new_weather")
        
        if new_weather == Weather.BLOOD_MOON:
            print("\n🩸 The blood moon rises! Dark forces grow stronger!")
        elif new_weather == Weather.AURORA:
            print("\n✨ The aurora fills the sky with magic!")
        
        return None
    
    def _on_level_up(self, data):
        level = data.get("level", 1)
        
        # Unlock new areas at milestones
        if level == 10:
            print("\n🗺️ New areas may now be accessible!")
        elif level == 20:
            print("\n🗺️ Legendary locations have been discovered!")
        
        return None
    
    # =========================================================================
    # Commands
    # =========================================================================
    
    def register_commands(self, command_system) -> Dict:
        return {
            "locations": {
                "handler": self._cmd_list_locations,
                "help": "List extended locations",
                "category": "info"
            },
            "secrets": {
                "handler": self._cmd_list_secrets,
                "help": "List discovered secrets",
                "category": "info"
            },
            "events": {
                "handler": self._cmd_active_events,
                "help": "Show active world events",
                "category": "info"
            },
            "exploration": {
                "handler": self._cmd_exploration,
                "help": "Show exploration progress",
                "category": "stats"
            }
        }
    
    def _cmd_list_locations(self, game, args, context):
        locations = self._get_locations()
        
        # Group by type
        by_type = {}
        for loc_id, loc in locations.items():
            loc_type = loc.get("location_type", "unknown")
            if loc_type not in by_type:
                by_type[loc_type] = []
            by_type[loc_type].append((loc_id, loc))
        
        lines = ["Extended Locations:", "=" * 50]
        for loc_type, locs in sorted(by_type.items()):
            lines.append(f"\n[{loc_type.upper()}]")
            for loc_id, loc in locs:
                hidden = " (Hidden)" if loc.get("hidden") else ""
                lines.append(f"  • {loc['name']}{hidden} (Lv.{loc['level_range'][0]}-{loc['level_range'][1]})")
        
        return "\n".join(lines)
    
    def _cmd_list_secrets(self, game, args, context):
        secrets = self._get_world_secrets()
        
        lines = ["World Secrets:", "=" * 50]
        lines.append(f"Discovered: {len(self._discovered_secrets)}/{len(secrets)}")
        
        for secret_id, secret in secrets.items():
            discovered = "✓" if secret_id in self._discovered_secrets else "?"
            lines.append(f"  [{discovered}] {secret['name']} ({secret['location']})")
        
        return "\n".join(lines)
    
    def _cmd_active_events(self, game, args, context):
        events = self._get_world_events()
        
        lines = ["World Events:", "=" * 50]
        for event_id, event in events.items():
            lines.append(f"\n{event['name']}:")
            lines.append(f"  Type: {event['event_type']}")
            lines.append(f"  Duration: {event['duration'] if event['duration'] > 0 else 'Permanent'}")
            lines.append(f"  {event['description']}")
        
        return "\n".join(lines)
    
    def _cmd_exploration(self, game, args, context):
        rewards = self.get_exploration_rewards()
        
        lines = ["Exploration Rewards:", "=" * 50]
        for count, reward in sorted(rewards.items()):
            lines.append(f"\n{count} locations: {reward['title']}")
            if "stat_bonus" in reward:
                lines.append(f"  Stats: {reward['stat_bonus']}")
            if "exp_bonus" in reward:
                lines.append(f"  EXP Bonus: +{reward['exp_bonus']}%")
        
        return "\n".join(lines)


# Plugin instance
plugin = ExtendedWorldPlugin()

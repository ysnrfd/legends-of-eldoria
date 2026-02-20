"""
Extended World Plugin - New Locations, Events, and Secrets
Demonstrates comprehensive world building with dynamic features.
"""

from __future__ import annotations
from systems.plugins import Plugin, PluginInfo, PluginPriority, EventType
from core.engine import Rarity, Weather, TimeOfDay
from typing import Dict, List, Any
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


class ExtendedWorldPlugin(Plugin):
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
    
    def __init__(self):
        info = PluginInfo(
            id="extended_world",
            name="Extended World",
            version="2.0.0",
            author="YSNRFD",
            description="Expands the world with 14 new locations, dynamic events, "
                       "secrets, weather effects, and exploration features.",
            dependencies=[],
            soft_dependencies=["extended_npcs"],
            conflicts=[],
            priority=PluginPriority.NORMAL,
            tags=["world", "locations", "events", "secrets", "exploration"]
        )
        super().__init__(info)
        self._discovered_secrets: set = set()
        self._active_events: Dict[str, Any] = {}
        self._exploration_count: int = 0
        self._config: Dict[str, Any] = {}
    
    def on_load(self, game) -> bool:
        """Initialize world features"""
        print("[Extended World] Loading extended world...")
        
        self._config = {
            "event_frequency": 5,
            "secret_discovery_chance": 0.15,
            "exploration_bonus": True
        }
        
        return True
    
    def on_unload(self, game) -> bool:
        """Cleanup"""
        print("[Extended World] Unloading...")
        return True
    
    def on_enable(self, game) -> bool:
        """Enable world features"""
        print("[Extended World] Enabled!")
        return True
    
    def on_disable(self, game) -> bool:
        """Disable world features"""
        return True
    
    def register_hooks(self, event_system) -> Dict[EventType, Any]:
        """
        Register world-related event hooks.
        
        Returns:
            Dict mapping EventType to handler functions
        """
        return {
            EventType.LOCATION_ENTER: self._on_location_enter,
            EventType.LOCATION_LEAVE: self._on_location_leave,
            EventType.WEATHER_CHANGE: self._on_weather_change,
            EventType.TIME_CHANGE: self._on_time_change,
            EventType.PLAYER_MOVE: self._on_player_move,
        }
    
    def _on_location_enter(self, game, data):
        """Handle location entry"""
        location_id = data.get("location_id")
        locations = self._get_locations()
        
        if location_id in locations:
            loc = locations[location_id]
            self._exploration_count += 1
            
            # Check for secrets
            secrets = self._get_world_secrets()
            for secret_id, secret in secrets.items():
                if secret["location"] == location_id and secret_id not in self._discovered_secrets:
                    if random.random() < self._config["secret_discovery_chance"]:
                        self._discovered_secrets.add(secret_id)
                        print(f"\n🔍 SECRET DISCOVERED: {secret['name']}!")
                        print(f"   {secret['description']}")
            
            # Check for exploration rewards
            rewards = self.get_exploration_rewards()
            if self._exploration_count in rewards:
                reward = rewards[self._exploration_count]
                print(f"\n🎉 EXPLORATION MILESTONE: {reward['title']}!")
                if "stat_bonus" in reward:
                    print(f"   Bonus: {reward['stat_bonus']}")
    
    def _on_location_leave(self, game, data):
        """Handle location exit"""
        pass
    
    def _on_weather_change(self, game, data):
        """Handle weather changes"""
        weather = data.get("weather")
        
        # Weather effects on locations
        weather_effects = {
            Weather.STORM: "Lightning illuminates hidden paths.",
            Weather.FOG: "Mist conceals ancient secrets.",
            Weather.SNOW: "The cold reveals frozen treasures."
        }
        
        if weather in weather_effects:
            print(f"\n🌦️  {weather_effects[weather]}")
    
    def _on_time_change(self, game, data):
        """Handle time changes"""
        time = data.get("time")
        
        # Time-based events
        if time == TimeOfDay.NIGHT:
            print("\n🌙 The night reveals hidden dangers...")
    
    def _on_player_move(self, game, data):
        """Handle player movement"""
        pass
    
    def register_commands(self, command_system) -> Dict[str, Any]:
        """
        Register world-related commands.
        
        Returns:
            Dict mapping command names to handler info
        """
        return {
            "locations": {
                "handler": self._cmd_list_locations,
                "help": "List all extended locations",
                "category": "info"
            },
            "secrets": {
                "handler": self._cmd_list_secrets,
                "help": "List discovered and undiscovered secrets",
                "category": "info"
            },
            "events": {
                "handler": self._cmd_active_events,
                "help": "List active world events",
                "category": "info"
            },
            "exploration": {
                "handler": self._cmd_exploration,
                "help": "Show exploration progress",
                "category": "stats"
            },
            "world_config": {
                "handler": self._cmd_config,
                "help": "Configure world settings",
                "usage": "/world_config [key] [value]",
                "category": "config"
            }
        }
    
    def _cmd_list_locations(self, game, args, context) -> str:
        """List all locations"""
        locations = self._get_locations()
        
        # Group by type
        by_type: Dict[str, List] = {}
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
                level = loc.get("level_range", [1, 1])
                lines.append(f"  • {loc['name']}{hidden} (Lv.{level[0]}-{level[1]})")
        
        return "\n".join(lines)
    
    def _cmd_list_secrets(self, game, args, context) -> str:
        """List secrets"""
        secrets = self._get_world_secrets()
        
        lines = ["World Secrets:", "=" * 50]
        lines.append(f"Discovered: {len(self._discovered_secrets)}/{len(secrets)}")
        
        for secret_id, secret in secrets.items():
            discovered = "✓" if secret_id in self._discovered_secrets else "?"
            lines.append(f"  [{discovered}] {secret['name']} ({secret['location']})")
        
        return "\n".join(lines)
    
    def _cmd_active_events(self, game, args, context) -> str:
        """List world events"""
        events = self._get_world_events()
        
        lines = ["World Events:", "=" * 50]
        for event_id, event in events.items():
            lines.append(f"\n{event['name']}:")
            lines.append(f"  Type: {event['event_type']}")
            lines.append(f"  Duration: {event['duration'] if event['duration'] > 0 else 'Permanent'}")
            lines.append(f"  {event['description']}")
        
        return "\n".join(lines)
    
    def _cmd_exploration(self, game, args, context) -> str:
        """Show exploration progress"""
        rewards = self.get_exploration_rewards()
        
        lines = ["Exploration Progress:", "=" * 50]
        lines.append(f"Locations visited: {self._exploration_count}")
        lines.append("")
        
        for count, reward in sorted(rewards.items()):
            status = "✓" if self._exploration_count >= count else " "
            lines.append(f"[{status}] {count} locations: {reward['title']}")
            if "stat_bonus" in reward:
                lines.append(f"    Bonus: {reward['stat_bonus']}")
        
        return "\n".join(lines)
    
    def _cmd_config(self, game, args, context) -> str:
        """Configure world settings"""
        if not args:
            return f"World Config: {self._config}"
        
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
                value = float(value)
            except ValueError:
                pass
        
        old_value = self._config.get(key)
        self._config[key] = value
        
        return f"Set {key}: {old_value} -> {value}"
    
    def get_new_locations(self) -> Dict[str, Dict]:
        """
        Return new locations added by this plugin.
        
        Returns:
            Dict mapping location IDs to location data
        """
        return self._get_locations()
    
    def _get_locations(self) -> Dict[str, Dict]:
        """Get all location definitions"""
        return {
            # UNDERGROUND LOCATIONS
            "crystal_caverns": {
                "name": "Crystal Caverns",
                "description": "A vast underground network of caves filled with glowing crystals.",
                "location_type": "cave",
                "level_range": [5, 15],
                "connections": ["mining_town", "deep_mines"],
                "enemies": ["crystal_spider", "rock_elemental"],
                "resources": ["magic_crystal", "gemstone"],
                "features": ["crystal_formations", "underground_lake"],
                "hidden": False
            },
            "deep_mines": {
                "name": "Deep Mines",
                "description": "Abandoned mines that delve deep into the earth.",
                "location_type": "cave",
                "level_range": [8, 18],
                "connections": ["crystal_caverns"],
                "enemies": ["mine_spider", "undead_miner", "earth_elemental"],
                "resources": ["iron_ore", "gold_ore", "diamond"],
                "features": ["mine_shafts", "abandoned_equipment"],
                "hidden": False
            },
            "underground_city": {
                "name": "Underground City",
                "description": "A forgotten dwarven city deep beneath the mountains.",
                "location_type": "ruins",
                "level_range": [15, 25],
                "connections": ["deep_mines"],
                "enemies": ["dwarven_ghost", "underground_beast"],
                "resources": ["ancient_artifacts", "mithril"],
                "features": ["dwarven_forge", "throne_room", "treasury"],
                "hidden": True,
                "requirements": {"level": 15, "quest": "deep_delving"}
            },
            
            # MAGICAL LOCATIONS
            "fairy_grove": {
                "name": "Fairy Grove",
                "description": "An enchanted forest clearing where fairies dance.",
                "location_type": "forest",
                "level_range": [3, 12],
                "connections": ["whispering_woods"],
                "enemies": ["pixie", "forest_sprite"],
                "resources": ["fairy_dust", "enchanted_herbs"],
                "features": ["fairy_ring", "glowing_mushrooms"],
                "hidden": False
            },
            "mystic_sanctuary": {
                "name": "Mystic Sanctuary",
                "description": "A hidden sanctuary of magical learning.",
                "location_type": "temple",
                "level_range": [10, 20],
                "connections": ["capital_city"],
                "enemies": ["magical_guardian"],
                "resources": ["spell_tomes", "mana_crystals"],
                "features": ["library", "meditation_chambers", "portal_room"],
                "hidden": True,
                "requirements": {"magic_level": 5}
            },
            "elemental_plane": {
                "name": "Elemental Plane Nexus",
                "description": "A place where the elemental planes touch the mortal world.",
                "location_type": "special",
                "level_range": [20, 30],
                "connections": ["mystic_sanctuary"],
                "enemies": ["fire_elemental", "water_elemental", "air_elemental", "earth_elemental"],
                "resources": ["elemental_essence"],
                "features": ["elemental_portals", "nexus_crystal"],
                "hidden": True,
                "requirements": {"level": 20, "magic_level": 10}
            },
            
            # DARK LOCATIONS
            "shadow_forest": {
                "name": "Shadow Forest",
                "description": "A forest where light rarely penetrates.",
                "location_type": "forest",
                "level_range": [8, 18],
                "connections": ["deep_forest"],
                "enemies": ["shadow_wolf", "dark_spirit", "wraith"],
                "resources": ["shadow_essence", "dark_herbs"],
                "features": ["shadow_trees", "dark_altar"],
                "hidden": False
            },
            "cursed_ruins": {
                "name": "Cursed Ruins",
                "description": "Ancient ruins shrouded in dark magic.",
                "location_type": "ruins",
                "level_range": [12, 22],
                "connections": ["shadow_forest"],
                "enemies": ["cursed_knight", "necromancer", "undead_horde"],
                "resources": ["cursed_artifacts", "dark_crystals"],
                "features": ["cursed_throne", "necromantic_circle"],
                "hidden": False
            },
            "void_rift": {
                "name": "Void Rift",
                "description": "A tear in reality where void creatures emerge.",
                "location_type": "special",
                "level_range": [25, 35],
                "connections": ["cursed_ruins"],
                "enemies": ["void_beast", "reality_tear", "void_lord"],
                "resources": ["void_essence"],
                "features": ["unstable_ground", "reality_warp"],
                "hidden": True,
                "requirements": {"level": 25}
            },
            
            # SPECIAL LOCATIONS
            "dragon_peak": {
                "name": "Dragon's Peak",
                "description": "The highest mountain where dragons nest.",
                "location_type": "mountain",
                "level_range": [20, 30],
                "connections": ["mountain_pass"],
                "enemies": ["young_dragon", "drake", "ancient_dragon"],
                "resources": ["dragon_scale", "dragon_bone"],
                "features": ["dragon_nest", "treasure_hoard", "peak_shrine"],
                "hidden": False
            },
            "sky_temple": {
                "name": "Temple of the Sky",
                "description": "A floating temple accessible only to the worthy.",
                "location_type": "temple",
                "level_range": [18, 28],
                "connections": ["dragon_peak"],
                "enemies": ["sky_guardian", "cloud_serpent"],
                "resources": ["sky_crystals", "cloud_essence"],
                "features": ["floating_platforms", "wind_chambers"],
                "hidden": True,
                "requirements": {"level": 18, "reputation": "honored"}
            },
            "ancient_temple": {
                "name": "Temple of the Forgotten God",
                "description": "An ancient temple to a deity long forgotten.",
                "location_type": "temple",
                "level_range": [15, 25],
                "connections": ["desert_border"],
                "enemies": ["temple_guardian", "forgotten_priest", "ancient_construct"],
                "resources": ["holy_relics", "ancient_texts"],
                "features": ["main_chamber", "hidden_vault", "prayer_room"],
                "hidden": False
            },
            "desert_oasis": {
                "name": "Hidden Oasis",
                "description": "A secret oasis in the desert.",
                "location_type": "special",
                "level_range": [5, 15],
                "connections": ["desert_border"],
                "enemies": ["desert_bandit", "sand_worm"],
                "resources": ["water", "desert_herbs", "oasis_gems"],
                "features": ["palm_trees", "fresh_spring", "nomad_camp"],
                "hidden": True,
                "requirements": {"quest": "desert_guide"}
            }
        }
    
    def _get_world_secrets(self) -> Dict[str, Dict]:
        """Get all world secrets"""
        return {
            "dwarven_treasury": {
                "name": "Dwarven Treasury",
                "description": "The legendary treasury of the underground city.",
                "location": "underground_city",
                "discovery_method": "Find the hidden key in the throne room",
                "requirements": {"level": 20},
                "rewards": {"gold": 10000, "items": ["dwarven_crown"]}
            },
            "fairy_queen_grove": {
                "name": "Fairy Queen's Private Grove",
                "description": "A hidden section of the Fairy Grove.",
                "location": "fairy_grove",
                "discovery_method": "Dance in the fairy ring at midnight",
                "requirements": {"friendship": 100, "npc": "fairy_princess_aurora"},
                "rewards": {"blessing": "fae_luck", "items": ["fairy_queen_blessing"]}
            },
            "dragon_hoard_secret": {
                "name": "Secondary Dragon Hoard",
                "description": "A hidden cache of dragon treasure.",
                "location": "dragon_peak",
                "discovery_method": "Climb the hidden path behind the waterfall",
                "requirements": {"stealth": 15},
                "rewards": {"gold": 5000, "items": ["dragon_heart_gem"]}
            },
            "void_whispers": {
                "name": "Whispers of the Void",
                "description": "Ancient knowledge from beyond reality.",
                "location": "void_rift",
                "discovery_method": "Listen during a void storm",
                "requirements": {"magic_level": 15, "sanity": "high"},
                "rewards": {"spell": "void_magic", "knowledge": "cosmic_secrets"}
            }
        }
    
    def _get_world_events(self) -> Dict[str, Dict]:
        """Get all world events"""
        return {
            "crystal_surge": {
                "name": "Crystal Surge",
                "description": "Magic crystals are resonating with unusual power.",
                "event_type": "magical",
                "duration": 3,
                "effects": {
                    "magic_power": 1.5,
                    "crystal_drop_rate": 2.0
                },
                "locations": ["crystal_caverns", "mystic_sanctuary"],
                "conditions": {"random_chance": 0.1}
            },
            "dragon_awakening": {
                "name": "Dragon Awakening",
                "description": "Ancient dragons stir from their slumber.",
                "event_type": "dangerous",
                "duration": 5,
                "effects": {
                    "dragon_spawn_rate": 3.0,
                    "dragon_treasure": 2.0
                },
                "locations": ["dragon_peak"],
                "conditions": {"random_chance": 0.05}
            },
            "fairy_festival": {
                "name": "Fairy Moon Festival",
                "description": "The fairies celebrate with magical revelry.",
                "event_type": "festive",
                "duration": 2,
                "effects": {
                    "fairy_friendship_gain": 2.0,
                    "enchantment_success": 1.5
                },
                "locations": ["fairy_grove"],
                "conditions": {"time": "night", "moon_phase": "full"}
            },
            "void_instability": {
                "name": "Void Instability",
                "description": "Reality weakens as void energy surges.",
                "event_type": "dangerous",
                "duration": 3,
                "effects": {
                    "void_damage": 1.5,
                    "void_loot": 2.0
                },
                "locations": ["void_rift", "cursed_ruins"],
                "conditions": {"random_chance": 0.08}
            }
        }
    
    def get_exploration_rewards(self) -> Dict[int, Dict]:
        """
        Get exploration milestone rewards.
        
        Returns:
            Dict mapping location count to reward info
        """
        return {
            5: {
                "title": "Wanderer",
                "stat_bonus": {"wisdom": 1},
                "exp_bonus": 0.05
            },
            10: {
                "title": "Explorer",
                "stat_bonus": {"wisdom": 2, "luck": 1},
                "exp_bonus": 0.10
            },
            15: {
                "title": "Pathfinder",
                "stat_bonus": {"wisdom": 3, "luck": 2, "constitution": 1},
                "exp_bonus": 0.15
            },
            20: {
                "title": "World Walker",
                "stat_bonus": {"wisdom": 5, "luck": 3, "constitution": 2},
                "exp_bonus": 0.20
            }
        }


# Plugin instance - REQUIRED
plugin = ExtendedWorldPlugin()

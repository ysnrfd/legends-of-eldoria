"""
World System - Open World Exploration with Locations, NPCs, and Events
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any, Callable, Set, TYPE_CHECKING
from enum import Enum
import sys
import os
import random
import time
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.engine import (
    Entity, TimeOfDay, Weather, EventType, StatType,
    colored_text, print_border, pause, get_input
)

if TYPE_CHECKING:
    from core.character import Character


class LocationType(Enum):
    TOWN = "town"
    CITY = "city"
    VILLAGE = "village"
    DUNGEON = "dungeon"
    FOREST = "forest"
    MOUNTAIN = "mountain"
    DESERT = "desert"
    SWAMP = "swamp"
    CAVE = "cave"
    RUINS = "ruins"
    CASTLE = "castle"
    TEMPLE = "temple"
    SHOP = "shop"
    INN = "inn"
    WILDERNESS = "wilderness"
    SPECIAL = "special"


@dataclass
class Location:
    """Represents a location in the world"""
    id: str
    name: str
    description: str
    location_type: LocationType
    level_range: Tuple[int, int] = (1, 5)
    connections: List[str] = field(default_factory=list)
    npcs: List[str] = field(default_factory=list)
    shops: List[str] = field(default_factory=list)
    enemies: List[str] = field(default_factory=list)
    items: List[str] = field(default_factory=list)
    events: List[str] = field(default_factory=list)
    discovered: bool = False
    visited_count: int = 0
    danger_level: int = 1
    special_features: Dict[str, Any] = field(default_factory=dict)
    
    def get_description(self) -> str:
        """Get full location description"""
        lines = [
            f"\n{'='*60}",
            f"📍 {self.name}",
            f"{'='*60}",
            f"{self.description}",
            f"",
            f"Type: {self.location_type.value.title()}",
            f"Level Range: {self.level_range[0]}-{self.level_range[1]}",
            f"Danger Level: {'⚠️' * self.danger_level}",
        ]
        
        if self.discovered:
            lines.append(f"Visited: {self.visited_count} times")
        
        if self.connections:
            lines.append(f"\nConnected Locations: {', '.join(self.connections)}")
        
        if self.npcs:
            lines.append(f"NPCs Present: {len(self.npcs)}")
        
        if self.shops:
            lines.append(f"Shops Available: {len(self.shops)}")
        
        return "\n".join(lines)
    
    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "location_type": self.location_type.value,
            "level_range": self.level_range,
            "connections": self.connections,
            "npcs": self.npcs,
            "shops": self.shops,
            "enemies": self.enemies,
            "items": self.items,
            "events": self.events,
            "discovered": self.discovered,
            "visited_count": self.visited_count,
            "danger_level": self.danger_level,
            "special_features": self.special_features
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Location':
        return cls(
            id=data["id"],
            name=data["name"],
            description=data["description"],
            location_type=LocationType(data["location_type"]),
            level_range=tuple(data["level_range"]),
            connections=data.get("connections", []),
            npcs=data.get("npcs", []),
            shops=data.get("shops", []),
            enemies=data.get("enemies", []),
            items=data.get("items", []),
            events=data.get("events", []),
            discovered=data.get("discovered", False),
            visited_count=data.get("visited_count", 0),
            danger_level=data.get("danger_level", 1),
            special_features=data.get("special_features", {})
        )


@dataclass
class WorldEvent:
    """Random world events"""
    id: str
    name: str
    description: str
    event_type: str
    choices: List[Dict[str, Any]] = field(default_factory=list)
    rewards: Dict[str, Any] = field(default_factory=dict)
    requirements: Dict[str, Any] = field(default_factory=dict)
    one_time: bool = False
    triggered: bool = False


class WorldMap:
    """Manages the game world"""
    
    def __init__(self):
        self.locations: Dict[str, Location] = {}
        self.current_location: Optional[str] = None
        self.time_of_day: TimeOfDay = TimeOfDay.MORNING
        self.weather: Weather = Weather.CLEAR
        self.day: int = 1
        self.hour: int = 8
        self.events: Dict[str, WorldEvent] = {}
        self.discovered_locations: Set[str] = set()
        
        self._init_world()
    
    def _init_world(self):
        """Initialize the game world with locations"""
        # Create locations
        locations_data = [
            {
                "id": "start_village",
                "name": "Willowbrook Village",
                "description": "A peaceful farming village nestled in a green valley. "
                             "Simple cottages line dirt roads, and farmers tend to their fields. "
                             "The village square features a ancient oak tree where villagers gather.",
                "location_type": LocationType.VILLAGE,
                "level_range": (1, 3),
                "connections": ["forest_path", "main_road"],
                "npcs": ["elder_thorne", "blacksmith_gareth", "healer_rose", "merchant_finn"],
                "shops": ["village_shop", "blacksmith"],
                "danger_level": 0
            },
            {
                "id": "forest_path",
                "name": "Whispering Woods Path",
                "description": "A winding path through an ancient forest. Tall trees tower overhead, "
                             "their branches forming a canopy that filters the sunlight. "
                             "Strange sounds echo from the deeper woods.",
                "location_type": LocationType.FOREST,
                "level_range": (1, 5),
                "connections": ["start_village", "deep_forest", "ranger_outpost"],
                "enemies": ["wolf", "goblin", "boar"],
                "items": ["herb", "mushroom", "branch"],
                "danger_level": 2
            },
            {
                "id": "deep_forest",
                "name": "Deep Whispering Woods",
                "description": "The heart of the ancient forest. Here, the trees are oldest and tallest, "
                             "and the shadows are deepest. Ancient magic permeates the air. "
                             "Legends speak of a forgotten temple hidden somewhere within.",
                "location_type": LocationType.FOREST,
                "level_range": (5, 10),
                "connections": ["forest_path", "ancient_temple", "fairy_grove"],
                "enemies": ["wolf", "bear", "treant", "fairy"],
                "danger_level": 4
            },
            {
                "id": "main_road",
                "name": "King's Highway",
                "description": "A well-maintained road connecting the major settlements of the realm. "
                             "Merchants, travelers, and soldiers frequent this route. "
                             "Waystations offer rest for weary travelers.",
                "location_type": LocationType.WILDERNESS,
                "level_range": (1, 8),
                "connections": ["start_village", "capital_city", "mining_town", "crossroads"],
                "enemies": ["bandit", "wolf"],
                "danger_level": 1
            },
            {
                "id": "capital_city",
                "name": "Aurelia, Capital of the Realm",
                "description": "The magnificent capital city rises from the plains, its white walls "
                             "gleaming in the sun. The royal castle dominates the skyline, while "
                             "bustling markets, grand temples, and noble estates fill the city.",
                "location_type": LocationType.CITY,
                "level_range": (1, 20),
                "connections": ["main_road", "royal_castle", "sewers"],
                "npcs": ["king_aldric", "archmage_silas", "guild_master", "innkeeper_mara"],
                "shops": ["grand_market", "armory", "magic_shop", "alchemy_shop"],
                "danger_level": 0
            },
            {
                "id": "royal_castle",
                "name": "Castle Aurelius",
                "description": "The seat of royal power, this ancient castle has stood for centuries. "
                             "Its halls contain both great treasures and dark secrets. "
                             "The throne room awaits those with business for the king.",
                "location_type": LocationType.CASTLE,
                "level_range": (10, 20),
                "connections": ["capital_city", "royal_dungeons"],
                "npcs": ["king_aldric", "royal_guard_captain"],
                "danger_level": 0,
                "special_features": {"throne_room": True, "treasury": True}
            },
            {
                "id": "ancient_temple",
                "name": "Temple of the Forgotten God",
                "description": "An ancient temple dedicated to a god whose name has been lost to time. "
                             "Crumbled pillars and faded murals hint at forgotten glories. "
                             "A dark presence lurks in the inner sanctum.",
                "location_type": LocationType.TEMPLE,
                "level_range": (10, 15),
                "connections": ["deep_forest"],
                "enemies": ["skeleton", "ghost", "cultist", "temple_guardian"],
                "danger_level": 5,
                "special_features": {"boss": "forgotten_priest", "treasure": True}
            },
            {
                "id": "mining_town",
                "name": "Irondeep Mining Town",
                "description": "A rugged town built around the entrance to vast mines. "
                             "Miners, smiths, and merchants fill the streets. "
                             "The constant ringing of pickaxes echoes from the mountains.",
                "location_type": LocationType.TOWN,
                "level_range": (5, 12),
                "connections": ["main_road", "mountain_pass", "deep_mines"],
                "npcs": ["mine_foreman", "dwarf_smith", "prospector"],
                "shops": ["mine_shop", "dwarf_smithy"],
                "danger_level": 1
            },
            {
                "id": "mountain_pass",
                "name": "Highrock Pass",
                "description": "A treacherous mountain pass winds between snow-capped peaks. "
                             "The air is thin and cold. Ancient watchtowers stand guard "
                             "against threats from beyond the mountains.",
                "location_type": LocationType.MOUNTAIN,
                "level_range": (8, 15),
                "connections": ["mining_town", "northern_realm", "dragon_peak"],
                "enemies": ["mountain_troll", "harpy", "ice_elemental"],
                "danger_level": 4
            },
            {
                "id": "dragon_peak",
                "name": "Dragon's Peak",
                "description": "The highest mountain in the realm, legendary as the lair of dragons. "
                             "Scorched earth and ancient bones litter the slopes. "
                             "Those who dare enter face certain death - or legendary treasure.",
                "location_type": LocationType.MOUNTAIN,
                "level_range": (20, 30),
                "connections": ["mountain_pass"],
                "enemies": ["dragon_wyrmling", "dragon"],
                "danger_level": 5,
                "special_features": {"boss": "ancient_dragon", "legendary_treasure": True}
            },
            {
                "id": "swamp_lands",
                "name": "Murkmire Swamp",
                "description": "A vast, misty swamp where the ground is never solid. "
                             "Twisted trees rise from murky waters, and strange lights "
                             "dance in the darkness. Many have entered, few have returned.",
                "location_type": LocationType.SWAMP,
                "level_range": (5, 12),
                "connections": ["crossroads", "witch_hut"],
                "enemies": ["swamp_creature", "witch", "crocodile", "will_o_wisp"],
                "danger_level": 3
            },
            {
                "id": "crossroads",
                "name": "Four Ways Crossroads",
                "description": "Where four major roads meet, a small settlement has grown. "
                             "An ancient inn offers shelter, and a mysterious statue stands "
                             "at the center, said to grant boons to the worthy.",
                "location_type": LocationType.WILDERNESS,
                "level_range": (1, 10),
                "connections": ["main_road", "swamp_lands", "desert_border", "ruined_kingdom"],
                "npcs": ["innkeeper", "wandering_merchant", "mysterious_stranger"],
                "shops": ["crossroads_inn"],
                "danger_level": 1
            },
            {
                "id": "desert_border",
                "name": "Scorchfire Desert Edge",
                "description": "Where the fertile lands meet the endless desert. "
                             "Sand dunes stretch to the horizon under a blazing sun. "
                             "Ancient ruins are sometimes uncovered by the shifting sands.",
                "location_type": LocationType.DESERT,
                "level_range": (10, 18),
                "connections": ["crossroads", "desert_oasis", "sand_temple"],
                "enemies": ["scorpion", "sand_worm", "desert_raider"],
                "danger_level": 3
            },
            {
                "id": "dungeon_depths",
                "name": "The Endless Dungeon",
                "description": "An ancient dungeon of unknown origin, said to descend infinitely. "
                             "Each floor holds greater challenges and greater treasures. "
                             "Only the bravest adventurers dare to plumb its depths.",
                "location_type": LocationType.DUNGEON,
                "level_range": (1, 50),
                "connections": ["capital_city"],
                "enemies": ["skeleton", "goblin", "orc", "troll", "demon", "boss_monster"],
                "danger_level": 5,
                "special_features": {"infinite_dungeon": True, "floor": 1}
            },
            {
                "id": "fairy_grove",
                "name": "Enchanted Fairy Grove",
                "description": "A hidden glen where fairies dance under eternal moonlight. "
                             "Beautiful flowers bloom everywhere, and the air shimmers with magic. "
                             "The fairies may grant wishes - for a price.",
                "location_type": LocationType.SPECIAL,
                "level_range": (1, 10),
                "connections": ["deep_forest"],
                "npcs": ["fairy_queen"],
                "danger_level": 0,
                "special_features": {"wishing_well": True, "fairy_blessing": True}
            },
            {
                "id": "ruined_kingdom",
                "name": "Ruins of Valdris",
                "description": "The remains of an ancient kingdom destroyed in a great cataclysm. "
                             "Crumbling towers and shattered palaces speak of former glory. "
                             "Undead horrors now stalk these haunted ruins.",
                "location_type": LocationType.RUINS,
                "level_range": (15, 25),
                "connections": ["crossroads"],
                "enemies": ["skeleton", "ghost", "wraith", "lich"],
                "danger_level": 5,
                "special_features": {"boss": "ancient_lich", "legendary_treasure": True}
            }
        ]
        
        for loc_data in locations_data:
            location = Location(
                id=loc_data["id"],
                name=loc_data["name"],
                description=loc_data["description"],
                location_type=loc_data["location_type"],
                level_range=loc_data["level_range"],
                connections=loc_data.get("connections", []),
                npcs=loc_data.get("npcs", []),
                shops=loc_data.get("shops", []),
                enemies=loc_data.get("enemies", []),
                items=loc_data.get("items", []),
                events=loc_data.get("events", []),
                danger_level=loc_data.get("danger_level", 1),
                special_features=loc_data.get("special_features", {})
            )
            self.locations[location.id] = location
        
        # Set starting location
        self.current_location = "start_village"
        self.locations["start_village"].discovered = True
        self.discovered_locations.add("start_village")
        
        # Initialize world events
        self._init_events()
    
    def _init_events(self):
        """Initialize random world events"""
        events_data = [
            {
                "id": "merchant_caravan",
                "name": "Merchant Caravan",
                "description": "A merchant caravan has stopped nearby. They offer rare goods at special prices.",
                "event_type": "shop",
                "choices": [
                    {"text": "Trade with the merchants", "effect": "open_shop"},
                    {"text": "Rob the caravan", "effect": "combat", "enemies": ["bandit", "bandit", "merchant_guard"]},
                    {"text": "Leave", "effect": "nothing"}
                ]
            },
            {
                "id": "treasure_chest",
                "name": "Mysterious Chest",
                "description": "You discover an ornate chest partially buried. It might be trapped.",
                "event_type": "treasure",
                "choices": [
                    {"text": "Open it carefully", "effect": "treasure", "trap_chance": 0.3},
                    {"text": "Smash it open", "effect": "treasure", "trap_chance": 0.6},
                    {"text": "Leave it", "effect": "nothing"}
                ],
                "rewards": {"gold": (50, 200), "item_chance": 0.5}
            },
            {
                "id": "wounded_traveler",
                "name": "Wounded Traveler",
                "description": "A wounded traveler lies by the path. They seem to be in distress.",
                "event_type": "social",
                "choices": [
                    {"text": "Help them", "effect": "heal", "karma": 5},
                    {"text": "Rob them", "effect": "steal", "karma": -10},
                    {"text": "Leave them", "effect": "nothing"}
                ],
                "rewards": {"gold": 20, "reputation": 5}
            },
            {
                "id": "fairy_circle",
                "name": "Fairy Circle",
                "description": "A perfect ring of mushrooms glows with an otherworldly light.",
                "event_type": "magic",
                "choices": [
                    {"text": "Step inside", "effect": "teleport"},
                    {"text": "Make a wish", "effect": "wish"},
                    {"text": "Leave", "effect": "nothing"}
                ],
                "one_time": True
            },
            {
                "id": "ancient_shrine",
                "name": "Ancient Shrine",
                "description": "An ancient shrine to a forgotten deity. The stone altar still emanates power.",
                "event_type": "blessing",
                "choices": [
                    {"text": "Pray at the shrine", "effect": "blessing"},
                    {"text": "Desecrate it", "effect": "curse"},
                    {"text": "Take the offerings", "effect": "gold", "karma": -5}
                ]
            },
            {
                "id": "mysterious_portal",
                "name": "Mysterious Portal",
                "description": "A swirling portal of energy hovers in the air. Who knows where it leads?",
                "event_type": "special",
                "choices": [
                    {"text": "Enter the portal", "effect": "portal"},
                    {"text": "Dispel it", "effect": "dispel"},
                    {"text": "Leave", "effect": "nothing"}
                ],
                "requirements": {"level": 10}
            }
        ]
        
        for event_data in events_data:
            event = WorldEvent(
                id=event_data["id"],
                name=event_data["name"],
                description=event_data["description"],
                event_type=event_data["event_type"],
                choices=event_data.get("choices", []),
                rewards=event_data.get("rewards", {}),
                requirements=event_data.get("requirements", {}),
                one_time=event_data.get("one_time", False)
            )
            self.events[event.id] = event
    
    def get_current_location(self) -> Optional[Location]:
        """Get current location object"""
        return self.locations.get(self.current_location)
    
    def travel_to(self, location_id: str, player: 'Character') -> Tuple[bool, str]:
        """Travel to a location"""
        current = self.get_current_location()
        if not current:
            return False, "You are nowhere."
        
        if location_id not in current.connections:
            return False, "Cannot travel there from here."
        
        destination = self.locations.get(location_id)
        if not destination:
            return False, "Location does not exist."
        
        # Check level requirement
        if player.level < destination.level_range[0]:
            return False, f"This area is too dangerous for you (Recommended level: {destination.level_range[0]})."
        
        # Move player
        old_location = current.id
        self.current_location = location_id
        
        # Mark as discovered
        destination.discovered = True
        destination.visited_count += 1
        self.discovered_locations.add(location_id)
        player.position = location_id
        
        # Advance time
        self.advance_time(1)
        
        return True, f"Traveled to {destination.name}."
    
    def advance_time(self, hours: int = 1):
        """Advance game time"""
        self.hour += hours
        
        while self.hour >= 24:
            self.hour -= 24
            self.day += 1
        
        # Update time of day
        if 5 <= self.hour < 7:
            self.time_of_day = TimeOfDay.DAWN
        elif 7 <= self.hour < 12:
            self.time_of_day = TimeOfDay.MORNING
        elif self.hour == 12:
            self.time_of_day = TimeOfDay.NOON
        elif 13 <= self.hour < 17:
            self.time_of_day = TimeOfDay.AFTERNOON
        elif 17 <= self.hour < 20:
            self.time_of_day = TimeOfDay.DUSK
        elif 20 <= self.hour < 24:
            self.time_of_day = TimeOfDay.EVENING
        elif 0 <= self.hour < 5:
            self.time_of_day = TimeOfDay.NIGHT
        else:
            self.time_of_day = TimeOfDay.MIDNIGHT
        
        # Random weather change
        if random.random() < 0.1:
            self.weather = random.choice(list(Weather))
    
    def get_random_event(self) -> Optional[WorldEvent]:
        """Get a random event that can trigger"""
        available_events = [
            event for event in self.events.values()
            if not event.triggered or not event.one_time
        ]
        
        if not available_events or random.random() > 0.15:
            return None
        
        return random.choice(available_events)
    
    def explore(self, player: 'Character') -> Tuple[List[str], Optional[Any]]:
        """Explore current location for events, items, or enemies"""
        location = self.get_current_location()
        if not location:
            return ["You cannot explore here."], None
        
        messages = []
        encounter = None
        
        # Chance for random event
        event = self.get_random_event()
        if event:
            messages.append(f"\n{'='*50}")
            messages.append(f"EVENT: {event.name}")
            messages.append(f"{'='*50}")
            messages.append(event.description)
            return messages, event
        
        # Chance for enemy encounter
        if location.enemies and random.random() < 0.3 + (location.danger_level * 0.1):
            from systems.combat import EnemyFactory
            
            enemy_template = random.choice(location.enemies)
            enemy_level = random.randint(*location.level_range)
            enemy = EnemyFactory.create_enemy(enemy_template, enemy_level)
            
            if enemy:
                messages.append(f"\n⚔️ You encountered a {enemy.name}!")
                encounter = enemy
                return messages, encounter
        
        # Chance to find items
        if location.items and random.random() < 0.2:
            from core.items import get_item
            
            item_template = random.choice(location.items)
            item = get_item(item_template)
            
            if item:
                messages.append(f"\n📦 You found: {item.name}!")
                return messages, item
        
        # Nothing found
        messages.append("\nYou explore the area but find nothing of interest.")
        messages.append("The area seems peaceful for now.")
        
        return messages, None
    
    def get_time_display(self) -> str:
        """Get formatted time display"""
        period_emoji = {
            TimeOfDay.DAWN: "🌅",
            TimeOfDay.MORNING: "☀️",
            TimeOfDay.NOON: "🌞",
            TimeOfDay.AFTERNOON: "🌤️",
            TimeOfDay.DUSK: "🌇",
            TimeOfDay.EVENING: "🌙",
            TimeOfDay.NIGHT: "🌑",
            TimeOfDay.MIDNIGHT: "🌙"
        }
        
        weather_emoji = {
            Weather.CLEAR: "☀️",
            Weather.CLOUDY: "☁️",
            Weather.RAIN: "🌧️",
            Weather.STORM: "⛈️",
            Weather.SNOW: "❄️",
            Weather.FOG: "🌫️",
            Weather.SANDSTORM: "🌪️",
            Weather.BLOOD_MOON: "🔴",
            Weather.AURORA: "🌌"
        }
        
        hour_12 = self.hour % 12
        if hour_12 == 0:
            hour_12 = 12
        am_pm = "AM" if self.hour < 12 else "PM"
        
        return f"Day {self.day} | {hour_12}:00 {am_pm} | {period_emoji[self.time_of_day]} {self.time_of_day.value} | {weather_emoji[self.weather]} {self.weather.value}"
    
    def register_location(self, loc_data: Dict[str, Any]) -> bool:
        """Register a new location from plugin data"""
        try:
            location = Location(
                id=loc_data["id"],
                name=loc_data["name"],
                description=loc_data["description"],
                location_type=LocationType(loc_data.get("location_type", "wilderness")),
                level_range=tuple(loc_data.get("level_range", (1, 5))),
                connections=loc_data.get("connections", []),
                npcs=loc_data.get("npcs", []),
                shops=loc_data.get("shops", []),
                enemies=loc_data.get("enemies", []),
                items=loc_data.get("items", []),
                events=loc_data.get("events", []),
                danger_level=loc_data.get("danger_level", 1),
                special_features=loc_data.get("special_features", {})
            )
            
            self.locations[location.id] = location
            print(f"  [Extended World] Registered location: {location.name}")
            return True
            
        except Exception as e:
            print(f"  [Extended World] Error registering location {loc_data.get('id', 'unknown')}: {e}")
            return False
    
    def register_locations(self, locations_data: Dict[str, Dict[str, Any]]) -> int:
        """Register multiple locations from plugin data. Returns count of successful registrations."""
        count = 0
        for loc_id, loc_data in locations_data.items():
            loc_data["id"] = loc_id
            if self.register_location(loc_data):
                count += 1
        
        # Update connections for existing locations
        for loc_id, loc_data in locations_data.items():
            for connected_id in loc_data.get("connections", []):
                if connected_id in self.locations:
                    if loc_id not in self.locations[connected_id].connections:
                        self.locations[connected_id].connections.append(loc_id)
        
        return count
    
    def get_map_display(self) -> str:
        """Get map of discovered locations"""
        lines = [
            f"\n{'='*60}",
            "WORLD MAP",
            f"{'='*60}",
            f"{self.get_time_display()}",
            f"",
            "Discovered Locations:",
        ]
        
        for loc_id in self.discovered_locations:
            location = self.locations.get(loc_id)
            if location:
                current_marker = "📍 " if loc_id == self.current_location else "   "
                danger = "⚠️" * location.danger_level if location.danger_level > 0 else ""
                lines.append(f"{current_marker}{location.name} (Lv.{location.level_range[0]}-{location.level_range[1]}) {danger}")
        
        return "\n".join(lines)
    
    def to_dict(self) -> Dict:
        return {
            "locations": {k: v.to_dict() for k, v in self.locations.items()},
            "current_location": self.current_location,
            "time_of_day": self.time_of_day.value,
            "weather": self.weather.value,
            "day": self.day,
            "hour": self.hour,
            "discovered_locations": list(self.discovered_locations)
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'WorldMap':
        world = cls.__new__(cls)
        world.locations = {
            k: Location.from_dict(v) for k, v in data["locations"].items()
        }
        world.current_location = data["current_location"]
        world.time_of_day = TimeOfDay(data["time_of_day"])
        world.weather = Weather(data["weather"])
        world.day = data["day"]
        world.hour = data["hour"]
        world.discovered_locations = set(data.get("discovered_locations", []))
        world.events = {}
        world._init_events()
        return world


print("World system loaded successfully!")

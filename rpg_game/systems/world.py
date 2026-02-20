"""
World System - Open World Exploration with Locations, NPCs, and Events

Author: YSNRFD
Version: 1.0.0
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any, Callable, Set, TYPE_CHECKING
from enum import Enum
import sys
import os
import random
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.engine import (
    TimeOfDay, Weather
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
    """A world event that can occur"""
    id: str
    name: str
    description: str
    event_type: str
    choices: List[Dict[str, Any]] = field(default_factory=list)
    rewards: Dict[str, Any] = field(default_factory=dict)
    one_time: bool = False
    triggered: bool = False
    condition: Optional[Callable] = None
    
    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "event_type": self.event_type,
            "choices": self.choices,
            "rewards": self.rewards,
            "one_time": self.one_time,
            "triggered": self.triggered
        }


class WorldMap:
    """Manages the game world"""
    
    def __init__(self):
        self.locations: Dict[str, Location] = {}
        self.current_location: str = "start_village"
        self.time_of_day: TimeOfDay = TimeOfDay.MORNING
        self.weather: Weather = Weather.CLEAR
        self.day: int = 1
        self.hour: int = 8
        self.discovered_locations: Set[str] = set()
        self.events: Dict[str, WorldEvent] = {}
        
        self._init_world()
    
    def _init_world(self):
        """Initialize default world locations"""
        default_locations = {
            "start_village": Location(
                id="start_village",
                name="Willowbrook Village",
                description="A peaceful village surrounded by willow trees. The air smells of fresh bread and woodsmoke.",
                location_type=LocationType.VILLAGE,
                level_range=(1, 3),
                connections=["forest_edge", "trade_road"],
                npcs=["village_elder", "village_merchant", "village_guard", "mysterious_stranger"],
                danger_level=0
            ),
            "forest_edge": Location(
                id="forest_edge",
                name="Whispering Woods",
                description="Ancient trees whisper secrets to those who listen. The forest is dark and foreboding.",
                location_type=LocationType.FOREST,
                level_range=(1, 5),
                connections=["start_village", "deep_forest", "ruins"],
                enemies=["goblin", "wolf"],
                danger_level=2
            ),
            "deep_forest": Location(
                id="deep_forest",
                name="Deep Forest",
                description="The trees grow thicker here, blocking out most sunlight. Strange sounds echo from the shadows.",
                location_type=LocationType.FOREST,
                level_range=(3, 8),
                connections=["forest_edge", "cave_entrance"],
                enemies=["goblin", "wolf", "orc_warrior"],
                danger_level=3
            ),
            "cave_entrance": Location(
                id="cave_entrance",
                name="Dark Cave",
                description="A gaping maw in the earth leads into darkness. The air smells of damp stone and something... else.",
                location_type=LocationType.CAVE,
                level_range=(5, 10),
                connections=["deep_forest", "underground_ruins"],
                enemies=["skeleton", "dark_mage"],
                danger_level=4
            ),
            "ruins": Location(
                id="ruins",
                name="Ancient Ruins",
                description="Crumbling stone structures hint at a once-great civilization. Now only monsters dwell here.",
                location_type=LocationType.RUINS,
                level_range=(5, 12),
                connections=["forest_edge", "temple"],
                enemies=["skeleton", "dark_mage", "troll"],
                danger_level=4
            ),
            "temple": Location(
                id="temple",
                name="Forgotten Temple",
                description="An ancient temple to forgotten gods. Dark energy pulses from within.",
                location_type=LocationType.TEMPLE,
                level_range=(10, 20),
                connections=["ruins"],
                enemies=["dark_mage", "vampire"],
                danger_level=5
            ),
            "trade_road": Location(
                id="trade_road",
                name="Merchant's Road",
                description="A well-traveled road connecting villages and towns. Bandits sometimes lurk here.",
                location_type=LocationType.WILDERNESS,
                level_range=(2, 6),
                connections=["start_village", "capital_city"],
                enemies=["wolf"],
                danger_level=1
            ),
            "capital_city": Location(
                id="capital_city",
                name="Aldor Capital",
                description="The grand capital city of the realm. Towers of white stone reach for the sky.",
                location_type=LocationType.CITY,
                level_range=(5, 20),
                connections=["trade_road", "mountain_pass"],
                npcs=["king", "royal_merchant", "guild_master"],
                shops=["royal_armory", "magic_emporium", "general_store"],
                danger_level=0
            ),
            "mountain_pass": Location(
                id="mountain_pass",
                name="Dragon's Pass",
                description="A treacherous mountain path. Legends say dragons nest in the peaks above.",
                location_type=LocationType.MOUNTAIN,
                level_range=(15, 30),
                connections=["capital_city", "dragon_peak"],
                enemies=["troll", "dragon_wyrmling"],
                danger_level=5
            ),
            "dragon_peak": Location(
                id="dragon_peak",
                name="Dragon's Peak",
                description="The highest peak in the realm. An ancient dragon is said to dwell in a cave here.",
                location_type=LocationType.MOUNTAIN,
                level_range=(25, 50),
                connections=["mountain_pass"],
                enemies=["dragon_wyrmling", "ancient_dragon"],
                danger_level=5
            ),
            "underground_ruins": Location(
                id="underground_ruins",
                name="Deep Ruins",
                description="Ancient catacombs beneath the earth. Undead horrors stalk these halls.",
                location_type=LocationType.RUINS,
                level_range=(10, 25),
                connections=["cave_entrance"],
                enemies=["skeleton", "vampire", "demon"],
                danger_level=5
            )
        }
        
        for loc_id, location in default_locations.items():
            self.locations[loc_id] = location
        
        # Mark starting location as discovered
        self.discovered_locations.add("start_village")
        self.locations["start_village"].discovered = True
        
        # Initialize events
        self._init_events()
    
    def _init_events(self):
        """Initialize world events"""
        self.events = {
            "abandoned_chest": WorldEvent(
                id="abandoned_chest",
                name="Abandoned Chest",
                description="You discover an old chest half-buried in the dirt. It might contain valuables... or danger.",
                event_type="treasure",
                choices=[
                    {"text": "Open it carefully", "effect": "treasure"},
                    {"text": "Leave it alone", "effect": "nothing"},
                    {"text": "Smash it open", "effect": "trap"}
                ],
                rewards={"gold": (10, 50), "item_chance": 0.3}
            ),
            "wandering_merchant": WorldEvent(
                id="wandering_merchant",
                name="Wandering Merchant",
                description="A traveling merchant has set up a temporary camp. He offers rare goods at inflated prices.",
                event_type="shop",
                choices=[
                    {"text": "Browse his wares", "effect": "open_shop"},
                    {"text": "Decline and move on", "effect": "nothing"}
                ]
            ),
            "injured_traveler": WorldEvent(
                id="injured_traveler",
                name="Injured Traveler",
                description="You find a wounded traveler by the roadside. They beg for help.",
                event_type="choice",
                choices=[
                    {"text": "Heal them", "effect": "heal"},
                    {"text": "Rob them", "effect": "evil"},
                    {"text": "Move on", "effect": "nothing"}
                ],
                rewards={"friendship": 10, "experience": 50}
            ),
            "mysterious_shrine": WorldEvent(
                id="mysterious_shrine",
                name="Mysterious Shrine",
                description="An ancient shrine stands before you, pulsing with magical energy.",
                event_type="choice",
                choices=[
                    {"text": "Pray at the shrine", "effect": "blessing"},
                    {"text": "Study the magic", "effect": "knowledge"},
                    {"text": "Destroy it", "effect": "curse"}
                ],
                one_time=True
            ),
            "portal": WorldEvent(
                id="portal",
                name="Unstable Portal",
                description="A shimmering portal hovers in the air. Its destination is unknown.",
                event_type="choice",
                choices=[
                    {"text": "Step through", "effect": "portal"},
                    {"text": "Leave it alone", "effect": "nothing"}
                ],
                one_time=True
            ),
            "ambush": WorldEvent(
                id="ambush",
                name="Ambush!",
                description="Enemies leap from hiding! You must fight or flee!",
                event_type="combat",
                choices=[
                    {"text": "Fight!", "effect": "combat", "enemies": ["goblin", "goblin"]},
                    {"text": "Flee!", "effect": "flee"}
                ]
            )
        }
    
    def get_current_location(self) -> Optional[Location]:
        """Get the current location"""
        return self.locations.get(self.current_location)
    
    def travel_to(self, location_id: str, player: 'Character') -> Tuple[bool, str]:
        """Travel to a new location"""
        if location_id not in self.locations:
            return False, "Location does not exist."
        
        current = self.get_current_location()
        if current and location_id not in current.connections:
            return False, "You cannot travel there from here."
        
        # Update current location
        self.current_location = location_id
        location = self.locations[location_id]
        
        # Mark as discovered
        if not location.discovered:
            location.discovered = True
            self.discovered_locations.add(location_id)
            message = f"Discovered: {location.name}!"
        else:
            message = f"Traveled to: {location.name}"
        
        location.visited_count += 1
        
        # Advance time
        self.advance_time(1)
        
        return True, message
    
    def explore(self, player: 'Character') -> Tuple[List[str], Optional[Any]]:
        """Explore the current location"""
        location = self.get_current_location()
        messages = []
        encounter = None
        
        if not location:
            return ["You are nowhere."], None
        
        # Check for random encounters based on danger level
        if location.danger_level > 0:
            encounter_chance = location.danger_level * 0.2
            
            if random.random() < encounter_chance:
                # Generate encounter
                from systems.combat import EnemyFactory
                enemy_level = random.randint(location.level_range[0], location.level_range[1])
                enemy = EnemyFactory.get_random_enemy(
                    min_level=max(1, enemy_level - 2),
                    max_level=enemy_level + 2
                )
                if enemy:
                    messages.append(f"You encounter a {enemy.name}!")
                    encounter = enemy
                    return messages, encounter
        
        # Check for events
        if location.events and random.random() < 0.3:
            event_id = random.choice(location.events)
            event = self.events.get(event_id)
            if event and (not event.one_time or not event.triggered):
                messages.append(f"Event: {event.name}")
                encounter = event
                return messages, encounter
        
        # Random findings
        findings = [
            "You find some interesting plants.",
            "You discover old tracks.",
            "You find a hidden cache of supplies.",
            "You spot wildlife in the distance.",
            "You find nothing of interest."
        ]
        messages.append(random.choice(findings))
        
        # Small chance to find gold
        if random.random() < 0.2:
            gold = random.randint(1, 10) * location.danger_level
            player.add_gold(gold)
            messages.append(f"You found {gold} gold!")
        
        return messages, encounter
    
    def advance_time(self, hours: int = 1):
        """Advance game time"""
        self.hour += hours
        
        while self.hour >= 24:
            self.hour -= 24
            self.day += 1
        
        # Update time of day
        if 5 <= self.hour < 8:
            self.time_of_day = TimeOfDay.DAWN
        elif 8 <= self.hour < 12:
            self.time_of_day = TimeOfDay.MORNING
        elif 12 <= self.hour < 14:
            self.time_of_day = TimeOfDay.NOON
        elif 14 <= self.hour < 18:
            self.time_of_day = TimeOfDay.AFTERNOON
        elif 18 <= self.hour < 20:
            self.time_of_day = TimeOfDay.DUSK
        elif 20 <= self.hour < 24:
            self.time_of_day = TimeOfDay.NIGHT
        else:
            self.time_of_day = TimeOfDay.MIDNIGHT
        
        # Random weather change
        if random.random() < 0.1:
            self.weather = random.choice(list(Weather))
    
    def get_time_display(self) -> str:
        """Get time and weather display"""
        time_icons = {
            TimeOfDay.DAWN: "🌅",
            TimeOfDay.MORNING: "☀️",
            TimeOfDay.NOON: "☀️",
            TimeOfDay.AFTERNOON: "🌤️",
            TimeOfDay.DUSK: "🌆",
            TimeOfDay.NIGHT: "🌙",
            TimeOfDay.MIDNIGHT: "🌙"
        }
        
        weather_icons = {
            Weather.CLEAR: "☀️",
            Weather.CLOUDY: "☁️",
            Weather.RAIN: "🌧️",
            Weather.STORM: "⛈️",
            Weather.SNOW: "🌨️",
            Weather.FOG: "🌫️",
            Weather.WINDY: "💨"
        }
        
        icon = time_icons.get(self.time_of_day, "⏰")
        weather_icon = weather_icons.get(self.weather, "🌡️")
        
        return f"{icon} Day {self.day}, {self.time_of_day.value.title()} | {weather_icon} {self.weather.value.title()}"
    
    def register_location(self, location_data: Dict[str, Any]) -> bool:
        """Register a new location from plugin data"""
        try:
            location = Location.from_dict(location_data)
            self.locations[location.id] = location
            return True
        except Exception as e:
            print(f"Error registering location: {e}")
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

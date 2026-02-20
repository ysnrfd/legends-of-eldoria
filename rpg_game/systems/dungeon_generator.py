"""
Random Dungeon Generator - Procedurally generated dungeons

Author: YSNRFD
Version: 1.0.0
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any, Set, TYPE_CHECKING
from enum import Enum
import random
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.engine import Rarity, colored_text, clear_screen
from systems.combat import EnemyFactory

if TYPE_CHECKING:
    from core.character import Character


class RoomType(Enum):
    """Types of dungeon rooms"""
    EMPTY = "empty"
    COMBAT = "combat"
    TREASURE = "treasure"
    TRAP = "trap"
    REST = "rest"
    BOSS = "boss"
    SHRINE = "shrine"
    PUZZLE = "puzzle"
    SHOP = "shop"
    EXIT = "exit"


class DungeonTheme(Enum):
    """Dungeon themes"""
    CRYPT = "crypt"
    CAVERN = "cavern"
    RUINS = "ruins"
    PRISON = "prison"
    TEMPLE = "temple"
    FOREST = "forest"
    VOLCANO = "volcano"
    ICE = "ice"
    VOID = "void"


@dataclass
class DungeonRoom:
    """A room in the dungeon"""
    x: int
    y: int
    room_type: RoomType
    visited: bool = False
    cleared: bool = False
    connections: List[Tuple[int, int]] = field(default_factory=list)
    enemies: List[str] = field(default_factory=list)
    loot: List[str] = field(default_factory=list)
    trap_difficulty: int = 0
    description: str = ""
    special_event: Optional[str] = None
    
    def get_display_symbol(self) -> str:
        """Get symbol for map display"""
        if not self.visited:
            return "?"
        symbols = {
            RoomType.EMPTY: "·",
            RoomType.COMBAT: "⚔",
            RoomType.TREASURE: "💰",
            RoomType.TRAP: "💀",
            RoomType.REST: "🛏",
            RoomType.BOSS: "👹",
            RoomType.SHRINE: "⛩",
            RoomType.PUZZLE: "❓",
            RoomType.SHOP: "🏪",
            RoomType.EXIT: "🚪"
        }
        return symbols.get(self.room_type, "?")
    
    def to_dict(self) -> Dict:
        return {
            "x": self.x,
            "y": self.y,
            "room_type": self.room_type.value,
            "visited": self.visited,
            "cleared": self.cleared,
            "connections": self.connections,
            "enemies": self.enemies,
            "loot": self.loot,
            "trap_difficulty": self.trap_difficulty,
            "description": self.description,
            "special_event": self.special_event
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'DungeonRoom':
        return cls(
            x=data["x"],
            y=data["y"],
            room_type=RoomType(data["room_type"]),
            visited=data.get("visited", False),
            cleared=data.get("cleared", False),
            connections=data.get("connections", []),
            enemies=data.get("enemies", []),
            loot=data.get("loot", []),
            trap_difficulty=data.get("trap_difficulty", 0),
            description=data.get("description", ""),
            special_event=data.get("special_event")
        )


@dataclass
class DungeonFloor:
    """A floor in the dungeon"""
    floor_number: int
    rooms: Dict[Tuple[int, int], DungeonRoom] = field(default_factory=dict)
    player_position: Tuple[int, int] = (0, 0)
    size: int = 5
    theme: DungeonTheme = DungeonTheme.CRYPT
    difficulty: int = 1
    cleared: bool = False
    
    def get_room(self, x: int, y: int) -> Optional[DungeonRoom]:
        """Get room at coordinates"""
        return self.rooms.get((x, y))
    
    def get_current_room(self) -> Optional[DungeonRoom]:
        """Get room at player position"""
        return self.get_room(self.player_position[0], self.player_position[1])
    
    def move_player(self, direction: str) -> Tuple[bool, str]:
        """Move player in a direction"""
        x, y = self.player_position
        dx, dy = 0, 0
        
        if direction == "north":
            dy = -1
        elif direction == "south":
            dy = 1
        elif direction == "east":
            dx = 1
        elif direction == "west":
            dx = -1
        else:
            return False, "Invalid direction."
        
        new_x, new_y = x + dx, y + dy
        
        # Check if room exists
        if (new_x, new_y) not in self.rooms:
            return False, "You cannot go that way."
        
        # Check if connected
        current_room = self.get_current_room()
        if (new_x, new_y) not in current_room.connections:
            return False, "There is no path in that direction."
        
        self.player_position = (new_x, new_y)
        new_room = self.get_current_room()
        new_room.visited = True
        
        return True, f"You move {direction}."
    
    def get_map_display(self) -> str:
        """Get visual map of floor"""
        lines = [f"\n{'='*50}", f"Floor {self.floor_number} - {self.theme.value.title()}", f"{'='*50}"]
        
        # Find bounds
        min_x = min(x for x, y in self.rooms.keys())
        max_x = max(x for x, y in self.rooms.keys())
        min_y = min(y for x, y in self.rooms.keys())
        max_y = max(y for x, y in self.rooms.keys())
        
        # Build map
        for y in range(min_y, max_y + 1):
            row = ""
            for x in range(min_x, max_x + 1):
                if (x, y) == self.player_position:
                    row += "🧙"  # Player
                elif (x, y) in self.rooms:
                    room = self.rooms[(x, y)]
                    row += room.get_display_symbol()
                else:
                    row += " "
                row += " "
            lines.append(row)
        
        # Legend
        lines.append("\nLegend: 🧙 You  ⚔ Combat  💰 Treasure  💀 Trap")
        lines.append("        🛏 Rest  👹 Boss  ⛩ Shrine  🚪 Exit")
        
        return "\n".join(lines)
    
    def to_dict(self) -> Dict:
        return {
            "floor_number": self.floor_number,
            "rooms": {f"{x},{y}": room.to_dict() for (x, y), room in self.rooms.items()},
            "player_position": self.player_position,
            "size": self.size,
            "theme": self.theme.value,
            "difficulty": self.difficulty,
            "cleared": self.cleared
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'DungeonFloor':
        floor = cls(
            floor_number=data["floor_number"],
            player_position=tuple(data["player_position"]),
            size=data.get("size", 5),
            theme=DungeonTheme(data.get("theme", "crypt")),
            difficulty=data.get("difficulty", 1),
            cleared=data.get("cleared", False)
        )
        
        # Restore rooms
        for key, room_data in data.get("rooms", {}).items():
            x, y = map(int, key.split(","))
            floor.rooms[(x, y)] = DungeonRoom.from_dict(room_data)
        
        return floor


class DungeonGenerator:
    """Generates random dungeons"""
    
    THEMES = {
        DungeonTheme.CRYPT: {
            "descriptions": {
                RoomType.EMPTY: ["A dusty corridor stretches before you.", "Ancient bones litter the floor."],
                RoomType.COMBAT: ["Undead guardians block your path!", "Shadows coalesce into hostile forms."],
                RoomType.TREASURE: ["A sarcophagus gleams with treasure.", "Ancient offerings lie undisturbed."],
                RoomType.TRAP: ["Pressure plates are visible on the floor.", "Strange runes glow ominously."],
                RoomType.REST: ["A peaceful alcove offers respite.", "Holy wards protect this chamber."],
                RoomType.BOSS: ["A massive tomb dominates the room.", "Dark energy pulses from ahead."],
                RoomType.EXIT: ["Stairs lead downward.", "A portal shimmers with dark energy."]
            },
            "enemies": ["skeleton", "zombie", "ghost", "vampire", "lich"],
            "traps": ["poison_dart", "falling_rocks", "spike_pit"]
        },
        DungeonTheme.CAVERN: {
            "descriptions": {
                RoomType.EMPTY: ["Stalactites drip water rhythmically.", "The cave echoes with distant sounds."],
                RoomType.COMBAT: ["Monstrous shapes emerge from shadows.", "Cave dwellers attack!"],
                RoomType.TREASURE: ["Crystals glitter in the torchlight.", "A natural treasure chamber!"],
                RoomType.TRAP: ["The floor looks unstable.", "Strange mushrooms release spores."],
                RoomType.REST: ["A dry ledge offers safety.", "Underground hot spring bubbles nearby."],
                RoomType.BOSS: ["A massive cavern opens before you.", "The air grows thick with danger."],
                RoomType.EXIT: ["A tunnel descends deeper.", "Natural stairs lead down."]
            },
            "enemies": ["goblin", "troll", "spider", "bat", "dragon_wyrmling"],
            "traps": ["pitfall", "rockslide", "poison_gas"]
        },
        DungeonTheme.RUINS: {
            "descriptions": {
                RoomType.EMPTY: ["Crumbling walls tell of ancient glory.", "Vines cover the stone floor."],
                RoomType.COMBAT: ["Guardian constructs activate!", "Cursed defenders attack!"],
                RoomType.TREASURE: ["An ancient vault lies open.", "Forgotten riches await."],
                RoomType.TRAP: ["The floor is unstable.", "Ancient mechanisms whir to life."],
                RoomType.REST: ["A relatively intact chamber.", "Ancient wards still function here."],
                RoomType.BOSS: ["The throne room lies ahead.", "Massive pillars support the ceiling."],
                RoomType.EXIT: ["A grand staircase descends.", "An archway leads deeper."]
            },
            "enemies": ["golem", "animated_armor", "cultist", "dark_mage", "demon"],
            "traps": ["arrow_trap", "magic_barrier", "illusion_floor"]
        }
    }
    
    @staticmethod
    def generate_floor(floor_number: int, player_level: int, theme: Optional[DungeonTheme] = None) -> DungeonFloor:
        """Generate a random dungeon floor"""
        if theme is None:
            theme = random.choice(list(DungeonTheme))
        
        # Calculate difficulty
        difficulty = floor_number + (player_level // 5)
        
        # Determine size (increases with floor number)
        size = min(5 + (floor_number // 3), 10)
        
        floor = DungeonFloor(
            floor_number=floor_number,
            theme=theme,
            difficulty=difficulty,
            size=size
        )
        
        # Generate rooms
        rooms_to_create = size * size // 2  # About half the grid
        created_rooms: Set[Tuple[int, int]] = set()
        
        # Start at center
        start_x, start_y = 0, 0
        floor.player_position = (start_x, start_y)
        
        # Create entrance
        entrance = DungeonRoom(
            x=start_x, y=start_y,
            room_type=RoomType.EMPTY,
            visited=True,
            description="The entrance to this floor."
        )
        floor.rooms[(start_x, start_y)] = entrance
        created_rooms.add((start_x, start_y))
        
        # Generate connected rooms
        current_rooms = [(start_x, start_y)]
        
        for _ in range(rooms_to_create - 1):
            if not current_rooms:
                break
            
            # Pick a random existing room to branch from
            parent_x, parent_y = random.choice(current_rooms)
            
            # Try to create a room in a random direction
            directions = [(0, -1), (0, 1), (-1, 0), (1, 0)]
            random.shuffle(directions)
            
            for dx, dy in directions:
                new_x, new_y = parent_x + dx, parent_y + dy
                
                # Check if spot is available
                if (new_x, new_y) not in created_rooms and abs(new_x) <= size//2 and abs(new_y) <= size//2:
                    # Determine room type
                    room_type = DungeonGenerator._determine_room_type(floor_number, len(created_rooms), rooms_to_create)
                    
                    # Create room
                    room = DungeonRoom(
                        x=new_x, y=new_y,
                        room_type=room_type,
                        description=DungeonGenerator._get_description(theme, room_type)
                    )
                    
                    # Add content based on type
                    if room_type == RoomType.COMBAT:
                        room.enemies = DungeonGenerator._generate_enemies(difficulty, theme)
                    elif room_type == RoomType.TREASURE:
                        room.loot = DungeonGenerator._generate_loot(difficulty)
                    elif room_type == RoomType.TRAP:
                        room.trap_difficulty = difficulty
                    elif room_type == RoomType.BOSS:
                        room.enemies = DungeonGenerator._generate_boss(difficulty, theme)
                        room.loot = DungeonGenerator._generate_loot(difficulty + 5)
                    
                    # Connect rooms
                    room.connections.append((parent_x, parent_y))
                    parent_room = floor.rooms[(parent_x, parent_y)]
                    parent_room.connections.append((new_x, new_y))
                    
                    floor.rooms[(new_x, new_y)] = room
                    created_rooms.add((new_x, new_y))
                    current_rooms.append((new_x, new_y))
                    break
        
        # Ensure there's an exit room (furthest room from entrance)
        furthest_room = max(created_rooms, key=lambda pos: abs(pos[0]) + abs(pos[1]))
        exit_room = floor.rooms[furthest_room]
        exit_room.room_type = RoomType.EXIT
        exit_room.description = "Stairs lead to the next floor."
        
        return floor
    
    @staticmethod
    def _determine_room_type(floor_number: int, current_rooms: int, total_rooms: int) -> RoomType:
        """Determine what type of room to create"""
        # Boss room on last room of every 5th floor
        if current_rooms == total_rooms - 1 and floor_number % 5 == 0:
            return RoomType.BOSS
        
        # Weighted random selection
        weights = {
            RoomType.EMPTY: 30,
            RoomType.COMBAT: 25,
            RoomType.TREASURE: 15,
            RoomType.TRAP: 10,
            RoomType.REST: 5,
            RoomType.SHRINE: 5,
            RoomType.PUZZLE: 5,
            RoomType.SHOP: 5
        }
        
        return random.choices(list(weights.keys()), weights=list(weights.values()))[0]
    
    @staticmethod
    def _get_description(theme: DungeonTheme, room_type: RoomType) -> str:
        """Get a random description for room"""
        theme_data = DungeonGenerator.THEMES.get(theme, DungeonGenerator.THEMES[DungeonTheme.CRYPT])
        descriptions = theme_data["descriptions"].get(room_type, ["A mysterious room."])
        return random.choice(descriptions)
    
    @staticmethod
    def _generate_enemies(difficulty: int, theme: DungeonTheme) -> List[str]:
        """Generate enemy list for a room"""
        theme_data = DungeonGenerator.THEMES.get(theme, DungeonGenerator.THEMES[DungeonTheme.CRYPT])
        available_enemies = theme_data["enemies"]
        
        num_enemies = min(random.randint(1, 3) + (difficulty // 5), 5)
        return [random.choice(available_enemies) for _ in range(num_enemies)]
    
    @staticmethod
    def _generate_boss(difficulty: int, theme: DungeonTheme) -> List[str]:
        """Generate boss enemy"""
        bosses = {
            DungeonTheme.CRYPT: ["vampire", "lich"],
            DungeonTheme.CAVERN: ["troll", "dragon_wyrmling"],
            DungeonTheme.RUINS: ["demon", "ancient_dragon"]
        }
        
        available_bosses = bosses.get(theme, ["demon"])
        return [random.choice(available_bosses)]
    
    @staticmethod
    def _generate_loot(difficulty: int) -> List[str]:
        """Generate loot for a room"""
        loot_table = {
            "common": ["health_potion", "gold", "iron_ore"],
            "uncommon": ["mana_potion", "magic_essence", "leather"],
            "rare": ["elixir", "enchanted_scroll", "rare_gem"],
            "epic": ["legendary_weapon", "epic_armor", "ancient_relic"]
        }
        
        loot = []
        num_items = random.randint(1, 3)
        
        for _ in range(num_items):
            roll = random.random()
            if roll < 0.5:
                rarity = "common"
            elif roll < 0.8:
                rarity = "uncommon"
            elif roll < 0.95:
                rarity = "rare"
            else:
                rarity = "epic"
            
            item = random.choice(loot_table[rarity])
            loot.append(item)
        
        return loot


class RandomDungeon:
    """A complete random dungeon with multiple floors"""
    
    def __init__(self, name: str, player_level: int, num_floors: int = 5):
        self.name = name
        self.player_level = player_level
        self.num_floors = num_floors
        self.current_floor_index = 0
        self.floors: List[DungeonFloor] = []
        self.completed = False
        self.total_gold_earned = 0
        self.total_exp_earned = 0
        self.bosses_defeated = 0
        
        # Generate floors
        theme = random.choice(list(DungeonTheme))
        for i in range(1, num_floors + 1):
            floor = DungeonGenerator.generate_floor(i, player_level, theme)
            self.floors.append(floor)
    
    def get_current_floor(self) -> Optional[DungeonFloor]:
        """Get current floor"""
        if 0 <= self.current_floor_index < len(self.floors):
            return self.floors[self.current_floor_index]
        return None
    
    def next_floor(self) -> Tuple[bool, str]:
        """Move to next floor"""
        if self.current_floor_index < len(self.floors) - 1:
            self.current_floor_index += 1
            return True, f"You descend to floor {self.current_floor_index + 1}..."
        else:
            self.completed = True
            return True, "You have reached the end of the dungeon!"
    
    def get_dungeon_status(self) -> str:
        """Get overall dungeon status"""
        lines = [
            f"\n{'='*60}",
            f"DUNGEON: {self.name}",
            f"{'='*60}",
            f"Floor: {self.current_floor_index + 1}/{self.num_floors}",
            f"Status: {'Completed' if self.completed else 'In Progress'}",
            f"Gold Earned: {self.total_gold_earned}",
            f"EXP Earned: {self.total_exp_earned}",
            f"Bosses Defeated: {self.bosses_defeated}"
        ]
        return "\n".join(lines)
    
    def to_dict(self) -> Dict:
        return {
            "name": self.name,
            "player_level": self.player_level,
            "num_floors": self.num_floors,
            "current_floor_index": self.current_floor_index,
            "floors": [floor.to_dict() for floor in self.floors],
            "completed": self.completed,
            "total_gold_earned": self.total_gold_earned,
            "total_exp_earned": self.total_exp_earned,
            "bosses_defeated": self.bosses_defeated
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'RandomDungeon':
        dungeon = cls.__new__(cls)
        dungeon.name = data["name"]
        dungeon.player_level = data["player_level"]
        dungeon.num_floors = data["num_floors"]
        dungeon.current_floor_index = data["current_floor_index"]
        dungeon.floors = [DungeonFloor.from_dict(floor_data) for floor_data in data["floors"]]
        dungeon.completed = data.get("completed", False)
        dungeon.total_gold_earned = data.get("total_gold_earned", 0)
        dungeon.total_exp_earned = data.get("total_exp_earned", 0)
        dungeon.bosses_defeated = data.get("bosses_defeated", 0)
        return dungeon


print("Dungeon generator system loaded successfully!")

"""
Housing System - Player homes with customization and storage

Author: YSNRFD
Version: 1.0.0
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any, Set, TYPE_CHECKING
from enum import Enum
import time
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.engine import Rarity, colored_text, format_number

if TYPE_CHECKING:
    from core.character import Character
    from core.items import Item


class HouseType(Enum):
    """Types of player housing"""
    SHACK = ("Shack", 1000, 10, 2)
    COTTAGE = ("Cottage", 5000, 20, 4)
    HOUSE = ("House", 15000, 40, 6)
    MANSION = ("Mansion", 50000, 80, 10)
    CASTLE = ("Castle", 200000, 200, 20)
    TOWER = ("Wizard Tower", 100000, 60, 8)
    UNDERGROUND = ("Underground Base", 80000, 50, 8)
    TREEHOUSE = ("Treehouse", 30000, 30, 5)
    SHIP = ("House Ship", 120000, 45, 6)
    FLOATING = ("Floating Island", 500000, 100, 15)
    
    def __init__(self, display_name: str, base_cost: int, storage_capacity: int, max_rooms: int):
        self.display_name = display_name
        self.base_cost = base_cost
        self.storage_capacity = storage_capacity
        self.max_rooms = max_rooms


class RoomType(Enum):
    """Types of rooms"""
    BEDROOM = "bedroom"
    KITCHEN = "kitchen"
    STORAGE = "storage"
    GARDEN = "garden"
    SMITHY = "smithy"
    ALCHEMY = "alchemy"
    LIBRARY = "library"
    TRAINING = "training"
    TROPHY = "trophy"
    GUEST = "guest"
    VAULT = "vault"
    PORTAL = "portal"
    SHRINE = "shrine"


class FurnitureType(Enum):
    """Types of furniture"""
    BED = "bed"
    CHEST = "chest"
    TABLE = "table"
    CHAIR = "chair"
    BOOKSHELF = "bookshelf"
    FORGE = "forge"
    CAULDRON = "cauldron"
    MANNEQUIN = "mannequin"
    PAINTING = "painting"
    RUG = "rug"
    LAMP = "lamp"
    PLANT = "plant"
    TROPHY_CASE = "trophy_case"
    WEAPON_RACK = "weapon_rack"
    ARMOR_STAND = "armor_stand"


@dataclass
class Furniture:
    """A piece of furniture"""
    id: str
    name: str
    furniture_type: FurnitureType
    description: str
    cost: int
    rarity: Rarity = Rarity.COMMON
    effects: Dict[str, Any] = field(default_factory=dict)
    is_placed: bool = False
    position: Optional[Tuple[int, int]] = None
    
    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "name": self.name,
            "furniture_type": self.furniture_type.value,
            "description": self.description,
            "cost": self.cost,
            "rarity": self.rarity.name,
            "effects": self.effects,
            "is_placed": self.is_placed,
            "position": self.position
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Furniture':
        return cls(
            id=data["id"],
            name=data["name"],
            furniture_type=FurnitureType(data["furniture_type"]),
            description=data["description"],
            cost=data["cost"],
            rarity=Rarity[data.get("rarity", "COMMON")],
            effects=data.get("effects", {}),
            is_placed=data.get("is_placed", False),
            position=tuple(data["position"]) if data.get("position") else None
        )


@dataclass
class Room:
    """A room in a house"""
    id: str
    room_type: RoomType
    name: str
    description: str
    furniture: List[Furniture] = field(default_factory=list)
    max_furniture: int = 5
    bonuses: Dict[str, Any] = field(default_factory=dict)
    is_unlocked: bool = True
    upgrade_level: int = 1
    
    def add_furniture(self, furniture: Furniture) -> Tuple[bool, str]:
        """Add furniture to room"""
        if len(self.furniture) >= self.max_furniture:
            return False, "Room is full."
        
        if furniture.is_placed:
            return False, "Furniture already placed elsewhere."
        
        furniture.is_placed = True
        self.furniture.append(furniture)
        
        # Apply bonuses
        for effect, value in furniture.effects.items():
            if effect in self.bonuses:
                self.bonuses[effect] += value
            else:
                self.bonuses[effect] = value
        
        return True, f"Placed {furniture.name} in {self.name}."
    
    def remove_furniture(self, furniture_id: str) -> Tuple[bool, str, Optional[Furniture]]:
        """Remove furniture from room"""
        for i, furniture in enumerate(self.furniture):
            if furniture.id == furniture_id:
                removed = self.furniture.pop(i)
                removed.is_placed = False
                removed.position = None
                
                # Remove bonuses
                for effect, value in removed.effects.items():
                    if effect in self.bonuses:
                        self.bonuses[effect] -= value
                        if self.bonuses[effect] <= 0:
                            del self.bonuses[effect]
                
                return True, f"Removed {removed.name}.", removed
        
        return False, "Furniture not found.", None
    
    def get_display(self) -> str:
        """Get room display"""
        lines = [
            f"\n{'='*50}",
            f"{self.name} [{self.room_type.value.title()}]",
            f"{'='*50}",
            f"{self.description}",
            f"Furniture: {len(self.furniture)}/{self.max_furniture}",
        ]
        
        if self.bonuses:
            lines.append("\nRoom Bonuses:")
            for bonus, value in self.bonuses.items():
                lines.append(f"  +{value} {bonus.replace('_', ' ').title()}")
        
        if self.furniture:
            lines.append("\nFurniture:")
            for furniture in self.furniture:
                rarity_color = furniture.rarity.color
                lines.append(f"  • {rarity_color}{furniture.name}\033[0m")
        
        return "\n".join(lines)
    
    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "room_type": self.room_type.value,
            "name": self.name,
            "description": self.description,
            "furniture": [f.to_dict() for f in self.furniture],
            "max_furniture": self.max_furniture,
            "bonuses": self.bonuses,
            "is_unlocked": self.is_unlocked,
            "upgrade_level": self.upgrade_level
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Room':
        return cls(
            id=data["id"],
            room_type=RoomType(data["room_type"]),
            name=data["name"],
            description=data["description"],
            furniture=[Furniture.from_dict(f) for f in data.get("furniture", [])],
            max_furniture=data.get("max_furniture", 5),
            bonuses=data.get("bonuses", {}),
            is_unlocked=data.get("is_unlocked", True),
            upgrade_level=data.get("upgrade_level", 1)
        )


@dataclass
class House:
    """A player house"""
    id: str
    owner_id: str
    owner_name: str
    name: str
    house_type: HouseType
    location: str
    rooms: Dict[str, Room] = field(default_factory=dict)
    storage: List[Dict[str, Any]] = field(default_factory=list)
    storage_used: int = 0
    garden_plots: List[Dict[str, Any]] = field(default_factory=list)
    trophies: List[str] = field(default_factory=list)
    visitors_allowed: bool = True
    is_primary: bool = False
    purchase_date: float = field(default_factory=time.time)
    total_value: int = 0
    servants: List[Dict[str, Any]] = field(default_factory=list)
    
    def __post_init__(self):
        # Initialize default rooms based on house type
        if not self.rooms:
            self._init_default_rooms()
        
        # Initialize garden plots
        if not self.garden_plots:
            garden_size = self.house_type.max_rooms // 2
            for i in range(garden_size):
                self.garden_plots.append({
                    "id": f"plot_{i}",
                    "planted": None,
                    "growth": 0,
                    "watered": False
                })
    
    def _init_default_rooms(self):
        """Initialize default rooms for house type"""
        default_rooms = {
            HouseType.SHACK: [RoomType.BEDROOM, RoomType.STORAGE],
            HouseType.COTTAGE: [RoomType.BEDROOM, RoomType.KITCHEN, RoomType.STORAGE],
            HouseType.HOUSE: [RoomType.BEDROOM, RoomType.KITCHEN, RoomType.STORAGE, RoomType.GARDEN],
            HouseType.MANSION: [RoomType.BEDROOM, RoomType.KITCHEN, RoomType.STORAGE, 
                            RoomType.GARDEN, RoomType.LIBRARY, RoomType.TROPHY],
            HouseType.CASTLE: [RoomType.BEDROOM, RoomType.KITCHEN, RoomType.STORAGE,
                             RoomType.GARDEN, RoomType.LIBRARY, RoomType.TROPHY,
                             RoomType.TRAINING, RoomType.VAULT, RoomType.SMITHY],
            HouseType.TOWER: [RoomType.BEDROOM, RoomType.LIBRARY, RoomType.ALCHEMY, RoomType.PORTAL],
            HouseType.UNDERGROUND: [RoomType.BEDROOM, RoomType.STORAGE, RoomType.VAULT, 
                                  RoomType.SMITHY, RoomType.ALCHEMY],
            HouseType.TREEHOUSE: [RoomType.BEDROOM, RoomType.STORAGE, RoomType.GARDEN],
            HouseType.SHIP: [RoomType.BEDROOM, RoomType.STORAGE, RoomType.KITCHEN],
            HouseType.FLOATING: [RoomType.BEDROOM, RoomType.KITCHEN, RoomType.STORAGE,
                               RoomType.GARDEN, RoomType.PORTAL, RoomType.SHRINE]
        }
        
        room_types = default_rooms.get(self.house_type, [RoomType.BEDROOM, RoomType.STORAGE])
        
        for i, room_type in enumerate(room_types):
            room_id = f"room_{i}"
            room = self._create_room(room_id, room_type)
            self.rooms[room_id] = room
    
    def _create_room(self, room_id: str, room_type: RoomType) -> Room:
        """Create a room of specific type"""
        room_data = {
            RoomType.BEDROOM: {
                "name": "Master Bedroom",
                "description": "A comfortable place to rest.",
                "max_furniture": 5,
                "bonuses": {"rest_quality": 10}
            },
            RoomType.KITCHEN: {
                "name": "Kitchen",
                "description": "Prepare meals and store food.",
                "max_furniture": 4,
                "bonuses": {"cooking_exp": 5}
            },
            RoomType.STORAGE: {
                "name": "Storage Room",
                "description": "Store your belongings.",
                "max_furniture": 8,
                "bonuses": {"storage_space": 20}
            },
            RoomType.GARDEN: {
                "name": "Garden",
                "description": "Grow herbs and plants.",
                "max_furniture": 6,
                "bonuses": {"herb_growth": 10}
            },
            RoomType.SMITHY: {
                "name": "Smithy",
                "description": "Forge weapons and armor.",
                "max_furniture": 4,
                "bonuses": {"smithing_exp": 10, "crafting_quality": 5}
            },
            RoomType.ALCHEMY: {
                "name": "Alchemy Lab",
                "description": "Brew potions and elixirs.",
                "max_furniture": 4,
                "bonuses": {"alchemy_exp": 10, "potion_strength": 5}
            },
            RoomType.LIBRARY: {
                "name": "Library",
                "description": "Study and research.",
                "max_furniture": 6,
                "bonuses": {"experience_gain": 5, "skill_learning": 10}
            },
            RoomType.TRAINING: {
                "name": "Training Room",
                "description": "Practice combat skills.",
                "max_furniture": 4,
                "bonuses": {"combat_exp": 10, "skill_mastery": 5}
            },
            RoomType.TROPHY: {
                "name": "Trophy Hall",
                "description": "Display your achievements.",
                "max_furniture": 10,
                "bonuses": {"prestige": 5}
            },
            RoomType.GUEST: {
                "name": "Guest Room",
                "description": "For visitors and companions.",
                "max_furniture": 4,
                "bonuses": {"companion_comfort": 10}
            },
            RoomType.VAULT: {
                "name": "Treasure Vault",
                "description": "Secure storage for valuables.",
                "max_furniture": 10,
                "bonuses": {"security": 20, "gold_storage": 50}
            },
            RoomType.PORTAL: {
                "name": "Portal Chamber",
                "description": "Fast travel to locations.",
                "max_furniture": 2,
                "bonuses": {"fast_travel": 1}
            },
            RoomType.SHRINE: {
                "name": "Divine Shrine",
                "description": "Receive blessings.",
                "max_furniture": 3,
                "bonuses": {"blessing_duration": 20, "prayer_power": 10}
            }
        }
        
        data = room_data.get(room_type, {
            "name": "Room",
            "description": "A basic room.",
            "max_furniture": 3,
            "bonuses": {}
        })
        
        return Room(
            id=room_id,
            room_type=room_type,
            name=data["name"],
            description=data["description"],
            max_furniture=data["max_furniture"],
            bonuses=data["bonuses"].copy()
        )
    
    def add_room(self, room_type: RoomType) -> Tuple[bool, str, Optional[Room]]:
        """Add a new room to the house"""
        if len(self.rooms) >= self.house_type.max_rooms:
            return False, "Maximum rooms reached for this house type.", None
        
        room_id = f"room_{len(self.rooms)}"
        room = self._create_room(room_id, room_type)
        self.rooms[room_id] = room
        
        return True, f"Added {room.name} to your house!", room
    
    def store_item(self, item: 'Item', quantity: int = 1) -> Tuple[bool, str]:
        """Store an item in house storage"""
        if self.storage_used >= self.house_type.storage_capacity:
            return False, "Storage is full."
        
        # Check if item already exists
        for stored in self.storage:
            if stored["item_id"] == item.name:
                stored["quantity"] += quantity
                self.storage_used += quantity
                return True, f"Stored {quantity}x {item.name}."
        
        # Add new item
        self.storage.append({
            "item_id": item.name,
            "name": item.name,
            "quantity": quantity,
            "rarity": item.rarity.name,
            "stored_at": time.time()
        })
        self.storage_used += quantity
        
        return True, f"Stored {quantity}x {item.name}."
    
    def retrieve_item(self, item_id: str, quantity: int = 1) -> Tuple[bool, str, Optional[Dict]]:
        """Retrieve an item from storage"""
        for stored in self.storage:
            if stored["item_id"] == item_id:
                if stored["quantity"] < quantity:
                    return False, "Not enough quantity stored.", None
                
                stored["quantity"] -= quantity
                self.storage_used -= quantity
                
                if stored["quantity"] <= 0:
                    self.storage.remove(stored)
                
                return True, f"Retrieved {quantity}x {item_id}.", stored
        
        return False, "Item not found in storage.", None
    
    def plant_seed(self, plot_id: str, seed_type: str) -> Tuple[bool, str]:
        """Plant a seed in garden plot"""
        for plot in self.garden_plots:
            if plot["id"] == plot_id:
                if plot["planted"]:
                    return False, "Plot already has something planted."
                
                plot["planted"] = seed_type
                plot["growth"] = 0
                plot["watered"] = False
                return True, f"Planted {seed_type} in garden plot."
        
        return False, "Garden plot not found."
    
    def water_plants(self) -> Tuple[int, str]:
        """Water all plants"""
        watered = 0
        for plot in self.garden_plots:
            if plot["planted"] and not plot["watered"]:
                plot["watered"] = True
                watered += 1
        
        return watered, f"Watered {watered} plants."
    
    def harvest_plant(self, plot_id: str) -> Tuple[bool, str, Optional[str]]:
        """Harvest a mature plant"""
        for plot in self.garden_plots:
            if plot["id"] == plot_id:
                if not plot["planted"]:
                    return False, "Nothing planted here.", None
                
                if plot["growth"] < 100:
                    return False, f"Plant is not ready. Growth: {plot['growth']}%", None
                
                harvested = plot["planted"]
                plot["planted"] = None
                plot["growth"] = 0
                plot["watered"] = False
                
                return True, f"Harvested {harvested}!", harvested
        
        return False, "Garden plot not found.", None
    
    def add_trophy(self, trophy_name: str) -> Tuple[bool, str]:
        """Add a trophy to the house"""
        if trophy_name in self.trophies:
            return False, "Trophy already displayed."
        
        self.trophies.append(trophy_name)
        return True, f"Added {trophy_name} to your trophy hall!"
    
    def get_display(self) -> str:
        """Get house display"""
        lines = [
            f"\n{'='*60}",
            f"🏠 {self.name}",
            f"{'='*60}",
            f"Type: {self.house_type.display_name}",
            f"Owner: {self.owner_name}",
            f"Location: {self.location}",
            f"",
            f"Rooms: {len(self.rooms)}/{self.house_type.max_rooms}",
            f"Storage: {self.storage_used}/{self.house_type.storage_capacity}",
            f"Garden Plots: {len([p for p in self.garden_plots if p['planted']])}/{len(self.garden_plots)}",
            f"Trophies: {len(self.trophies)}",
            f"Total Value: {format_number(self.total_value)} gold",
        ]
        
        if self.trophies:
            lines.append(f"\nTrophy Collection:")
            for trophy in self.trophies[:10]:
                lines.append(f"  🏆 {trophy}")
        
        if self.servants:
            lines.append(f"\nServants: {len(self.servants)}")
        
        return "\n".join(lines)
    
    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "owner_id": self.owner_id,
            "owner_name": self.owner_name,
            "name": self.name,
            "house_type": self.house_type.name,
            "location": self.location,
            "rooms": {k: v.to_dict() for k, v in self.rooms.items()},
            "storage": self.storage,
            "storage_used": self.storage_used,
            "garden_plots": self.garden_plots,
            "trophies": self.trophies,
            "visitors_allowed": self.visitors_allowed,
            "is_primary": self.is_primary,
            "purchase_date": self.purchase_date,
            "total_value": self.total_value,
            "servants": self.servants
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'House':
        house = cls(
            id=data["id"],
            owner_id=data["owner_id"],
            owner_name=data["owner_name"],
            name=data["name"],
            house_type=HouseType[data["house_type"]],
            location=data["location"],
            storage=data.get("storage", []),
            storage_used=data.get("storage_used", 0),
            garden_plots=data.get("garden_plots", []),
            trophies=data.get("trophies", []),
            visitors_allowed=data.get("visitors_allowed", True),
            is_primary=data.get("is_primary", False),
            purchase_date=data.get("purchase_date", time.time()),
            total_value=data.get("total_value", 0),
            servants=data.get("servants", [])
        )
        
        # Restore rooms
        house.rooms = {k: Room.from_dict(v) for k, v in data.get("rooms", {}).items()}
        
        return house


class HousingManager:
    """Manages player housing"""
    
    def __init__(self):
        self.houses: Dict[str, House] = {}  # house_id -> House
        self.owner_houses: Dict[str, List[str]] = {}  # owner_id -> [house_ids]
        self.furniture_catalog: Dict[str, Furniture] = {}
        self._init_furniture_catalog()
    
    def _init_furniture_catalog(self):
        """Initialize default furniture"""
        default_furniture = {
            "simple_bed": Furniture(
                id="simple_bed",
                name="Simple Bed",
                furniture_type=FurnitureType.BED,
                description="A basic bed for resting.",
                cost=100,
                effects={"rest_quality": 5}
            ),
            "comfortable_bed": Furniture(
                id="comfortable_bed",
                name="Comfortable Bed",
                furniture_type=FurnitureType.BED,
                description="A nice bed with soft pillows.",
                cost=500,
                rarity=Rarity.UNCOMMON,
                effects={"rest_quality": 15, "hp_regen": 5}
            ),
            "wooden_chest": Furniture(
                id="wooden_chest",
                name="Wooden Chest",
                furniture_type=FurnitureType.CHEST,
                description="Store your items safely.",
                cost=200,
                effects={"storage_space": 10}
            ),
            "bookshelf": Furniture(
                id="bookshelf",
                name="Bookshelf",
                furniture_type=FurnitureType.BOOKSHELF,
                description="Store and display your books.",
                cost=300,
                rarity=Rarity.UNCOMMON,
                effects={"experience_gain": 3}
            ),
            "forge": Furniture(
                id="forge",
                name="Blacksmith's Forge",
                furniture_type=FurnitureType.FORGE,
                description="Forge weapons and armor.",
                cost=2000,
                rarity=Rarity.RARE,
                effects={"smithing_exp": 10, "crafting_quality": 5}
            ),
            "alchemy_table": Furniture(
                id="alchemy_table",
                name="Alchemy Table",
                furniture_type=FurnitureType.CAULDRON,
                description="Brew potions and elixirs.",
                cost=1500,
                rarity=Rarity.RARE,
                effects={"alchemy_exp": 10, "potion_duration": 10}
            ),
            "weapon_rack": Furniture(
                id="weapon_rack",
                name="Weapon Rack",
                furniture_type=FurnitureType.WEAPON_RACK,
                description="Display your weapons.",
                cost=400,
                effects={"weapon_damage": 2}
            ),
            "trophy_case": Furniture(
                id="trophy_case",
                name="Trophy Case",
                furniture_type=FurnitureType.TROPHY_CASE,
                description="Show off your achievements.",
                cost=1000,
                rarity=Rarity.EPIC,
                effects={"prestige": 10, "charisma": 2}
            )
        }
        
        for furniture_id, furniture in default_furniture.items():
            self.furniture_catalog[furniture_id] = furniture
    
    def purchase_house(self, character: 'Character', house_type: HouseType, 
                       location: str, name: str) -> Tuple[bool, str, Optional[House]]:
        """Purchase a new house"""
        # Check if character can afford it
        if character.inventory.gold < house_type.base_cost:
            return False, f"Not enough gold. Cost: {house_type.base_cost}", None
        
        # Deduct gold
        character.inventory.gold -= house_type.base_cost
        
        # Create house
        import hashlib
        house_id = hashlib.md5(f"{character.id}{name}{time.time()}".encode()).hexdigest()[:12]
        
        house = House(
            id=house_id,
            owner_id=character.id,
            owner_name=character.name,
            name=name,
            house_type=house_type,
            location=location,
            total_value=house_type.base_cost
        )
        
        self.houses[house_id] = house
        
        # Track ownership
        if character.id not in self.owner_houses:
            self.owner_houses[character.id] = []
        self.owner_houses[character.id].append(house_id)
        
        return True, f"Purchased {house_type.display_name}! Welcome home!", house
    
    def get_house(self, house_id: str) -> Optional[House]:
        """Get a house by ID"""
        return self.houses.get(house_id)
    
    def get_owner_houses(self, owner_id: str) -> List[House]:
        """Get all houses owned by a character"""
        house_ids = self.owner_houses.get(owner_id, [])
        return [self.houses[hid] for hid in house_ids if hid in self.houses]
    
    def get_primary_house(self, owner_id: str) -> Optional[House]:
        """Get the primary house for an owner"""
        houses = self.get_owner_houses(owner_id)
        for house in houses:
            if house.is_primary:
                return house
        return houses[0] if houses else None
    
    def set_primary_house(self, owner_id: str, house_id: str) -> Tuple[bool, str]:
        """Set a house as the primary residence"""
        house = self.houses.get(house_id)
        if not house:
            return False, "House not found."
        
        if house.owner_id != owner_id:
            return False, "You don't own this house."
        
        # Unset other primary houses
        for h in self.get_owner_houses(owner_id):
            h.is_primary = False
        
        house.is_primary = True
        return True, f"{house.name} is now your primary residence."
    
    def sell_house(self, owner_id: str, house_id: str) -> Tuple[bool, str, int]:
        """Sell a house"""
        house = self.houses.get(house_id)
        if not house:
            return False, "House not found.", 0
        
        if house.owner_id != owner_id:
            return False, "You don't own this house.", 0
        
        # Calculate sell value (70% of total value)
        sell_value = int(house.total_value * 0.7)
        
        # Remove house
        del self.houses[house_id]
        if owner_id in self.owner_houses:
            self.owner_houses[owner_id].remove(house_id)
        
        return True, f"Sold {house.name} for {sell_value} gold.", sell_value
    
    def get_furniture_catalog(self) -> Dict[str, Furniture]:
        """Get available furniture"""
        return self.furniture_catalog.copy()
    
    def purchase_furniture(self, character: 'Character', furniture_id: str) -> Tuple[bool, str, Optional[Furniture]]:
        """Purchase furniture"""
        furniture = self.furniture_catalog.get(furniture_id)
        if not furniture:
            return False, "Furniture not found.", None
        
        if character.inventory.gold < furniture.cost:
            return False, "Not enough gold.", None
        
        # Deduct gold
        character.inventory.gold -= furniture.cost
        
        # Create copy
        import hashlib
        new_id = hashlib.md5(f"{character.id}{furniture_id}{time.time()}".encode()).hexdigest()[:8]
        
        new_furniture = Furniture(
            id=new_id,
            name=furniture.name,
            furniture_type=furniture.furniture_type,
            description=furniture.description,
            cost=furniture.cost,
            rarity=furniture.rarity,
            effects=furniture.effects.copy()
        )
        
        return True, f"Purchased {furniture.name}!", new_furniture
    
    def to_dict(self) -> Dict:
        return {
            "houses": {k: v.to_dict() for k, v in self.houses.items()},
            "owner_houses": self.owner_houses,
            "furniture_catalog": {k: v.to_dict() for k, v in self.furniture_catalog.items()}
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'HousingManager':
        hm = cls()
        hm.houses = {k: House.from_dict(v) for k, v in data.get("houses", {}).items()}
        hm.owner_houses = data.get("owner_houses", {})
        hm.furniture_catalog = {k: Furniture.from_dict(v) for k, v in data.get("furniture_catalog", {}).items()}
        return hm


print("Housing system loaded successfully!")

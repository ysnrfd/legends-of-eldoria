"""
NPC and Dialogue System - Interactive Characters and Conversations
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any, Callable, TYPE_CHECKING
from enum import Enum
import sys
import os
import random
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.engine import EventType, Rarity, StatType

if TYPE_CHECKING:
    from core.character import Character


class NPCType(Enum):
    QUEST_GIVER = "quest_giver"
    MERCHANT = "merchant"
    BLACKSMITH = "blacksmith"
    HEALER = "healer"
    TRAINER = "trainer"
    GUARD = "guard"
    INNKEEPER = "innkeeper"
    VILLAGER = "villager"
    NOBLE = "noble"
    MYSTERIOUS = "mysterious"
    ENEMY = "enemy"


class DialogueAction(Enum):
    NONE = "none"
    OPEN_SHOP = "open_shop"
    START_QUEST = "start_quest"
    COMPLETE_QUEST = "complete_quest"
    GIVE_ITEM = "give_item"
    TAKE_ITEM = "take_item"
    TELEPORT = "teleport"
    HEAL = "heal"
    TRAIN = "train"
    START_COMBAT = "start_combat"
    UNLOCK_LOCATION = "unlock_location"
    GIVE_GOLD = "give_gold"
    CHECK_STAT = "check_stat"
    CUSTOM = "custom"


@dataclass
class DialogueChoice:
    """A dialogue choice option"""
    text: str
    condition: Dict[str, Any] = field(default_factory=dict)
    action: DialogueAction = DialogueAction.NONE
    action_data: Dict[str, Any] = field(default_factory=dict)
    next_node: str = ""
    skill_check: Optional[Tuple[StatType, int]] = None


@dataclass
class DialogueNode:
    """A single dialogue node"""
    id: str
    text: str
    speaker: str = ""
    choices: List[DialogueChoice] = field(default_factory=list)
    auto_action: DialogueAction = DialogueAction.NONE
    auto_action_data: Dict[str, Any] = field(default_factory=dict)
    condition: Dict[str, Any] = field(default_factory=dict)
    on_enter: Optional[Callable] = None


@dataclass
class NPC:
    """Non-player character"""
    id: str
    name: str
    description: str
    npc_type: NPCType
    location: str = ""
    dialogue_tree: Dict[str, DialogueNode] = field(default_factory=dict)
    current_node: str = "start"
    quest_giver: bool = False
    shop_id: str = ""
    shop_items: List[str] = field(default_factory=list)
    buy_multiplier: float = 1.0
    sell_multiplier: float = 0.5
    services: List[str] = field(default_factory=list)
    schedule: Dict[str, str] = field(default_factory=dict)
    friendship: int = 0
    friendship_max: int = 100
    friendship_rewards: Dict[int, str] = field(default_factory=dict)
    can_train: List[str] = field(default_factory=list)
    training_cost: int = 100
    custom_data: Dict[str, Any] = field(default_factory=dict)
    
    def get_greeting(self) -> str:
        """Get NPC greeting based on friendship"""
        if self.friendship >= 80:
            return f"\"My dear friend! It's wonderful to see you!\""
        elif self.friendship >= 50:
            return f"\"Good to see you again, friend.\""
        elif self.friendship >= 20:
            return f"\"Hello there.\""
        else:
            return f"\"...\""
    
    def get_dialogue(self, node_id: str = None) -> Optional[DialogueNode]:
        """Get dialogue node"""
        node_id = node_id or self.current_node
        return self.dialogue_tree.get(node_id)
    
    def advance_dialogue(self, choice_idx: int, player: 'Character') -> Tuple[DialogueAction, Dict[str, Any]]:
        """Advance dialogue based on choice"""
        node = self.get_dialogue()
        if not node or choice_idx >= len(node.choices):
            return DialogueAction.NONE, {}
        
        choice = node.choices[choice_idx]
        
        # Check skill check if present
        if choice.skill_check:
            stat_type, required = choice.skill_check
            if player.get_stat(stat_type) < required:
                self.current_node = "skill_fail"
                return DialogueAction.NONE, {"message": f"Skill check failed (needed {stat_type.value}: {required})"}
        
        # Update current node
        if choice.next_node:
            self.current_node = choice.next_node
        
        return choice.action, choice.action_data
    
    def change_friendship(self, amount: int) -> bool:
        """Change friendship level, returns True if friendship level changed"""
        old_level = self.friendship
        self.friendship = max(0, min(self.friendship_max, self.friendship + amount))
        return old_level // 20 != self.friendship // 20
    
    def get_interactions(self) -> List[str]:
        """Get available interactions"""
        interactions = ["[1] Talk"]
        
        if self.shop_id or self.shop_items:
            interactions.append("[2] Trade")
        
        if "heal" in self.services:
            interactions.append("[3] Heal")
        
        if "rest" in self.services:
            interactions.append("[4] Rest")
        
        if self.can_train:
            interactions.append("[5] Train")
        
        interactions.append("[0] Leave")
        
        return interactions
    
    def get_display(self) -> str:
        """Get NPC display info"""
        lines = [
            f"\n{'='*50}",
            f"👤 {self.name}",
            f"{'='*50}",
            f"{self.description}",
            f"",
            f"Type: {self.npc_type.value.replace('_', ' ').title()}"
        ]
        
        if self.friendship > 0:
            hearts = "❤️" * (self.friendship // 20)
            lines.append(f"Friendship: {hearts} ({self.friendship}/{self.friendship_max})")
        
        return "\n".join(lines)
    
    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "npc_type": self.npc_type.value,
            "location": self.location,
            "current_node": self.current_node,
            "quest_giver": self.quest_giver,
            "shop_id": self.shop_id,
            "shop_items": self.shop_items,
            "buy_multiplier": self.buy_multiplier,
            "sell_multiplier": self.sell_multiplier,
            "services": self.services,
            "friendship": self.friendship,
            "friendship_max": self.friendship_max,
            "can_train": self.can_train,
            "training_cost": self.training_cost
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'NPC':
        npc = cls(
            id=data["id"],
            name=data["name"],
            description=data["description"],
            npc_type=NPCType(data["npc_type"]),
            location=data.get("location", ""),
            quest_giver=data.get("quest_giver", False),
            shop_id=data.get("shop_id", ""),
            shop_items=data.get("shop_items", []),
            buy_multiplier=data.get("buy_multiplier", 1.0),
            sell_multiplier=data.get("sell_multiplier", 0.5),
            services=data.get("services", []),
            friendship=data.get("friendship", 0),
            friendship_max=data.get("friendship_max", 100),
            can_train=data.get("can_train", []),
            training_cost=data.get("training_cost", 100)
        )
        npc.current_node = data.get("current_node", "start")
        return npc


class NPCManager:
    """Manages all NPCs"""
    
    def __init__(self):
        self.npcs: Dict[str, NPC] = {}
        self._init_npcs()
    
    def _init_npcs(self):
        """Initialize NPCs"""
        npcs_data = [
            {
                "id": "elder_thorne",
                "name": "Elder Thorne",
                "description": "An elderly man with kind eyes and a long white beard. "
                             "He wears simple robes and carries a wooden staff.",
                "npc_type": NPCType.QUEST_GIVER,
                "location": "start_village",
                "quest_giver": True,
                "services": ["information"],
                "dialogue_greeting": "Welcome, traveler. Our village has seen better days..."
            },
            {
                "id": "blacksmith_gareth",
                "name": "Gareth the Blacksmith",
                "description": "A burly man with soot-stained arms and a leather apron. "
                             "The sounds of his hammer echo from his forge.",
                "npc_type": NPCType.BLACKSMITH,
                "location": "start_village",
                "shop_id": "blacksmith",
                "shop_items": ["iron_sword", "leather_armor", "iron_helmet", "leather_boots"],
                "services": ["repair", "craft"],
                "buy_multiplier": 1.0,
                "sell_multiplier": 0.4
            },
            {
                "id": "healer_rose",
                "name": "Rose the Healer",
                "description": "A gentle woman in flowing green robes. "
                             "The scent of herbs follows her everywhere.",
                "npc_type": NPCType.HEALER,
                "location": "start_village",
                "shop_id": "herb_shop",
                "shop_items": ["health_potion_minor", "health_potion", "mana_potion", "antidote", "herb"],
                "services": ["heal", "cure"],
                "buy_multiplier": 1.2,
                "sell_multiplier": 0.5
            },
            {
                "id": "merchant_finn",
                "name": "Finn the Merchant",
                "description": "A traveling merchant with a friendly smile and sharp eyes. "
                             "His pack is filled with various goods.",
                "npc_type": NPCType.MERCHANT,
                "location": "start_village",
                "shop_id": "village_shop",
                "shop_items": ["health_potion_minor", "stamina_potion", "torch", "rope", "rations"],
                "services": ["trade"],
                "buy_multiplier": 1.0,
                "sell_multiplier": 0.5
            },
            {
                "id": "innkeeper_mara",
                "name": "Mara the Innkeeper",
                "description": "A warm-hearted woman who runs the local inn. "
                             "She offers food, drink, and a place to rest.",
                "npc_type": NPCType.INNKEEPER,
                "location": "capital_city",
                "services": ["rest", "food", "information"],
                "buy_multiplier": 1.0,
                "sell_multiplier": 0.3
            },
            {
                "id": "king_aldric",
                "name": "King Aldric",
                "description": "The ruler of the realm, sitting upon his golden throne. "
                             "His crown gleams, but worry lines mark his face.",
                "npc_type": NPCType.NOBLE,
                "location": "royal_castle",
                "quest_giver": True,
                "services": ["audience"],
                "friendship_max": 200
            },
            {
                "id": "archmage_silas",
                "name": "Archmage Silas",
                "description": "An ancient wizard with flowing robes and a pointed hat. "
                             "Sparks of magic dance around his fingertips.",
                "npc_type": NPCType.TRAINER,
                "location": "capital_city",
                "shop_id": "magic_shop",
                "shop_items": ["mana_potion", "magic_crystal", "frost_staff", "spell_scroll"],
                "services": ["train_magic", "identify"],
                "can_train": ["Magic", "Wisdom"],
                "training_cost": 500,
                "buy_multiplier": 1.5,
                "sell_multiplier": 0.6
            },
            {
                "id": "guild_master",
                "name": "Guild Master",
                "description": "The head of the Adventurer's Guild. "
                             "His scarred face speaks of many battles.",
                "npc_type": NPCType.QUEST_GIVER,
                "location": "capital_city",
                "quest_giver": True,
                "services": ["quests", "training"],
                "can_train": ["Swordsmanship", "Stealth"]
            },
            {
                "id": "fairy_queen",
                "name": "Queen Titania",
                "description": "A beautiful fairy with gossamer wings that shimmer with all colors. "
                             "Her presence brings a sense of wonder.",
                "npc_type": NPCType.MYSTERIOUS,
                "location": "fairy_grove",
                "quest_giver": True,
                "services": ["blessing", "wishes"],
                "friendship_max": 150
            },
            {
                "id": "mysterious_stranger",
                "name": "Mysterious Stranger",
                "description": "A cloaked figure whose face remains hidden in shadow. "
                             "They seem to know more than they reveal.",
                "npc_type": NPCType.MYSTERIOUS,
                "location": "crossroads",
                "quest_giver": True,
                "services": ["information", "quests"]
            },
            {
                "id": "dwarf_smith",
                "name": "Thorin Ironforge",
                "description": "A stout dwarf with a magnificent braided beard. "
                             "His forge produces the finest metalwork in the realm.",
                "npc_type": NPCType.BLACKSMITH,
                "location": "mining_town",
                "shop_id": "dwarf_smithy",
                "shop_items": ["steel_greatsword", "plate_armor", "chainmail", "steel_shield"],
                "services": ["craft", "repair", "enchant"],
                "buy_multiplier": 1.2,
                "sell_multiplier": 0.5
            }
        ]
        
        for npc_data in npcs_data:
            npc = NPC(
                id=npc_data["id"],
                name=npc_data["name"],
                description=npc_data["description"],
                npc_type=npc_data["npc_type"],
                location=npc_data.get("location", ""),
                quest_giver=npc_data.get("quest_giver", False),
                shop_id=npc_data.get("shop_id", ""),
                shop_items=npc_data.get("shop_items", []),
                buy_multiplier=npc_data.get("buy_multiplier", 1.0),
                sell_multiplier=npc_data.get("sell_multiplier", 0.5),
                services=npc_data.get("services", []),
                can_train=npc_data.get("can_train", []),
                training_cost=npc_data.get("training_cost", 100),
                friendship_max=npc_data.get("friendship_max", 100)
            )
            
            # Add basic dialogue tree
            npc.dialogue_tree = self._create_basic_dialogue(npc)
            self.npcs[npc.id] = npc
    
    def _create_basic_dialogue(self, npc: NPC) -> Dict[str, DialogueNode]:
        """Create basic dialogue tree for an NPC"""
        dialogue = {}
        
        # Start node
        dialogue["start"] = DialogueNode(
            id="start",
            text=f"{npc.get_greeting()}\n\nWhat brings you here?",
            choices=[
                DialogueChoice(text="Tell me about this place.", next_node="about"),
                DialogueChoice(text="Do you have any work for me?", 
                             action=DialogueAction.START_QUEST,
                             condition={"has_quests": True}),
                DialogueChoice(text="I should go.", next_node="end")
            ]
        )
        
        # About node
        dialogue["about"] = DialogueNode(
            id="about",
            text="This place has a long history. Many adventurers have passed through here...",
            choices=[
                DialogueChoice(text="Interesting.", next_node="start"),
                DialogueChoice(text="Goodbye.", next_node="end")
            ]
        )
        
        # End node
        dialogue["end"] = DialogueNode(
            id="end",
            text="Farewell, traveler. May your journey be safe.",
            choices=[]
        )
        
        # Skill fail node
        dialogue["skill_fail"] = DialogueNode(
            id="skill_fail",
            text="You don't seem skilled enough for that...",
            choices=[
                DialogueChoice(text="I see.", next_node="start")
            ]
        )
        
        return dialogue
    
    def get_npc(self, npc_id: str) -> Optional[NPC]:
        """Get NPC by ID"""
        return self.npcs.get(npc_id)
    
    def get_npcs_at_location(self, location_id: str) -> List[NPC]:
        """Get all NPCs at a location"""
        return [npc for npc in self.npcs.values() if npc.location == location_id]
    
    def register_npc(self, npc_data: Dict[str, Any]) -> bool:
        """Register a new NPC from plugin data"""
        try:
            npc = NPC(
                id=npc_data["id"],
                name=npc_data["name"],
                description=npc_data["description"],
                npc_type=NPCType(npc_data.get("npc_type", "villager")),
                location=npc_data.get("location", ""),
                quest_giver=npc_data.get("quest_giver", False),
                shop_id=npc_data.get("shop_id", ""),
                shop_items=npc_data.get("shop_items", []),
                buy_multiplier=npc_data.get("buy_multiplier", 1.0),
                sell_multiplier=npc_data.get("sell_multiplier", 0.5),
                services=npc_data.get("services", []),
                can_train=npc_data.get("can_train", []),
                training_cost=npc_data.get("training_cost", 100),
                friendship_max=npc_data.get("friendship_max", 100)
            )
            
            # Add dialogue tree
            npc.dialogue_tree = self._create_basic_dialogue(npc)
            
            # Store custom data
            npc.custom_data = {
                "dialogue": npc_data.get("dialogue", {}),
                "special_abilities": npc_data.get("special_abilities", {}),
                "arena_levels": npc_data.get("arena_levels", []),
                "prophecies": npc_data.get("prophecies", []),
                "guide_services": npc_data.get("guide_services", {}),
                "mining_jobs": npc_data.get("mining_jobs", []),
                "blessing_types": npc_data.get("blessing_types", []),
                "temple_trials": npc_data.get("temple_trials", []),
                "dragon_preparation": npc_data.get("dragon_preparation", {}),
                "fortune_prices": npc_data.get("fortune_prices", {}),
                "wish_system": npc_data.get("wish_system", {}),
                "class_advancement": npc_data.get("class_advancement", {}),
                "friendship_rewards": npc_data.get("friendship_rewards", {})
            }
            
            self.npcs[npc.id] = npc
            print(f"  [Extended NPCs] Registered: {npc.name}")
            return True
            
        except Exception as e:
            print(f"  [Extended NPCs] Error registering NPC {npc_data.get('id', 'unknown')}: {e}")
            return False
    
    def register_npcs(self, npcs_data: Dict[str, Dict[str, Any]]) -> int:
        """Register multiple NPCs from plugin data. Returns count of successful registrations."""
        count = 0
        for npc_id, npc_data in npcs_data.items():
            npc_data["id"] = npc_id
            if self.register_npc(npc_data):
                count += 1
        return count
    
    def interact(self, npc_id: str, player: 'Character') -> Tuple[bool, str]:
        """Start interaction with NPC"""
        npc = self.get_npc(npc_id)
        if not npc:
            return False, "NPC not found."
        
        npc.current_node = "start"
        return True, npc.get_display()
    
    def to_dict(self) -> Dict:
        return {
            "npcs": {k: v.to_dict() for k, v in self.npcs.items()}
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'NPCManager':
        nm = cls.__new__(cls)
        nm.npcs = {k: NPC.from_dict(v) for k, v in data.get("npcs", {}).items()}
        nm._init_npcs()
        # Restore friendship levels
        for npc_id, npc_data in data.get("npcs", {}).items():
            if npc_id in nm.npcs:
                nm.npcs[npc_id].friendship = npc_data.get("friendship", 0)
        return nm


print("NPC system loaded successfully!")

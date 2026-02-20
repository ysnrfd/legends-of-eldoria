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

from core.engine import StatType

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
    can_train: List[str] = field(default_factory=list)
    training_cost: int = 100
    special_dialogue: Dict[str, str] = field(default_factory=dict)
    
    def get_greeting(self) -> str:
        """Get NPC greeting based on friendship"""
        if self.friendship >= 80:
            return f"{self.name} greets you warmly: 'Welcome back, friend!'"
        elif self.friendship >= 50:
            return f"{self.name} smiles: 'Good to see you again.'"
        elif self.friendship >= 20:
            return f"{self.name} nods: 'Hello.'"
        else:
            return f"{self.name} looks at you neutrally: 'What do you want?'"
    
    def get_interactions(self) -> List[str]:
        """Get available interaction options"""
        options = []
        
        if self.dialogue_tree:
            options.append("[1] Talk")
        
        if self.shop_id or self.shop_items:
            options.append("[2] Trade")
        
        if "heal" in self.services:
            options.append("[3] Heal (50 gold)")
        
        if "rest" in self.services:
            options.append("[4] Rest")
        
        if self.can_train:
            options.append(f"[5] Train ({self.training_cost} gold)")
        
        options.append("[0] Leave")
        
        return options
    
    def get_dialogue(self) -> Optional[DialogueNode]:
        """Get current dialogue node"""
        return self.dialogue_tree.get(self.current_node)
    
    def advance_dialogue(self, choice_index: int, player: 'Character', quest_manager=None) -> Tuple[DialogueAction, Any]:
        """Advance dialogue based on choice"""
        node = self.get_dialogue()
        if not node or choice_index >= len(node.choices):
            return DialogueAction.NONE, {}
        
        choice = node.choices[choice_index]
        
        # Check skill check if present
        if choice.skill_check:
            stat_type, dc = choice.skill_check
            roll = random.randint(1, 20)
            stat_bonus = player.stats.get_modifier(stat_type)
            total = roll + stat_bonus
            
            if total >= dc:
                return choice.action, choice.action_data
            else:
                return DialogueAction.NONE, {"message": f"Failed {stat_type.value} check (rolled {total} vs DC {dc})"}
        
        # Move to next node if specified
        if choice.next_node:
            self.current_node = choice.next_node
        
        return choice.action, choice.action_data
    
    def change_friendship(self, amount: int) -> Tuple[bool, str]:
        """Change friendship level"""
        old_level = self.friendship
        self.friendship = max(0, min(self.friendship_max, self.friendship + amount))
        
        if amount > 0:
            return True, f"Friendship with {self.name} increased!"
        elif amount < 0:
            return True, f"Friendship with {self.name} decreased."
        return False, ""
    
    def get_display(self) -> str:
        """Get NPC display"""
        lines = [
            f"\n{'='*50}",
            f"NPC: {self.name}",
            f"{'='*50}",
            f"{self.description}",
            f"",
            f"Type: {self.npc_type.value.replace('_', ' ').title()}",
            f"Friendship: {self.friendship}/{self.friendship_max}",
        ]
        
        if self.shop_items:
            lines.append(f"Shop Items: {len(self.shop_items)}")
        
        if self.services:
            lines.append(f"Services: {', '.join(self.services)}")
        
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
        return cls(
            id=data["id"],
            name=data["name"],
            description=data["description"],
            npc_type=NPCType(data.get("npc_type", "villager")),
            location=data.get("location", ""),
            current_node=data.get("current_node", "start"),
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


class NPCManager:
    """Manages all NPCs in the game"""
    
    def __init__(self):
        self.npcs: Dict[str, NPC] = {}
        self._init_npcs()
    
    def _init_npcs(self):
        """Initialize default NPCs"""
        default_npcs = {
            "village_elder": NPC(
                id="village_elder",
                name="Elder Thomas",
                description="The wise elder of Willowbrook Village.",
                npc_type=NPCType.QUEST_GIVER,
                location="start_village",
                quest_giver=True,
                services=["heal"],
                dialogue_tree={
                    "start": DialogueNode(
                        id="start",
                        text="Welcome to Willowbrook, traveler. What brings you to our humble village?",
                        choices=[
                            DialogueChoice(
                                text="I'm looking for adventure.",
                                next_node="adventure",
                                action=DialogueAction.NONE
                            ),
                            DialogueChoice(
                                text="Do you have any work for me?",
                                action=DialogueAction.START_QUEST,
                                action_data={"quest_id": "first_steps"}
                            ),
                            DialogueChoice(
                                text="Goodbye.",
                                action=DialogueAction.NONE
                            )
                        ]
                    ),
                    "adventure": DialogueNode(
                        id="adventure",
                        text="The world is full of dangers and treasures. Be careful out there.",
                        choices=[
                            DialogueChoice(
                                text="Tell me more about the dangers.",
                                next_node="dangers"
                            ),
                            DialogueChoice(
                                text="Where can I find treasure?",
                                next_node="treasure"
                            ),
                            DialogueChoice(
                                text="Thank you for the advice.",
                                action=DialogueAction.NONE
                            )
                        ]
                    ),
                    "dangers": DialogueNode(
                        id="dangers",
                        text="Goblins roam the forests to the east, and ancient ruins hold undead horrors. Tread carefully.",
                        choices=[
                            DialogueChoice(
                                text="I'll be careful. Goodbye.",
                                action=DialogueAction.NONE
                            )
                        ]
                    ),
                    "treasure": DialogueNode(
                        id="treasure",
                        text="Rumors speak of a dragon's hoard in the mountains, but few return from such quests.",
                        choices=[
                            DialogueChoice(
                                text="Perhaps I'll seek it one day. Goodbye.",
                                action=DialogueAction.NONE
                            )
                        ]
                    )
                }
            ),
            "village_merchant": NPC(
                id="village_merchant",
                name="Merchant Gina",
                description="A friendly merchant who trades goods.",
                npc_type=NPCType.MERCHANT,
                location="start_village",
                shop_items=["health_potion_minor", "iron_sword", "leather_armor", "herb"],
                services=["rest"],
                dialogue_tree={
                    "start": DialogueNode(
                        id="start",
                        text="Welcome to my shop! I have the finest goods in the village.",
                        choices=[
                            DialogueChoice(
                                text="Show me your wares.",
                                action=DialogueAction.OPEN_SHOP
                            ),
                            DialogueChoice(
                                text="Goodbye.",
                                action=DialogueAction.NONE
                            )
                        ]
                    )
                }
            ),
            "village_guard": NPC(
                id="village_guard",
                name="Guard Captain",
                description="The captain of the village guard.",
                npc_type=NPCType.GUARD,
                location="start_village",
                can_train=["Swordsmanship"],
                dialogue_tree={
                    "start": DialogueNode(
                        id="start",
                        text="Halt! State your business in Willowbrook.",
                        choices=[
                            DialogueChoice(
                                text="I'm just a traveler passing through.",
                                next_node="traveler"
                            ),
                            DialogueChoice(
                                text="I'd like to train with you.",
                                action=DialogueAction.TRAIN
                            ),
                            DialogueChoice(
                                text="Goodbye.",
                                action=DialogueAction.NONE
                            )
                        ]
                    ),
                    "traveler": DialogueNode(
                        id="traveler",
                        text="Very well. Keep the peace and cause no trouble.",
                        choices=[
                            DialogueChoice(
                                text="I will. Goodbye.",
                                action=DialogueAction.NONE
                            )
                        ]
                    )
                }
            ),
            "mysterious_stranger": NPC(
                id="mysterious_stranger",
                name="Hooded Figure",
                description="A mysterious figure cloaked in shadows.",
                npc_type=NPCType.MYSTERIOUS,
                location="start_village",
                quest_giver=True,
                dialogue_tree={
                    "start": DialogueNode(
                        id="start",
                        text="*The figure whispers* I have... special items for those who can afford them.",
                        choices=[
                            DialogueChoice(
                                text="What kind of items?",
                                next_node="items"
                            ),
                            DialogueChoice(
                                text="I don't trust you.",
                                action=DialogueAction.NONE
                            ),
                            DialogueChoice(
                                text="Goodbye.",
                                action=DialogueAction.NONE
                            )
                        ]
                    ),
                    "items": DialogueNode(
                        id="items",
                        text="Things that cannot be found in ordinary shops. Information, artifacts... services.",
                        choices=[
                            DialogueChoice(
                                text="Tell me more.",
                                action=DialogueAction.START_QUEST,
                                action_data={"quest_id": "shadow_dealings"}
                            ),
                            DialogueChoice(
                                text="No thanks.",
                                action=DialogueAction.NONE
                            )
                        ]
                    )
                }
            )
        }
        
        for npc_id, npc in default_npcs.items():
            self.npcs[npc_id] = npc
    
    def get_npc(self, npc_id: str) -> Optional[NPC]:
        """Get NPC by ID"""
        return self.npcs.get(npc_id)
    
    def get_npcs_at_location(self, location_id: str) -> List[NPC]:
        """Get all NPCs at a location"""
        return [npc for npc in self.npcs.values() if npc.location == location_id]
    
    def register_npc(self, npc_data: Dict[str, Any]) -> bool:
        """Register a new NPC from plugin data"""
        try:
            npc = NPC.from_dict(npc_data)
            self.npcs[npc.id] = npc
            return True
        except Exception as e:
            print(f"Error registering NPC {npc_data.get('id', 'unknown')}: {e}")
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

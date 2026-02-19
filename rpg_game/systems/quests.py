"""
Quest System - Dynamic Quests, Objectives, and Rewards
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any, Callable, Set, TYPE_CHECKING
from enum import Enum
import sys
import os
import random
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.engine import QuestStatus, EventType, Rarity


class QuestType(Enum):
    MAIN = "main"
    SIDE = "side"
    DAILY = "daily"
    REPEATABLE = "repeatable"
    BOSS = "boss"
    EXPLORATION = "exploration"
    COLLECTION = "collection"
    ESCORT = "escort"
    DELIVERY = "delivery"
    HUNT = "hunt"
    PUZZLE = "puzzle"


class ObjectiveType(Enum):
    KILL = "kill"
    COLLECT = "collect"
    TALK = "talk"
    REACH = "reach"
    USE_ITEM = "use_item"
    CRAFT = "craft"
    ESCORT = "escort"
    SURVIVE = "survive"
    DEFEAT_BOSS = "defeat_boss"
    DISCOVER = "discover"
    CUSTOM = "custom"


@dataclass
class QuestObjective:
    """A single objective within a quest"""
    objective_type: ObjectiveType
    target: str
    required: int
    current: int = 0
    description: str = ""
    
    def is_complete(self) -> bool:
        return self.current >= self.required
    
    def progress(self, amount: int = 1) -> int:
        """Add progress and return new value"""
        self.current = min(self.required, self.current + amount)
        return self.current
    
    def get_progress_text(self) -> str:
        if self.is_complete():
            return f"✅ {self.description}"
        return f"⏳ {self.description} ({self.current}/{self.required})"
    
    def to_dict(self) -> Dict:
        return {
            "objective_type": self.objective_type.value,
            "target": self.target,
            "required": self.required,
            "current": self.current,
            "description": self.description
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'QuestObjective':
        return cls(
            objective_type=ObjectiveType(data["objective_type"]),
            target=data["target"],
            required=data["required"],
            current=data.get("current", 0),
            description=data.get("description", "")
        )


@dataclass
class QuestReward:
    """Rewards for completing a quest"""
    experience: int = 0
    gold: int = 0
    items: List[str] = field(default_factory=list)
    reputation: Dict[str, int] = field(default_factory=dict)
    skill_experience: Dict[str, int] = field(default_factory=dict)
    unlocks: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict:
        return {
            "experience": self.experience,
            "gold": self.gold,
            "items": self.items,
            "reputation": self.reputation,
            "skill_experience": self.skill_experience,
            "unlocks": self.unlocks
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'QuestReward':
        return cls(
            experience=data.get("experience", 0),
            gold=data.get("gold", 0),
            items=data.get("items", []),
            reputation=data.get("reputation", {}),
            skill_experience=data.get("skill_experience", {}),
            unlocks=data.get("unlocks", [])
        )


@dataclass
class Quest:
    """A quest with objectives and rewards"""
    id: str
    name: str
    description: str
    quest_type: QuestType
    status: QuestStatus = QuestStatus.LOCKED
    objectives: List[QuestObjective] = field(default_factory=list)
    rewards: QuestReward = field(default_factory=QuestReward)
    prerequisites: List[str] = field(default_factory=list)
    level_required: int = 1
    time_limit: int = 0  # 0 = no limit, otherwise turns
    giver: str = ""
    location: str = ""
    dialogue_start: str = ""
    dialogue_progress: str = ""
    dialogue_complete: str = ""
    next_quests: List[str] = field(default_factory=list)
    failure_conditions: Dict[str, Any] = field(default_factory=dict)
    
    def start(self) -> bool:
        """Start the quest"""
        if self.status != QuestStatus.AVAILABLE:
            return False
        self.status = QuestStatus.IN_PROGRESS
        return True
    
    def complete(self) -> bool:
        """Complete the quest"""
        if self.status != QuestStatus.IN_PROGRESS:
            return False
        if not self.is_complete():
            return False
        self.status = QuestStatus.COMPLETED
        return True
    
    def fail(self):
        """Fail the quest"""
        self.status = QuestStatus.FAILED
    
    def is_complete(self) -> bool:
        """Check if all objectives are complete"""
        return all(obj.is_complete() for obj in self.objectives)
    
    def update_objective(self, objective_type: ObjectiveType, target: str, amount: int = 1) -> bool:
        """Update an objective's progress"""
        updated = False
        for obj in self.objectives:
            if obj.objective_type == objective_type and obj.target == target:
                if not obj.is_complete():
                    obj.progress(amount)
                    updated = True
        return updated
    
    def get_progress(self) -> Tuple[int, int]:
        """Get quest progress (completed, total)"""
        completed = sum(1 for obj in self.objectives if obj.is_complete())
        return completed, len(self.objectives)
    
    def get_display(self) -> str:
        """Get formatted quest display"""
        lines = [
            f"\n{'='*60}",
            f"[{self.quest_type.value.upper()}] {self.name}",
            f"{'='*60}",
            f"{self.description}",
            f"",
            f"Status: {self.status.value.title()}",
            f""
        ]
        
        if self.objectives:
            lines.append("Objectives:")
            for obj in self.objectives:
                lines.append(f"  {obj.get_progress_text()}")
        
        lines.append(f"\nRewards:")
        if self.rewards.experience:
            lines.append(f"  • {self.rewards.experience} XP")
        if self.rewards.gold:
            lines.append(f"  • {self.rewards.gold} Gold")
        if self.rewards.items:
            for item in self.rewards.items:
                lines.append(f"  • {item}")
        
        return "\n".join(lines)
    
    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "quest_type": self.quest_type.value,
            "status": self.status.value,
            "objectives": [obj.to_dict() for obj in self.objectives],
            "rewards": self.rewards.to_dict(),
            "prerequisites": self.prerequisites,
            "level_required": self.level_required,
            "time_limit": self.time_limit,
            "giver": self.giver,
            "location": self.location,
            "dialogue_start": self.dialogue_start,
            "dialogue_progress": self.dialogue_progress,
            "dialogue_complete": self.dialogue_complete,
            "next_quests": self.next_quests,
            "failure_conditions": self.failure_conditions
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Quest':
        return cls(
            id=data["id"],
            name=data["name"],
            description=data["description"],
            quest_type=QuestType(data["quest_type"]),
            status=QuestStatus(data["status"]),
            objectives=[QuestObjective.from_dict(obj) for obj in data.get("objectives", [])],
            rewards=QuestReward.from_dict(data.get("rewards", {})),
            prerequisites=data.get("prerequisites", []),
            level_required=data.get("level_required", 1),
            time_limit=data.get("time_limit", 0),
            giver=data.get("giver", ""),
            location=data.get("location", ""),
            dialogue_start=data.get("dialogue_start", ""),
            dialogue_progress=data.get("dialogue_progress", ""),
            dialogue_complete=data.get("dialogue_complete", ""),
            next_quests=data.get("next_quests", []),
            failure_conditions=data.get("failure_conditions", {})
        )


class QuestManager:
    """Manages all quests in the game"""
    
    def __init__(self):
        self.quests: Dict[str, Quest] = {}
        self.completed_quests: Set[str] = set()
        self.active_quests: Set[str] = set()
        self._init_quests()
    
    def _init_quests(self):
        """Initialize predefined quests"""
        quests_data = [
            # Main Story Quests
            {
                "id": "main_001",
                "name": "The Beginning",
                "description": "You've arrived in Willowbrook Village. Speak with Elder Thorne "
                             "to learn about recent troubles in the region.",
                "quest_type": QuestType.MAIN,
                "objectives": [
                    QuestObjective(ObjectiveType.TALK, "elder_thorne", 1, 0, "Speak with Elder Thorne")
                ],
                "rewards": QuestReward(experience=50, gold=25),
                "giver": "intro",
                "location": "start_village",
                "next_quests": ["main_002"]
            },
            {
                "id": "main_002",
                "name": "Goblin Menace",
                "description": "Goblins have been raiding the village outskirts. "
                             "Clear out the goblin camp in the Whispering Woods.",
                "quest_type": QuestType.MAIN,
                "prerequisites": ["main_001"],
                "level_required": 2,
                "objectives": [
                    QuestObjective(ObjectiveType.KILL, "goblin", 5, 0, "Defeat goblins"),
                    QuestObjective(ObjectiveType.KILL, "goblin_chieftain", 1, 0, "Defeat the Goblin Chieftain")
                ],
                "rewards": QuestReward(experience=150, gold=100, items=["iron_sword"]),
                "giver": "elder_thorne",
                "location": "start_village",
                "next_quests": ["main_003"]
            },
            {
                "id": "main_003",
                "name": "The King's Request",
                "description": "Elder Thorne has received a royal summons. Travel to the capital "
                             "and speak with the King's advisor about growing darkness.",
                "quest_type": QuestType.MAIN,
                "prerequisites": ["main_002"],
                "level_required": 5,
                "objectives": [
                    QuestObjective(ObjectiveType.REACH, "capital_city", 1, 0, "Travel to the capital"),
                    QuestObjective(ObjectiveType.TALK, "royal_advisor", 1, 0, "Speak with the Royal Advisor")
                ],
                "rewards": QuestReward(experience=300, gold=200),
                "giver": "elder_thorne",
                "location": "start_village",
                "next_quests": ["main_004"]
            },
            {
                "id": "main_004",
                "name": "Temple of Shadows",
                "description": "Ancient evil stirs in the Temple of the Forgotten God. "
                             "Investigate and put an end to whatever darkness lurks within.",
                "quest_type": QuestType.MAIN,
                "prerequisites": ["main_003"],
                "level_required": 10,
                "objectives": [
                    QuestObjective(ObjectiveType.REACH, "ancient_temple", 1, 0, "Find the ancient temple"),
                    QuestObjective(ObjectiveType.DEFEAT_BOSS, "forgotten_priest", 1, 0, "Defeat the Forgotten Priest")
                ],
                "rewards": QuestReward(
                    experience=1000, gold=500, 
                    items=["flame_blade", "rare_gem"],
                    unlocks=["temple_treasure"]
                ),
                "giver": "royal_advisor",
                "location": "capital_city",
                "next_quests": ["main_005"]
            },
            {
                "id": "main_005",
                "name": "Dragon's Legacy",
                "description": "The ancient dragon awakens. Gather allies and prepare for "
                             "the ultimate battle to save the realm.",
                "quest_type": QuestType.MAIN,
                "prerequisites": ["main_004"],
                "level_required": 20,
                "objectives": [
                    QuestObjective(ObjectiveType.TALK, "dragon_expert", 1, 0, "Consult the Dragon Expert"),
                    QuestObjective(ObjectiveType.COLLECT, "dragon_artifact", 3, 0, "Collect Dragon Artifacts"),
                    QuestObjective(ObjectiveType.DEFEAT_BOSS, "ancient_dragon", 1, 0, "Defeat the Ancient Dragon")
                ],
                "rewards": QuestReward(
                    experience=5000, gold=10000,
                    items=["dragon_scale_armor", "excalibur"],
                    unlocks=["true_ending"]
                ),
                "giver": "king_aldric",
                "location": "royal_castle"
            },
            
            # Side Quests
            {
                "id": "side_herbs",
                "name": "Healer's Request",
                "description": "Healer Rose needs healing herbs from the Whispering Woods.",
                "quest_type": QuestType.SIDE,
                "level_required": 1,
                "objectives": [
                    QuestObjective(ObjectiveType.COLLECT, "healing_herb", 10, 0, "Gather healing herbs")
                ],
                "rewards": QuestReward(experience=50, gold=30, items=["health_potion", "health_potion"]),
                "giver": "healer_rose",
                "location": "start_village"
            },
            {
                "id": "side_blacksmith",
                "name": "Ore for the Forge",
                "description": "Blacksmith Gareth needs iron ore to craft new equipment.",
                "quest_type": QuestType.SIDE,
                "level_required": 3,
                "objectives": [
                    QuestObjective(ObjectiveType.COLLECT, "iron_ore", 15, 0, "Mine iron ore"),
                    QuestObjective(ObjectiveType.TALK, "blacksmith_gareth", 1, 0, "Return to Gareth")
                ],
                "rewards": QuestReward(experience=100, gold=75, items=["steel_greatsword"]),
                "giver": "blacksmith_gareth",
                "location": "start_village"
            },
            {
                "id": "side_wolves",
                "name": "Wolf Pack Problem",
                "description": "Wolves have been attacking livestock. Thin their numbers.",
                "quest_type": QuestType.SIDE,
                "level_required": 2,
                "objectives": [
                    QuestObjective(ObjectiveType.KILL, "wolf", 10, 0, "Hunt wolves")
                ],
                "rewards": QuestReward(experience=80, gold=50),
                "giver": "farmer_john",
                "location": "start_village"
            },
            {
                "id": "side_explorer",
                "name": "Cartographer's Request",
                "description": "A cartographer wants you to explore and map new locations.",
                "quest_type": QuestType.EXPLORATION,
                "level_required": 5,
                "objectives": [
                    QuestObjective(ObjectiveType.DISCOVER, "new_location", 5, 0, "Discover new locations")
                ],
                "rewards": QuestReward(experience=200, gold=150, items=["map", "compass"]),
                "giver": "cartographer",
                "location": "capital_city"
            },
            {
                "id": "side_dungeon",
                "name": "Dungeon Depths",
                "description": "Descend into the Endless Dungeon and clear 5 floors.",
                "quest_type": QuestType.BOSS,
                "level_required": 5,
                "objectives": [
                    QuestObjective(ObjectiveType.CUSTOM, "dungeon_floor", 5, 0, "Clear 5 dungeon floors")
                ],
                "rewards": QuestReward(experience=500, gold=300, items=["rare_chest_key"]),
                "giver": "guild_master",
                "location": "capital_city"
            },
            {
                "id": "side_treasure",
                "name": "Buried Treasure",
                "description": "Follow the clues to find a legendary treasure.",
                "quest_type": QuestType.EXPLORATION,
                "level_required": 8,
                "objectives": [
                    QuestObjective(ObjectiveType.REACH, "treasure_location_1", 1, 0, "Find the first clue"),
                    QuestObjective(ObjectiveType.REACH, "treasure_location_2", 1, 0, "Find the second clue"),
                    QuestObjective(ObjectiveType.REACH, "treasure_location_3", 1, 0, "Find the treasure")
                ],
                "rewards": QuestReward(experience=300, gold=1000, items=["legendary_gem"]),
                "giver": "mysterious_stranger",
                "location": "crossroads"
            },
            
            # Daily Quests
            {
                "id": "daily_monsters",
                "name": "Daily Monster Hunt",
                "description": "Help keep the roads safe by defeating monsters.",
                "quest_type": QuestType.DAILY,
                "level_required": 1,
                "objectives": [
                    QuestObjective(ObjectiveType.KILL, "any_monster", 5, 0, "Defeat 5 monsters")
                ],
                "rewards": QuestReward(experience=50, gold=25),
                "giver": "guild_board",
                "location": "capital_city"
            },
            {
                "id": "daily_gathering",
                "name": "Daily Gathering",
                "description": "Collect crafting materials for the guild.",
                "quest_type": QuestType.DAILY,
                "level_required": 1,
                "objectives": [
                    QuestObjective(ObjectiveType.COLLECT, "any_material", 10, 0, "Gather 10 materials")
                ],
                "rewards": QuestReward(experience=30, gold=20),
                "giver": "guild_board",
                "location": "capital_city"
            }
        ]
        
        for quest_data in quests_data:
            quest = Quest(
                id=quest_data["id"],
                name=quest_data["name"],
                description=quest_data["description"],
                quest_type=quest_data["quest_type"],
                objectives=quest_data.get("objectives", []),
                rewards=quest_data.get("rewards", QuestReward()),
                prerequisites=quest_data.get("prerequisites", []),
                level_required=quest_data.get("level_required", 1),
                time_limit=quest_data.get("time_limit", 0),
                giver=quest_data.get("giver", ""),
                location=quest_data.get("location", ""),
                dialogue_start=quest_data.get("dialogue_start", ""),
                dialogue_progress=quest_data.get("dialogue_progress", ""),
                dialogue_complete=quest_data.get("dialogue_complete", ""),
                next_quests=quest_data.get("next_quests", [])
            )
            self.quests[quest.id] = quest
    
    def update_quest_availability(self, completed_quests: Set[str], player_level: int):
        """Update quest availability based on prerequisites"""
        for quest_id, quest in self.quests.items():
            if quest.status == QuestStatus.LOCKED:
                # Check prerequisites
                prereqs_met = all(pq in completed_quests for pq in quest.prerequisites)
                level_met = player_level >= quest.level_required
                
                if prereqs_met and level_met:
                    quest.status = QuestStatus.AVAILABLE
    
    def get_available_quests(self, location: str = None) -> List[Quest]:
        """Get quests available to start"""
        quests = [
            q for q in self.quests.values()
            if q.status == QuestStatus.AVAILABLE
        ]
        if location:
            quests = [q for q in quests if q.location == location or not q.location]
        return quests
    
    def get_active_quests(self) -> List[Quest]:
        """Get currently active quests"""
        return [self.quests[qid] for qid in self.active_quests if qid in self.quests]
    
    def start_quest(self, quest_id: str) -> Tuple[bool, str]:
        """Start a quest"""
        quest = self.quests.get(quest_id)
        if not quest:
            return False, "Quest not found."
        
        if quest.status != QuestStatus.AVAILABLE:
            return False, "Quest is not available."
        
        if quest.start():
            self.active_quests.add(quest_id)
            return True, f"Started quest: {quest.name}"
        
        return False, "Could not start quest."
    
    def update_objective(self, objective_type: ObjectiveType, target: str, amount: int = 1):
        """Update all active quests with matching objective"""
        completed_quests = []
        
        for quest_id in list(self.active_quests):
            quest = self.quests.get(quest_id)
            if quest and quest.status == QuestStatus.IN_PROGRESS:
                updated = quest.update_objective(objective_type, target, amount)
                
                if updated and quest.is_complete():
                    completed_quests.append(quest)
        
        return completed_quests
    
    def complete_quest(self, quest_id: str) -> Tuple[bool, Quest]:
        """Complete a quest"""
        quest = self.quests.get(quest_id)
        if not quest:
            return False, None
        
        if quest.complete():
            self.active_quests.discard(quest_id)
            self.completed_quests.add(quest_id)
            
            # Unlock next quests
            for next_id in quest.next_quests:
                if next_id in self.quests:
                    self.quests[next_id].status = QuestStatus.AVAILABLE
            
            return True, quest
        
        return False, None
    
    def get_quest_display(self) -> str:
        """Get display of all quests"""
        lines = [f"\n{'='*60}", "QUEST LOG", f"{'='*60}"]
        
        active = self.get_active_quests()
        if active:
            lines.append("\nActive Quests:")
            for quest in active:
                completed, total = quest.get_progress()
                lines.append(f"  • {quest.name} [{completed}/{total}]")
        
        available = self.get_available_quests()
        if available:
            lines.append("\nAvailable Quests:")
            for quest in available:
                lines.append(f"  ○ {quest.name} (Lv.{quest.level_required})")
        
        if self.completed_quests:
            lines.append(f"\nCompleted: {len(self.completed_quests)} quests")
        
        if not active and not available and not self.completed_quests:
            lines.append("\nNo quests available.")
        
        return "\n".join(lines)
    
    def to_dict(self) -> Dict:
        return {
            "quests": {k: v.to_dict() for k, v in self.quests.items()},
            "completed_quests": list(self.completed_quests),
            "active_quests": list(self.active_quests)
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'QuestManager':
        qm = cls.__new__(cls)
        qm.quests = {k: Quest.from_dict(v) for k, v in data.get("quests", {}).items()}
        qm.completed_quests = set(data.get("completed_quests", []))
        qm.active_quests = set(data.get("active_quests", []))
        return qm


print("Quest system loaded successfully!")

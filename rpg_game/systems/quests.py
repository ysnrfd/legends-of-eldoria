"""
Quest System - Dynamic Quests, Objectives, and Rewards
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Set
from enum import Enum
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.engine import QuestStatus


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
    unlock_quests: List[str] = field(default_factory=list)
    unlock_locations: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict:
        return {
            "experience": self.experience,
            "gold": self.gold,
            "items": self.items,
            "reputation": self.reputation,
            "skill_experience": self.skill_experience,
            "unlock_quests": self.unlock_quests,
            "unlock_locations": self.unlock_locations
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'QuestReward':
        return cls(
            experience=data.get("experience", 0),
            gold=data.get("gold", 0),
            items=data.get("items", []),
            reputation=data.get("reputation", {}),
            skill_experience=data.get("skill_experience", {}),
            unlock_quests=data.get("unlock_quests", []),
            unlock_locations=data.get("unlock_locations", [])
        )


@dataclass
class Quest:
    """A quest with objectives and rewards"""
    id: str
    name: str
    description: str
    quest_type: QuestType
    level_required: int = 1
    objectives: List[QuestObjective] = field(default_factory=list)
    rewards: QuestReward = field(default_factory=QuestReward)
    giver: str = ""
    location: str = ""
    status: QuestStatus = QuestStatus.AVAILABLE
    prerequisites: List[str] = field(default_factory=list)
    next_quests: List[str] = field(default_factory=list)
    time_limit: int = 0  # 0 = no limit
    is_repeatable: bool = False
    completion_count: int = 0
    
    def is_complete(self) -> bool:
        """Check if all objectives are complete"""
        return all(obj.is_complete() for obj in self.objectives)
    
    def update_objective(self, objective_type: ObjectiveType, target: str, amount: int = 1) -> bool:
        """Update an objective and return True if any progress was made"""
        updated = False
        for objective in self.objectives:
            if objective.objective_type == objective_type and objective.target == target:
                if not objective.is_complete():
                    objective.progress(amount)
                    updated = True
        return updated
    
    def get_progress(self) -> Tuple[int, int]:
        """Get (completed, total) objectives"""
        completed = sum(1 for obj in self.objectives if obj.is_complete())
        return completed, len(self.objectives)
    
    def get_display(self) -> str:
        """Get quest display"""
        lines = [
            f"\n{'='*60}",
            f"QUEST: {self.name}",
            f"{'='*60}",
            f"{self.description}",
            f"",
            f"Type: {self.quest_type.value.title()}",
            f"Status: {self.status.value.replace('_', ' ').title()}",
            f"",
            "Objectives:"
        ]
        
        for obj in self.objectives:
            lines.append(f"  {obj.get_progress_text()}")
        
        lines.append("")
        lines.append("Rewards:")
        if self.rewards.experience > 0:
            lines.append(f"  • {self.rewards.experience} Experience")
        if self.rewards.gold > 0:
            lines.append(f"  • {self.rewards.gold} Gold")
        for item_id in self.rewards.items:
            lines.append(f"  • {item_id.replace('_', ' ').title()}")
        
        return "\n".join(lines)
    
    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "quest_type": self.quest_type.value,
            "level_required": self.level_required,
            "objectives": [obj.to_dict() for obj in self.objectives],
            "rewards": self.rewards.to_dict(),
            "giver": self.giver,
            "location": self.location,
            "status": self.status.value,
            "prerequisites": self.prerequisites,
            "next_quests": self.next_quests,
            "time_limit": self.time_limit,
            "is_repeatable": self.is_repeatable,
            "completion_count": self.completion_count
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Quest':
        return cls(
            id=data["id"],
            name=data["name"],
            description=data["description"],
            quest_type=QuestType(data["quest_type"]),
            level_required=data.get("level_required", 1),
            objectives=[QuestObjective.from_dict(obj) for obj in data.get("objectives", [])],
            rewards=QuestReward.from_dict(data.get("rewards", {})),
            giver=data.get("giver", ""),
            location=data.get("location", ""),
            status=QuestStatus(data.get("status", "available")),
            prerequisites=data.get("prerequisites", []),
            next_quests=data.get("next_quests", []),
            time_limit=data.get("time_limit", 0),
            is_repeatable=data.get("is_repeatable", False),
            completion_count=data.get("completion_count", 0)
        )


class QuestManager:
    """Manages all quests in the game"""
    
    def __init__(self):
        self.quests: Dict[str, Quest] = {}
        self.completed_quests: Set[str] = set()
        self.active_quests: Set[str] = set()
        self._init_quests()
    
    def _init_quests(self):
        """Initialize default quests"""
        default_quests = {
            "first_steps": Quest(
                id="first_steps",
                name="First Steps",
                description="The village elder wants you to prove yourself by defeating some goblins in the nearby forest.",
                quest_type=QuestType.SIDE,
                level_required=1,
                giver="village_elder",
                location="start_village",
                objectives=[
                    QuestObjective(
                        objective_type=ObjectiveType.KILL,
                        target="goblin",
                        required=3,
                        description="Defeat 3 goblins in the Whispering Woods"
                    )
                ],
                rewards=QuestReward(
                    experience=100,
                    gold=50,
                    items=["health_potion_minor"],
                    reputation={"village_elder": 10}
                ),
                next_quests=["deeper_threats"]
            ),
            "deeper_threats": Quest(
                id="deeper_threats",
                name="Deeper Threats",
                description="Goblins are just the beginning. Darker forces stir in the ruins to the east.",
                quest_type=QuestType.MAIN,
                level_required=3,
                giver="village_elder",
                location="start_village",
                objectives=[
                    QuestObjective(
                        objective_type=ObjectiveType.REACH,
                        target="ruins",
                        required=1,
                        description="Explore the Ancient Ruins"
                    ),
                    QuestObjective(
                        objective_type=ObjectiveType.KILL,
                        target="skeleton",
                        required=5,
                        description="Defeat 5 skeletons"
                    )
                ],
                rewards=QuestReward(
                    experience=300,
                    gold=150,
                    items=["steel_sword"],
                    reputation={"village_elder": 20},
                    unlock_locations=["temple"]
                ),
                prerequisites=["first_steps"]
            ),
            "shadow_dealings": Quest(
                id="shadow_dealings",
                name="Shadow Dealings",
                description="The mysterious stranger has a dangerous proposal. Are you willing to get your hands dirty?",
                quest_type=QuestType.SIDE,
                level_required=5,
                giver="mysterious_stranger",
                location="start_village",
                objectives=[
                    QuestObjective(
                        objective_type=ObjectiveType.COLLECT,
                        target="magic_essence",
                        required=5,
                        description="Collect 5 Magic Essence from dark mages"
                    ),
                    QuestObjective(
                        objective_type=ObjectiveType.TALK,
                        target="mysterious_stranger",
                        required=1,
                        description="Return to the Hooded Figure"
                    )
                ],
                rewards=QuestReward(
                    experience=500,
                    gold=300,
                    items=["shadow_dagger"],
                    reputation={"mysterious_stranger": 15}
                )
            ),
            "dragon_slayer": Quest(
                id="dragon_slayer",
                name="Dragon Slayer",
                description="An ancient dragon threatens the realm. Only a true hero can defeat it.",
                quest_type=QuestType.BOSS,
                level_required=25,
                giver="king",
                location="capital_city",
                objectives=[
                    QuestObjective(
                        objective_type=ObjectiveType.REACH,
                        target="dragon_peak",
                        required=1,
                        description="Journey to Dragon's Peak"
                    ),
                    QuestObjective(
                        objective_type=ObjectiveType.DEFEAT_BOSS,
                        target="ancient_dragon",
                        required=1,
                        description="Defeat the Ancient Dragon"
                    )
                ],
                rewards=QuestReward(
                    experience=5000,
                    gold=10000,
                    items=["legendary_blade", "dragon_scale_armor"],
                    reputation={"king": 100, "realm": 50}
                )
            )
        }
        
        for quest_id, quest in default_quests.items():
            self.quests[quest_id] = quest
    
    def get_quest(self, quest_id: str) -> Optional[Quest]:
        """Get quest by ID"""
        return self.quests.get(quest_id)
    
    def get_active_quests(self) -> List[Quest]:
        """Get all active quests"""
        return [self.quests[qid] for qid in self.active_quests if qid in self.quests]
    
    def get_available_quests(self, location: str = None) -> List[Quest]:
        """Get all available quests"""
        available = []
        for quest in self.quests.values():
            if quest.status == QuestStatus.AVAILABLE:
                if location is None or quest.location == location:
                    available.append(quest)
        return available
    
    def update_quest_availability(self, completed_quests: Set[str], player_level: int):
        """Update quest availability based on player progress and level"""
        for quest in self.quests.values():
            # Skip if already completed or in progress
            if quest.status in (QuestStatus.COMPLETED, QuestStatus.IN_PROGRESS):
                continue
            
            # Check if all prerequisites are met
            prerequisites_met = all(prereq in completed_quests for prereq in quest.prerequisites)
            
            # Check if level requirement is met
            level_met = player_level >= quest.level_required
            
            # Update status to available if both conditions are met
            if prerequisites_met and level_met:
                quest.status = QuestStatus.AVAILABLE
    
    def get_completed_quests(self) -> List[Quest]:
        """Get all completed quests"""
        return [self.quests[qid] for qid in self.completed_quests if qid in self.quests]
    
    def start_quest(self, quest_id: str) -> Tuple[bool, str]:
        """Start a quest"""
        quest = self.quests.get(quest_id)
        if not quest:
            return False, "Quest not found."
        
        if quest.status != QuestStatus.AVAILABLE:
            return False, f"Quest is not available (status: {quest.status.value})"
        
        # Check prerequisites
        for prereq in quest.prerequisites:
            if prereq not in self.completed_quests:
                return False, f"Prerequisite quest not completed: {prereq}"
        
        quest.status = QuestStatus.IN_PROGRESS
        self.active_quests.add(quest_id)
        
        return True, f"Started quest: {quest.name}"
    
    def update_objective(self, objective_type: ObjectiveType, target: str, amount: int = 1) -> List[Quest]:
        """Update objectives across all active quests"""
        completed_quests = []
        
        for quest_id in self.active_quests:
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

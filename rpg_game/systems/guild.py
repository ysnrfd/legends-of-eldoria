"""
Guild System - Player organizations with shared resources and missions

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


class GuildRank(Enum):
    """Ranks within a guild"""
    RECRUIT = ("Recruit", 0)
    MEMBER = ("Member", 1)
    VETERAN = ("Veteran", 2)
    OFFICER = ("Officer", 3)
    LEADER = ("Leader", 4)
    
    def __init__(self, display_name: str, level: int):
        self.display_name = display_name
        self.level = level


class GuildPermission(Enum):
    """Permissions for guild ranks"""
    INVITE = "invite"
    KICK = "kick"
    PROMOTE = "promote"
    DEMOTE = "demote"
    BANK_DEPOSIT = "bank_deposit"
    BANK_WITHDRAW = "bank_withdraw"
    MISSION_START = "mission_start"
    UPGRADE_GUILD = "upgrade_guild"
    EDIT_MOTD = "edit_motd"


@dataclass
class GuildMember:
    """A member of a guild"""
    character_id: str
    character_name: str
    rank: GuildRank
    joined_at: float
    contribution_points: int = 0
    last_online: float = 0
    is_online: bool = False
    
    def to_dict(self) -> Dict:
        return {
            "character_id": self.character_id,
            "character_name": self.character_name,
            "rank": self.rank.value,
            "joined_at": self.joined_at,
            "contribution_points": self.contribution_points,
            "last_online": self.last_online,
            "is_online": self.is_online
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'GuildMember':
        return cls(
            character_id=data["character_id"],
            character_name=data["character_name"],
            rank=GuildRank(data["rank"]),
            joined_at=data["joined_at"],
            contribution_points=data.get("contribution_points", 0),
            last_online=data.get("last_online", 0),
            is_online=data.get("is_online", False)
        )


@dataclass
class GuildMission:
    """A guild mission/quest"""
    id: str
    name: str
    description: str
    difficulty: int
    required_members: int
    rewards: Dict[str, Any]
    time_limit: int  # in minutes
    objectives: List[Dict[str, Any]]
    is_active: bool = False
    started_at: Optional[float] = None
    completed_by: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "difficulty": self.difficulty,
            "required_members": self.required_members,
            "rewards": self.rewards,
            "time_limit": self.time_limit,
            "objectives": self.objectives,
            "is_active": self.is_active,
            "started_at": self.started_at,
            "completed_by": self.completed_by
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'GuildMission':
        return cls(
            id=data["id"],
            name=data["name"],
            description=data["description"],
            difficulty=data["difficulty"],
            required_members=data["required_members"],
            rewards=data["rewards"],
            time_limit=data["time_limit"],
            objectives=data["objectives"],
            is_active=data.get("is_active", False),
            started_at=data.get("started_at"),
            completed_by=data.get("completed_by", [])
        )


@dataclass
class Guild:
    """A player guild"""
    id: str
    name: str
    tag: str  # Short abbreviation like [GUILD]
    description: str
    leader_id: str
    created_at: float
    level: int = 1
    experience: int = 0
    members: Dict[str, GuildMember] = field(default_factory=dict)
    bank_gold: int = 0
    bank_items: List[Dict[str, Any]] = field(default_factory=list)
    motd: str = "Welcome to the guild!"
    permissions: Dict[str, List[GuildPermission]] = field(default_factory=dict)
    active_mission: Optional[str] = None
    completed_missions: int = 0
    total_contributions: int = 0
    max_members: int = 20
    upgrades: List[str] = field(default_factory=list)
    
    def __post_init__(self):
        # Set default permissions if not set
        if not self.permissions:
            self.permissions = {
                GuildRank.RECRUIT.value: [GuildPermission.BANK_DEPOSIT],
                GuildRank.MEMBER.value: [GuildPermission.BANK_DEPOSIT, GuildPermission.BANK_WITHDRAW],
                GuildRank.VETERAN.value: [GuildPermission.BANK_DEPOSIT, GuildPermission.BANK_WITHDRAW, 
                                         GuildPermission.INVITE, GuildPermission.MISSION_START],
                GuildRank.OFFICER.value: [GuildPermission.BANK_DEPOSIT, GuildPermission.BANK_WITHDRAW,
                                         GuildPermission.INVITE, GuildPermission.KICK, 
                                         GuildPermission.PROMOTE, GuildPermission.DEMOTE,
                                         GuildPermission.MISSION_START, GuildPermission.EDIT_MOTD],
                GuildRank.LEADER.value: list(GuildPermission)  # All permissions
            }
    
    def get_member(self, character_id: str) -> Optional[GuildMember]:
        """Get a guild member by character ID"""
        return self.members.get(character_id)
    
    def add_member(self, character: 'Character', rank: GuildRank = GuildRank.RECRUIT) -> Tuple[bool, str]:
        """Add a new member to the guild"""
        if len(self.members) >= self.max_members:
            return False, "Guild is full."
        
        if character.id in self.members:
            return False, "Already a member."
        
        member = GuildMember(
            character_id=character.id,
            character_name=character.name,
            rank=rank,
            joined_at=time.time(),
            last_online=time.time(),
            is_online=True
        )
        
        self.members[character.id] = member
        return True, f"Welcome to {self.name}, {character.name}!"
    
    def remove_member(self, character_id: str) -> Tuple[bool, str]:
        """Remove a member from the guild"""
        if character_id not in self.members:
            return False, "Not a member."
        
        member = self.members[character_id]
        if member.rank == GuildRank.LEADER:
            return False, "Cannot remove the guild leader."
        
        del self.members[character_id]
        return True, "Member removed."
    
    def promote_member(self, character_id: str) -> Tuple[bool, str]:
        """Promote a member to next rank"""
        if character_id not in self.members:
            return False, "Not a member."
        
        member = self.members[character_id]
        current_rank = member.rank
        
        if current_rank == GuildRank.LEADER:
            return False, "Already at highest rank."
        
        # Get next rank
        ranks = list(GuildRank)
        next_rank = ranks[ranks.index(current_rank) + 1]
        
        member.rank = next_rank
        return True, f"Promoted to {next_rank.display_name}!"
    
    def demote_member(self, character_id: str) -> Tuple[bool, str]:
        """Demote a member to previous rank"""
        if character_id not in self.members:
            return False, "Not a member."
        
        member = self.members[character_id]
        current_rank = member.rank
        
        if current_rank == GuildRank.RECRUIT:
            return False, "Already at lowest rank."
        
        # Get previous rank
        ranks = list(GuildRank)
        prev_rank = ranks[ranks.index(current_rank) - 1]
        
        member.rank = prev_rank
        return True, f"Demoted to {prev_rank.display_name}."
    
    def has_permission(self, character_id: str, permission: GuildPermission) -> bool:
        """Check if member has a specific permission"""
        member = self.members.get(character_id)
        if not member:
            return False
        
        allowed_permissions = self.permissions.get(member.rank.value, [])
        return permission in allowed_permissions
    
    def deposit_gold(self, character_id: str, amount: int) -> Tuple[bool, str]:
        """Deposit gold into guild bank"""
        if not self.has_permission(character_id, GuildPermission.BANK_DEPOSIT):
            return False, "No permission to deposit."
        
        self.bank_gold += amount
        self.total_contributions += amount
        
        # Add contribution points to member
        member = self.members.get(character_id)
        if member:
            member.contribution_points += amount
        
        return True, f"Deposited {amount} gold. Guild bank: {self.bank_gold}"
    
    def withdraw_gold(self, character_id: str, amount: int) -> Tuple[bool, str]:
        """Withdraw gold from guild bank"""
        if not self.has_permission(character_id, GuildPermission.BANK_WITHDRAW):
            return False, "No permission to withdraw."
        
        if self.bank_gold < amount:
            return False, "Not enough gold in guild bank."
        
        self.bank_gold -= amount
        return True, f"Withdrew {amount} gold. Guild bank: {self.bank_gold}"
    
    def add_experience(self, amount: int) -> bool:
        """Add experience to guild and check for level up"""
        self.experience += amount
        
        exp_needed = self.get_exp_to_level()
        if self.experience >= exp_needed and self.level < 10:
            self.experience -= exp_needed
            self.level += 1
            self.max_members += 5  # More members per level
            return True
        return False
    
    def get_exp_to_level(self) -> int:
        """Calculate experience needed for next guild level"""
        return int(1000 * (1.5 ** (self.level - 1)))
    
    def get_display(self) -> str:
        """Get formatted guild display"""
        lines = [
            f"\n{'='*60}",
            f"[{self.tag}] {self.name}",
            f"{'='*60}",
            f"Level: {self.level} (EXP: {self.experience}/{self.get_exp_to_level()})",
            f"Members: {len(self.members)}/{self.max_members}",
            f"Leader: {self.members.get(self.leader_id, GuildMember('', 'Unknown', GuildRank.LEADER, 0)).character_name}",
            f"",
            f"Message of the Day:",
            f"  {self.motd}",
            f"",
            f"Guild Bank: {format_number(self.bank_gold)} gold",
            f"Total Contributions: {format_number(self.total_contributions)}",
            f"Completed Missions: {self.completed_missions}",
        ]
        
        if self.upgrades:
            lines.append(f"\nUpgrades: {', '.join(self.upgrades)}")
        
        # Show online members
        online = [m for m in self.members.values() if m.is_online]
        lines.append(f"\nOnline Members ({len(online)}):")
        for member in online[:10]:  # Show first 10
            lines.append(f"  • {member.character_name} [{member.rank.display_name}]")
        
        if len(online) > 10:
            lines.append(f"  ... and {len(online) - 10} more")
        
        return "\n".join(lines)
    
    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "name": self.name,
            "tag": self.tag,
            "description": self.description,
            "leader_id": self.leader_id,
            "created_at": self.created_at,
            "level": self.level,
            "experience": self.experience,
            "members": {k: v.to_dict() for k, v in self.members.items()},
            "bank_gold": self.bank_gold,
            "bank_items": self.bank_items,
            "motd": self.motd,
            "permissions": {k: [p.value for p in v] for k, v in self.permissions.items()},
            "active_mission": self.active_mission,
            "completed_missions": self.completed_missions,
            "total_contributions": self.total_contributions,
            "max_members": self.max_members,
            "upgrades": self.upgrades
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Guild':
        guild = cls(
            id=data["id"],
            name=data["name"],
            tag=data["tag"],
            description=data["description"],
            leader_id=data["leader_id"],
            created_at=data["created_at"],
            level=data.get("level", 1),
            experience=data.get("experience", 0),
            bank_gold=data.get("bank_gold", 0),
            bank_items=data.get("bank_items", []),
            motd=data.get("motd", "Welcome!"),
            active_mission=data.get("active_mission"),
            completed_missions=data.get("completed_missions", 0),
            total_contributions=data.get("total_contributions", 0),
            max_members=data.get("max_members", 20),
            upgrades=data.get("upgrades", [])
        )
        
        # Restore members
        guild.members = {k: GuildMember.from_dict(v) for k, v in data.get("members", {}).items()}
        
        # Restore permissions
        guild.permissions = {}
        for rank_value, perms in data.get("permissions", {}).items():
            guild.permissions[rank_value] = [GuildPermission(p) for p in perms]
        
        return guild


class GuildManager:
    """Manages all guilds"""
    
    def __init__(self):
        self.guilds: Dict[str, Guild] = {}
        self.missions: Dict[str, GuildMission] = {}
        self._init_missions()
    
    def _init_missions(self):
        """Initialize default guild missions"""
        default_missions = {
            "dungeon_assault": GuildMission(
                id="dungeon_assault",
                name="Dungeon Assault",
                description="Clear a random dungeon floor with guild members.",
                difficulty=3,
                required_members=3,
                rewards={"gold": 1000, "exp": 500, "guild_exp": 200},
                time_limit=60,
                objectives=[{"type": "clear_dungeon", "target": "any", "required": 1}]
            ),
            "world_boss": GuildMission(
                id="world_boss",
                name="World Boss Hunt",
                description="Defeat a powerful world boss together.",
                difficulty=5,
                required_members=5,
                rewards={"gold": 5000, "exp": 2000, "guild_exp": 500, "rare_item": True},
                time_limit=120,
                objectives=[{"type": "defeat_boss", "target": "world_boss", "required": 1}]
            ),
            "resource_gathering": GuildMission(
                id="resource_gathering",
                name="Resource Gathering",
                description="Collect resources for the guild.",
                difficulty=1,
                required_members=2,
                rewards={"gold": 500, "exp": 200, "guild_exp": 100},
                time_limit=30,
                objectives=[{"type": "collect", "target": "any_material", "required": 50}]
            ),
            "territory_defense": GuildMission(
                id="territory_defense",
                name="Territory Defense",
                description="Defend guild territory from invaders.",
                difficulty=4,
                required_members=4,
                rewards={"gold": 2000, "exp": 1000, "guild_exp": 300},
                time_limit=90,
                objectives=[{"type": "defend", "target": "waves", "required": 5}]
            )
        }
        
        for mission_id, mission in default_missions.items():
            self.missions[mission_id] = mission
    
    def create_guild(self, name: str, tag: str, description: str, leader: 'Character') -> Tuple[bool, str, Optional[Guild]]:
        """Create a new guild"""
        # Validate name and tag
        if len(name) < 3 or len(name) > 30:
            return False, "Guild name must be 3-30 characters.", None
        
        if len(tag) < 2 or len(tag) > 5:
            return False, "Guild tag must be 2-5 characters.", None
        
        # Check if name/tag exists
        for guild in self.guilds.values():
            if guild.name.lower() == name.lower():
                return False, "Guild name already exists.", None
            if guild.tag.lower() == tag.lower():
                return False, "Guild tag already exists.", None
        
        # Check if leader is already in a guild
        for guild in self.guilds.values():
            if leader.id in guild.members:
                return False, "You are already in a guild.", None
        
        # Create guild
        import hashlib
        guild_id = hashlib.md5(f"{name}{time.time()}".encode()).hexdigest()[:8]
        
        guild = Guild(
            id=guild_id,
            name=name,
            tag=tag.upper(),
            description=description,
            leader_id=leader.id,
            created_at=time.time()
        )
        
        # Add leader as member
        guild.add_member(leader, GuildRank.LEADER)
        
        self.guilds[guild_id] = guild
        return True, f"Guild '{name}' created successfully!", guild
    
    def get_guild(self, guild_id: str) -> Optional[Guild]:
        """Get guild by ID"""
        return self.guilds.get(guild_id)
    
    def get_character_guild(self, character_id: str) -> Optional[Guild]:
        """Get guild that character belongs to"""
        for guild in self.guilds.values():
            if character_id in guild.members:
                return guild
        return None
    
    def disband_guild(self, guild_id: str, character_id: str) -> Tuple[bool, str]:
        """Disband a guild (only leader can do this)"""
        guild = self.guilds.get(guild_id)
        if not guild:
            return False, "Guild not found."
        
        if guild.leader_id != character_id:
            return False, "Only the guild leader can disband."
        
        del self.guilds[guild_id]
        return True, f"Guild '{guild.name}' has been disbanded."
    
    def get_available_missions(self, guild_level: int) -> List[GuildMission]:
        """Get missions available for guild level"""
        return [m for m in self.missions.values() if m.difficulty <= guild_level + 2]
    
    def to_dict(self) -> Dict:
        return {
            "guilds": {k: v.to_dict() for k, v in self.guilds.items()},
            "missions": {k: v.to_dict() for k, v in self.missions.items()}
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'GuildManager':
        gm = cls.__new__(cls)
        gm.guilds = {k: Guild.from_dict(v) for k, v in data.get("guilds", {}).items()}
        gm.missions = {k: GuildMission.from_dict(v) for k, v in data.get("missions", {}).items()}
        return gm


print("Guild system loaded successfully!")

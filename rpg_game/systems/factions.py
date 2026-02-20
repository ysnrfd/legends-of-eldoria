"""
Faction System - Joinable organizations with reputation and benefits

Author: YSNRFD
Version: 1.0.0
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any, Set, TYPE_CHECKING
from enum import Enum
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.engine import Rarity, colored_text

if TYPE_CHECKING:
    from core.character import Character


class FactionType(Enum):
    """Types of factions"""
    KINGDOM = "kingdom"
    GUILD = "guild"
    CULT = "cult"
    TRIBE = "tribe"
    ORDER = "order"
    MERCHANT_COMPANY = "merchant_company"
    MILITARY = "military"
    RELIGIOUS = "religious"
    CRIMINAL = "criminal"
    SCHOLARLY = "scholarly"


class FactionRelation(Enum):
    """Relationship between factions"""
    ALLY = "ally"
    NEUTRAL = "neutral"
    ENEMY = "enemy"
    WAR = "war"


class FactionRank(Enum):
    """Ranks within a faction"""
    OUTCAST = ("Outcast", -100, -50)
    HOSTILE = ("Hostile", -50, -20)
    UNFRIENDLY = ("Unfriendly", -20, 0)
    NEUTRAL = ("Neutral", 0, 10)
    FRIENDLY = ("Friendly", 10, 25)
    HONORED = ("Honored", 25, 50)
    REVERED = ("Revered", 50, 100)
    EXALTED = ("Exalted", 100, 999999)

    def __init__(self, display_name: str, min_rep: int, max_rep: int):
        self.display_name = display_name
        self.min_rep = min_rep
        self.max_rep = max_rep


@dataclass
class Faction:
    """A joinable faction"""
    id: str
    name: str
    description: str
    faction_type: FactionType
    leader: str = ""
    headquarters: str = ""
    territory: List[str] = field(default_factory=list)
    enemies: List[str] = field(default_factory=list)
    allies: List[str] = field(default_factory=list)
    shops: List[str] = field(default_factory=list)
    quests: List[str] = field(default_factory=list)
    benefits: Dict[str, Any] = field(default_factory=dict)
    requirements: Dict[str, Any] = field(default_factory=dict)
    is_joinable: bool = True
    color_code: str = "\033[94m"  # Default blue
    
    def get_relation(self, reputation: int) -> FactionRank:
        """Get faction rank based on reputation"""
        for rank in FactionRank:
            if rank.min_rep <= reputation < rank.max_rep:
                return rank
        return FactionRank.NEUTRAL
    
    def get_shop_discount(self, reputation: int) -> float:
        """Get shop discount based on reputation"""
        rank = self.get_relation(reputation)
        discounts = {
            FactionRank.OUTCAST: 1.5,      # 50% more expensive
            FactionRank.HOSTILE: 1.25,     # 25% more expensive
            FactionRank.UNFRIENDLY: 1.1,   # 10% more expensive
            FactionRank.NEUTRAL: 1.0,      # Normal price
            FactionRank.FRIENDLY: 0.9,     # 10% discount
            FactionRank.HONORED: 0.8,      # 20% discount
            FactionRank.REVERED: 0.7,      # 30% discount
            FactionRank.EXALTED: 0.6,      # 40% discount
        }
        return discounts.get(rank, 1.0)
    
    def can_join(self, character: 'Character') -> Tuple[bool, str]:
        """Check if character can join this faction"""
        # Check level requirement
        min_level = self.requirements.get("level", 1)
        if character.level < min_level:
            return False, f"Requires level {min_level}"
        
        # Check reputation requirement
        min_rep = self.requirements.get("reputation", 0)
        current_rep = character.reputation.get(self.id, 0)
        if current_rep < min_rep:
            return False, f"Requires {min_rep} reputation (you have {current_rep})"
        
        # Check class requirement
        required_class = self.requirements.get("class")
        if required_class and character.character_class.value != required_class:
            return False, f"Requires {required_class} class"
        
        # Check if enemy of allies
        for ally_id in self.allies:
            ally_rep = character.reputation.get(ally_id, 0)
            if ally_rep < -20:  # Hostile to ally
                return False, f"Cannot join - hostile to ally faction"
        
        return True, "Can join"
    
    def get_display(self, player_reputation: int = 0) -> str:
        """Get formatted faction display"""
        rank = self.get_relation(player_reputation)
        
        lines = [
            f"\n{'='*60}",
            f"{self.color_code}{self.name}\033[0m",
            f"{'='*60}",
            f"Type: {self.faction_type.value.replace('_', ' ').title()}",
            f"Leader: {self.leader}",
            f"Headquarters: {self.headquarters}",
            f"",
            f"Your Status: {rank.display_name} ({player_reputation} rep)",
            f"Shop Discount: {int((1 - self.get_shop_discount(player_reputation)) * 100)}%",
            f"",
            f"Description:",
            f"{self.description}",
        ]
        
        if self.territory:
            lines.append(f"\nTerritory: {', '.join(self.territory)}")
        
        if self.allies:
            lines.append(f"Allies: {', '.join(self.allies)}")
        
        if self.enemies:
            lines.append(f"Enemies: {', '.join(self.enemies)}")
        
        # Show benefits at current rank
        rank_benefits = self.benefits.get(rank.name.lower(), [])
        if rank_benefits:
            lines.append(f"\nBenefits at {rank.display_name}:")
            for benefit in rank_benefits:
                lines.append(f"  • {benefit}")
        
        return "\n".join(lines)
    
    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "faction_type": self.faction_type.value,
            "leader": self.leader,
            "headquarters": self.headquarters,
            "territory": self.territory,
            "enemies": self.enemies,
            "allies": self.allies,
            "shops": self.shops,
            "quests": self.quests,
            "benefits": self.benefits,
            "requirements": self.requirements,
            "is_joinable": self.is_joinable,
            "color_code": self.color_code
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Faction':
        return cls(
            id=data["id"],
            name=data["name"],
            description=data["description"],
            faction_type=FactionType(data["faction_type"]),
            leader=data.get("leader", ""),
            headquarters=data.get("headquarters", ""),
            territory=data.get("territory", []),
            enemies=data.get("enemies", []),
            allies=data.get("allies", []),
            shops=data.get("shops", []),
            quests=data.get("quests", []),
            benefits=data.get("benefits", {}),
            requirements=data.get("requirements", {}),
            is_joinable=data.get("is_joinable", True),
            color_code=data.get("color_code", "\033[94m")
        )


class FactionManager:
    """Manages all factions and player reputation"""
    
    def __init__(self):
        self.factions: Dict[str, Faction] = {}
        self.faction_wars: List[Tuple[str, str]] = []  # Pairs of warring factions
        self._init_factions()
    
    def _init_factions(self):
        """Initialize default factions"""
        default_factions = {
            # Kingdoms
            "kingdom_aldor": Faction(
                id="kingdom_aldor",
                name="Kingdom of Aldor",
                description="The largest human kingdom, known for its strong military and prosperous cities.",
                faction_type=FactionType.KINGDOM,
                leader="King Aldric III",
                headquarters="capital_city",
                territory=["capital_city", "trade_road", "start_village"],
                allies=["guild_merchants", "order_paladins"],
                enemies=["cult_shadows", "tribe_orks"],
                shops=["royal_armory", "royal_apothecary"],
                quests=["defend_the_realm", "royal_delivery"],
                benefits={
                    "friendly": ["Access to Royal Shops"],
                    "honored": ["10% Discount", "Royal Guard Assistance"],
                    "revered": ["20% Discount", "Access to Royal Vault"],
                    "exalted": ["30% Discount", "Noble Title", "Castle Access"]
                },
                requirements={"level": 5},
                color_code="\033[93m"  # Gold
            ),
            
            "kingdom_valoria": Faction(
                id="kingdom_valoria",
                name="Kingdom of Valoria",
                description="A rival kingdom to the north, focused on magic and scholarship.",
                faction_type=FactionType.KINGDOM,
                leader="Queen Elara",
                headquarters="valoria_city",
                territory=["valoria_city", "mystic_sanctuary"],
                allies=["order_mages", "scholarly_academy"],
                enemies=["kingdom_aldor", "cult_shadows"],
                shops=["magic_emporium", "arcane_library"],
                quests=["magical_research", "arcane_defense"],
                benefits={
                    "friendly": ["Access to Magic Shops"],
                    "honored": ["Magic Training", "Spell Discounts"],
                    "revered": ["Rare Spell Access", "Arcane Knowledge"],
                    "exalted": ["Archmage Title", "Legendary Spells"]
                },
                requirements={"level": 8, "class": "Mage"},
                color_code="\033[96m"  # Cyan
            ),
            
            # Guilds
            "guild_merchants": Faction(
                id="guild_merchants",
                name="Merchant's Guild",
                description="A powerful organization of traders and businessmen.",
                faction_type=FactionType.GUILD,
                leader="Guild Master Thorne",
                headquarters="capital_city",
                territory=["capital_city", "trade_road"],
                allies=["kingdom_aldor"],
                enemies=["criminal_thieves"],
                shops=["guild_market", "auction_house"],
                quests=["trade_route", "rare_goods"],
                benefits={
                    "friendly": ["Better Trade Prices"],
                    "honored": ["Guild Bank Access", "Investment Options"],
                    "revered": ["Exclusive Goods", "Trade Secrets"],
                    "exalted": ["Guild Master Title", "Trade Monopoly"]
                },
                requirements={"level": 3},
                color_code="\033[92m"  # Green
            ),
            
            "guild_adventurers": Faction(
                id="guild_adventurers",
                name="Adventurer's Guild",
                description="An organization for brave souls who seek fortune and glory.",
                faction_type=FactionType.GUILD,
                leader="Grand Master Vex",
                headquarters="capital_city",
                territory=["capital_city", "all_dungeons"],
                allies=["kingdom_aldor", "kingdom_valoria"],
                enemies=["cult_shadows", "criminal_thieves"],
                shops=["adventurer_supplies", "dungeon_maps"],
                quests=["dungeon_exploration", "monster_hunts", "treasure_recovery"],
                benefits={
                    "friendly": ["Quest Board Access"],
                    "honored": ["Healing Services", "Equipment Repair"],
                    "revered": ["Rare Quests", "Guild Hall Access"],
                    "exalted": ["Guild Leader Title", "Legendary Quests"]
                },
                requirements={"level": 1},
                color_code="\033[91m"  # Red
            ),
            
            # Religious Orders
            "order_paladins": Faction(
                id="order_paladins",
                name="Order of the Radiant Light",
                description="Holy warriors dedicated to protecting the innocent.",
                faction_type=FactionType.ORDER,
                leader="Grand Paladin Michael",
                headquarters="temple",
                territory=["temple", "capital_city"],
                allies=["kingdom_aldor", "religious_temple"],
                enemies=["cult_shadows", "undead_horde"],
                shops=["holy_reliquary", "blessed_armory"],
                quests=["undead_slaying", "holy_crusade", "temple_defense"],
                benefits={
                    "friendly": ["Holy Blessing"],
                    "honored": ["Divine Protection", "Healing Discount"],
                    "revered": ["Holy Weapons", "Sacred Knowledge"],
                    "exalted": ["Paladin Title", "Divine Mount"]
                },
                requirements={"level": 10, "class": "Paladin"},
                color_code="\033[97m"  # White
            ),
            
            "order_mages": Faction(
                id="order_mages",
                name="Order of the Arcane",
                description="An organization of mages dedicated to magical research.",
                faction_type=FactionType.ORDER,
                leader="Archmage Zephos",
                headquarters="mystic_sanctuary",
                territory=["mystic_sanctuary", "valoria_city"],
                allies=["kingdom_valoria", "scholarly_academy"],
                enemies=["cult_shadows"],
                shops=["arcane_library", "magical_components"],
                quests=["magical_research", "artifact_recovery"],
                benefits={
                    "friendly": ["Library Access"],
                    "honored": ["Spell Training", "Component Discounts"],
                    "revered": ["Rare Spells", "Arcane Secrets"],
                    "exalted": ["Archmage Title", "Legendary Magic"]
                },
                requirements={"level": 8, "class": "Mage"},
                color_code="\033[95m"  # Magenta
            ),
            
            # Criminal
            "criminal_thieves": Faction(
                id="criminal_thieves",
                name="Thieves' Guild",
                description="A secret organization of rogues and criminals.",
                faction_type=FactionType.CRIMINAL,
                leader="The Shadow Master",
                headquarters="hidden",
                territory=["underground", "shadow_district"],
                allies=[],
                enemies=["kingdom_aldor", "guild_merchants", "guild_adventurers"],
                shops=["black_market", "stolen_goods"],
                quests=["heist", "assassination", "smuggling"],
                benefits={
                    "friendly": ["Black Market Access"],
                    "honored": ["Lockpicking Training", "Poison Recipes"],
                    "revered": ["Master Thief Tools", "Assassin Contracts"],
                    "exalted": ["Shadow Master Title", "Guild Leadership"]
                },
                requirements={"level": 5, "class": "Rogue"},
                is_joinable=True,
                color_code="\033[90m"  # Gray
            ),
            
            # Cults
            "cult_shadows": Faction(
                id="cult_shadows",
                name="Cult of Shadows",
                description="A dark cult that worships forbidden powers.",
                faction_type=FactionType.CULT,
                leader="The Shadow Lord",
                headquarters="forgotten_temple",
                territory=["underground_ruins", "dark_forest"],
                allies=["undead_horde"],
                enemies=["kingdom_aldor", "kingdom_valoria", "order_paladins", "order_mages"],
                shops=["dark_reliquary", "forbidden_knowledge"],
                quests=["dark_ritual", "corruption", "summoning"],
                benefits={
                    "friendly": ["Dark Magic Access"],
                    "honored": ["Shadow Powers", "Forbidden Knowledge"],
                    "revered": ["Dark Artifacts", "Demon Summoning"],
                    "exalted": ["Shadow Lord Title", "Immortality Ritual"]
                },
                requirements={"level": 15, "class": "Necromancer"},
                is_joinable=True,
                color_code="\033[91m"  # Dark Red
            ),
        }
        
        for faction_id, faction in default_factions.items():
            self.factions[faction_id] = faction
    
    def get_faction(self, faction_id: str) -> Optional[Faction]:
        """Get faction by ID"""
        return self.factions.get(faction_id)
    
    def get_all_factions(self) -> List[Faction]:
        """Get all factions"""
        return list(self.factions.values())
    
    def get_joinable_factions(self, character: 'Character') -> List[Tuple[Faction, bool, str]]:
        """Get factions character can potentially join with status"""
        result = []
        for faction in self.factions.values():
            if faction.is_joinable:
                can_join, reason = faction.can_join(character)
                result.append((faction, can_join, reason))
        return result
    
    def modify_reputation(self, character: 'Character', faction_id: str, amount: int) -> str:
        """Modify character's reputation with a faction"""
        if faction_id not in self.factions:
            return f"Faction {faction_id} not found."
        
        current_rep = character.reputation.get(faction_id, 0)
        new_rep = current_rep + amount
        character.reputation[faction_id] = new_rep
        
        faction = self.factions[faction_id]
        old_rank = faction.get_relation(current_rep)
        new_rank = faction.get_relation(new_rep)
        
        # Check for rank change
        if old_rank != new_rank:
            if amount > 0:
                return f"Reputation with {faction.name} increased to {new_rank.display_name}!"
            else:
                return f"Reputation with {faction.name} decreased to {new_rank.display_name}!"
        
        return f"Reputation with {faction.name}: {new_rep} ({'+' if amount > 0 else ''}{amount})"
    
    def get_faction_display(self, character: 'Character') -> str:
        """Get display of all factions and their status with player"""
        lines = [
            f"\n{'='*60}",
            "FACTIONS",
            f"{'='*60}"
        ]
        
        for faction in self.factions.values():
            rep = character.reputation.get(faction.id, 0)
            rank = faction.get_relation(rep)
            status = "✓ Member" if faction.id in getattr(character, 'factions', []) else rank.display_name
            lines.append(f"\n{faction.color_code}{faction.name}\033[0m - {status} ({rep} rep)")
            lines.append(f"  Type: {faction.faction_type.value.replace('_', ' ').title()}")
            if faction.headquarters:
                lines.append(f"  HQ: {faction.headquarters}")
        
        return "\n".join(lines)
    
    def declare_war(self, faction1_id: str, faction2_id: str):
        """Declare war between two factions"""
        if faction1_id in self.factions and faction2_id in self.factions:
            self.faction_wars.append((faction1_id, faction2_id))
            
            # Update enemy lists
            f1 = self.factions[faction1_id]
            f2 = self.factions[faction2_id]
            
            if faction2_id not in f1.enemies:
                f1.enemies.append(faction2_id)
            if faction1_id not in f2.enemies:
                f2.enemies.append(faction1_id)
    
    def to_dict(self) -> Dict:
        return {
            "factions": {k: v.to_dict() for k, v in self.factions.items()},
            "faction_wars": self.faction_wars
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'FactionManager':
        fm = cls.__new__(cls)
        fm.factions = {k: Faction.from_dict(v) for k, v in data.get("factions", {}).items()}
        fm.faction_wars = data.get("faction_wars", [])
        return fm


print("Faction system loaded successfully!")

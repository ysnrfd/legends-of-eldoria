"""
Infinite Dungeon System - Endless dungeon with increasing difficulty

Author: YSNRFD
Version: 1.0.0
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any, Set, TYPE_CHECKING
from enum import Enum
import random
import time
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.engine import Rarity, colored_text, format_number, clear_screen
from systems.dungeon_generator import DungeonGenerator, DungeonTheme, RoomType, DungeonRoom

if TYPE_CHECKING:
    from core.character import Character


class InfiniteDungeonMode(Enum):
    """Modes for infinite dungeon"""
    NORMAL = "normal"
    HARDCORE = "hardcore"  # No healing between floors
    TIME_ATTACK = "time_attack"  # Time limit
    ENDLESS = "endless"  # No floor limit


@dataclass
class FloorRecord:
    """Record for a cleared floor"""
    floor_number: int
    clear_time: float  # seconds
    enemies_defeated: int
    damage_taken: int
    damage_dealt: int
    score: int
    perfect_clear: bool  # No damage taken


@dataclass
class InfiniteDungeonRun:
    """A single run through the infinite dungeon"""
    id: str
    player_id: str
    player_name: str
    mode: InfiniteDungeonMode
    current_floor: int = 1
    start_time: float = field(default_factory=time.time)
    total_time: float = 0
    enemies_defeated: int = 0
    bosses_defeated: int = 0
    gold_earned: int = 0
    exp_earned: int = 0
    items_found: List[str] = field(default_factory=list)
    floor_records: List[FloorRecord] = field(default_factory=list)
    is_active: bool = True
    is_completed: bool = False
    death_floor: Optional[int] = None
    highest_floor_reached: int = 1
    total_score: int = 0
    lives_remaining: int = 3
    time_limit: Optional[float] = None  # For time attack mode
    checkpoints_reached: List[int] = field(default_factory=list)
    
    def __post_init__(self):
        if self.mode == InfiniteDungeonMode.TIME_ATTACK and not self.time_limit:
            self.time_limit = 3600  # 1 hour default
    
    @property
    def time_elapsed(self) -> float:
        """Get time elapsed in current run"""
        if not self.is_active:
            return self.total_time
        return time.time() - self.start_time
    
    @property
    def time_remaining(self) -> Optional[float]:
        """Get time remaining for time attack mode"""
        if self.mode != InfiniteDungeonMode.TIME_ATTACK or not self.time_limit:
            return None
        
        remaining = self.time_limit - self.time_elapsed
        return max(0, remaining)
    
    @property
    def is_time_up(self) -> bool:
        """Check if time has run out"""
        if self.mode != InfiniteDungeonMode.TIME_ATTACK:
            return False
        remaining = self.time_remaining
        return remaining is not None and remaining <= 0
    
    def calculate_difficulty(self) -> int:
        """Calculate current difficulty level"""
        base_difficulty = self.current_floor
        
        # Mode multipliers
        if self.mode == InfiniteDungeonMode.HARDCORE:
            base_difficulty = int(base_difficulty * 1.5)
        elif self.mode == InfiniteDungeonMode.ENDLESS:
            base_difficulty = int(base_difficulty * 1.2)
        
        return base_difficulty
    
    def advance_floor(self) -> bool:
        """Advance to next floor"""
        if not self.is_active:
            return False
        
        # Check time limit
        if self.is_time_up:
            self.complete_run(False)
            return False
        
        # Record current floor
        if self.current_floor > 0:
            record = FloorRecord(
                floor_number=self.current_floor,
                clear_time=self.time_elapsed,
                enemies_defeated=self.enemies_defeated,
                damage_taken=0,  # Would track during combat
                damage_dealt=0,
                score=self.calculate_floor_score(),
                perfect_clear=False
            )
            self.floor_records.append(record)
        
        self.current_floor += 1
        
        if self.current_floor > self.highest_floor_reached:
            self.highest_floor_reached = self.current_floor
        
        # Check for checkpoint
        if self.current_floor % 10 == 0:
            self.checkpoints_reached.append(self.current_floor)
            if self.mode == InfiniteDungeonMode.HARDCORE:
                self.lives_remaining += 1  # Bonus life every 10 floors
        
        return True
    
    def calculate_floor_score(self) -> int:
        """Calculate score for current floor"""
        score = self.current_floor * 100
        
        # Bonuses
        if self.mode == InfiniteDungeonMode.HARDCORE:
            score = int(score * 1.5)
        
        # Time bonus (faster = more points)
        time_bonus = max(0, 300 - (self.time_elapsed % 300))  # Bonus for clearing within 5 min
        score += int(time_bonus)
        
        # Enemy bonus
        score += self.enemies_defeated * 10
        
        return score
    
    def update_total_score(self):
        """Update total score from floor records"""
        self.total_score = sum(record.score for record in self.floor_records)
    
    def take_damage(self, damage: int):
        """Record damage taken"""
        if self.mode == InfiniteDungeonMode.HARDCORE:
            # In hardcore, damage reduces lives
            if damage > 50:  # Major damage
                self.lives_remaining -= 1
                if self.lives_remaining <= 0:
                    self.die()
    
    def die(self):
        """Handle player death"""
        self.is_active = False
        self.death_floor = self.current_floor
        self.total_time = self.time_elapsed
        self.update_total_score()
    
    def complete_run(self, success: bool = True):
        """Complete the dungeon run"""
        self.is_active = False
        self.is_completed = success
        self.total_time = self.time_elapsed
        self.update_total_score()
    
    def get_status_display(self) -> str:
        """Get current run status"""
        lines = [
            f"\n{'='*60}",
            "INFINITE DUNGEON",
            f"{'='*60}",
            f"Mode: {self.mode.value.title()}",
            f"Floor: {self.current_floor}",
            f"Time: {self._format_time(self.time_elapsed)}",
        ]
        
        if self.time_remaining is not None:
            lines.append(f"Time Remaining: {self._format_time(self.time_remaining)}")
        
        lines.extend([
            f"Score: {format_number(self.total_score)}",
            f"Enemies Defeated: {self.enemies_defeated}",
            f"Bosses Defeated: {self.bosses_defeated}",
            f"Lives: {self.lives_remaining}",
            f"Gold Earned: {format_number(self.gold_earned)}",
            f"EXP Earned: {format_number(self.exp_earned)}",
        ])
        
        if self.items_found:
            lines.append(f"\nItems Found: {len(self.items_found)}")
        
        return "\n".join(lines)
    
    def _format_time(self, seconds: float) -> str:
        """Format seconds as time string"""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        
        if hours > 0:
            return f"{hours}h {minutes}m {secs}s"
        elif minutes > 0:
            return f"{minutes}m {secs}s"
        else:
            return f"{secs}s"
    
    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "player_id": self.player_id,
            "player_name": self.player_name,
            "mode": self.mode.value,
            "current_floor": self.current_floor,
            "start_time": self.start_time,
            "total_time": self.total_time,
            "enemies_defeated": self.enemies_defeated,
            "bosses_defeated": self.bosses_defeated,
            "gold_earned": self.gold_earned,
            "exp_earned": self.exp_earned,
            "items_found": self.items_found,
            "floor_records": [
                {
                    "floor_number": r.floor_number,
                    "clear_time": r.clear_time,
                    "enemies_defeated": r.enemies_defeated,
                    "damage_taken": r.damage_taken,
                    "damage_dealt": r.damage_dealt,
                    "score": r.score,
                    "perfect_clear": r.perfect_clear
                }
                for r in self.floor_records
            ],
            "is_active": self.is_active,
            "is_completed": self.is_completed,
            "death_floor": self.death_floor,
            "highest_floor_reached": self.highest_floor_reached,
            "total_score": self.total_score,
            "lives_remaining": self.lives_remaining,
            "time_limit": self.time_limit,
            "checkpoints_reached": self.checkpoints_reached
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'InfiniteDungeonRun':
        run = cls(
            id=data["id"],
            player_id=data["player_id"],
            player_name=data["player_name"],
            mode=InfiniteDungeonMode(data["mode"]),
            current_floor=data.get("current_floor", 1),
            start_time=data["start_time"],
            total_time=data.get("total_time", 0),
            enemies_defeated=data.get("enemies_defeated", 0),
            bosses_defeated=data.get("bosses_defeated", 0),
            gold_earned=data.get("gold_earned", 0),
            exp_earned=data.get("exp_earned", 0),
            items_found=data.get("items_found", []),
            is_active=data.get("is_active", True),
            is_completed=data.get("is_completed", False),
            death_floor=data.get("death_floor"),
            highest_floor_reached=data.get("highest_floor_reached", 1),
            total_score=data.get("total_score", 0),
            lives_remaining=data.get("lives_remaining", 3),
            time_limit=data.get("time_limit"),
            checkpoints_reached=data.get("checkpoints_reached", [])
        )
        
        # Restore floor records
        for record_data in data.get("floor_records", []):
            record = FloorRecord(
                floor_number=record_data["floor_number"],
                clear_time=record_data["clear_time"],
                enemies_defeated=record_data["enemies_defeated"],
                damage_taken=record_data["damage_taken"],
                damage_dealt=record_data["damage_dealt"],
                score=record_data["score"],
                perfect_clear=record_data["perfect_clear"]
            )
            run.floor_records.append(record)
        
        return run


class InfiniteDungeon:
    """The infinite dungeon system"""
    
    FLOOR_THEMES = [
        DungeonTheme.CRYPT,
        DungeonTheme.CAVERN,
        DungeonTheme.RUINS,
        DungeonTheme.PRISON,
        DungeonTheme.TEMPLE,
        DungeonTheme.FOREST,
        DungeonTheme.VOLCANO,
        DungeonTheme.ICE,
        DungeonTheme.VOID
    ]
    
    MILESTONE_REWARDS = {
        10: {"title": "Dungeon Crawler", "gold": 1000, "exp": 500},
        25: {"title": "Depth Explorer", "gold": 2500, "exp": 1500},
        50: {"title": "Abyss Walker", "gold": 5000, "exp": 3000, "rare_item": True},
        100: {"title": "Infinite Champion", "gold": 10000, "exp": 5000, "epic_item": True},
        250: {"title": "Legendary Delver", "gold": 25000, "exp": 10000, "legendary_item": True},
        500: {"title": "Dungeon Master", "gold": 50000, "exp": 20000, "mythic_item": True},
        1000: {"title": "Eternal Conqueror", "gold": 100000, "exp": 50000, "divine_item": True}
    }
    
    def __init__(self):
        self.active_runs: Dict[str, InfiniteDungeonRun] = {}  # run_id -> run
        self.player_best_floors: Dict[str, int] = {}  # player_id -> best floor
        self.global_leaderboard: List[Dict[str, Any]] = []
        self.weekly_leaderboard: List[Dict[str, Any]] = []
        self.total_clears: int = 0
    
    def start_run(self, player: 'Character', mode: InfiniteDungeonMode = InfiniteDungeonMode.NORMAL) -> Tuple[bool, str, Optional[InfiniteDungeonRun]]:
        """Start a new infinite dungeon run"""
        # Check if player already has active run
        for run in self.active_runs.values():
            if run.player_id == player.id and run.is_active:
                return False, "You already have an active dungeon run!", None
        
        # Create new run
        import hashlib
        run_id = hashlib.md5(f"{player.id}{time.time()}".encode()).hexdigest()[:12]
        
        run = InfiniteDungeonRun(
            id=run_id,
            player_id=player.id,
            player_name=player.name,
            mode=mode
        )
        
        self.active_runs[run_id] = run
        
        mode_descriptions = {
            InfiniteDungeonMode.NORMAL: "Standard dungeon crawl with checkpoints every 10 floors.",
            InfiniteDungeonMode.HARDCORE: "No healing between floors. Extra lives every 10 floors.",
            InfiniteDungeonMode.TIME_ATTACK: "Race against the clock! Clear as many floors as possible in 1 hour.",
            InfiniteDungeonMode.ENDLESS: "No floor limit. How deep can you go?"
        }
        
        message = f"\n{'='*60}\n"
        message += f"INFINITE DUNGEON - {mode.value.title()} MODE\n"
        message += f"{'='*60}\n"
        message += f"{mode_descriptions[mode]}\n"
        message += f"Good luck, {player.name}!"
        
        return True, message, run
    
    def get_run(self, run_id: str) -> Optional[InfiniteDungeonRun]:
        """Get an active run"""
        return self.active_runs.get(run_id)
    
    def get_player_active_run(self, player_id: str) -> Optional[InfiniteDungeonRun]:
        """Get player's active run"""
        for run in self.active_runs.values():
            if run.player_id == player_id and run.is_active:
                return run
        return None
    
    def generate_floor(self, run: InfiniteDungeonRun) -> Dict[str, Any]:
        """Generate the next floor for a run"""
        difficulty = run.calculate_difficulty()
        
        # Determine theme (cycles through themes)
        theme_index = (run.current_floor - 1) % len(self.FLOOR_THEMES)
        theme = self.FLOOR_THEMES[theme_index]
        
        # Generate floor layout
        from systems.dungeon_generator import DungeonFloor
        floor = DungeonGenerator.generate_floor(run.current_floor, difficulty, theme)
        
        # Scale enemies based on difficulty
        enemy_count = min(3 + (difficulty // 10), 8)
        enemies = self._generate_floor_enemies(difficulty, enemy_count)
        
        # Generate rewards
        rewards = self._calculate_floor_rewards(run)
        
        # Check for boss floor
        is_boss_floor = run.current_floor % 10 == 0
        
        return {
            "floor_number": run.current_floor,
            "theme": theme,
            "difficulty": difficulty,
            "enemies": enemies,
            "rewards": rewards,
            "is_boss_floor": is_boss_floor,
            "layout": floor,
            "special_events": self._generate_special_events(run)
        }
    
    def _generate_floor_enemies(self, difficulty: int, count: int) -> List[Dict[str, Any]]:
        """Generate enemies for a floor"""
        enemies = []
        
        enemy_types = ["goblin", "skeleton", "wolf", "orc_warrior", "dark_mage", 
                      "troll", "vampire", "demon", "dragon_wyrmling"]
        
        # Scale enemy selection based on difficulty
        available_enemies = enemy_types[:min(3 + difficulty // 5, len(enemy_types))]
        
        for _ in range(count):
            enemy_type = random.choice(available_enemies)
            level = max(1, difficulty + random.randint(-2, 2))
            
            enemies.append({
                "type": enemy_type,
                "level": level,
                "elite": random.random() < (difficulty * 0.01),  # Chance increases with difficulty
                "rare": random.random() < (difficulty * 0.005)
            })
        
        return enemies
    
    def _calculate_floor_rewards(self, run: InfiniteDungeonRun) -> Dict[str, Any]:
        """Calculate rewards for clearing a floor"""
        base_gold = 50 * run.current_floor
        base_exp = 25 * run.current_floor
        
        # Mode multipliers
        if run.mode == InfiniteDungeonMode.HARDCORE:
            base_gold = int(base_gold * 1.5)
            base_exp = int(base_exp * 1.5)
        elif run.mode == InfiniteDungeonMode.TIME_ATTACK:
            base_gold = int(base_gold * 1.2)
            base_exp = int(base_exp * 1.2)
        
        # Item chance
        item_chance = min(0.1 + (run.current_floor * 0.001), 0.5)
        
        return {
            "gold": base_gold,
            "exp": base_exp,
            "item_chance": item_chance,
            "chest_quality": self._determine_chest_quality(run.current_floor)
        }
    
    def _determine_chest_quality(self, floor: int) -> str:
        """Determine quality of chest on floor"""
        if floor >= 500:
            return "divine"
        elif floor >= 250:
            return "mythic"
        elif floor >= 100:
            return "legendary"
        elif floor >= 50:
            return "epic"
        elif floor >= 25:
            return "rare"
        elif floor >= 10:
            return "uncommon"
        else:
            return "common"
    
    def _generate_special_events(self, run: InfiniteDungeonRun) -> List[str]:
        """Generate special events for floor"""
        events = []
        
        # Shrine chance
        if random.random() < 0.1:
            events.append("shrine")
        
        # Shop chance
        if random.random() < 0.05:
            events.append("shop")
        
        # Treasure room chance
        if random.random() < 0.08:
            events.append("treasure")
        
        # Challenge room chance (higher floors)
        if run.current_floor > 20 and random.random() < 0.05:
            events.append("challenge")
        
        return events
    
    def clear_floor(self, run_id: str, combat_stats: Optional[Dict] = None) -> Tuple[bool, str, Optional[Dict]]:
        """Mark a floor as cleared and advance"""
        run = self.active_runs.get(run_id)
        if not run:
            return False, "Run not found.", None
        
        if not run.is_active:
            return False, "Run is no longer active.", None
        
        # Calculate rewards
        rewards = self._calculate_floor_rewards(run)
        
        # Apply rewards
        run.gold_earned += rewards["gold"]
        run.exp_earned += rewards["exp"]
        
        # Check for item drop
        if random.random() < rewards["item_chance"]:
            item_tier = rewards["chest_quality"]
            run.items_found.append(f"{item_tier}_item_floor_{run.current_floor}")
        
        # Update combat stats
        if combat_stats:
            run.enemies_defeated += combat_stats.get("enemies_defeated", 0)
            if combat_stats.get("boss_defeated"):
                run.bosses_defeated += 1
        
        # Check for milestone
        milestone_reward = None
        if run.current_floor in self.MILESTONE_REWARDS:
            milestone_reward = self.MILESTONE_REWARDS[run.current_floor]
        
        # Advance to next floor
        success = run.advance_floor()
        
        if not success:
            return False, "Failed to advance floor.", None
        
        # Generate next floor
        next_floor = self.generate_floor(run)
        
        message = f"\n{'='*60}\n"
        message += f"FLOOR {run.current_floor - 1} CLEARED!\n"
        message += f"{'='*60}\n"
        message += f"Gold: +{rewards['gold']}\n"
        message += f"EXP: +{rewards['exp']}\n"
        
        if milestone_reward:
            message += f"\n🏆 MILESTONE REACHED! Floor {run.current_floor - 1}\n"
            message += f"Title Unlocked: {milestone_reward['title']}\n"
            message += f"Bonus: {milestone_reward['gold']} gold, {milestone_reward['exp']} EXP\n"
        
        message += f"\nDescending to Floor {run.current_floor}..."
        
        return True, message, {
            "rewards": rewards,
            "milestone": milestone_reward,
            "next_floor": next_floor,
            "run_status": run.get_status_display()
        }
    
    def abandon_run(self, run_id: str, player_id: str) -> Tuple[bool, str, Optional[Dict]]:
        """Abandon an active run"""
        run = self.active_runs.get(run_id)
        if not run:
            return False, "Run not found.", None
        
        if run.player_id != player_id:
            return False, "You don't own this run.", None
        
        # Complete the run
        run.complete_run(False)
        
        # Calculate partial rewards (50%)
        partial_rewards = {
            "gold": run.gold_earned // 2,
            "exp": run.exp_earned // 2,
            "score": run.total_score // 2,
            "floors_cleared": run.current_floor - 1
        }
        
        # Update best floor
        if run.current_floor - 1 > self.player_best_floors.get(player_id, 0):
            self.player_best_floors[player_id] = run.current_floor - 1
        
        # Remove from active
        del self.active_runs[run_id]
        
        return True, f"Run abandoned. Partial rewards: {partial_rewards['gold']} gold, {partial_rewards['exp']} EXP", partial_rewards
    
    def complete_run(self, run_id: str, success: bool = True) -> Tuple[bool, str, Optional[Dict]]:
        """Complete a dungeon run"""
        run = self.active_runs.get(run_id)
        if not run:
            return False, "Run not found.", None
        
        run.complete_run(success)
        
        # Update best floor
        if run.highest_floor_reached > self.player_best_floors.get(run.player_id, 0):
            self.player_best_floors[run.player_id] = run.highest_floor_reached
        
        # Add to leaderboard if worthy
        if run.total_score > 0:
            self._update_leaderboard(run)
        
        self.total_clears += 1
        
        # Calculate final rewards
        final_rewards = {
            "gold": run.gold_earned,
            "exp": run.exp_earned,
            "score": run.total_score,
            "highest_floor": run.highest_floor_reached,
            "items": run.items_found,
            "time": run.total_time
        }
        
        # Remove from active
        del self.active_runs[run_id]
        
        message = f"\n{'='*60}\n"
        message += f"DUNGEON RUN COMPLETE!\n"
        message += f"{'='*60}\n"
        message += f"Highest Floor: {run.highest_floor_reached}\n"
        message += f"Total Score: {format_number(run.total_score)}\n"
        message += f"Time: {run._format_time(run.total_time)}\n"
        message += f"\nRewards:\n"
        message += f"  Gold: {format_number(run.gold_earned)}\n"
        message += f"  EXP: {format_number(run.exp_earned)}\n"
        message += f"  Items: {len(run.items_found)}\n"
        
        return True, message, final_rewards
    
    def _update_leaderboard(self, run: InfiniteDungeonRun):
        """Update leaderboards with run results"""
        entry = {
            "player_id": run.player_id,
            "player_name": run.player_name,
            "score": run.total_score,
            "highest_floor": run.highest_floor_reached,
            "mode": run.mode.value,
            "date": time.time()
        }
        
        # Add to global leaderboard
        self.global_leaderboard.append(entry)
        self.global_leaderboard.sort(key=lambda x: x["score"], reverse=True)
        self.global_leaderboard = self.global_leaderboard[:100]  # Keep top 100
        
        # Add to weekly leaderboard
        self.weekly_leaderboard.append(entry)
        self.weekly_leaderboard.sort(key=lambda x: x["score"], reverse=True)
        self.weekly_leaderboard = self.weekly_leaderboard[:50]  # Keep top 50
    
    def get_leaderboard(self, weekly: bool = False) -> List[Dict[str, Any]]:
        """Get current leaderboard"""
        if weekly:
            return self.weekly_leaderboard
        return self.global_leaderboard
    
    def get_player_stats(self, player_id: str) -> Dict[str, Any]:
        """Get player's infinite dungeon stats"""
        best_floor = self.player_best_floors.get(player_id, 0)
        
        # Find best run in leaderboards
        best_score = 0
        for entry in self.global_leaderboard:
            if entry["player_id"] == player_id and entry["score"] > best_score:
                best_score = entry["score"]
        
        return {
            "best_floor": best_floor,
            "best_score": best_score,
            "next_milestone": self._get_next_milestone(best_floor)
        }
    
    def _get_next_milestone(self, current_floor: int) -> Optional[Dict]:
        """Get next milestone reward"""
        for floor, reward in sorted(self.MILESTONE_REWARDS.items()):
            if floor > current_floor:
                return {
                    "floor": floor,
                    "reward": reward
                }
        return None
    
    def get_display(self) -> str:
        """Get infinite dungeon display"""
        lines = [
            f"\n{'='*60}",
            "INFINITE DUNGEON",
            f"{'='*60}",
            f"Total Clears: {self.total_clears}",
            f"Active Runs: {len(self.active_runs)}",
            f"",
            "Available Modes:",
            "  • Normal - Standard dungeon crawl",
            "  • Hardcore - No healing between floors",
            "  • Time Attack - Race against the clock",
            "  • Endless - No floor limit",
            f"",
            "Milestone Rewards:"
        ]
        
        for floor, reward in sorted(self.MILESTONE_REWARDS.items())[:5]:
            lines.append(f"  Floor {floor}: {reward['title']}")
        
        # Show top 3 leaderboard
        if self.global_leaderboard:
            lines.append(f"\nTop Runners:")
            for i, entry in enumerate(self.global_leaderboard[:3], 1):
                lines.append(f"  {i}. {entry['player_name']} - Floor {entry['highest_floor']} "
                           f"(Score: {format_number(entry['score'])})")
        
        return "\n".join(lines)
    
    def to_dict(self) -> Dict:
        return {
            "active_runs": {k: v.to_dict() for k, v in self.active_runs.items()},
            "player_best_floors": self.player_best_floors,
            "global_leaderboard": self.global_leaderboard,
            "weekly_leaderboard": self.weekly_leaderboard,
            "total_clears": self.total_clears
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'InfiniteDungeon':
        dungeon = cls()
        dungeon.active_runs = {k: InfiniteDungeonRun.from_dict(v) for k, v in data.get("active_runs", {}).items()}
        dungeon.player_best_floors = data.get("player_best_floors", {})
        dungeon.global_leaderboard = data.get("global_leaderboard", [])
        dungeon.weekly_leaderboard = data.get("weekly_leaderboard", [])
        dungeon.total_clears = data.get("total_clears", 0)
        return dungeon


print("Infinite dungeon system loaded successfully!")

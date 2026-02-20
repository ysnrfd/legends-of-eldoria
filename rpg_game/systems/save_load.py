"""
Save/Load System - Persistent Game State Management
"""

from __future__ import annotations
import json
import os
from datetime import datetime
from typing import Dict, List, Tuple
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class SaveManager:
    """Manages game save files"""
    
    SAVE_DIR = "saves"
    MAX_SAVES = 10
    AUTO_SAVE_NAME = "autosave"
    CURRENT_VERSION = "1.0.0"
    
    def __init__(self, base_path: str = ""):
        self.base_path = base_path or os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.save_dir = os.path.join(self.base_path, self.SAVE_DIR)
        self._ensure_save_dir()
    
    def _ensure_save_dir(self):
        """Ensure save directory exists"""
        if not os.path.exists(self.save_dir):
            os.makedirs(self.save_dir)
    
    def _serialize_game_state(self, game_state: Dict) -> Dict:
        """Serialize game state with proper enum handling"""
        serialized = {}
        
        for key, value in game_state.items():
            if key == "player" and value:
                serialized[key] = value.to_dict()
            elif key == "world" and value:
                serialized[key] = value.to_dict()
            elif key == "quest_manager" and value:
                serialized[key] = value.to_dict()
            elif key == "npc_manager" and value:
                serialized[key] = value.to_dict()
            elif key == "crafting_manager" and value:
                serialized[key] = value.to_dict()
            elif key == "plugin_manager" and value:
                # Skip plugin manager - will be reinitialized
                continue
            elif isinstance(value, (str, int, float, bool, list, dict, type(None))):
                serialized[key] = value
            else:
                # Try to convert to dict if possible
                try:
                    serialized[key] = value.to_dict() if hasattr(value, 'to_dict') else str(value)
                except:
                    serialized[key] = str(value)
        
        return serialized
    
    def _deserialize_game_state(self, data: Dict) -> Dict:
        """Deserialize game state with proper object reconstruction"""
        from core.character import Character
        from systems.world import WorldMap
        from systems.quests import QuestManager
        from systems.npc import NPCManager
        from systems.crafting import CraftingManager
        
        deserialized = {}
        
        for key, value in data.items():
            if key == "player" and value:
                deserialized[key] = Character.from_dict(value)
            elif key == "world" and value:
                deserialized[key] = WorldMap.from_dict(value)
            elif key == "quest_manager" and value:
                deserialized[key] = QuestManager.from_dict(value)
            elif key == "npc_manager" and value:
                deserialized[key] = NPCManager.from_dict(value)
            elif key == "crafting_manager" and value:
                deserialized[key] = CraftingManager.from_dict(value)
            else:
                deserialized[key] = value
        
        return deserialized
    
    def save_game(self, game_state: Dict, save_name: str = None) -> Tuple[bool, str]:
        """Save game state to file"""
        try:
            if save_name is None:
                save_name = self.AUTO_SAVE_NAME
            
            # Validate save name
            save_name = "".join(c for c in save_name if c.isalnum() or c in ('_', '-'))
            if not save_name:
                save_name = self.AUTO_SAVE_NAME
            
            # Add metadata
            game_state["metadata"] = {
                "save_time": datetime.now().isoformat(),
                "game_version": self.CURRENT_VERSION,
                "save_name": save_name
            }
            
            # Serialize game state
            serialized = self._serialize_game_state(game_state)
            
            # Save file path
            file_path = os.path.join(self.save_dir, f"{save_name}.json")
            
            # Write to file
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(serialized, f, indent=2, ensure_ascii=False, default=str)
            
            return True, f"Game saved as '{save_name}'"
        
        except Exception as e:
            return False, f"Failed to save game: {str(e)}"
    
    def load_game(self, save_name: str) -> Tuple[bool, Dict, str]:
        """Load game state from file"""
        try:
            file_path = os.path.join(self.save_dir, f"{save_name}.json")
            
            if not os.path.exists(file_path):
                return False, {}, f"Save file '{save_name}' not found"
            
            with open(file_path, 'r', encoding='utf-8') as f:
                game_state = json.load(f)
            
            # Validate version
            metadata = game_state.get("metadata", {})
            save_version = metadata.get("game_version", "unknown")
            
            if save_version != self.CURRENT_VERSION:
                # Try to migrate or warn
                print(f"Warning: Save version mismatch (save: {save_version}, current: {self.CURRENT_VERSION})")
            
            # Deserialize
            deserialized = self._deserialize_game_state(game_state)
            
            return True, deserialized, "Game loaded successfully"
        
        except json.JSONDecodeError as e:
            return False, {}, f"Corrupted save file: {str(e)}"
        except Exception as e:
            return False, {}, f"Failed to load game: {str(e)}"
    
    def delete_save(self, save_name: str) -> Tuple[bool, str]:
        """Delete a save file"""
        try:
            file_path = os.path.join(self.save_dir, f"{save_name}.json")
            
            if not os.path.exists(file_path):
                return False, f"Save file '{save_name}' not found"
            
            os.remove(file_path)
            return True, f"Save '{save_name}' deleted"
        
        except Exception as e:
            return False, f"Failed to delete save: {str(e)}"
    
    def list_saves(self) -> List[Dict]:
        """List all save files with metadata"""
        saves = []
        
        try:
            if not os.path.exists(self.save_dir):
                return saves
            
            for filename in os.listdir(self.save_dir):
                if filename.endswith('.json'):
                    file_path = os.path.join(self.save_dir, filename)
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            data = json.load(f)
                        
                        metadata = data.get("metadata", {})
                        saves.append({
                            "name": filename[:-5],
                            "player_name": data.get("player", {}).get("name", "Unknown"),
                            "player_level": data.get("player", {}).get("level", 1),
                            "player_class": data.get("player", {}).get("character_class", "Unknown"),
                            "play_time": data.get("play_time", 0),
                            "location": data.get("world", {}).get("current_location", "Unknown"),
                            "save_time": metadata.get("save_time", "Unknown"),
                            "day": data.get("world", {}).get("day", 1),
                            "version": metadata.get("game_version", "unknown")
                        })
                    except:
                        saves.append({
                            "name": filename[:-5],
                            "error": "Could not read save file"
                        })
        
        except Exception as e:
            print(f"Error listing saves: {e}")
        
        # Sort by save time (newest first)
        saves.sort(key=lambda x: x.get("save_time", ""), reverse=True)
        
        return saves
    
    def quick_save(self, game_state: Dict) -> Tuple[bool, str]:
        """Quick save to autosave slot"""
        return self.save_game(game_state, self.AUTO_SAVE_NAME)
    
    def quick_load(self) -> Tuple[bool, Dict, str]:
        """Quick load from autosave slot"""
        return self.load_game(self.AUTO_SAVE_NAME)
    
    def get_save_display(self) -> str:
        """Get display of all saves"""
        saves = self.list_saves()
        
        lines = [
            f"\n{'='*60}",
            "SAVE FILES",
            f"{'='*60}"
        ]
        
        if not saves:
            lines.append("\nNo save files found.")
        else:
            for i, save in enumerate(saves, 1):
                if "error" in save:
                    lines.append(f"\n[{i}] {save['name']} - CORRUPTED")
                else:
                    version_warning = ""
                    if save.get("version") != self.CURRENT_VERSION:
                        version_warning = " [VERSION MISMATCH]"
                    
                    lines.append(
                        f"\n[{i}] {save['name']}{version_warning}\n"
                        f"    {save.get('player_name', 'Unknown')} - "
                        f"Lv.{save.get('player_level', 1)} {save.get('player_class', '')}\n"
                        f"    Location: {save.get('location', 'Unknown').replace('_', ' ').title()}\n"
                        f"    Day {save.get('day', 1)} | "
                        f"Play Time: {save.get('play_time', 0)//60}min\n"
                        f"    Saved: {save.get('save_time', 'Unknown')}"
                    )
        
        return "\n".join(lines)


print("Save/Load system loaded successfully!")

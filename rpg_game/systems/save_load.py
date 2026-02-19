"""
Save/Load System - Persistent Game State Management
"""

from __future__ import annotations
import json
import pickle
import os
import time
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
from pathlib import Path
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class SaveManager:
    """Manages game save files"""
    
    SAVE_DIR = "saves"
    MAX_SAVES = 10
    AUTO_SAVE_NAME = "autosave"
    
    def __init__(self, base_path: str = ""):
        self.base_path = base_path or os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.save_dir = os.path.join(self.base_path, self.SAVE_DIR)
        self._ensure_save_dir()
    
    def _ensure_save_dir(self):
        """Ensure save directory exists"""
        if not os.path.exists(self.save_dir):
            os.makedirs(self.save_dir)
    
    def save_game(self, game_state: Dict, save_name: str = None) -> Tuple[bool, str]:
        """Save game state to file"""
        try:
            if save_name is None:
                save_name = self.AUTO_SAVE_NAME
            
            # Add metadata
            game_state["metadata"] = {
                "save_time": datetime.now().isoformat(),
                "game_version": "1.0.0",
                "save_name": save_name
            }
            
            # Save file path
            file_path = os.path.join(self.save_dir, f"{save_name}.json")
            
            # Write to file
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(game_state, f, indent=2, ensure_ascii=False, default=str)
            
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
            
            return True, game_state, "Game loaded successfully"
        
        except Exception as e:
            return False, {}, f"Failed to load game: {str(e)}"
    
    def delete_save(self, save_name: str) -> Tuple[bool, str]:
        """Delete a save file"""
        try:
            file_path = os.path.join(self.save_dir, f"{save_name}.json")
            
            if os.path.exists(file_path):
                os.remove(file_path)
                return True, f"Save '{save_name}' deleted"
            
            return False, f"Save file '{save_name}' not found"
        
        except Exception as e:
            return False, f"Failed to delete save: {str(e)}"
    
    def list_saves(self) -> List[Dict[str, Any]]:
        """List all save files with metadata"""
        saves = []
        
        try:
            for filename in os.listdir(self.save_dir):
                if filename.endswith('.json'):
                    file_path = os.path.join(self.save_dir, filename)
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            data = json.load(f)
                        
                        metadata = data.get("metadata", {})
                        saves.append({
                            "name": filename[:-5],  # Remove .json
                            "player_name": data.get("player", {}).get("name", "Unknown"),
                            "player_level": data.get("player", {}).get("level", 1),
                            "player_class": data.get("player", {}).get("character_class", "Unknown"),
                            "play_time": data.get("play_time", 0),
                            "location": data.get("world", {}).get("current_location", "Unknown"),
                            "save_time": metadata.get("save_time", "Unknown"),
                            "day": data.get("world", {}).get("day", 1)
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
                    lines.append(
                        f"\n[{i}] {save['name']}\n"
                        f"    {save.get('player_name', 'Unknown')} - "
                        f"Lv.{save.get('player_level', 1)} {save.get('player_class', '')}\n"
                        f"    Location: {save.get('location', 'Unknown').replace('_', ' ').title()}\n"
                        f"    Day {save.get('day', 1)} | "
                        f"Play Time: {save.get('play_time', 0)//60}min\n"
                        f"    Saved: {save.get('save_time', 'Unknown')}"
                    )
        
        return "\n".join(lines)


print("Save/Load system loaded successfully!")

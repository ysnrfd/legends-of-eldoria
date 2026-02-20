"""
Extended NPCs Plugin - New Characters Across the World
Demonstrates comprehensive NPC system with dialogue, services, and quest provision.
"""

from __future__ import annotations
from systems.plugins import Plugin, PluginInfo, PluginPriority, EventType
from typing import Dict, List, Any


class ExtendedNPCsPlugin(Plugin):
    """
    Extended NPCs plugin with diverse characters.
    
    Features:
    - Master craftsmen (blacksmiths, enchanters)
    - Trainers for different skills
    - Quest givers with unique quests
    - Special merchants with rare goods
    - Unique characters with dialogue trees
    - Friendship system integration
    - Location-based NPC spawning
    """
    
    def __init__(self):
        info = PluginInfo(
            id="extended_npcs",
            name="Extended NPCs",
            version="2.0.0",
            author="YSNRFD",
            description="Adds 14 new NPCs across the world including master craftsmen, "
                       "trainers, quest givers, and special characters with dialogue.",
            dependencies=[],
            soft_dependencies=["extended_world", "extended_items"],
            conflicts=[],
            priority=PluginPriority.NORMAL,
            tags=["npcs", "characters", "merchants", "trainers", "quests"]
        )
        super().__init__(info)
        self._friendship_data: Dict[str, int] = {}
    
    def on_load(self, game) -> bool:
        """Initialize NPCs"""
        print("[Extended NPCs] Loading extended NPC roster...")
        self._friendship_data = {}
        return True
    
    def on_unload(self, game) -> bool:
        """Cleanup"""
        print("[Extended NPCs] Unloading...")
        return True
    
    def on_enable(self, game) -> bool:
        """Enable NPCs"""
        print("[Extended NPCs] Enabled!")
        return True
    
    def on_disable(self, game) -> bool:
        """Disable NPCs"""
        return True
    
    def register_hooks(self, event_system) -> Dict[EventType, Any]:
        """
        Register NPC-related event hooks.
        
        Returns:
            Dict mapping EventType to handler functions
        """
        return {
            EventType.NPC_INTERACT: self._on_npc_interact,
            EventType.LOCATION_ENTER: self._on_location_enter,
            EventType.PLAYER_LEVEL_UP: self._on_level_up,
            EventType.QUEST_COMPLETE: self._on_quest_complete,
        }
    
    def _on_npc_interact(self, game, data):
        """Handle NPC interactions"""
        npc_id = data.get("npc_id")
        npcs = self._get_npcs()
        
        if npc_id in npcs:
            npc_data = npcs[npc_id]
            friendship = data.get("friendship", 0)
            self._friendship_data[npc_id] = friendship
            
            dialogue = npc_data.get("dialogue", {}).get("greeting", {})
            if friendship >= 150 and "high_friendship" in dialogue:
                print(f"\n{npc_data['name']}: {dialogue['high_friendship']}")
            elif friendship >= 50 and "medium_friendship" in dialogue:
                print(f"\n{npc_data['name']}: {dialogue['medium_friendship']}")
            elif "low_friendship" in dialogue:
                print(f"\n{npc_data['name']}: {dialogue['low_friendship']}")
            
            services = npc_data.get("services", [])
            if services:
                print(f"  Services: {', '.join(services)}")
    
    def _on_location_enter(self, game, data):
        """Show NPCs available in location"""
        location_id = data.get("location_id")
        npcs = self._get_npcs()
        
        location_npcs = [
            (npc_id, npc) for npc_id, npc in npcs.items() 
            if npc.get("location") == location_id
        ]
        
        if location_npcs:
            print(f"\n[Extended NPCs] Characters in this area:")
            for npc_id, npc in location_npcs:
                print(f"  • {npc['name']} ({npc.get('npc_type', 'unknown')})")
    
    def _on_level_up(self, game, data):
        """Notify about new NPCs at level milestones"""
        level = data.get("level", 1)
        npcs = self._get_npcs()
        
        for npc_id, npc in npcs.items():
            requires = npc.get("requirements", {})
            if requires.get("level") == level:
                print(f"\n[Extended NPCs] A new acquaintance awaits: {npc['name']}!")
    
    def _on_quest_complete(self, game, data):
        """Handle quest completion for friendship"""
        quest_id = data.get("quest_id")
        quests = self._get_quests()
        
        if quest_id in quests:
            giver = quests[quest_id].get("giver")
            if giver:
                current = self._friendship_data.get(giver, 0)
                self._friendship_data[giver] = min(current + 25, 200)
                print(f"  Friendship with {giver} increased!")
    
    def register_commands(self, command_system) -> Dict[str, Any]:
        """Register NPC-related commands."""
        return {
            "npcs": {
                "handler": self._cmd_list_npcs,
                "help": "List all extended NPCs by location",
                "category": "info"
            },
            "npc_info": {
                "handler": self._cmd_npc_info,
                "help": "Show detailed info about an NPC",
                "usage": "/npc_info <npc_id>",
                "category": "info"
            },
            "friendship": {
                "handler": self._cmd_friendship,
                "help": "Check friendship levels with NPCs",
                "category": "stats"
            }
        }
    
    def _cmd_list_npcs(self, game, args, context) -> str:
        """List all NPCs by location"""
        npcs = self._get_npcs()
        by_location: Dict[str, List] = {}
        
        for npc_id, npc in npcs.items():
            loc = npc.get("location", "unknown")
            if loc not in by_location:
                by_location[loc] = []
            by_location[loc].append((npc_id, npc))
        
        lines = ["Extended NPCs:", "=" * 50]
        for location, npc_list in sorted(by_location.items()):
            lines.append(f"\n{location.replace('_', ' ').title()}:")
            for npc_id, npc in npc_list:
                npc_type = npc.get("npc_type", "unknown")
                lines.append(f"  • {npc['name']} ({npc_type})")
        
        return "\n".join(lines)
    
    def _cmd_npc_info(self, game, args, context) -> str:
        """Show detailed NPC information"""
        if not args:
            return "Usage: /npc_info <npc_id>"
        
        npc_id = args[0].lower()
        npcs = self._get_npcs()
        
        if npc_id not in npcs:
            return f"NPC '{npc_id}' not found."
        
        npc = npcs[npc_id]
        lines = [
            f"NPC: {npc['name']}",
            f"Type: {npc.get('npc_type', 'Unknown')}",
            f"Location: {npc.get('location', 'Unknown')}",
            f"",
            f"Description: {npc['description']}"
        ]
        
        if "services" in npc:
            lines.append(f"Services: {', '.join(npc['services'])}")
        
        if "can_train" in npc:
            lines.append(f"Train: {', '.join(npc['can_train'])}")
        
        return "\n".join(lines)
    
    def _cmd_friendship(self, game, args, context) -> str:
        """Show friendship levels"""
        if not self._friendship_data:
            return "No friendships established yet."
        
        lines = ["NPC Friendships:", "=" * 50]
        npcs = self._get_npcs()
        
        for npc_id, level in sorted(self._friendship_data.items(), key=lambda x: -x[1]):
            npc_name = npcs.get(npc_id, {}).get("name", npc_id)
            lines.append(f"{npc_name:25} {level}/200")
        
        return "\n".join(lines)
    
    def get_new_npcs(self) -> Dict[str, Dict]:
        """Return new NPCs."""
        return self._get_npcs()
    
    def get_new_quests(self) -> Dict[str, Dict]:
        """Return new quests."""
        return self._get_quests()
    
    def _get_npcs(self) -> Dict[str, Dict]:
        """Get all NPC definitions"""
        return {
            "master_blacksmith_bjorn": {
                "name": "Master Blacksmith Bjorn",
                "description": "A legendary dwarven blacksmith. His forge has crafted weapons for kings.",
                "npc_type": "blacksmith",
                "location": "capital_city",
                "services": ["craft", "repair", "enchant"],
                "can_train": ["Crafting", "Swordsmanship"],
                "training_cost": 300,
                "dialogue": {
                    "greeting": {
                        "low_friendship": "\"State your business.\"",
                        "medium_friendship": "\"Back again?\"",
                        "high_friendship": "\"My friend!\""
                    }
                }
            },
            "grand_magister_elara": {
                "name": "Grand Magister Elara",
                "description": "The head of the Arcane University.",
                "npc_type": "trainer",
                "location": "capital_city",
                "services": ["train_magic", "identify", "enchant"],
                "can_train": ["Magic"],
                "training_cost": 800,
                "dialogue": {
                    "greeting": {
                        "low_friendship": "\"You seek knowledge?\"",
                        "medium_friendship": "\"Your aura grows stronger.\"",
                        "high_friendship": "\"Dear pupil!\""
                    }
                }
            },
            "arena_master_ragnor": {
                "name": "Arena Master Ragnor",
                "description": "A scarred veteran who runs the Arena.",
                "npc_type": "trainer",
                "location": "capital_city",
                "services": ["arena_battles", "training"],
                "can_train": ["Swordsmanship", "Stealth"],
                "training_cost": 200,
                "dialogue": {
                    "greeting": {
                        "low_friendship": "\"Looking for glory?\"",
                        "high_friendship": "\"Champion!\""
                    }
                }
            },
            "old_sage_merlin": {
                "name": "Old Sage Merlin",
                "description": "An elderly man offering wisdom beneath the ancient oak.",
                "npc_type": "quest_giver",
                "location": "start_village",
                "services": ["prophecy", "wisdom"],
                "dialogue": {
                    "greeting": {
                        "low_friendship": "\"Come closer, young one.\""
                    }
                }
            },
            "huntress_lyra": {
                "name": "Huntress Lyra",
                "description": "A skilled ranger who knows the forest.",
                "npc_type": "trainer",
                "location": "start_village",
                "services": ["guide", "training"],
                "can_train": ["Survival", "Stealth"],
                "training_cost": 100,
                "dialogue": {
                    "greeting": {
                        "low_friendship": "\"Looking for a guide?\""
                    }
                }
            },
            "gem_trader_sapphire": {
                "name": "Sapphire the Gem Trader",
                "description": "An elegant woman with gems and jewelry.",
                "npc_type": "merchant",
                "location": "mining_town",
                "services": ["trade", "appraise"],
                "dialogue": {
                    "greeting": {
                        "low_friendship": "\"Welcome!\""
                    }
                }
            },
            "mine_foreman_gimli": {
                "name": "Foreman Gimli",
                "description": "A stout dwarf who knows every tunnel in the mines.",
                "npc_type": "quest_giver",
                "location": "mining_town",
                "services": ["mining_jobs"],
                "dialogue": {
                    "greeting": {
                        "low_friendship": "\"Looking for work?\""
                    }
                }
            },
            "wandering_merchant_zephyr": {
                "name": "Zephyr the Wandering Merchant",
                "description": "A mysterious merchant with exotic goods.",
                "npc_type": "merchant",
                "location": "crossroads",
                "services": ["trade", "rare_goods"],
                "dialogue": {
                    "greeting": {
                        "low_friendship": "\"Ah, a traveler!\""
                    }
                }
            },
            "fortune_teller_mystique": {
                "name": "Madame Mystique",
                "description": "An enigmatic woman with a crystal ball.",
                "npc_type": "mysterious",
                "location": "crossroads",
                "services": ["fortune", "blessing"],
                "dialogue": {
                    "greeting": {
                        "low_friendship": "\"Come, let the cards reveal your path...\""
                    }
                }
            },
            "fairy_princess_aurora": {
                "name": "Princess Aurora of the Fae",
                "description": "A radiant fairy with wings like stained glass.",
                "npc_type": "quest_giver",
                "location": "fairy_grove",
                "services": ["fairy_blessing", "enchant"],
                "dialogue": {
                    "greeting": {
                        "low_friendship": "\"A mortal! How delightful!\""
                    }
                }
            },
            "temple_guardian_spirit": {
                "name": "Temple Guardian Spirit",
                "description": "A translucent figure wreathed in ethereal light.",
                "npc_type": "mysterious",
                "location": "ancient_temple",
                "services": ["temple_trials", "blessing"],
                "dialogue": {
                    "greeting": {
                        "low_friendship": "\"Mortal... prove your worth.\""
                    }
                }
            },
            "dragon_scholar_ignis": {
                "name": "Ignis the Dragon Scholar",
                "description": "An elderly scholar who studies dragons.",
                "npc_type": "quest_giver",
                "location": "dragon_peak",
                "services": ["dragon_lore", "preparation"],
                "dialogue": {
                    "greeting": {
                        "low_friendship": "\"Foolish mortal!\"",
                        "high_friendship": "\"Dragon-slayer!\""
                    }
                }
            },
            "nomad_chief_khalid": {
                "name": "Chief Khalid of the Sandrunners",
                "description": "A weathered desert warrior.",
                "npc_type": "quest_giver",
                "location": "desert_border",
                "services": ["guide", "trade"],
                "dialogue": {
                    "greeting": {
                        "low_friendship": "\"The desert takes the unprepared.\""
                    }
                }
            },
            "mysterious_hermit": {
                "name": "The Eternal Hermit",
                "description": "A figure wrapped in shadow and mystery.",
                "npc_type": "mysterious",
                "location": "deep_forest",
                "services": ["class_advancement", "legendary_quest"],
                "requirements": {"level": 20},
                "dialogue": {
                    "greeting": {
                        "low_friendship": "\"...You see me. Few do.\""
                    }
                }
            }
        }
    
    def _get_quests(self) -> Dict[str, Dict]:
        """Get all quest definitions"""
        return {
            "artifact_recovery": {
                "name": "The Arcane Artifact",
                "description": "Recover a powerful artifact from the Ancient Temple.",
                "quest_type": "side",
                "giver": "grand_magister_elara",
                "location": "capital_city",
                "level_required": 10,
                "objectives": [
                    {"type": "reach", "target": "ancient_temple", "required": 1,
                     "description": "Reach the Ancient Temple"},
                    {"type": "defeat_boss", "target": "forgotten_priest", "required": 1,
                     "description": "Defeat the Forgotten Priest"}
                ],
                "rewards": {
                    "experience": 1500,
                    "gold": 800,
                    "items": ["magic_crystal"]
                }
            },
            "dragon_preparation": {
                "name": "Preparing for the Dragon",
                "description": "Prepare for battle with the Ancient Dragon.",
                "quest_type": "boss",
                "giver": "dragon_scholar_ignis",
                "location": "dragon_peak",
                "level_required": 20,
                "objectives": [
                    {"type": "collect", "target": "dragon_scale", "required": 5,
                     "description": "Collect dragon scales"}
                ],
                "rewards": {
                    "experience": 2000,
                    "gold": 1500,
                    "stat_bonus": {"strength": 2, "constitution": 2}
                }
            },
            "mining_expedition": {
                "name": "Deep Mine Expedition",
                "description": "Explore the Crystal Caverns for the foreman.",
                "quest_type": "side",
                "giver": "mine_foreman_gimli",
                "location": "mining_town",
                "level_required": 5,
                "objectives": [
                    {"type": "reach", "target": "crystal_caverns", "required": 1,
                     "description": "Explore the Crystal Caverns"},
                    {"type": "collect", "target": "magic_crystal", "required": 10,
                     "description": "Gather magic crystals"}
                ],
                "rewards": {
                    "experience": 800,
                    "gold": 500
                }
            },
            "fairy_favor": {
                "name": "The Fae's Favor",
                "description": "Help the fairy princess recover stolen treasure.",
                "quest_type": "side",
                "giver": "fairy_princess_aurora",
                "location": "fairy_grove",
                "level_required": 8,
                "objectives": [
                    {"type": "kill", "target": "goblin", "required": 5,
                     "description": "Defeat goblin thieves"}
                ],
                "rewards": {
                    "experience": 1000,
                    "gold": 400,
                    "stat_bonus": {"luck": 1}
                }
            }
        }


# Plugin instance - REQUIRED
plugin = ExtendedNPCsPlugin()

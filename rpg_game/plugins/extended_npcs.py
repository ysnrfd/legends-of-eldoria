"""
Extended NPCs Plugin - New Characters Across the World
Demonstrates comprehensive NPC system with dialogue and services
"""

from __future__ import annotations
from systems.plugins import (
    PluginBase, PluginInfo, PluginType, PluginPriority,
    IContentProvider, IHotReloadablePlugin, EventPriority
)
from core.engine import Rarity, StatType, EventType
from typing import Dict, List, Any


class ExtendedNPCsPlugin(PluginBase, IContentProvider, IHotReloadablePlugin):
    """
    Extended NPCs plugin with diverse characters.
    
    Features:
    - Master craftsmen
    - Trainers for different skills
    - Quest givers
    - Special merchants
    - Unique characters
    """
    
    @property
    def info(self) -> PluginInfo:
        return PluginInfo(
            id="extended_npcs",
            name="Extended NPCs",
            version="2.0.0",
            author="YSNRFD",
            description="Adds 14 new NPCs across the world including master craftsmen, "
                       "trainers, quest givers, and special characters.",
            
            dependencies=[],
            soft_dependencies=["extended_world"],
            conflicts=[],
            provides=["extended_npcs"],
            
            priority=PluginPriority.NORMAL.value + 5,  # Load after locations
            plugin_type=PluginType.CLASS,
            
            configurable=False,
            supports_hot_reload=True,
            
            tags=["npcs", "characters", "merchants", "trainers"],
            custom={"npc_count": 14}
        )
    
    # =========================================================================
    # Lifecycle
    # =========================================================================
    
    def on_load(self, game):
        print("[Extended NPCs] Loading extended NPC roster...")
    
    def on_unload(self, game):
        print("[Extended NPCs] Unloading...")
    
    def on_before_reload(self, game) -> Dict[str, Any]:
        return {}
    
    def on_after_reload(self, game, state: Dict[str, Any]) -> None:
        print("[Extended NPCs] Reloaded!")
    
    # =========================================================================
    # Content Provider
    # =========================================================================
    
    def get_content_types(self) -> List[str]:
        return ["npcs", "quests"]
    
    def get_content(self, content_type: str) -> Dict[str, Any]:
        if content_type == "npcs":
            return self._get_npcs()
        elif content_type == "quests":
            return self._get_quests()
        return {}
    
    # =========================================================================
    # NPC Definitions
    # =========================================================================
    
    def _get_npcs(self) -> Dict[str, Dict]:
        return {
            # =========================================================================
            # CAPITAL CITY NPCs
            # =========================================================================
            
            "master_blacksmith_bjorn": {
                "name": "Master Blacksmith Bjorn",
                "description": "A legendary dwarven blacksmith with arms like tree trunks. "
                             "His forge has crafted weapons for kings and heroes for over 200 years.",
                "npc_type": "blacksmith",
                "location": "capital_city",
                "shop_items": [
                    "steel_greatsword", "plate_armor", "chainmail"
                ],
                "services": ["craft", "repair", "enchant", "identify"],
                "buy_multiplier": 1.3,
                "sell_multiplier": 0.6,
                "friendship_max": 200,
                "friendship_rewards": {
                    50: "10% discount on all services",
                    100: "Access to legendary crafting recipes",
                    150: "Free weapon sharpening",
                    200: "Masterwork enhancement service"
                },
                "can_train": ["Crafting", "Swordsmanship"],
                "training_cost": 300,
                "dialogue": {
                    "greeting": {
                        "low_friendship": "\"State your business. I've got work to do.\"",
                        "medium_friendship": "\"Ah, back again? Let me see what you need.\"",
                        "high_friendship": "\"My friend! Come, let me show you my latest work!\""
                    }
                }
            },
            
            "grand_magister_elara": {
                "name": "Grand Magister Elara",
                "description": "The head of the Arcane University. Her eyes shimmer with contained "
                             "magical energy, and ancient runes float around her fingertips.",
                "npc_type": "trainer",
                "location": "capital_city",
                "shop_items": [
                    "mana_potion", "magic_crystal", "frost_staff"
                ],
                "services": ["train_magic", "identify", "enchant", "teleport"],
                "buy_multiplier": 1.5,
                "sell_multiplier": 0.5,
                "friendship_max": 200,
                "can_train": ["Magic"],
                "training_cost": 800,
                "special_abilities": {
                    "teleport": {
                        "description": "Teleport to any discovered location",
                        "cost": 100,
                        "requires_friendship": 50
                    }
                },
                "dialogue": {
                    "greeting": {
                        "low_friendship": "\"You seek knowledge? The Arcane University welcomes all.\"",
                        "medium_friendship": "\"Ah, student of the arcane. Your aura grows stronger.\"",
                        "high_friendship": "\"My dearest pupil! I have something special for you.\""
                    }
                }
            },
            
            "arena_master_ragnor": {
                "name": "Arena Master Ragnor",
                "description": "A scarred veteran of a thousand battles who runs the Arena. "
                             "His missing eye tells tales of battles won.",
                "npc_type": "trainer",
                "location": "capital_city",
                "services": ["arena_battles", "training", "betting"],
                "can_train": ["Swordsmanship", "Stealth"],
                "training_cost": 200,
                "arena_levels": [
                    {"name": "Novice Pit", "min_level": 1, 
                     "enemies": ["goblin", "wolf"], "reward_gold": 50, "reward_exp": 25},
                    {"name": "Warrior's Gauntlet", "min_level": 5,
                     "enemies": ["orc_warrior", "skeleton"], "reward_gold": 150, "reward_exp": 75},
                    {"name": "Champion's Arena", "min_level": 10,
                     "enemies": ["troll", "dark_mage"], "reward_gold": 400, "reward_exp": 200}
                ],
                "dialogue": {
                    "greeting": {
                        "low_friendship": "\"Looking for glory? Step forward and prove yourself!\"",
                        "medium_friendship": "\"The crowd loves you, fighter. Keep winning.\"",
                        "high_friendship": "\"Champion! The arena hasn't seen your like in decades!\""
                    }
                }
            },
            
            # =========================================================================
            # WILLOWBROOK VILLAGE NPCs
            # =========================================================================
            
            "old_sage_merlin": {
                "name": "Old Sage Merlin",
                "description": "An elderly man with a beard reaching his waist. "
                             "He sits beneath the ancient oak, offering wisdom.",
                "npc_type": "quest_giver",
                "location": "start_village",
                "services": ["prophecy", "wisdom", "identify"],
                "friendship_max": 150,
                "prophecies": [
                    {
                        "id": "hero_path",
                        "text": "I see a great destiny before you. Darkness gathers in the east...",
                        "requires": {"level": 5}
                    }
                ],
                "dialogue": {
                    "greeting": {
                        "low_friendship": "\"Come closer, young one. The wind carries whispers.\"",
                        "medium_friendship": "\"Ah, you return. The stars foretold this meeting.\"",
                        "high_friendship": "\"My old friend! Your destiny unfolds beautifully.\""
                    }
                }
            },
            
            "huntress_lyra": {
                "name": "Huntress Lyra",
                "description": "A skilled ranger with a bow always at her back. "
                             "She knows the forest better than anyone.",
                "npc_type": "trainer",
                "location": "start_village",
                "services": ["hunting_tips", "guide", "training"],
                "can_train": ["Survival", "Stealth"],
                "training_cost": 100,
                "guide_services": {
                    "whispering_woods": {"cost": 0},
                    "deep_forest": {"cost": 50}
                },
                "dialogue": {
                    "greeting": {
                        "low_friendship": "\"Looking for a guide? I know every trail.\"",
                        "medium_friendship": "\"Friend of the forest! What game do you hunt?\"",
                        "high_friendship": "\"My trusted companion! The wilderness calls to us.\""
                    }
                }
            },
            
            # =========================================================================
            # MINING TOWN NPCs
            # =========================================================================
            
            "gem_trader_sapphire": {
                "name": "Sapphire the Gem Trader",
                "description": "An elegant woman with deep blue eyes that match her namesake. "
                             "Her cart overflows with gems and jewelry.",
                "npc_type": "merchant",
                "location": "mining_town",
                "shop_items": [
                    "silver_ring", "ruby_amulet", "lucky_coin"
                ],
                "services": ["appraise", "trade", "craft_jewelry"],
                "buy_multiplier": 1.2,
                "sell_multiplier": 0.7,
                "friendship_max": 100,
                "dialogue": {
                    "greeting": {
                        "low_friendship": "\"Welcome! The finest gems in the realm.\"",
                        "medium_friendship": "\"Ah, a connoisseur! I have something special.\"",
                        "high_friendship": "\"My favorite customer! I saved my best for you.\""
                    }
                }
            },
            
            "mine_foreman_gimli": {
                "name": "Foreman Gimli",
                "description": "A stout dwarf with a braided beard and permanent squint. "
                             "He knows every tunnel in the mines.",
                "npc_type": "quest_giver",
                "location": "mining_town",
                "services": ["mining_jobs", "equipment_rental"],
                "mining_jobs": [
                    {
                        "id": "iron_run",
                        "name": "Iron Ore Collection",
                        "reward_gold": 30,
                        "reward_exp": 15
                    },
                    {
                        "id": "deep_delve",
                        "name": "Deep Mine Expedition",
                        "requires_level": 5,
                        "reward_gold": 100,
                        "reward_exp": 50
                    }
                ],
                "dialogue": {
                    "greeting": {
                        "low_friendship": "\"Looking for work? The mines always need workers.\"",
                        "medium_friendship": "\"Good to see you, friend!\"",
                        "high_friendship": "\"Partner! I've got a lead on something big.\""
                    }
                }
            },
            
            # =========================================================================
            # CROSSROADS NPCs
            # =========================================================================
            
            "wandering_merchant_zephyr": {
                "name": "Zephyr the Wandering Merchant",
                "description": "A mysterious merchant whose cart appears in different locations. "
                             "His goods are exotic and rare.",
                "npc_type": "merchant",
                "location": "crossroads",
                "shop_items": [
                    "mega_potion", "elixir_of_power", "phoenix_feather"
                ],
                "services": ["trade", "information", "rare_goods"],
                "buy_multiplier": 1.5,
                "sell_multiplier": 0.8,
                "friendship_max": 200,
                "dialogue": {
                    "greeting": {
                        "low_friendship": "\"Ah, a traveler! Wares from distant lands.\"",
                        "medium_friendship": "\"My friend! I kept this special item for you.\"",
                        "high_friendship": "\"Ah! Something extraordinary for my best customer.\""
                    }
                }
            },
            
            "fortune_teller_mystique": {
                "name": "Madame Mystique",
                "description": "An enigmatic woman with a silk scarf and crystal ball. "
                             "Incense smoke curls around her.",
                "npc_type": "mysterious",
                "location": "crossroads",
                "services": ["fortune", "curse_removal", "blessing"],
                "friendship_max": 100,
                "fortune_prices": {
                    "basic": {"cost": 50, "description": "A glimpse of your near future"},
                    "detailed": {"cost": 200, "description": "Detailed reading with advice"}
                },
                "dialogue": {
                    "greeting": {
                        "low_friendship": "\"Come, let the cards reveal your path... for a price.\"",
                        "medium_friendship": "\"The stars told me you would come.\"",
                        "high_friendship": "\"My dear! The spirits have much to show you.\""
                    }
                }
            },
            
            # =========================================================================
            # FAIRY GROVE NPC
            # =========================================================================
            
            "fairy_princess_aurora": {
                "name": "Princess Aurora of the Fae",
                "description": "A radiant fairy with wings like stained glass. "
                             "Her tiny crown glows with inner light.",
                "npc_type": "quest_giver",
                "location": "fairy_grove",
                "services": ["fairy_blessing", "enchant", "wish"],
                "friendship_max": 200,
                "blessing_types": [
                    {"name": "Luck of the Fae", "effect": "luck", "bonus": 5, "duration": 10}
                ],
                "dialogue": {
                    "greeting": {
                        "low_friendship": "\"A mortal! How delightful!\"",
                        "medium_friendship": "\"My mortal friend! The grove brightens.\"",
                        "high_friendship": "\"Chosen one of the Fae! Name your desire.\""
                    }
                }
            },
            
            # =========================================================================
            # ANCIENT TEMPLE NPC
            # =========================================================================
            
            "temple_guardian_spirit": {
                "name": "Temple Guardian Spirit",
                "description": "A translucent figure wreathed in ethereal light. "
                             "Ancient armor floats on its spectral form.",
                "npc_type": "mysterious",
                "location": "ancient_temple",
                "services": ["temple_trials", "ancient_wisdom", "blessing"],
                "friendship_max": 100,
                "temple_trials": [
                    {
                        "name": "Trial of Strength",
                        "description": "Defeat the temple guardians",
                        "enemies": ["temple_guardian", "temple_guardian"]
                    }
                ],
                "dialogue": {
                    "greeting": {
                        "low_friendship": "\"Mortal... prove your worth.\"",
                        "medium_friendship": "\"Seeker of ancient knowledge.\"",
                        "high_friendship": "\"Champion of the Temple.\""
                    }
                }
            },
            
            # =========================================================================
            # DRAGON'S PEAK NPC
            # =========================================================================
            
            "dragon_scholar_ignis": {
                "name": "Ignis the Dragon Scholar",
                "description": "An elderly scholar who has dedicated his life to studying dragons. "
                             "His robes are singed from close encounters.",
                "npc_type": "quest_giver",
                "location": "dragon_peak",
                "services": ["dragon_lore", "dragon_preparation", "identify_dragon_items"],
                "friendship_max": 150,
                "dragon_preparation": {
                    "fire_resistance_potion": {"cost": 500, "effect": "fire_resistance"}
                },
                "dialogue": {
                    "greeting": {
                        "low_friendship": "\"Foolish mortal! Dragons are not to be trifled with.\"",
                        "medium_friendship": "\"You still live? Impressive.\"",
                        "high_friendship": "\"Dragon-slayer in training! I will share all I know.\""
                    }
                }
            },
            
            # =========================================================================
            # DESERT NPC
            # =========================================================================
            
            "nomad_chief_khalid": {
                "name": "Chief Khalid of the Sandrunners",
                "description": "A weathered desert warrior with a curved scimitar. "
                             "His eyes are sharp from years of scanning dunes.",
                "npc_type": "quest_giver",
                "location": "desert_border",
                "services": ["guide", "trade", "shelter"],
                "friendship_max": 150,
                "guide_services": {
                    "desert_crossing": {"cost": 100},
                    "oasis_locations": {"cost": 50}
                },
                "dialogue": {
                    "greeting": {
                        "low_friendship": "\"The desert takes the unprepared. What do you seek?\"",
                        "medium_friendship": "\"Friend of the Sandrunners!\"",
                        "high_friendship": "\"My brother of the sands!\""
                    }
                }
            },
            
            # =========================================================================
            # SPECIAL SECRET NPC
            # =========================================================================
            
            "mysterious_hermit": {
                "name": "The Eternal Hermit",
                "description": "A figure wrapped in shadow and mystery. "
                             "They appear only to those who have proven themselves.",
                "npc_type": "mysterious",
                "location": "deep_forest",
                "services": ["class_advancement", "legendary_quest"],
                "friendship_max": 300,
                "requirements": {
                    "min_level": 20,
                    "required_quests": ["main_004"]
                },
                "class_advancement": {
                    "Warrior": {"new_class": "Warlord", "bonus": {"strength": 5}},
                    "Mage": {"new_class": "Archmage", "bonus": {"intelligence": 5}},
                    "Rogue": {"new_class": "Shadow Lord", "bonus": {"dexterity": 5}}
                },
                "dialogue": {
                    "greeting": {
                        "low_friendship": "\"...You see me. Few do.\"",
                        "medium_friendship": "\"The threads of fate weave around you.\"",
                        "high_friendship": "\"Chosen one. I have waited centuries.\""
                    }
                }
            }
        }
    
    def _get_quests(self) -> Dict[str, Dict]:
        """Quests provided by these NPCs"""
        return {
            "artifact_recovery": {
                "name": "The Arcane Artifact",
                "description": "Grand Magister Elara senses a powerful artifact. "
                              "Recover it from the Temple of the Forgotten God.",
                "quest_type": "side",
                "giver": "grand_magister_elara",
                "location": "capital_city",
                "level_required": 10,
                "objectives": [
                    {"type": "reach", "target": "ancient_temple", "required": 1,
                     "description": "Reach the Ancient Temple"},
                    {"type": "defeat_boss", "target": "forgotten_priest", "required": 1,
                     "description": "Defeat the Forgotten Priest"},
                    {"type": "talk", "target": "grand_magister_elara", "required": 1,
                     "description": "Return to Grand Magister Elara"}
                ],
                "rewards": {
                    "experience": 1500,
                    "gold": 800,
                    "items": ["magic_crystal"],
                    "skill_exp": {"Magic": 100}
                }
            },
            "dragon_preparation": {
                "name": "Preparing for the Dragon",
                "description": "Ignis helps you prepare for battle with the Ancient Dragon.",
                "quest_type": "boss",
                "giver": "dragon_scholar_ignis",
                "location": "dragon_peak",
                "level_required": 20,
                "objectives": [
                    {"type": "collect", "target": "dragon_scale", "required": 5,
                     "description": "Collect dragon scales"},
                    {"type": "talk", "target": "dragon_scholar_ignis", "required": 1,
                     "description": "Learn dragon weaknesses"}
                ],
                "rewards": {
                    "experience": 2000,
                    "gold": 1500,
                    "stat_bonus": {"strength": 2, "constitution": 2}
                }
            }
        }
    
    # =========================================================================
    # Legacy Support
    # =========================================================================
    
    def get_new_npcs(self) -> Dict[str, Dict]:
        return self._get_npcs()
    
    def get_new_quests(self) -> Dict[str, Dict]:
        return self._get_quests()
    
    # =========================================================================
    # Event Hooks
    # =========================================================================
    
    def register_hooks(self, event_system) -> Dict:
        return {
            EventType.NPC_INTERACT: (self._on_npc_interact, EventPriority.NORMAL),
            EventType.LOCATION_ENTER: (self._on_location_enter, EventPriority.LOW),
            EventType.PLAYER_LEVEL_UP: self._on_level_up
        }
    
    def _on_npc_interact(self, data):
        npc_id = data.get("npc_id")
        npcs = self._get_npcs()
        
        if npc_id in npcs:
            npc_data = npcs[npc_id]
            friendship = data.get("friendship", 0)
            print(f"[Extended NPCs] Interacting with {npc_data['name']}")
        
        return None
    
    def _on_location_enter(self, data):
        location_id = data.get("location_id")
        npcs = self._get_npcs()
        
        location_npcs = [npc for npc in npcs.values() if npc.get("location") == location_id]
        
        if location_npcs:
            print(f"\n[Extended NPCs] NPCs available here:")
            for npc in location_npcs:
                print(f"  • {npc['name']}")
        
        return None
    
    def _on_level_up(self, data):
        player = data.get("player")
        level = data.get("level", 1)
        
        npcs = self._get_npcs()
        for npc_id, npc in npcs.items():
            if npc.get("requires_level") == level:
                print(f"\n[Extended NPCs] A new acquaintance awaits: {npc['name']}!")
        
        return None
    
    # =========================================================================
    # Commands
    # =========================================================================
    
    def register_commands(self, command_system) -> Dict:
        return {
            "npcs": {
                "handler": self._cmd_list_npcs,
                "help": "List extended NPCs",
                "category": "info"
            },
            "friendship": {
                "handler": self._cmd_friendship,
                "help": "Check friendship levels",
                "category": "info"
            }
        }
    
    def _cmd_list_npcs(self, game, args, context):
        npcs = self._get_npcs()
        
        # Group by location
        by_location = {}
        for npc_id, npc in npcs.items():
            loc = npc.get("location", "unknown")
            if loc not in by_location:
                by_location[loc] = []
            by_location[loc].append(npc)
        
        lines = ["Extended NPCs:", "=" * 50]
        for location, npc_list in sorted(by_location.items()):
            lines.append(f"\n{location.replace('_', ' ').title()}:")
            for npc in npc_list:
                lines.append(f"  • {npc['name']} ({npc['npc_type']})")
        
        return "\n".join(lines)
    
    def _cmd_friendship(self, game, args, context):
        return "Friendship tracking coming soon!"


# Plugin instance
plugin = ExtendedNPCsPlugin()

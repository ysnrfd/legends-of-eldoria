#!/usr/bin/env python3
"""
LEGENDS OF ELDORIA
A Complete Text-Based RPG Game
Version: 1.0.0

Features:
- Open World Exploration
- Turn-Based Combat
- Quest System
- NPC Interactions
- Crafting System
- Plugin Support
- Save/Load System
- Day/Night Cycle
- Weather System
- Skills and Abilities
- Equipment System
- Inventory Management

Author: YSNRFD
"""

from __future__ import annotations
import sys
import os
import time
import random

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.engine import (
    clear_screen, colored_text, get_input, pause, EventType, CharacterClass,
    StatusEffectType
)
from core.character import Character
from core.items import get_item
from systems.world import WorldMap
from systems.combat import CombatEncounter
from systems.quests import QuestManager, ObjectiveType
from systems.npc import NPCManager
from systems.crafting import CraftingManager
from systems.save_load import SaveManager
from systems.plugins import PluginManager


class Game:
    """Main game class"""
    
    VERSION = "1.0.0"
    TITLE = "LEGENDS OF ELDORIA"
    
    def __init__(self):
        self.running = False
        self.player: Character = None
        self.world: WorldMap = None
        self.quest_manager: QuestManager = None
        self.npc_manager: NPCManager = None
        self.crafting_manager: CraftingManager = None
        self.save_manager: SaveManager = None
        self.plugin_manager: PluginManager = None
        self.start_time: float = 0
        self.play_time: int = 0
        self.god_mode: bool = False
    
    def initialize(self):
        """Initialize all game systems"""
        print("Initializing game systems...")
        
        self.world = WorldMap()
        self.quest_manager = QuestManager()
        self.npc_manager = NPCManager()
        self.crafting_manager = CraftingManager()
        self.save_manager = SaveManager()
        
        # Initialize plugin system (needs game reference)
        self.plugin_manager = PluginManager(self)
        
        # Load plugins
        success, fail = self.plugin_manager.load_all_plugins()
        print(f"Plugins loaded: {success} successful, {fail} failed")
        
        print("Game initialized successfully!\n")
    
    def start(self):
        """Start the game"""
        self.initialize()
        self.running = True
        self.start_time = time.time()
        
        # Show title screen
        self.show_title_screen()
        
        # Main menu loop
        while self.running:
            choice = self.show_main_menu()
            self.handle_main_menu_choice(choice)
    
    def show_title_screen(self):
        """Display the title screen"""
        clear_screen()
        title = f"""
     ██╗       ██████╗     ███████╗
     ██║      ██╔═══██╗    ██╔════╝
     ██║      ██║   ██║    █████╗
     ██║      ██║   ██║    ██╔══╝
     ███████╗ ╚██████╔╝    ███████╗
     ╚══════╝  ╚═════╝     ╚══════╝
        (LEGENDS OF ELDORIA)

        A Text-Based RPG Adventure
                Version {self.VERSION}
        """
        print(colored_text(title, "\033[93m"))
        print("\n" + " " * 30 + "Press Enter to continue...")
        pause("")
    
    def show_main_menu(self) -> str:
        """Display main menu and get choice"""
        clear_screen()
        print("\n" + "="*60)
        print(colored_text(f"  {self.TITLE}", "\033[93m"))
        print("="*60)
        print("\n  [1] New Game")
        print("  [2] Load Game")
        print("  [3] Settings")
        print("  [4] Credits")
        print("  [5] Exit")
        print("\n" + "-"*60)
        
        return get_input("Choose an option: ", ["1", "2", "3", "4", "5", "new", "load", "settings", "credits", "exit"])
    
    def handle_main_menu_choice(self, choice: str):
        """Handle main menu selection"""
        if choice in ["1", "new"]:
            self.new_game()
        elif choice in ["2", "load"]:
            self.load_game_menu()
        elif choice in ["3", "settings"]:
            self.settings_menu()
        elif choice in ["4", "credits"]:
            self.show_credits()
        elif choice in ["5", "exit"]:
            self.exit_game()
    
    def new_game(self):
        """Start a new game"""
        clear_screen()
        print("\n" + "="*60)
        print(colored_text("  CREATE YOUR CHARACTER", "\033[92m"))
        print("="*60)
        
        # Get character name
        name = input("\nEnter your name: ").strip()
        if not name:
            name = "Hero"
        
        # Choose class
        print("\nChoose your class:")
        classes = list(CharacterClass)
        for i, char_class in enumerate(classes, 1):
            print(f"  [{i}] {char_class.value}")
        
        class_choice = get_input("\nSelect class (1-10): ", [str(i) for i in range(1, len(classes) + 1)])
        
        try:
            selected_class = classes[int(class_choice) - 1]
        except (ValueError, IndexError):
            selected_class = CharacterClass.WARRIOR
        
        # Create character
        self.player = Character(name, selected_class)
        self.player.position = "start_village"
        
        # Give starting items
        self._give_starting_items()
        
        # Initialize world for new game
        self.world = WorldMap()
        
        # Start game
        print(f"\nWelcome, {name} the {selected_class.value}!")
        print("Your adventure begins in Willowbrook Village...")
        pause()
        
        # Emit game start event
        self.plugin_manager.emit_event(EventType.GAME_START, {"player": self.player})
        
        # Enter game loop
        self.game_loop()
    
    def _give_starting_items(self):
        """Give starting items to new character"""
        # Starting gold
        self.player.inventory.gold = 100
        
        # Basic weapon based on class
        starting_weapons = {
            CharacterClass.WARRIOR: "rusty_sword",
            CharacterClass.MAGE: "rusty_sword",
            CharacterClass.ROGUE: "rusty_sword",
            CharacterClass.RANGER: "rusty_sword",
            CharacterClass.PALADIN: "rusty_sword",
            CharacterClass.NECROMANCER: "rusty_sword",
            CharacterClass.MONK: "rusty_sword",
            CharacterClass.BARD: "rusty_sword",
            CharacterClass.DRUID: "rusty_sword",
            CharacterClass.WARLOCK: "rusty_sword"
        }
        
        weapon_id = starting_weapons.get(self.player.character_class, "rusty_sword")
        weapon = get_item(weapon_id)
        if weapon:
            self.player.inventory.add_item(weapon)
            self.player.equip_item(weapon.name)
        
        # Basic armor
        armor = get_item("cloth_shirt")
        if armor:
            self.player.inventory.add_item(armor)
            self.player.equip_item(armor.name)
        
        # Starting potions
        for _ in range(3):
            potion = get_item("health_potion_minor")
            if potion:
                self.player.inventory.add_item(potion)
    
    def load_game_menu(self):
        """Show load game menu"""
        clear_screen()
        print(self.save_manager.get_save_display())
        
        saves = self.save_manager.list_saves()
        if not saves:
            pause("\nNo save files found. Press Enter to return...")
            return
        
        choice = input("\nEnter save name to load (or 'back'): ").strip()
        
        if choice.lower() != "back":
            self.load_game(choice)
    
    def load_game(self, save_name: str):
        """Load a saved game"""
        success, data, message = self.save_manager.load_game(save_name)
        
        if success:
            try:
                # Reconstruct game state
                self.player = Character.from_dict(data.get("player", {}))
                self.world = WorldMap.from_dict(data.get("world", {}))
                self.quest_manager = QuestManager.from_dict(data.get("quests", {}))
                self.play_time = data.get("play_time", 0)
                
                print(f"\nGame loaded: {self.player.name}, Level {self.player.level}")
                pause()
                
                # Emit load event
                self.plugin_manager.emit_event(EventType.GAME_LOAD, {"player": self.player})
                
                # Enter game loop
                self.game_loop()
                
            except Exception as e:
                print(f"\nError loading save: {e}")
                pause()
        else:
            print(f"\n{message}")
            pause()
    
    def save_game(self, save_name: str = None):
        """Save the current game"""
        if not self.player:
            return False, "No game in progress."
        
        # Update play time
        self.play_time += int(time.time() - self.start_time)
        self.start_time = time.time()
        
        game_state = {
            "player": self.player.to_dict(),
            "world": self.world.to_dict(),
            "quests": self.quest_manager.to_dict(),
            "play_time": self.play_time
        }
        
        success, message = self.save_manager.save_game(game_state, save_name)
        
        if success:
            self.plugin_manager.emit_event(EventType.GAME_SAVE, {"player": self.player})
        
        return success, message
    
    def settings_menu(self):
        """Display settings menu"""
        clear_screen()
        print("\n" + "="*60)
        print("  SETTINGS")
        print("="*60)
        print("\n  [1] Text Speed: Normal")
        print("  [2] Sound: Off (Text game)")
        print("  [3] Autosave: On")
        print("  [0] Back")
        print("\nSettings are automatically saved.")
        pause("\nPress Enter to return...")
    
    def show_credits(self):
        """Display credits"""
        clear_screen()
        credits = f"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                                 CREDITS                                      ║
╠══════════════════════════════════════════════════════════════════════════════╣
║                                                                              ║
║     LEGENDS OF ELDORIA                                                       ║
║     A Complete Text-Based RPG                                                ║
║                                                                              ║
║     Development: YSNRFD                                                      ║
║     Version: {self.VERSION}                                                          ║
║                                                                              ║
║     Features:                                                                ║
║       • Open World Exploration                                               ║
║       • Turn-Based Combat System                                             ║
║       • Quest & Story System                                                 ║
║       • NPC Interactions & Dialogue                                          ║
║       • Crafting & Item System                                               ║
║       • Plugin Architecture                                                  ║
║       • Save/Load System                                                     ║
║                                                                              ║
║     Special Thanks:                                                          ║
║       • Python Community                                                     ║
║       • All RPG Enthusiasts                                                  ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
        """
        print(colored_text(credits, "\033[96m"))
        pause("\nPress Enter to return...")
    
    def exit_game(self):
        """Exit the game"""
        if self.player:
            choice = get_input("\nSave before exiting? (y/n): ", ["y", "n", "yes", "no"])
            if choice in ["y", "yes"]:
                save_name = input("Enter save name (or press Enter for autosave): ").strip()
                self.save_game(save_name or None)
        
        self.running = False
        print("\nThank you for playing Legends of Eldoria!")
        print("Goodbye, adventurer!\n")
    
    def game_loop(self):
        """Main game loop"""
        while self.running:
            self.update()
            self.render()
            self.process_input()
    
    def update(self):
        """Update game state"""
        # Update quest availability
        self.quest_manager.update_quest_availability(
            self.player.completed_quests,
            self.player.level
        )
    
    def render(self):
        """Render the current game state"""
        clear_screen()
        self.show_game_header()
        self.show_location()
    
    def show_game_header(self):
        """Show game header with player info"""
        location = self.world.get_current_location()
        location_name = location.name if location else "Unknown"
        
        print("\n" + "="*80)
        print(f"{self.player.name} | Level {self.player.level} {self.player.character_class.value}")
        print(f"Location: {location_name}")
        print(self.world.get_time_display())
        print("="*80)
        print(f"HP: {self.player.get_hp_bar(20)}")
        print(f"MP: {self.player.get_mp_bar(20)}")
        print(f"Gold: {self.player.inventory.gold:,}")
        print("="*80)
    
    def show_location(self):
        """Show current location details"""
        location = self.world.get_current_location()
        if location:
            print(location.get_description())
            
            # Show NPCs
            npcs = self.npc_manager.get_npcs_at_location(location.id)
            if npcs:
                print("\nNPCs Present:")
                for npc in npcs:
                    print(f"  👤 {npc.name}")
            
            # Show connections
            if location.connections:
                print("\nTravel Options:")
                for conn_id in location.connections:
                    conn_loc = self.world.locations.get(conn_id)
                    if conn_loc:
                        discovered = "✓" if conn_loc.discovered else "?"
                        print(f"  [{discovered}] {conn_loc.name}")
    
    def process_input(self):
        """Process player input"""
        print("\n" + "-"*40)
        print("Actions: [E]xplore [T]ravel [I]nventory [C]haracter [Q]uests")
        print("         [S]ave [L]oad [M]ap [R]est [H]elp [X]Menu")
        
        choice = get_input("\nWhat do you want to do? ")
        
        self.handle_game_input(choice)
    
    def handle_game_input(self, choice: str):
        """Handle game input"""
        if choice == "e":
            self.explore()
        elif choice == "t":
            self.travel_menu()
        elif choice == "i":
            self.inventory_menu()
        elif choice == "c":
            self.character_menu()
        elif choice == "q":
            self.quest_menu()
        elif choice == "s":
            self.save_menu()
        elif choice == "l":
            self.load_game_menu()
        elif choice == "m":
            self.map_menu()
        elif choice == "r":
            self.rest()
        elif choice == "h":
            self.help_menu()
        elif choice == "x":
            self.game_menu()
        elif choice.startswith("/"):
            # Plugin command
            self.handle_plugin_command(choice[1:])
        else:
            self.interact_with_npc(choice)
    
    def explore(self):
        """Explore current location"""
        messages, encounter = self.world.explore(self.player)
        
        for msg in messages:
            print(msg)
        
        if encounter:
            if hasattr(encounter, 'is_alive'):  # Enemy
                pause("\nPress Enter to engage in combat...")
                self.start_combat([encounter])
            elif hasattr(encounter, 'event_type'):  # World Event
                self.handle_event(encounter)
            elif hasattr(encounter, 'item_type'):  # Item
                success, msg = self.player.inventory.add_item(encounter)
                print(f"\n{msg}")
        
        pause()
    
    def start_combat(self, enemies):
        """Start combat encounter"""
        combat = CombatEncounter(self.player, enemies, self.plugin_manager)
        result = combat.start()
        
        if result.victory:
            print(f"\nVictory!")
            print(f"Experience gained: {result.experience_gained}")
            print(f"Gold found: {result.gold_gained}")
            
            self.player.add_experience(result.experience_gained)
            self.player.add_gold(result.gold_gained)
            self.player.monsters_killed += len(enemies)
            
            for item in result.items_dropped:
                success, msg = self.player.inventory.add_item(item)
                print(f"Loot: {msg}")
            
            # Update quest objectives
            for enemy in enemies:
                self.quest_manager.update_objective(
                    ObjectiveType.KILL, 
                    enemy.name.lower().replace(" ", "_"),
                    1
                )
        
        elif result.fled:
            print("\nYou escaped!")
        
        else:
            print("\nYou have been defeated...")
            self.player.deaths += 1
            self.handle_death()
        
        pause()
    
    def handle_death(self):
        """Handle player death"""
        print("\nYou wake up back in the village, weakened but alive.")
        self.player.current_hp = self.player.max_hp // 2
        self.player.current_mp = self.player.max_mp // 2
        self.player.current_stamina = self.player.max_stamina // 2
        self.player.position = "start_village"
        self.world.current_location = "start_village"
        self.player.gold_lost_on_death = self.player.inventory.gold // 10
        self.player.inventory.gold -= self.player.gold_lost_on_death
        print(f"You lost {self.player.gold_lost_on_death} gold.")
        pause()
    
    def travel_menu(self):
        """Show travel menu"""
        location = self.world.get_current_location()
        if not location:
            return
        
        clear_screen()
        print("\n" + "="*60)
        print("TRAVEL")
        print("="*60)
        print("\nAvailable destinations:")
        
        for i, conn_id in enumerate(location.connections, 1):
            conn_loc = self.world.locations.get(conn_id)
            if conn_loc:
                discovered = "✓" if conn_loc.discovered else "?"
                danger = "⚠️" * conn_loc.danger_level
                print(f"  [{i}] [{discovered}] {conn_loc.name} {danger}")
        
        print("  [0] Cancel")
        
        choice = input("\nSelect destination: ").strip()
        
        try:
            idx = int(choice)
            if idx == 0:
                return
            if 1 <= idx <= len(location.connections):
                dest_id = location.connections[idx - 1]
                success, msg = self.world.travel_to(dest_id, self.player)
                print(f"\n{msg}")
                
                if success:
                    self.plugin_manager.emit_event(EventType.LOCATION_ENTER, {
                        "location": location,
                        "player": self.player
                    })
                
                pause()
        except ValueError:
            print("Invalid choice.")
            pause()
    
    def inventory_menu(self):
        """Show inventory menu"""
        clear_screen()
        print(self.player.inventory.get_display())
        
        print("\n[E]quip [U]se [D]rop [V]iew Item [B]ack")
        choice = get_input("\nChoose action: ", ["e", "u", "d", "v", "b"])
        
        if choice == "e":
            self.equip_menu()
        elif choice == "u":
            self.use_item_menu()
        elif choice == "d":
            self.drop_item_menu()
        elif choice == "v":
            self.view_item_menu()
    
    def equip_menu(self):
        """Equip item menu"""
        print("\nEquipment:")
        print(self.player.equipment.get_display())
        
        item_name = input("\nEnter item name to equip (or 'back'): ").strip()
        if item_name.lower() != "back":
            success, msg = self.player.equip_item(item_name)
            print(msg)
            pause()
    
    def use_item_menu(self):
        """Use item menu"""
        item_name = input("\nEnter item name to use (or 'back'): ").strip()
        if item_name.lower() != "back":
            success, msg = self.player.use_item(item_name)
            print(msg)
            pause()
    
    def drop_item_menu(self):
        """Drop item menu"""
        item_name = input("\nEnter item name to drop (or 'back'): ").strip()
        if item_name.lower() != "back":
            success, item = self.player.inventory.remove_item(item_name)
            if success:
                print(f"Dropped {item.name}.")
            else:
                print("Item not found.")
            pause()
    
    def view_item_menu(self):
        """View item details"""
        item_name = input("\nEnter item name to view (or 'back'): ").strip()
        if item_name.lower() != "back":
            item = self.player.inventory.get_item(item_name)
            if item:
                print(f"\n{item.examine()}")
            else:
                print("Item not found.")
            pause()
    
    def character_menu(self):
        """Show character information"""
        clear_screen()
        print(self.player.get_status_display())
        print(self.player.equipment.get_display())
        print(f"\nStatistics:")
        print(f"  Monsters Killed: {self.player.monsters_killed}")
        print(f"  Deaths: {self.player.deaths}")
        print(f"  Quests Completed: {self.player.quests_completed}")
        print(f"  Items Crafted: {self.player.items_crafted}")
        
        print("\n[S]kills [A]bilities [B]ack")
        choice = get_input("\nChoose: ", ["s", "a", "b"])
        
        if choice == "s":
            self.skills_menu()
        elif choice == "a":
            self.abilities_menu()
    
    def skills_menu(self):
        """Show skills"""
        print("\nSkills:")
        for skill_name, skill in self.player.skills.items():
            level_text = f"Lv.{skill.current_level}/{skill.max_level}"
            exp_text = f"({skill.experience}/{skill.get_exp_to_next_level()})" if skill.current_level < skill.max_level else "MAX"
            print(f"  {skill_name}: {level_text} {exp_text}")
        pause()
    
    def abilities_menu(self):
        """Show abilities"""
        print("\nAbilities:")
        if not self.player.abilities:
            print("  No abilities learned.")
        else:
            for ability in self.player.abilities:
                mp_text = f"MP:{ability.mp_cost}" if ability.mp_cost > 0 else ""
                stamina_text = f"SP:{ability.stamina_cost}" if ability.stamina_cost > 0 else ""
                print(f"  • {ability.name} {mp_text} {stamina_text}")
                print(f"    {ability.description}")
        pause()
    
    def quest_menu(self):
        """Show quest log"""
        clear_screen()
        print(self.quest_manager.get_quest_display())
        
        active = self.quest_manager.get_active_quests()
        if active:
            print("\nSelect quest for details (1-{}) or 0 to go back: ".format(len(active)))
            choice = input().strip()
            try:
                idx = int(choice)
                if 1 <= idx <= len(active):
                    quest = active[idx - 1]
                    print(quest.get_display())
            except ValueError:
                pass
        
        pause("\nPress Enter to continue...")
    
    def save_menu(self):
        """Save game menu"""
        save_name = input("\nEnter save name (or press Enter for autosave): ").strip()
        success, msg = self.save_game(save_name or None)
        print(msg)
        pause()
    
    def map_menu(self):
        """Show world map"""
        clear_screen()
        print(self.world.get_map_display())
        pause()
    
    def rest(self):
        """Rest to restore HP/MP"""
        location = self.world.get_current_location()
        
        # Check if can rest here
        can_rest = location and location.location_type.value in ["town", "city", "village", "inn"]
        
        if can_rest:
            print("\nYou find a place to rest...")
            time.sleep(1)
            
            self.player.current_hp = self.player.max_hp
            self.player.current_mp = self.player.max_mp
            self.player.current_stamina = self.player.max_stamina
            
            # Advance time
            self.world.advance_time(8)
            
            print("You feel well rested!")
            print(f"HP and MP fully restored.")
        else:
            print("\nYou cannot rest here. Find an inn or safe location.")
        
        pause()
    
    def help_menu(self):
        """Show help"""
        clear_screen()
        help_text = """
╔══════════════════════════════════════════════════════════════════════════════╗
║                              HELP & CONTROLS                                 ║
╠══════════════════════════════════════════════════════════════════════════════╣
║                                                                              ║
║  BASIC COMMANDS:                                                             ║
║    E - Explore the current location                                          ║
║    T - Travel to another location                                            ║
║    I - Open inventory                                                        ║
║    C - View character sheet                                                  ║
║    Q - View quest log                                                        ║
║    M - View world map                                                        ║
║    R - Rest (restore HP/MP)                                                  ║
║    S - Save game                                                             ║
║    L - Load game                                                             ║
║    H - Show this help                                                        ║
║    X - Return to main menu                                                   ║
║                                                                              ║
║  COMBAT:                                                                     ║
║    During combat, choose actions with number keys (1-5)                      ║
║    Attack, use abilities, items, defend, or flee                             ║
║                                                                              ║
║  PLUGINS:                                                                    ║
║    Use / before command to use plugin commands                               ║
║    Example: /help - shows plugin commands                                    ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
        """
        print(help_text)
        pause()
    
    def game_menu(self):
        """In-game menu"""
        print("\n" + "-"*40)
        print("[S]ave and Exit  [Q]uit without saving  [R]eturn to game")
        choice = get_input("Choose: ", ["s", "q", "r"])
        
        if choice == "s":
            self.save_game()
            self.running = False
        elif choice == "q":
            self.running = False
    
    def interact_with_npc(self, npc_name: str):
        """Interact with an NPC"""
        npcs = self.npc_manager.get_npcs_at_location(self.world.current_location)
        
        for npc in npcs:
            if npc_name.lower() in npc.name.lower():
                self.npc_interaction(npc)
                return
        
        print("\nNo one here by that name.")
        pause()
    
    def npc_interaction(self, npc):
        """Handle NPC interaction"""
        clear_screen()
        print(npc.get_display())
        
        while True:
            print("\n" + npc.get_greeting())
            print("\n" + "\n".join(npc.get_interactions()))
            
            choice = get_input("\nChoose: ")
            
            if choice == "1":  # Talk
                self.npc_dialogue(npc)
            elif choice == "2" and (npc.shop_id or npc.shop_items):  # Trade
                self.shop_menu(npc)
            elif choice == "3" and "heal" in npc.services:  # Heal
                self.npc_heal(npc)
            elif choice == "4" and "rest" in npc.services:  # Rest
                self.rest()
            elif choice == "5" and npc.can_train:  # Train
                self.npc_train(npc)
            elif choice == "0":  # Leave
                break
    
    def npc_dialogue(self, npc):
        """Handle NPC dialogue"""
        while True:
            node = npc.get_dialogue()
            if not node:
                break
            
            print(f"\n{npc.name}: {node.text}")
            
            if not node.choices:
                pause("\nPress Enter to continue...")
                break
            
            for i, choice in enumerate(node.choices, 1):
                print(f"  [{i}] {choice.text}")
            
            selection = input("\nChoose response: ").strip()
            try:
                idx = int(selection) - 1
                if 0 <= idx < len(node.choices):
                    choice = node.choices[idx]
                    action, data = npc.advance_dialogue(idx, self.player, self.quest_manager)
                    
                    if "message" in data:
                        print(f"\n{data['message']}")
                        pause("\nPress Enter to continue...")
                    
                    # Handle actions that should exit dialogue
                    if action.value == "open_shop":
                        self.shop_menu(npc)
                        break
                    elif action.value == "start_quest":
                        self.handle_dialogue_action(npc, action, data)
                        pause("\nPress Enter to continue...")
                        break
                    elif action.value == "train":
                        self.npc_train(npc)
                        break
                    elif action.value == "none" and not choice.next_node:
                        # End dialogue if no next node
                        pause("\nPress Enter to continue...")
                        break
                    elif action.value != "none":
                        self.handle_dialogue_action(npc, action, data)
                        pause("\nPress Enter to continue...")
                        break
                else:
                    print("Invalid choice.")
                    pause()
            except ValueError:
                print("Please enter a number.")
                pause()
    
    def handle_dialogue_action(self, npc, action, data):
        """Handle dialogue action"""
        if action.value == "start_quest":
            # Start available quest
            available = self.quest_manager.get_available_quests()
            quest_found = False
            for quest in available:
                if quest.giver == npc.id:
                    success, msg = self.quest_manager.start_quest(quest.id)
                    if success:
                        print(f"\n{msg}")
                        print(f"Quest objectives: {quest.description}")
                        self.player.quests[quest.id] = quest
                        quest_found = True
                    break
            
            if not quest_found:
                # Check if player already has this quest
                has_quest = any(q.giver == npc.id for q in self.quest_manager.get_active_quests())
                if has_quest:
                    print(f"\nYou already have a quest from {npc.name}. Check your quest log.")
                else:
                    print(f"\n{npc.name} has no work for you at the moment.")
        
        elif action.value == "give_item":
            item = get_item(data.get("item_id"))
            if item:
                self.player.inventory.add_item(item)
                print(f"\nReceived: {item.name}")
        
        elif action.value == "give_gold":
            amount = data.get("amount", 0)
            self.player.add_gold(amount)
            print(f"\nReceived: {amount} gold")
    
    def shop_menu(self, npc):
        """Shop interface"""
        while True:
            clear_screen()
            print(f"\n{'='*60}")
            print(f"  {npc.name}'s Shop")
            print(f"{'='*60}")
            print(f"\nYour Gold: {self.player.inventory.gold}")
            
            print("\nItems for Sale:")
            for i, item_id in enumerate(npc.shop_items, 1):
                from core.items import ITEM_DATABASE
                item_data = ITEM_DATABASE.get(item_id, {})
                price = int(item_data.get("value", 0) * npc.buy_multiplier)
                print(f"  [{i}] {item_data.get('name', item_id)} - {price} gold")
            
            print("\n[B]uy  [S]ell  [E]xit")
            choice = get_input("\nChoose: ", ["b", "s", "e"] + [str(i) for i in range(1, len(npc.shop_items) + 1)])
            
            if choice == "e":
                break
            elif choice == "b":
                self.buy_item(npc)
            elif choice == "s":
                self.sell_item(npc)
            elif choice.isdigit():
                idx = int(choice) - 1
                if 0 <= idx < len(npc.shop_items):
                    self.buy_item(npc, idx)
    
    def buy_item(self, npc, item_idx: int = None):
        """Buy an item from shop"""
        if item_idx is None:
            selection = input("\nEnter item number: ").strip()
            try:
                item_idx = int(selection) - 1
            except ValueError:
                return
        
        if 0 <= item_idx < len(npc.shop_items):
            item_id = npc.shop_items[item_idx]
            from core.items import ITEM_DATABASE
            item_data = ITEM_DATABASE.get(item_id, {})
            price = int(item_data.get("value", 0) * npc.buy_multiplier)
            
            if self.player.inventory.gold >= price:
                item = get_item(item_id)
                if item:
                    self.player.inventory.gold -= price
                    self.player.inventory.add_item(item)
                    print(f"\nPurchased {item.name} for {price} gold.")
            else:
                print("\nNot enough gold!")
        
        pause()
    
    def sell_item(self, npc):
        """Sell an item to shop"""
        item_name = input("\nEnter item name to sell: ").strip()
        item = self.player.inventory.get_item(item_name)
        
        if item:
            price = int(item.value * npc.sell_multiplier)
            self.player.inventory.remove_item(item_name)
            self.player.inventory.gold += price
            print(f"\nSold {item.name} for {price} gold.")
        else:
            print("\nItem not found.")
        
        pause()
    
    def npc_heal(self, npc):
        """Heal from NPC"""
        cost = 50
        if self.player.inventory.gold >= cost:
            self.player.inventory.gold -= cost
            self.player.current_hp = self.player.max_hp
            self.player.current_mp = self.player.max_mp
            print(f"\nFully healed for {cost} gold!")
        else:
            print("\nNot enough gold!")
        pause()
    
    def npc_train(self, npc):
        """Train skills with NPC"""
        print(f"\nTraining available for: {', '.join(npc.can_train)}")
        print(f"Cost: {npc.training_cost} gold")
        
        skill_name = input("\nEnter skill to train (or 'cancel'): ").strip()
        
        if skill_name.lower() == "cancel":
            return
        
        if skill_name in npc.can_train:
            if self.player.inventory.gold >= npc.training_cost:
                skill = self.player.skills.get(skill_name)
                if skill:
                    self.player.inventory.gold -= npc.training_cost
                    skill.add_experience(50)
                    print(f"\nTrained {skill_name}!")
                else:
                    print("\nSkill not found.")
            else:
                print("\nNot enough gold!")
        else:
            print("\nThis trainer doesn't teach that skill.")
        
        pause()
    
    def handle_event(self, event):
        """Handle a world event"""
        print(f"\n{'='*60}")
        print(f"EVENT: {event.name}")
        print(f"{'='*60}")
        print(event.description)
        print("\nChoices:")
        
        for i, choice in enumerate(event.choices, 1):
            print(f"  [{i}] {choice['text']}")
        
        selection = input("\nChoose: ").strip()
        try:
            idx = int(selection) - 1
            if 0 <= idx < len(event.choices):
                self.process_event_choice(event, event.choices[idx])
        except ValueError:
            pass
    
    def process_event_choice(self, event, choice):
        """Process event choice"""
        effect = choice.get("effect", "nothing")
        
        if effect == "treasure":
            rewards = event.rewards
            gold = random.randint(*rewards.get("gold", (0, 0)))
            if gold:
                self.player.add_gold(gold)
                print(f"\nFound {gold} gold!")
            
            if random.random() < rewards.get("item_chance", 0):
                from core.items import get_random_item
                item = get_random_item()
                if item:
                    self.player.inventory.add_item(item)
                    print(f"Found: {item.name}!")
        
        elif effect == "open_shop":
            print("\nA merchant offers their wares...")
            # Would open special shop
        
        elif effect == "heal":
            self.player.heal(50)
            print("\nYou helped someone in need.")
            self.player.change_friendship(event.id, 10)
        
        elif effect == "blessing":
            print("\nYou feel a divine blessing wash over you.")
            self.player.apply_status_effect(StatusEffectType.BLESSING, 10, 2)
        
        elif effect == "portal":
            locations = list(self.world.locations.keys())
            dest = random.choice(locations)
            self.world.travel_to(dest, self.player)
            print(f"\nThe portal transports you to {self.world.get_current_location().name}!")
        
        elif effect == "combat":
            from systems.combat import EnemyFactory
            enemies = []
            for enemy_id in choice.get("enemies", []):
                enemy = EnemyFactory.create_enemy(enemy_id, self.player.level)
                if enemy:
                    enemies.append(enemy)
            if enemies:
                self.start_combat(enemies)
        
        # Mark event as triggered if one-time
        if event.one_time:
            event.triggered = True
        
        pause()
    
    def handle_plugin_command(self, command: str):
        """Handle a plugin command"""
        parts = command.split()
        cmd_name = parts[0] if parts else ""
        args = parts[1:] if len(parts) > 1 else []
        
        success, result = self.plugin_manager.execute_command(cmd_name, self, args)
        print(f"\n{result}")
        pause()


def main():
    """Main entry point"""
    game = Game()
    game.start()


if __name__ == "__main__":
    main()

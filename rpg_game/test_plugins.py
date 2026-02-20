#!/usr/bin/env python3
"""Test script to verify all plugins load correctly"""

import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from systems.plugins import PluginManager

class MockGame:
    def __init__(self):
        self.world = None
        self.npc_manager = None
        self.quest_manager = None
        self.crafting_manager = None

print("Testing plugin loading...")
print("=" * 60)

game = MockGame()
pm = PluginManager(game)
success, failed = pm.load_all_plugins()

print(f"\nResults:")
print(f"  Plugins loaded successfully: {success}")
print(f"  Plugins failed: {failed}")
print(f"\nLoaded plugin IDs: {list(pm.plugins.keys())}")
print(f"\nTotal commands registered: {len(pm._commands)}")
print(f"\nCommands available: {sorted(pm._commands.keys())}")

print("\n" + "=" * 60)
if success == 6 and failed == 0:
    print("SUCCESS: All 6 plugins loaded correctly!")
else:
    print(f"WARNING: Expected 6 plugins, got {success} successful, {failed} failed")

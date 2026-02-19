# Bug Fix TODO List

## Critical Bugs (Must Fix First)
- [ ] 1. main.py: Fix import path (line 9)
- [ ] 2. character.py: Fix Inventory._item_to_dict() serialization
- [ ] 3. character.py: Fix Equipment.from_dict() ItemFactory issue
- [ ] 4. engine.py: Fix Item dataclass inheritance
- [ ] 5. engine.py: Fix Ability.from_dict() StatusEffectType bug
- [ ] 6. items.py: Fix Consumable.use() argument order
- [ ] 7. combat.py: Fix _player_item() argument type
- [ ] 8. npc.py: Fix advance_dialogue() signature mismatch
- [ ] 9. main.py: Fix handle_dialogue_action() quest_manager call
- [ ] 10. crafting.py: Fix material removal by ID
- [ ] 11. save_load.py: Fix enum serialization
- [ ] 12. plugins.py: Fix world.register_locations() call

## Medium Priority Bugs
- [ ] 13. combat.py: Fix defense buff damage calculation
- [ ] 14. main.py: Fix class-appropriate starting weapons
- [ ] 15. character.py: Fix equip_item() duplicate check
- [ ] 16. combat.py: Fix enemy AI ability usage check
- [ ] 17. world.py: Fix event attribute checking
- [ ] 18. plugins.py: Fix _load_quests() initialization
- [ ] 19. character.py: Fix add_experience() ability learning
- [ ] 20. combat.py: Fix loot scaling
- [ ] 21. save_load.py: Add version validation
- [ ] 22. character.py: Add missing __future__ import

## Progress
- Total: 22 bugs
- Fixed: 0
- Remaining: 22

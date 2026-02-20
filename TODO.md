# Plugin Rewrite TODO

## Tasks

- [x] 1. Analyze existing plugin system and all plugin files
- [x] 2. Rewrite `base_plugin_template.py` - Fix incompatible API references
- [x] 3. Rewrite `help_plugin.py` - Add enhanced features

- [x] 4. Rewrite `enhanced_combat.py` - Add complete content provider support

- [x] 5. Rewrite `extended_items.py` - Add recipes and enhanced features

- [x] 6. Rewrite `extended_npcs.py` - Add complete quest provider support

- [x] 7. Rewrite `extended_world.py` - Add complete location provider support

- [x] 8. Update `json_plugin_template.json` - Ensure compatibility

- [x] 9. Update `README.md` - Fix documentation
- [x] 10. Test all plugins load correctly



## Key Changes Needed

### base_plugin_template.py
- Replace `PluginBase` with actual `Plugin` class
- Remove non-existent imports (`PluginType`, `EventPriority`, `IPlugin`, etc.)
- Use actual `EventType` from `core.engine`
- Demonstrate working lifecycle methods
- Show proper hook and command registration

### All Plugins
- Ensure proper `on_load`, `on_unload`, `on_enable`, `on_disable` signatures
- Use correct `register_hooks` and `register_commands` return formats
- Implement proper content provider methods
- Add error handling

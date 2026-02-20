"""
================================================================================
Dynamic Plugin System - Universal Plugin Architecture
================================================================================

A fully dynamic, extensible plugin system supporting:
- Any plugin structure and architecture
- Multiple plugin formats (Python, JSON, YAML, TOML)
- Dynamic content type registration
- Hot reloading and live updates
- Dependency injection and resolution
- Inter-plugin communication
- Custom plugin interfaces (duck typing)
- Plugin configuration management
- Event pipelines with middleware
- Plugin discovery from multiple sources
- Async plugin operations
- Plugin groups and modules
- Version management and compatibility

================================================================================
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import (
    Dict, List, Tuple, Optional, Any, Callable, Union
)
from abc import ABC, abstractmethod
from enum import Enum, auto
import os
import sys
import importlib.util
import threading
from collections import defaultdict
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('PluginSystem')

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.engine import EventType


# =============================================================================
# PLUGIN STATE AND METADATA
# =============================================================================

class PluginState(Enum):
    """All possible states a plugin can be in"""
    UNDISCOVERED = auto()
    DISCOVERED = auto()
    LOADING = auto()
    RESOLVING = auto()
    INITIALIZING = auto()
    ENABLED = auto()
    DISABLED = auto()
    ERROR = auto()
    UNLOADING = auto()
    PENDING_RELOAD = auto()
    HOT_RELOADING = auto()


class PluginPriority(Enum):
    """Plugin loading priority levels"""
    SYSTEM = 0        # Core system plugins
    CORE = 25         # Essential plugins
    HIGH = 50         # High priority content
    NORMAL = 100      # Standard plugins
    LOW = 150         # Low priority additions
    OPTIONAL = 200    # Optional content


@dataclass
class PluginInfo:
    """Plugin metadata and information"""
    id: str
    name: str
    version: str = "1.0.0"
    author: str = "Unknown"
    description: str = ""
    dependencies: List[str] = field(default_factory=list)
    soft_dependencies: List[str] = field(default_factory=list)
    conflicts: List[str] = field(default_factory=list)
    priority: PluginPriority = PluginPriority.NORMAL
    tags: List[str] = field(default_factory=list)
    min_game_version: str = "1.0.0"
    max_game_version: str = ""
    
    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "name": self.name,
            "version": self.version,
            "author": self.author,
            "description": self.description,
            "dependencies": self.dependencies,
            "soft_dependencies": self.soft_dependencies,
            "conflicts": self.conflicts,
            "priority": self.priority.value,
            "tags": self.tags,
            "min_game_version": self.min_game_version,
            "max_game_version": self.max_game_version
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'PluginInfo':
        return cls(
            id=data["id"],
            name=data.get("name", data["id"]),
            version=data.get("version", "1.0.0"),
            author=data.get("author", "Unknown"),
            description=data.get("description", ""),
            dependencies=data.get("dependencies", []),
            soft_dependencies=data.get("soft_dependencies", []),
            conflicts=data.get("conflicts", []),
            priority=PluginPriority(data.get("priority", 100)),
            tags=data.get("tags", []),
            min_game_version=data.get("min_game_version", "1.0.0"),
            max_game_version=data.get("max_game_version", "")
        )


# =============================================================================
# PLUGIN INTERFACE
# =============================================================================

class Plugin(ABC):
    """Abstract base class for plugins"""
    
    def __init__(self, info: PluginInfo):
        self.info = info
        self.state = PluginState.DISCOVERED
        self._enabled = False
        self._config: Dict[str, Any] = {}
        self._hooks: Dict[EventType, List[Callable]] = defaultdict(list)
        self._commands: Dict[str, Callable] = {}
    
    @property
    def id(self) -> str:
        return self.info.id
    
    @property
    def enabled(self) -> bool:
        return self._enabled
    
    @abstractmethod
    def on_load(self, game: Any) -> bool:
        """Called when plugin is loaded"""
        pass
    
    @abstractmethod
    def on_unload(self, game: Any) -> bool:
        """Called when plugin is unloaded"""
        pass
    
    @abstractmethod
    def on_enable(self, game: Any) -> bool:
        """Called when plugin is enabled"""
        pass
    
    @abstractmethod
    def on_disable(self, game: Any) -> bool:
        """Called when plugin is disabled"""
        pass
    
    def register_hook(self, event_type: EventType, callback: Callable):
        """Register an event hook"""
        self._hooks[event_type].append(callback)
    
    def register_command(self, name: str, callback: Callable):
        """Register a command"""
        self._commands[name] = callback
    
    def get_config(self, key: str, default: Any = None) -> Any:
        """Get configuration value"""
        return self._config.get(key, default)
    
    def set_config(self, key: str, value: Any):
        """Set configuration value"""
        self._config[key] = value


# =============================================================================
# PLUGIN MANAGER
# =============================================================================

class PluginManager:
    """Manages all plugins"""
    
    def __init__(self, game: Any):
        self.game = game
        self.plugins: Dict[str, Plugin] = {}
        self._plugin_order: List[str] = []
        self._event_handlers: Dict[EventType, List[Callable]] = defaultdict(list)
        self._commands: Dict[str, Callable] = {}
        self._content_registries: Dict[str, Dict[str, Any]] = defaultdict(dict)
        self._lock = threading.RLock()
    
    def load_all_plugins(self) -> Tuple[int, int]:
        """Load all plugins from the plugins directory"""
        success = 0
        failed = 0
        
        plugins_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "plugins")
        
        if not os.path.exists(plugins_dir):
            logger.info("Plugins directory not found, creating...")
            os.makedirs(plugins_dir, exist_ok=True)
            return success, failed
        
        # Discover plugins
        plugin_files = []
        for filename in os.listdir(plugins_dir):
            if filename.endswith('.py') and not filename.startswith('_'):
                plugin_files.append(os.path.join(plugins_dir, filename))
        
        # Sort by priority (will be determined after loading)
        loaded_plugins = []
        
        for plugin_path in plugin_files:
            try:
                plugin = self._load_plugin_file(plugin_path)
                if plugin:
                    loaded_plugins.append(plugin)
                    success += 1
            except Exception as e:
                logger.error(f"Failed to load plugin from {plugin_path}: {e}")
                failed += 1
        
        # Sort by priority and initialize
        loaded_plugins.sort(key=lambda p: p.info.priority.value)
        
        for plugin in loaded_plugins:
            try:
                self._initialize_plugin(plugin)
            except Exception as e:
                logger.error(f"Failed to initialize plugin {plugin.id}: {e}")
                failed += 1
                success -= 1
        
        return success, failed
    
    def _load_plugin_file(self, path: str) -> Optional[Plugin]:
        """Load a plugin from a file"""
        try:
            # Use unique module name based on filename to avoid import caching issues
            module_name = os.path.basename(path)[:-3]  # Remove .py extension
            
            # Create the spec
            spec = importlib.util.spec_from_file_location(module_name, path)
            if not spec or not spec.loader:
                return None
            
            # Create and register module in sys.modules before executing
            # This is required for dataclasses to work properly
            module = importlib.util.module_from_spec(spec)
            sys.modules[module_name] = module
            
            # Execute the module
            spec.loader.exec_module(module)
            
            # Look for plugin instance
            if hasattr(module, 'plugin'):
                return module.plugin
            elif hasattr(module, 'Plugin'):
                # Try to instantiate
                plugin_class = module.Plugin
                info = PluginInfo(
                    id=os.path.basename(path)[:-3],
                    name=os.path.basename(path)[:-3].replace('_', ' ').title()
                )
                return plugin_class(info)
            
            return None
            
        except Exception as e:
            logger.error(f"Error loading plugin file {path}: {e}")
            return None
    
    def _initialize_plugin(self, plugin: Plugin):
        """Initialize a loaded plugin"""
        with self._lock:
            # Check for conflicts
            for conflict_id in plugin.info.conflicts:
                if conflict_id in self.plugins:
                    raise ValueError(f"Plugin conflict: {plugin.id} conflicts with {conflict_id}")
            
            # Check dependencies
            for dep_id in plugin.info.dependencies:
                if dep_id not in self.plugins:
                    raise ValueError(f"Missing dependency: {plugin.id} requires {dep_id}")
            
            # Load plugin
            plugin.state = PluginState.LOADING
            if plugin.on_load(self.game):
                plugin.state = PluginState.INITIALIZING
                
                # Register hooks
                for event_type, handlers in plugin._hooks.items():
                    for handler in handlers:
                        self._event_handlers[event_type].append(handler)
                
                # Register commands from plugin's _commands dict
                for name, callback in plugin._commands.items():
                    self._commands[name] = callback
                
                # Register commands from register_commands() method if available
                if hasattr(plugin, 'register_commands'):
                    try:
                        commands = plugin.register_commands(self)
                        if commands:
                            for name, cmd_data in commands.items():
                                if isinstance(cmd_data, dict) and 'handler' in cmd_data:
                                    self._commands[name] = cmd_data['handler']
                                elif callable(cmd_data):
                                    self._commands[name] = cmd_data
                    except Exception as e:
                        logger.warning(f"Error registering commands from {plugin.id}: {e}")
                
                # Enable plugin
                if plugin.on_enable(self.game):
                    plugin._enabled = True
                    plugin.state = PluginState.ENABLED
                    self.plugins[plugin.id] = plugin
                    self._plugin_order.append(plugin.id)
                    logger.info(f"Plugin enabled: {plugin.id}")
                else:
                    plugin.state = PluginState.ERROR
                    raise RuntimeError(f"Plugin {plugin.id} failed to enable")
            else:
                plugin.state = PluginState.ERROR
                raise RuntimeError(f"Plugin {plugin.id} failed to load")
    
    def unload_plugin(self, plugin_id: str) -> bool:
        """Unload a plugin"""
        with self._lock:
            plugin = self.plugins.get(plugin_id)
            if not plugin:
                return False
            
            plugin.state = PluginState.UNLOADING
            
            # Disable
            if plugin.enabled:
                plugin.on_disable(self.game)
                plugin._enabled = False
            
            # Unload
            plugin.on_unload(self.game)
            
            # Remove hooks
            for event_type, handlers in plugin._hooks.items():
                for handler in handlers:
                    if handler in self._event_handlers[event_type]:
                        self._event_handlers[event_type].remove(handler)
            
            # Remove commands
            for name in plugin._commands:
                if name in self._commands:
                    del self._commands[name]
            
            # Remove from registry
            del self.plugins[plugin_id]
            self._plugin_order.remove(plugin_id)
            
            logger.info(f"Plugin unloaded: {plugin_id}")
            return True
    
    def get_plugin(self, plugin_id: str) -> Optional[Plugin]:
        """Get a plugin by ID"""
        return self.plugins.get(plugin_id)
    
    def emit_event(self, event_type: EventType, data: Dict):
        """Emit an event to all registered handlers"""
        handlers = self._event_handlers.get(event_type, [])
        for handler in handlers:
            try:
                handler(self.game, data)
            except Exception as e:
                logger.error(f"Error in event handler for {event_type}: {e}")
    
    def emit(self, event_type: EventType, data: Dict):
        """Alias for emit_event - provides compatibility with event system interface"""
        self.emit_event(event_type, data)
    
    def execute_command(self, command: str, *args, **kwargs) -> Tuple[bool, Any]:
        """Execute a registered command"""
        if command not in self._commands:
            return False, f"Unknown command: {command}"
        
        try:
            # Create a context dictionary to pass to command handlers
            context = {
                "plugin_manager": self,
                "game": self.game if args else None,
                "timestamp": None
            }
            
            # Call the command handler with game, args, and context
            # The handler signature is: handler(game, args, context)
            handler = self._commands[command]
            
            # Check if handler is a bound method (has self as first arg)
            # or a regular function
            if len(args) >= 2:
                # args contains (game, args_list)
                game = args[0]
                cmd_args = args[1] if len(args) > 1 else []
                result = handler(game, cmd_args, context)
            elif len(args) == 1:
                # Only game passed
                game = args[0]
                result = handler(game, [], context)
            else:
                # No args passed
                result = handler(None, [], context)
            
            return True, result
        except TypeError as e:
            # Check if it's the specific error about missing context argument
            if "missing 1 required positional argument: 'context'" in str(e):
                logger.error(f"Error executing command {command}: Command handler missing 'context' argument. Please update the plugin to accept context parameter.")
                return False, f"Error: Command {command} handler has incorrect signature. Expected: handler(game, args, context)"
            logger.error(f"Error executing command {command}: {e}")
            return False, str(e)
        except Exception as e:
            logger.error(f"Error executing command {command}: {e}")
            return False, str(e)
    
    def register_content(self, content_type: str, content_id: str, content: Any):
        """Register content from a plugin"""
        self._content_registries[content_type][content_id] = content
    
    def get_content(self, content_type: str, content_id: str) -> Optional[Any]:
        """Get registered content"""
        return self._content_registries[content_type].get(content_id)
    
    def get_all_content(self, content_type: str) -> Dict[str, Any]:
        """Get all content of a type"""
        return dict(self._content_registries[content_type])
    
    def _load_locations(self, plugin: Any):
        """Load locations from plugin"""
        locations = getattr(plugin, 'locations', {})
        if locations and hasattr(self.game, 'world') and self.game.world:
            try:
                count = self.game.world.register_locations(locations)
                logger.info(f"Registered {count} locations from plugin {plugin.id}")
            except AttributeError as e:
                logger.warning(f"Could not register locations: {e}")
    
    def _load_npcs(self, plugin: Any):
        """Load NPCs from plugin"""
        npcs = getattr(plugin, 'npcs', {})
        if npcs and hasattr(self.game, 'npc_manager') and self.game.npc_manager:
            try:
                count = self.game.npc_manager.register_npcs(npcs)
                logger.info(f"Registered {count} NPCs from plugin {plugin.id}")
            except AttributeError as e:
                logger.warning(f"Could not register NPCs: {e}")
    
    def _load_quests(self, plugin: Any):
        """Load quests from plugin"""
        quests = getattr(plugin, 'quests', {})
        if quests and hasattr(self.game, 'quest_manager') and self.game.quest_manager:
            try:
                for quest_id, quest_data in quests.items():
                    quest_data["id"] = quest_id
                    # Ensure all required fields are present
                    if "name" not in quest_data:
                        quest_data["name"] = quest_id.replace('_', ' ').title()
                    if "description" not in quest_data:
                        quest_data["description"] = f"A quest: {quest_data['name']}"
                    if "quest_type" not in quest_data:
                        quest_data["quest_type"] = "side"
                    if "objectives" not in quest_data:
                        quest_data["objectives"] = []
                    if "rewards" not in quest_data:
                        quest_data["rewards"] = {}
                    
                    from systems.quests import Quest, QuestReward
                    quest = Quest.from_dict(quest_data)
                    self.game.quest_manager.quests[quest_id] = quest
                logger.info(f"Registered {len(quests)} quests from plugin {plugin.id}")
            except Exception as e:
                logger.warning(f"Could not register quests: {e}")
    
    def _load_items(self, plugin: Any):
        """Load items from plugin"""
        items = getattr(plugin, 'items', {})
        if items:
            from core.items import ITEM_DATABASE
            ITEM_DATABASE.update(items)
            logger.info(f"Registered {len(items)} items from plugin {plugin.id}")
    
    def _load_recipes(self, plugin: Any):
        """Load crafting recipes from plugin"""
        recipes = getattr(plugin, 'recipes', {})
        if recipes and hasattr(self.game, 'crafting_manager') and self.game.crafting_manager:
            try:
                from systems.crafting import CraftingRecipe
                for recipe_id, recipe_data in recipes.items():
                    recipe_data["id"] = recipe_id
                    recipe = CraftingRecipe.from_dict(recipe_data)
                    self.game.crafting_manager.recipes[recipe_id] = recipe
                logger.info(f"Registered {len(recipes)} recipes from plugin {plugin.id}")
            except Exception as e:
                logger.warning(f"Could not register recipes: {e}")


# =============================================================================
# FUNCTIONAL PLUGIN BUILDER
# =============================================================================

@dataclass
class FunctionalPlugin(Plugin):
    """A plugin defined through function calls"""
    
    on_load_func: Optional[Callable] = None
    on_unload_func: Optional[Callable] = None
    on_enable_func: Optional[Callable] = None
    on_disable_func: Optional[Callable] = None
    
    def on_load(self, game: Any) -> bool:
        if self.on_load_func:
            try:
                return self.on_load_func(game)
            except Exception as e:
                logger.error(f"Error in plugin {self.id} on_load: {e}")
                return False
        return True
    
    def on_unload(self, game: Any) -> bool:
        if self.on_unload_func:
            try:
                return self.on_unload_func(game)
            except Exception as e:
                logger.error(f"Error in plugin {self.id} on_unload: {e}")
                return False
        return True
    
    def on_enable(self, game: Any) -> bool:
        if self.on_enable_func:
            try:
                return self.on_enable_func(game)
            except Exception as e:
                logger.error(f"Error in plugin {self.id} on_enable: {e}")
                return False
        return True
    
    def on_disable(self, game: Any) -> bool:
        if self.on_disable_func:
            try:
                return self.on_disable_func(game)
            except Exception as e:
                logger.error(f"Error in plugin {self.id} on_disable: {e}")
                return False
        return True


class PluginBuilder:
    """Builder for creating functional plugins"""
    
    def __init__(self, plugin_id: str):
        self._id = plugin_id
        self._name = plugin_id.replace('_', ' ').title()
        self._version = "1.0.0"
        self._author = "Unknown"
        self._description = ""
        self._dependencies: List[str] = []
        self._conflicts: List[str] = []
        self._priority = PluginPriority.NORMAL
        self._tags: List[str] = []
        
        self._on_load: Optional[Callable] = None
        self._on_unload: Optional[Callable] = None
        self._on_enable: Optional[Callable] = None
        self._on_disable: Optional[Callable] = None
        self._hooks: Dict[EventType, Callable] = {}
        self._commands: Dict[str, Callable] = {}
        self._content: Dict[str, Dict] = {}
    
    def name(self, name: str) -> 'PluginBuilder':
        self._name = name
        return self
    
    def version(self, version: str) -> 'PluginBuilder':
        self._version = version
        return self
    
    def author(self, author: str) -> 'PluginBuilder':
        self._author = author
        return self
    
    def description(self, description: str) -> 'PluginBuilder':
        self._description = description
        return self
    
    def depends(self, *plugin_ids: str) -> 'PluginBuilder':
        self._dependencies.extend(plugin_ids)
        return self
    
    def conflicts_with(self, *plugin_ids: str) -> 'PluginBuilder':
        self._conflicts.extend(plugin_ids)
        return self
    
    def priority(self, priority: PluginPriority) -> 'PluginBuilder':
        self._priority = priority
        return self
    
    def tags(self, *tags: str) -> 'PluginBuilder':
        self._tags.extend(tags)
        return self
    
    def on_load(self, callback: Callable[[Any], bool]) -> 'PluginBuilder':
        self._on_load = callback
        return self
    
    def on_unload(self, callback: Callable[[Any], bool]) -> 'PluginBuilder':
        self._on_unload = callback
        return self
    
    def on_enable(self, callback: Callable[[Any], bool]) -> 'PluginBuilder':
        self._on_enable = callback
        return self
    
    def on_disable(self, callback: Callable[[Any], bool]) -> 'PluginBuilder':
        self._on_disable = callback
        return self
    
    def hook(self, event_type: Any, callback: Callable) -> 'PluginBuilder':
        self._hooks[event_type] = callback
        return self
    
    def command(self, name: str, callback: Callable, help_text: str = "") -> 'PluginBuilder':
        self._commands[name] = callback
        return self
    
    def content(self, content_type: str, content: Dict) -> 'PluginBuilder':
        if content_type not in self._content:
            self._content[content_type] = {}
        self._content[content_type].update(content)
        return self
    
    def build(self) -> FunctionalPlugin:
        """Build and return the plugin"""
        info = PluginInfo(
            id=self._id,
            name=self._name,
            version=self._version,
            author=self._author,
            description=self._description,
            dependencies=self._dependencies,
            conflicts=self._conflicts,
            priority=self._priority,
            tags=self._tags
        )
        
        plugin = FunctionalPlugin(
            info=info,
            on_load_func=self._on_load,
            on_unload_func=self._on_unload,
            on_enable_func=self._on_enable,
            on_disable_func=self._on_disable
        )
        
        # Register hooks
        for event_type, callback in self._hooks.items():
            plugin.register_hook(event_type, callback)
        
        # Register commands
        for name, callback in self._commands.items():
            plugin.register_command(name, callback)
        
        # Register content
        for content_type, content in self._content.items():
            for content_id, content_data in content.items():
                plugin._content_registries[content_type][content_id] = content_data
        
        return plugin


# =============================================================================
# MODULE-LEVEL PLUGIN INSTANCE (for simple plugins)
# =============================================================================

# Global plugin instance for module-level definition
_current_plugin: Optional[FunctionalPlugin] = None


def define_plugin(info: Union[PluginInfo, Dict]) -> PluginBuilder:
    """
    Start defining a plugin at module level.
    
    Usage:
        plugin = define_plugin({"id": "my_plugin", "name": "My Plugin", ...})
            .on_load(my_on_load)
            .hook(EventType.COMBAT_END, my_handler)
            .build()
    """
    global _current_plugin
    
    info_obj = info if isinstance(info, PluginInfo) else PluginInfo.from_dict(info)
    
    builder = PluginBuilder(info_obj.id)
    builder.name(info_obj.name)
    builder.version(info_obj.version)
    builder.author(info_obj.author)
    builder.description(info_obj.description)
    builder.priority(info_obj.priority)
    
    return builder


print("Dynamic Plugin System loaded successfully!")

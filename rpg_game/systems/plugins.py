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
    Dict, List, Tuple, Optional, Any, Callable, Type, TypeVar, Generic,
    Protocol, runtime_checkable, Union, Set, Iterator, Awaitable
)
from abc import ABC, abstractmethod
from enum import Enum, auto
from contextlib import contextmanager
from pathlib import Path
import os
import sys
import json
import importlib.util
import inspect
import hashlib
import threading
import asyncio
import time
import copy
import weakref
from collections import defaultdict
from functools import wraps, lru_cache
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
    OPTIONAL = 200    # Optional extras


class PluginType(Enum):
    """Types of plugins by structure"""
    CLASS = "class"           # Python class-based
    FUNCTIONAL = "functional" # Function-based
    DATA = "data"             # Data-only (JSON/YAML)
    HYBRID = "hybrid"         # Mixed structure
    MODULE = "module"         # Full module
    ARCHIVE = "archive"       # Zip/package


@dataclass
class PluginInfo:
    """
    Comprehensive plugin metadata.
    
    Supports both required and optional fields for maximum flexibility.
    """
    # Required fields
    id: str
    name: str
    version: str
    author: str
    description: str
    
    # Dependencies
    dependencies: List[str] = field(default_factory=list)
    soft_dependencies: List[str] = field(default_factory=list)  # Optional deps
    conflicts: List[str] = field(default_factory=list)
    provides: List[str] = field(default_factory=list)  # What this plugin provides
    
    # Loading
    priority: int = 100
    plugin_type: PluginType = PluginType.CLASS
    
    # Version compatibility
    min_game_version: str = "1.0.0"
    max_game_version: str = ""
    api_version: str = "1.0"
    
    # Configuration
    configurable: bool = False
    config_schema: Dict[str, Any] = field(default_factory=dict)
    default_config: Dict[str, Any] = field(default_factory=dict)
    
    # Hot reload
    supports_hot_reload: bool = False
    reload_priority: int = 100
    
    # Additional metadata
    tags: List[str] = field(default_factory=list)
    homepage: str = ""
    license: str = ""
    repository: str = ""
    custom: Dict[str, Any] = field(default_factory=dict)  # Custom metadata
    
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
            "provides": self.provides,
            "priority": self.priority,
            "plugin_type": self.plugin_type.value,
            "min_game_version": self.min_game_version,
            "max_game_version": self.max_game_version,
            "api_version": self.api_version,
            "configurable": self.configurable,
            "config_schema": self.config_schema,
            "default_config": self.default_config,
            "supports_hot_reload": self.supports_hot_reload,
            "tags": self.tags,
            "homepage": self.homepage,
            "license": self.license,
            "custom": self.custom
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'PluginInfo':
        return cls(
            id=data.get("id", ""),
            name=data.get("name", ""),
            version=data.get("version", "1.0.0"),
            author=data.get("author", "Unknown"),
            description=data.get("description", ""),
            dependencies=data.get("dependencies", []),
            soft_dependencies=data.get("soft_dependencies", []),
            conflicts=data.get("conflicts", []),
            provides=data.get("provides", []),
            priority=data.get("priority", 100),
            plugin_type=PluginType(data.get("plugin_type", "class")),
            min_game_version=data.get("min_game_version", "1.0.0"),
            max_game_version=data.get("max_game_version", ""),
            api_version=data.get("api_version", "1.0"),
            configurable=data.get("configurable", False),
            config_schema=data.get("config_schema", {}),
            default_config=data.get("default_config", {}),
            supports_hot_reload=data.get("supports_hot_reload", False),
            tags=data.get("tags", []),
            homepage=data.get("homepage", ""),
            license=data.get("license", ""),
            custom=data.get("custom", {})
        )


# =============================================================================
# PLUGIN INTERFACE PROTOCOLS (Duck Typing)
# =============================================================================

@runtime_checkable
class IPlugin(Protocol):
    """Protocol for basic plugin interface - allows duck typing"""
    
    @property
    def info(self) -> PluginInfo: ...
    
    def on_load(self, game: Any) -> None: ...
    def on_unload(self, game: Any) -> None: ...


@runtime_checkable  
class IConfigurablePlugin(Protocol):
    """Protocol for plugins with configuration"""
    
    def get_config(self) -> Dict[str, Any]: ...
    def set_config(self, config: Dict[str, Any]) -> None: ...
    def validate_config(self, config: Dict[str, Any]) -> Tuple[bool, str]: ...


@runtime_checkable
class IHotReloadablePlugin(Protocol):
    """Protocol for plugins that support hot reloading"""
    
    def on_before_reload(self, game: Any) -> Dict[str, Any]: ...  # Save state
    def on_after_reload(self, game: Any, state: Dict[str, Any]) -> None: ...  # Restore state


@runtime_checkable
class IContentProvider(Protocol):
    """Protocol for plugins that provide content"""
    
    def get_content_types(self) -> List[str]: ...
    def get_content(self, content_type: str) -> Dict[str, Any]: ...


@runtime_checkable
class IEventSubscriber(Protocol):
    """Protocol for plugins that subscribe to events"""
    
    def get_event_subscriptions(self) -> Dict[Any, Callable]: ...


@runtime_checkable
class ICommandProvider(Protocol):
    """Protocol for plugins that provide commands"""
    
    def get_commands(self) -> Dict[str, Callable]: ...


# =============================================================================
# BASE PLUGIN CLASS (Traditional Inheritance)
# =============================================================================

class PluginBase(ABC):
    """
    Base class for plugins using traditional inheritance.
    
    Plugins can also implement protocols directly without inheriting from this class.
    """
    
    _config: Dict[str, Any] = {}
    
    @property
    @abstractmethod
    def info(self) -> PluginInfo:
        """Return plugin information"""
        pass
    
    @abstractmethod
    def on_load(self, game):
        """Called when plugin is loaded"""
        pass
    
    @abstractmethod
    def on_unload(self, game):
        """Called when plugin is unloaded"""
        pass
    
    def on_enable(self, game):
        """Called when plugin is enabled"""
        pass
    
    def on_disable(self, game):
        """Called when plugin is disabled"""
        pass
    
    def on_config_changed(self, game, key: str, value: Any):
        """Called when configuration changes"""
        pass
    
    # Content registration methods (all optional)
    def register_hooks(self, event_system: 'EventSystem') -> Dict[Any, Callable]:
        return {}
    
    def register_commands(self, command_system: 'CommandSystem') -> Dict[str, Callable]:
        return {}
    
    def register_content(self, content_registry: 'ContentRegistry') -> Dict[str, Dict]:
        """Generic content registration - supports any content type"""
        return {}
    
    # Legacy support methods
    def register_items(self, item_registry: Dict) -> Dict[str, Any]:
        return {}
    
    def register_enemies(self, enemy_registry: Dict) -> Dict[str, Any]:
        return {}
    
    def register_locations(self, world) -> Dict[str, Any]:
        return {}
    
    def register_quests(self, quest_manager) -> Dict[str, Any]:
        return {}
    
    def register_recipes(self, crafting_manager) -> Dict[str, Any]:
        return {}
    
    def get_new_npcs(self) -> Dict[str, Dict]:
        return {}
    
    def get_new_locations(self) -> Dict[str, Dict]:
        return {}
    
    def get_new_quests(self) -> Dict[str, Dict]:
        return {}
    
    # Configuration support
    def get_config(self) -> Dict[str, Any]:
        return self._config.copy()
    
    def set_config(self, config: Dict[str, Any]) -> None:
        self._config = config.copy()
    
    def validate_config(self, config: Dict[str, Any]) -> Tuple[bool, str]:
        return True, ""
    
    # Hot reload support
    def on_before_reload(self, game) -> Dict[str, Any]:
        """Save state before hot reload"""
        return {"config": self._config}
    
    def on_after_reload(self, game, state: Dict[str, Any]) -> None:
        """Restore state after hot reload"""
        self._config = state.get("config", {})


# =============================================================================
# FUNCTIONAL PLUGIN (Function-based plugins)
# =============================================================================

@dataclass
class FunctionalPlugin:
    """
    A plugin defined by functions rather than a class.
    Useful for simple plugins that don't need full class structure.
    """
    info: PluginInfo
    on_load_func: Callable = None
    on_unload_func: Callable = None
    on_enable_func: Callable = None
    on_disable_func: Callable = None
    hooks: Dict[Any, Callable] = field(default_factory=dict)
    commands: Dict[str, Callable] = field(default_factory=dict)
    content: Dict[str, Dict] = field(default_factory=dict)
    
    def on_load(self, game):
        if self.on_load_func:
            self.on_load_func(game)
    
    def on_unload(self, game):
        if self.on_unload_func:
            self.on_unload_func(game)
    
    def on_enable(self, game):
        if self.on_enable_func:
            self.on_enable_func(game)
    
    def on_disable(self, game):
        if self.on_disable_func:
            self.on_disable_func(game)


# =============================================================================
# DYNAMIC CONTENT REGISTRY
# =============================================================================

T = TypeVar('T')


class ContentRegistry:
    """
    Dynamic content registry supporting any content type.
    
    Plugins can register any type of content dynamically without
    predefining content types.
    """
    
    def __init__(self):
        self._registry: Dict[str, Dict[str, Any]] = defaultdict(dict)
        self._factories: Dict[str, Callable] = {}
        self._validators: Dict[str, Callable] = {}
        self._loaders: Dict[str, Callable] = {}
        self._metadata: Dict[str, Dict[str, Any]] = defaultdict(dict)
        self._lock = threading.RLock()
    
    def register_type(self, 
                      content_type: str, 
                      factory: Callable = None,
                      validator: Callable = None,
                      loader: Callable = None,
                      metadata: Dict = None) -> None:
        """
        Register a new content type.
        
        Args:
            content_type: Unique identifier for the content type
            factory: Function to create content instances
            validator: Function to validate content data
            loader: Function to load content into game
            metadata: Additional metadata about the content type
        """
        with self._lock:
            if factory:
                self._factories[content_type] = factory
            if validator:
                self._validators[content_type] = validator
            if loader:
                self._loaders[content_type] = loader
            if metadata:
                self._metadata[content_type] = metadata
    
    def register(self, 
                 content_type: str, 
                 content_id: str, 
                 content_data: Any,
                 plugin_id: str = None) -> bool:
        """
        Register content of a specific type.
        
        Args:
            content_type: Type of content (e.g., 'items', 'enemies')
            content_id: Unique identifier for this content
            content_data: The content data/object
            plugin_id: ID of plugin registering this content
            
        Returns:
            True if registration successful, False otherwise
        """
        with self._lock:
            # Validate if validator exists
            if content_type in self._validators:
                try:
                    if not self._validators[content_type](content_data):
                        logger.warning(f"Validation failed for {content_type}:{content_id}")
                        return False
                except Exception as e:
                    logger.error(f"Validation error for {content_type}:{content_id}: {e}")
                    return False
            
            # Store content
            self._registry[content_type][content_id] = content_data
            
            # Track source plugin
            if plugin_id:
                self._metadata[content_type][content_id] = {
                    "plugin_id": plugin_id,
                    "registered_at": time.time()
                }
            
            logger.debug(f"Registered {content_type}:{content_id}")
            return True
    
    def register_batch(self,
                       content_type: str,
                       content: Dict[str, Any],
                       plugin_id: str = None) -> int:
        """
        Register multiple content items of the same type.
        
        Returns count of successfully registered items.
        """
        count = 0
        for content_id, content_data in content.items():
            if self.register(content_type, content_id, content_data, plugin_id):
                count += 1
        return count
    
    def unregister(self, content_type: str, content_id: str) -> bool:
        """Remove content from registry"""
        with self._lock:
            if content_type in self._registry:
                if content_id in self._registry[content_type]:
                    del self._registry[content_type][content_id]
                    if content_id in self._metadata.get(content_type, {}):
                        del self._metadata[content_type][content_id]
                    return True
        return False
    
    def unregister_plugin(self, plugin_id: str) -> int:
        """Remove all content from a specific plugin"""
        count = 0
        with self._lock:
            for content_type in list(self._metadata.keys()):
                for content_id in list(self._metadata[content_type].keys()):
                    if self._metadata[content_type][content_id].get("plugin_id") == plugin_id:
                        if self.unregister(content_type, content_id):
                            count += 1
        return count
    
    def get(self, content_type: str, content_id: str) -> Optional[Any]:
        """Get specific content"""
        return self._registry.get(content_type, {}).get(content_id)
    
    def get_all(self, content_type: str) -> Dict[str, Any]:
        """Get all content of a type"""
        return self._registry.get(content_type, {}).copy()
    
    def get_types(self) -> List[str]:
        """Get all registered content types"""
        return list(self._registry.keys())
    
    def create(self, content_type: str, content_id: str, **kwargs) -> Optional[Any]:
        """Create new content instance using factory"""
        if content_type in self._factories:
            return self._factories[content_type](content_id, **kwargs)
        return None
    
    def load_into_game(self, game: Any, content_type: str = None) -> int:
        """
        Load content into game using registered loaders.
        
        If content_type is None, loads all types.
        Returns count of loaded items.
        """
        count = 0
        types_to_load = [content_type] if content_type else list(self._loaders.keys())
        
        for ctype in types_to_load:
            if ctype in self._loaders and ctype in self._registry:
                try:
                    loaded = self._loaders[ctype](game, self._registry[ctype])
                    count += loaded if isinstance(loaded, int) else len(self._registry[ctype])
                except Exception as e:
                    logger.error(f"Error loading {ctype}: {e}")
        
        return count
    
    def query(self, content_type: str, filter_func: Callable = None) -> List[Any]:
        """Query content with optional filter"""
        content = self._registry.get(content_type, {})
        if filter_func:
            return [(k, v) for k, v in content.items() if filter_func(k, v)]
        return list(content.items())
    
    def clear(self, content_type: str = None):
        """Clear content, optionally by type"""
        with self._lock:
            if content_type:
                self._registry[content_type].clear()
                self._metadata[content_type].clear()
            else:
                self._registry.clear()
                self._metadata.clear()
    
    def get_stats(self) -> Dict[str, int]:
        """Get statistics about registered content"""
        return {
            content_type: len(content)
            for content_type, content in self._registry.items()
        }


# =============================================================================
# EVENT SYSTEM WITH PIPELINE
# =============================================================================

class EventPriority(Enum):
    """Priority for event handlers"""
    HIGHEST = 0
    HIGH = 25
    NORMAL = 50
    LOW = 75
    LOWEST = 100
    MONITOR = 200  # Always last, for monitoring only


@dataclass
class EventHandler:
    """Registered event handler with metadata"""
    callback: Callable
    priority: EventPriority = EventPriority.NORMAL
    plugin_id: str = ""
    once: bool = False  # Remove after first call
    filter_func: Callable = None  # Pre-filter events
    error_handler: Callable = None


class EventSystem:
    """
    Advanced event system with priority, filtering, and middleware.
    
    Supports both synchronous and asynchronous event handling.
    """
    
    def __init__(self):
        self._handlers: Dict[Any, List[EventHandler]] = defaultdict(list)
        self._middleware: List[Callable] = []
        self._async_handlers: Dict[Any, List[EventHandler]] = defaultdict(list)
        self._event_cache: Dict[str, Any] = {}
        self._propagation_stopped = False
    
    def subscribe(self,
                  event_type: Any,
                  handler: Callable,
                  priority: EventPriority = EventPriority.NORMAL,
                  plugin_id: str = "",
                  once: bool = False,
                  filter_func: Callable = None) -> None:
        """
        Subscribe to an event with full options.
        
        Args:
            event_type: The event type to subscribe to
            handler: Callback function (receives event data)
            priority: Handler priority (higher priority = called first)
            plugin_id: ID of plugin registering this handler
            once: If True, handler is removed after first call
            filter_func: Optional function to filter events
        """
        event_handler = EventHandler(
            callback=handler,
            priority=priority,
            plugin_id=plugin_id,
            once=once,
            filter_func=filter_func
        )
        
        self._handlers[event_type].append(event_handler)
        self._handlers[event_type].sort(key=lambda h: h.priority.value)
    
    def subscribe_async(self,
                        event_type: Any,
                        handler: Callable,
                        priority: EventPriority = EventPriority.NORMAL,
                        plugin_id: str = "") -> None:
        """Subscribe an async handler"""
        event_handler = EventHandler(
            callback=handler,
            priority=priority,
            plugin_id=plugin_id
        )
        self._async_handlers[event_type].append(event_handler)
        self._async_handlers[event_type].sort(key=lambda h: h.priority.value)
    
    def unsubscribe(self, event_type: Any, handler: Callable) -> bool:
        """Remove a specific handler"""
        handlers = self._handlers.get(event_type, [])
        for i, h in enumerate(handlers):
            if h.callback == handler:
                del handlers[i]
                return True
        return False
    
    def unsubscribe_plugin(self, plugin_id: str) -> int:
        """Remove all handlers from a plugin"""
        count = 0
        for event_type in list(self._handlers.keys()):
            handlers = self._handlers[event_type]
            original_len = len(handlers)
            self._handlers[event_type] = [h for h in handlers if h.plugin_id != plugin_id]
            count += original_len - len(self._handlers[event_type])
        return count
    
    def add_middleware(self, middleware: Callable) -> None:
        """
        Add middleware that processes all events.
        
        Middleware receives (event_type, data) and returns modified data.
        """
        self._middleware.append(middleware)
    
    def emit(self, 
             event_type: Any, 
             data: Dict = None,
             allow_async: bool = False) -> List[Any]:
        """
        Emit an event and collect results.
        
        Args:
            event_type: The event type to emit
            data: Event data dictionary
            allow_async: If True, also trigger async handlers
            
        Returns:
            List of results from all handlers
        """
        data = data or {}
        self._propagation_stopped = False
        results = []
        
        # Apply middleware
        for middleware in self._middleware:
            try:
                data = middleware(event_type, data) or data
            except Exception as e:
                logger.error(f"Middleware error: {e}")
        
        # Call handlers in priority order
        handlers = self._handlers.get(event_type, [])
        handlers_to_remove = []
        
        for handler in handlers:
            if self._propagation_stopped:
                break
            
            # Apply filter if present
            if handler.filter_func and not handler.filter_func(data):
                continue
            
            try:
                result = handler.callback(data)
                results.append(result)
                
                if handler.once:
                    handlers_to_remove.append(handler)
                    
            except Exception as e:
                logger.error(f"Event handler error in {handler.plugin_id}: {e}")
                if handler.error_handler:
                    handler.error_handler(e, data)
        
        # Remove once handlers
        for handler in handlers_to_remove:
            self._handlers[event_type].remove(handler)
        
        # Handle async handlers
        if allow_async and self._async_handlers.get(event_type):
            asyncio.create_task(self._emit_async(event_type, data))
        
        return results
    
    async def _emit_async(self, event_type: Any, data: Dict) -> List[Any]:
        """Emit to async handlers"""
        results = []
        for handler in self._async_handlers.get(event_type, []):
            try:
                result = await handler.callback(data)
                results.append(result)
            except Exception as e:
                logger.error(f"Async handler error: {e}")
        return results
    
    def emit_async(self, event_type: Any, data: Dict = None) -> asyncio.Task:
        """Emit event asynchronously"""
        return asyncio.create_task(self._emit_async(event_type, data or {}))
    
    def stop_propagation(self):
        """Stop event propagation from within a handler"""
        self._propagation_stopped = True
    
    def cache_event(self, key: str, data: Any):
        """Cache event data for later retrieval"""
        self._event_cache[key] = data
    
    def get_cached(self, key: str) -> Optional[Any]:
        """Get cached event data"""
        return self._event_cache.get(key)
    
    def clear_cache(self):
        """Clear event cache"""
        self._event_cache.clear()
    
    def get_handlers(self, event_type: Any = None) -> Dict:
        """Get handler information"""
        if event_type:
            return {
                "handlers": len(self._handlers.get(event_type, [])),
                "async_handlers": len(self._async_handlers.get(event_type, []))
            }
        return {
            "event_types": list(set(list(self._handlers.keys()) + list(self._async_handlers.keys()))),
            "total_handlers": sum(len(h) for h in self._handlers.values()),
            "total_async": sum(len(h) for h in self._async_handlers.values())
        }
    
    def clear(self):
        """Clear all handlers"""
        self._handlers.clear()
        self._async_handlers.clear()
        self._middleware.clear()


# =============================================================================
# COMMAND SYSTEM
# =============================================================================

@dataclass
class CommandInfo:
    """Command metadata"""
    name: str
    handler: Callable
    help_text: str = ""
    aliases: List[str] = field(default_factory=list)
    plugin_id: str = ""
    permissions: List[str] = field(default_factory=list)
    min_args: int = 0
    max_args: int = -1  # -1 = unlimited
    usage: str = ""
    category: str = "general"


class CommandSystem:
    """
    Dynamic command system with permissions, categories, and help generation.
    """
    
    def __init__(self):
        self._commands: Dict[str, CommandInfo] = {}
        self._aliases: Dict[str, str] = {}
        self._categories: Dict[str, List[str]] = defaultdict(list)
        self._middleware: List[Callable] = []
        self._error_handlers: List[Callable] = []
    
    def register(self,
                 name: str,
                 handler: Callable,
                 help_text: str = "",
                 aliases: List[str] = None,
                 plugin_id: str = "",
                 permissions: List[str] = None,
                 min_args: int = 0,
                 max_args: int = -1,
                 usage: str = "",
                 category: str = "general") -> None:
        """Register a command with full options"""
        name = name.lower()
        
        cmd_info = CommandInfo(
            name=name,
            handler=handler,
            help_text=help_text,
            aliases=aliases or [],
            plugin_id=plugin_id,
            permissions=permissions or [],
            min_args=min_args,
            max_args=max_args,
            usage=usage,
            category=category
        )
        
        self._commands[name] = cmd_info
        self._categories[category].append(name)
        
        # Register aliases
        for alias in (aliases or []):
            self._aliases[alias.lower()] = name
    
    def unregister(self, name: str) -> bool:
        """Remove a command"""
        name = name.lower()
        if name in self._commands:
            cmd = self._commands[name]
            # Remove from category
            if cmd.category in self._categories and name in self._categories[cmd.category]:
                self._categories[cmd.category].remove(name)
            # Remove aliases
            self._aliases = {k: v for k, v in self._aliases.items() if v != name}
            del self._commands[name]
            return True
        return False
    
    def unregister_plugin(self, plugin_id: str) -> int:
        """Remove all commands from a plugin"""
        count = 0
        for name in list(self._commands.keys()):
            if self._commands[name].plugin_id == plugin_id:
                self.unregister(name)
                count += 1
        return count
    
    def add_middleware(self, middleware: Callable):
        """Add middleware that runs before every command"""
        self._middleware.append(middleware)
    
    def add_error_handler(self, handler: Callable):
        """Add error handler for command execution"""
        self._error_handlers.append(handler)
    
    def execute(self, 
                name: str, 
                game: Any, 
                args: List[str] = None,
                context: Dict = None) -> Tuple[bool, str]:
        """
        Execute a command.
        
        Returns (success, result_message)
        """
        args = args or []
        context = context or {}
        
        # Resolve alias
        cmd_name = self._aliases.get(name.lower(), name.lower())
        
        if cmd_name not in self._commands:
            return False, f"Unknown command: {name}"
        
        cmd = self._commands[cmd_name]
        
        # Validate argument count
        if len(args) < cmd.min_args:
            return False, f"Too few arguments. Usage: {cmd.usage or cmd.help_text}"
        if cmd.max_args >= 0 and len(args) > cmd.max_args:
            return False, f"Too many arguments. Usage: {cmd.usage or cmd.help_text}"
        
        # Run middleware
        for middleware in self._middleware:
            try:
                result = middleware(game, cmd_name, args, context)
                if result is False:
                    return False, "Command blocked by middleware"
            except Exception as e:
                logger.error(f"Command middleware error: {e}")
        
        # Execute command
        try:
            result = cmd.handler(game, args, context)
            return True, result if isinstance(result, str) else str(result)
        except Exception as e:
            # Run error handlers
            for handler in self._error_handlers:
                try:
                    handler(e, game, cmd_name, args)
                except:
                    pass
            return False, f"Command error: {str(e)}"
    
    def get_help(self, name: str = None, category: str = None) -> str:
        """Get help text for command(s)"""
        if name:
            cmd_name = self._aliases.get(name.lower(), name.lower())
            if cmd_name not in self._commands:
                return f"Unknown command: {name}"
            cmd = self._commands[cmd_name]
            lines = [
                f"Command: /{cmd.name}",
                f"  {cmd.help_text}",
            ]
            if cmd.usage:
                lines.append(f"  Usage: {cmd.usage}")
            if cmd.aliases:
                lines.append(f"  Aliases: {', '.join(cmd.aliases)}")
            if cmd.permissions:
                lines.append(f"  Permissions: {', '.join(cmd.permissions)}")
            return "\n".join(lines)
        
        if category:
            commands = self._categories.get(category, [])
            if not commands:
                return f"No commands in category: {category}"
            lines = [f"Commands in '{category}':"]
            for cmd_name in commands:
                cmd = self._commands[cmd_name]
                lines.append(f"  /{cmd.name}: {cmd.help_text}")
            return "\n".join(lines)
        
        # All commands grouped by category
        lines = ["Available Commands:"]
        for cat, commands in self._categories.items():
            lines.append(f"\n[{cat.title()}]")
            for cmd_name in commands:
                cmd = self._commands[cmd_name]
                lines.append(f"  /{cmd_name}: {cmd.help_text}")
        return "\n".join(lines)
    
    def get_commands(self) -> List[str]:
        """Get list of all command names"""
        return list(self._commands.keys())
    
    def get_categories(self) -> List[str]:
        """Get list of all categories"""
        return list(self._categories.keys())


# =============================================================================
# PLUGIN DISCOVERY
# =============================================================================

@dataclass
class DiscoveredPlugin:
    """Information about a discovered plugin"""
    plugin_id: str
    path: str
    plugin_type: PluginType
    info: Optional[PluginInfo] = None
    loadable: bool = True
    error: str = ""


class PluginDiscovery:
    """
    Discovers plugins from multiple sources.
    
    Supports:
    - Filesystem directories
    - Python packages
    - Archive files (zip)
    - Remote sources (HTTP)
    """
    
    def __init__(self):
        self._discovered: Dict[str, DiscoveredPlugin] = {}
        self._watchers: List[Callable] = []
        self._file_hashes: Dict[str, str] = {}
    
    def discover_directory(self, 
                          directory: str,
                          recursive: bool = False) -> List[str]:
        """
        Discover plugins in a directory.
        
        Returns list of discovered plugin IDs.
        """
        discovered = []
        
        if not os.path.exists(directory):
            return discovered
        
        search_paths = [directory]
        if recursive:
            for root, dirs, files in os.walk(directory):
                search_paths.append(root)
        
        for path in search_paths:
            try:
                for filename in os.listdir(path):
                    filepath = os.path.join(path, filename)
                    plugin_id = self._try_discover_file(filepath, filename)
                    if plugin_id:
                        discovered.append(plugin_id)
            except PermissionError:
                continue
        
        return discovered
    
    def _try_discover_file(self, filepath: str, filename: str) -> Optional[str]:
        """Try to discover a plugin from a file"""
        # Python files
        if filename.endswith('.py') and not filename.startswith('_'):
            plugin_id = filename[:-3]
            self._discovered[plugin_id] = DiscoveredPlugin(
                plugin_id=plugin_id,
                path=filepath,
                plugin_type=PluginType.CLASS
            )
            # Calculate hash for change detection
            self._file_hashes[filepath] = self._calculate_hash(filepath)
            return plugin_id
        
        # JSON data plugins
        elif filename.endswith('.json'):
            plugin_id = filename[:-5]
            try:
                with open(filepath, 'r') as f:
                    data = json.load(f)
                info = PluginInfo.from_dict(data.get('info', {}))
                self._discovered[plugin_id] = DiscoveredPlugin(
                    plugin_id=plugin_id,
                    path=filepath,
                    plugin_type=PluginType.DATA,
                    info=info
                )
                return plugin_id
            except Exception as e:
                self._discovered[plugin_id] = DiscoveredPlugin(
                    plugin_id=plugin_id,
                    path=filepath,
                    plugin_type=PluginType.DATA,
                    loadable=False,
                    error=str(e)
                )
        
        # YAML data plugins (if PyYAML available)
        elif filename.endswith(('.yaml', '.yml')):
            try:
                import yaml
                plugin_id = filename.rsplit('.', 1)[0]
                with open(filepath, 'r') as f:
                    data = yaml.safe_load(f)
                info = PluginInfo.from_dict(data.get('info', {}))
                self._discovered[plugin_id] = DiscoveredPlugin(
                    plugin_id=plugin_id,
                    path=filepath,
                    plugin_type=PluginType.DATA,
                    info=info
                )
                return plugin_id
            except ImportError:
                pass
            except Exception as e:
                logger.warning(f"Error loading YAML plugin {filename}: {e}")
        
        # Archive plugins
        elif filename.endswith('.zip') or filename.endswith('.plugin'):
            plugin_id = filename.rsplit('.', 1)[0]
            self._discovered[plugin_id] = DiscoveredPlugin(
                plugin_id=plugin_id,
                path=filepath,
                plugin_type=PluginType.ARCHIVE
            )
            return plugin_id
        
        return None
    
    def _calculate_hash(self, filepath: str) -> str:
        """Calculate file hash for change detection"""
        try:
            with open(filepath, 'rb') as f:
                return hashlib.md5(f.read()).hexdigest()
        except:
            return ""
    
    def check_changes(self) -> Dict[str, str]:
        """
        Check for file changes.
        
        Returns dict of plugin_id -> change_type ('modified', 'added', 'removed')
        """
        changes = {}
        
        # Check existing files for modifications
        for plugin_id, discovered in list(self._discovered.items()):
            if not discovered.path:
                continue
            old_hash = self._file_hashes.get(discovered.path, "")
            new_hash = self._calculate_hash(discovered.path)
            
            if new_hash and old_hash and new_hash != old_hash:
                changes[plugin_id] = 'modified'
                self._file_hashes[discovered.path] = new_hash
        
        return changes
    
    def get_discovered(self) -> Dict[str, DiscoveredPlugin]:
        """Get all discovered plugins"""
        return self._discovered.copy()
    
    def get_plugin_path(self, plugin_id: str) -> Optional[str]:
        """Get path for a discovered plugin"""
        if plugin_id in self._discovered:
            return self._discovered[plugin_id].path
        return None
    
    def add_watcher(self, callback: Callable):
        """Add callback to be notified of changes"""
        self._watchers.append(callback)
    
    def clear(self):
        """Clear discovered plugins"""
        self._discovered.clear()
        self._file_hashes.clear()


# =============================================================================
# PLUGIN LOADER
# =============================================================================

class PluginLoader:
    """
    Loads plugins from various formats.
    
    Supports:
    - Python class-based plugins
    - Functional plugins
    - JSON data plugins
    - YAML data plugins
    - Archive plugins
    """
    
    def __init__(self, content_registry: ContentRegistry):
        self.content_registry = content_registry
        self._loaders = {
            PluginType.CLASS: self._load_class_plugin,
            PluginType.FUNCTIONAL: self._load_functional_plugin,
            PluginType.DATA: self._load_data_plugin,
            PluginType.ARCHIVE: self._load_archive_plugin,
            PluginType.MODULE: self._load_module_plugin,
        }
    
    def load(self, plugin_id: str, path: str, plugin_type: PluginType) -> Tuple[Any, PluginInfo]:
        """
        Load a plugin.
        
        Returns (plugin_instance, plugin_info)
        """
        if plugin_type in self._loaders:
            return self._loaders[plugin_type](plugin_id, path)
        
        raise ValueError(f"Unknown plugin type: {plugin_type}")
    
    def _load_class_plugin(self, plugin_id: str, path: str) -> Tuple[Any, PluginInfo]:
        """Load a Python class-based plugin"""
        try:
            spec = importlib.util.spec_from_file_location(plugin_id, path)
            module = importlib.util.module_from_spec(spec)
            sys.modules[plugin_id] = module
            spec.loader.exec_module(module)
            
            # Find plugin class (PluginBase subclass or IPlugin implementer)
            plugin_instance = None
            for name, obj in inspect.getmembers(module):
                if inspect.isclass(obj):
                    # Check if it's a PluginBase subclass
                    if issubclass(obj, PluginBase) and obj != PluginBase:
                        plugin_instance = obj()
                        break
                    # Check if it implements IPlugin protocol
                    if isinstance(obj, type) and hasattr(obj, 'info'):
                        try:
                            instance = obj()
                            if isinstance(instance, IPlugin):
                                plugin_instance = instance
                                break
                        except:
                            pass
            
            # Look for module-level plugin variable
            if not plugin_instance:
                if hasattr(module, 'plugin'):
                    plugin_instance = module.plugin
                elif hasattr(module, 'Plugin'):
                    plugin_instance = module.Plugin()
            
            if not plugin_instance:
                raise ValueError(f"No plugin class found in {path}")
            
            info = plugin_instance.info
            return plugin_instance, info
            
        except Exception as e:
            raise RuntimeError(f"Error loading class plugin {plugin_id}: {e}")
    
    def _load_functional_plugin(self, plugin_id: str, path: str) -> Tuple[Any, PluginInfo]:
        """Load a function-based plugin"""
        # This would load a functional plugin definition
        # For now, delegate to class plugin loader
        return self._load_class_plugin(plugin_id, path)
    
    def _load_data_plugin(self, plugin_id: str, path: str) -> Tuple[Any, PluginInfo]:
        """Load a data-only plugin (JSON/YAML)"""
        try:
            with open(path, 'r') as f:
                if path.endswith('.json'):
                    data = json.load(f)
                elif path.endswith(('.yaml', '.yml')):
                    try:
                        import yaml
                        data = yaml.safe_load(f)
                    except ImportError:
                        raise RuntimeError("PyYAML not installed")
                else:
                    raise ValueError(f"Unknown data format: {path}")
            
            info = PluginInfo.from_dict(data.get('info', {}))
            info.id = plugin_id  # Ensure ID matches
            
            # Create functional plugin from data
            content = {}
            for key in ['items', 'enemies', 'locations', 'npcs', 'quests', 'recipes']:
                if key in data:
                    content[key] = data[key]
            
            plugin = FunctionalPlugin(
                info=info,
                content=content
            )
            
            return plugin, info
            
        except Exception as e:
            raise RuntimeError(f"Error loading data plugin {plugin_id}: {e}")
    
    def _load_archive_plugin(self, plugin_id: str, path: str) -> Tuple[Any, PluginInfo]:
        """Load a plugin from an archive"""
        # Archive loading would extract and load the plugin
        raise NotImplementedError("Archive plugin loading not yet implemented")
    
    def _load_module_plugin(self, plugin_id: str, path: str) -> Tuple[Any, PluginInfo]:
        """Load a full Python module as plugin"""
        return self._load_class_plugin(plugin_id, path)
    
    def register_loader(self, plugin_type: PluginType, loader: Callable):
        """Register a custom loader for a plugin type"""
        self._loaders[plugin_type] = loader


# =============================================================================
# PLUGIN MANAGER
# =============================================================================

class PluginManager:
    """
    Main plugin management class.
    
    Handles:
    - Plugin discovery
    - Loading and unloading
    - Dependency resolution
    - State management
    - Configuration
    - Hot reloading
    - Content registration
    """
    
    def __init__(self, game: Any = None):
        self.game = game
        
        # Core systems
        self.discovery = PluginDiscovery()
        self.content_registry = ContentRegistry()
        self.event_system = EventSystem()
        self.command_system = CommandSystem()
        self.loader = PluginLoader(self.content_registry)
        
        # Plugin storage
        self._plugins: Dict[str, Any] = {}
        self._plugin_info: Dict[str, PluginInfo] = {}
        self._plugin_states: Dict[str, PluginState] = {}
        self._plugin_configs: Dict[str, Dict] = {}
        self._plugin_data: Dict[str, Any] = {}  # Custom plugin data
        
        # Paths
        self._plugin_paths: List[str] = []
        
        # Dependency graph
        self._dependency_graph: Dict[str, Set[str]] = defaultdict(set)
        self._dependents: Dict[str, Set[str]] = defaultdict(set)  # Reverse deps
        
        # Hot reload
        self._hot_reload_enabled = False
        self._hot_reload_thread = None
        self._stop_hot_reload = threading.Event()
        
        # Add default plugin path
        default_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "plugins")
        self.add_plugin_path(default_path)
        
        # Register built-in commands
        self._register_builtin_commands()
        
        # Register default content types
        self._register_default_content_types()
    
    def _register_builtin_commands(self):
        """Register built-in debug/utility commands"""
        self.command_system.register(
            "help", 
            lambda g, a, c: self.command_system.get_help(a[0] if a else None),
            "Show available commands",
            category="system"
        )
        self.command_system.register(
            "plugins",
            self._cmd_plugins,
            "List loaded plugins",
            category="system"
        )
        self.command_system.register(
            "plugin_info",
            self._cmd_plugin_info,
            "Show plugin information",
            usage="/plugin_info <plugin_id>",
            category="system"
        )
        self.command_system.register(
            "reload",
            self._cmd_reload,
            "Reload a plugin",
            usage="/reload <plugin_id>",
            category="system"
        )
        self.command_system.register(
            "enable",
            self._cmd_enable,
            "Enable a plugin",
            usage="/enable <plugin_id>",
            category="system"
        )
        self.command_system.register(
            "disable",
            self._cmd_disable,
            "Disable a plugin",
            usage="/disable <plugin_id>",
            category="system"
        )
        self.command_system.register(
            "hot_reload",
            self._cmd_hot_reload,
            "Toggle hot reload monitoring",
            category="system"
        )
        self.command_system.register(
            "give",
            self._cmd_give,
            "Give item to player",
            usage="/give <item_id> [quantity]",
            category="debug"
        )
        self.command_system.register(
            "teleport",
            self._cmd_teleport,
            "Teleport to location",
            usage="/teleport <location_id>",
            category="debug"
        )
        self.command_system.register(
            "spawn",
            self._cmd_spawn,
            "Spawn and fight enemy",
            usage="/spawn <enemy_type> [level]",
            category="debug"
        )
        self.command_system.register(
            "heal",
            self._cmd_heal,
            "Fully heal player",
            category="debug"
        )
        self.command_system.register(
            "gold",
            self._cmd_gold,
            "Add gold to player",
            usage="/gold <amount>",
            category="debug"
        )
        self.command_system.register(
            "setlevel",
            self._cmd_setlevel,
            "Set player level",
            usage="/setlevel <level>",
            category="debug"
        )
        self.command_system.register(
            "god",
            self._cmd_god,
            "Toggle god mode",
            category="debug"
        )
        self.command_system.register(
            "content",
            self._cmd_content,
            "Show content registry stats",
            category="debug"
        )
    
    def _register_default_content_types(self):
        """Register default game content types"""
        # Items
        self.content_registry.register_type(
            "items",
            validator=lambda data: isinstance(data, dict) and "name" in data
        )
        
        # Enemies
        self.content_registry.register_type(
            "enemies",
            validator=lambda data: isinstance(data, dict) and "name" in data
        )
        
        # Locations
        self.content_registry.register_type(
            "locations",
            validator=lambda data: isinstance(data, dict) and "name" in data
        )
        
        # NPCs
        self.content_registry.register_type(
            "npcs",
            validator=lambda data: isinstance(data, dict) and "name" in data
        )
        
        # Quests
        self.content_registry.register_type(
            "quests",
            validator=lambda data: isinstance(data, dict) and "name" in data
        )
        
        # Recipes
        self.content_registry.register_type(
            "recipes",
            validator=lambda data: isinstance(data, dict) and "name" in data
        )
        
        # Abilities
        self.content_registry.register_type(
            "abilities",
            validator=lambda data: isinstance(data, dict) and "name" in data
        )
        
        # Events
        self.content_registry.register_type(
            "world_events",
            validator=lambda data: isinstance(data, dict) and "name" in data
        )
    
    # -------------------------------------------------------------------------
    # Command Handlers
    # -------------------------------------------------------------------------
    
    def _cmd_plugins(self, game, args, context):
        lines = ["Loaded Plugins:", "=" * 50]
        for plugin_id, info in sorted(self._plugin_info.items(), key=lambda x: x[1].priority):
            state = self._plugin_states.get(plugin_id, PluginState.DISABLED)
            status = "✓" if state == PluginState.ENABLED else "✗"
            lines.append(f"  [{status}] {info.name} v{info.version} (priority: {info.priority})")
        lines.append(f"\nTotal: {len(self._plugins)} plugins")
        return "\n".join(lines)
    
    def _cmd_plugin_info(self, game, args, context):
        if not args:
            return "Usage: /plugin_info <plugin_id>"
        
        plugin_id = args[0]
        if plugin_id not in self._plugin_info:
            return f"Plugin '{plugin_id}' not found."
        
        info = self._plugin_info[plugin_id]
        state = self._plugin_states.get(plugin_id, PluginState.DISABLED)
        
        lines = [
            f"Plugin: {info.name}",
            "=" * 50,
            f"ID: {info.id}",
            f"Version: {info.version}",
            f"Author: {info.author}",
            f"State: {state.name}",
            f"Priority: {info.priority}",
            f"Type: {info.plugin_type.value}",
            "",
            f"Description: {info.description}",
        ]
        
        if info.dependencies:
            lines.append(f"\nDependencies: {', '.join(info.dependencies)}")
        if info.conflicts:
            lines.append(f"Conflicts: {', '.join(info.conflicts)}")
        if info.tags:
            lines.append(f"Tags: {', '.join(info.tags)}")
        
        return "\n".join(lines)
    
    def _cmd_reload(self, game, args, context):
        if not args:
            return "Usage: /reload <plugin_id>"
        return self.reload_plugin(args[0])
    
    def _cmd_enable(self, game, args, context):
        if not args:
            return "Usage: /enable <plugin_id>"
        return "Enable: " + ("Success" if self.enable_plugin(args[0]) else "Failed")
    
    def _cmd_disable(self, game, args, context):
        if not args:
            return "Usage: /disable <plugin_id>"
        return "Disable: " + ("Success" if self.disable_plugin(args[0]) else "Failed")
    
    def _cmd_hot_reload(self, game, args, context):
        if self._hot_reload_enabled:
            self.stop_hot_reload()
            return "Hot reload monitoring stopped."
        else:
            self.start_hot_reload()
            return "Hot reload monitoring started."
    
    def _cmd_give(self, game, args, context):
        if len(args) < 1:
            return "Usage: /give <item_id> [quantity]"
        from core.items import get_item
        item_id = args[0]
        quantity = int(args[1]) if len(args) > 1 else 1
        item = get_item(item_id, quantity)
        if item:
            game.player.inventory.add_item(item)
            return f"Gave {quantity}x {item.name} to player."
        return f"Item '{item_id}' not found."
    
    def _cmd_teleport(self, game, args, context):
        if not args:
            return "Usage: /teleport <location_id>"
        success, msg = game.world.travel_to(args[0], game.player)
        return msg
    
    def _cmd_spawn(self, game, args, context):
        if not args:
            return "Usage: /spawn <enemy_type> [level]"
        from systems.combat import EnemyFactory, CombatEncounter
        enemy_type = args[0]
        level = int(args[1]) if len(args) > 1 else game.player.level
        enemy = EnemyFactory.create_enemy(enemy_type, level)
        if enemy:
            combat = CombatEncounter(game.player, [enemy], self.event_system)
            result = combat.start()
            return f"Combat result: {'Victory' if result.victory else 'Defeat'}"
        return f"Enemy '{enemy_type}' not found."
    
    def _cmd_heal(self, game, args, context):
        game.player.current_hp = game.player.max_hp
        game.player.current_mp = game.player.max_mp
        game.player.current_stamina = game.player.max_stamina
        return "Player fully healed."
    
    def _cmd_gold(self, game, args, context):
        if not args:
            return "Usage: /gold <amount>"
        try:
            amount = int(args[0])
            game.player.inventory.gold += amount
            return f"Added {amount} gold. Total: {game.player.inventory.gold}"
        except ValueError:
            return "Invalid amount."
    
    def _cmd_setlevel(self, game, args, context):
        if not args:
            return "Usage: /setlevel <level>"
        try:
            level = int(args[0])
            game.player.level = level
            game.player.max_hp = game.player._calculate_max_hp()
            game.player.current_hp = game.player.max_hp
            game.player.max_mp = game.player._calculate_max_mp()
            game.player.current_mp = game.player.max_mp
            return f"Set player level to {level}."
        except ValueError:
            return "Invalid level."
    
    def _cmd_god(self, game, args, context):
        game.player.god_mode = not getattr(game.player, 'god_mode', False)
        return f"God mode: {'ON' if game.player.god_mode else 'OFF'}"
    
    def _cmd_content(self, game, args, context):
        stats = self.content_registry.get_stats()
        lines = ["Content Registry Stats:", "=" * 40]
        for content_type, count in stats.items():
            lines.append(f"  {content_type}: {count}")
        lines.append(f"\nTotal types: {len(stats)}")
        lines.append(f"Total items: {sum(stats.values())}")
        return "\n".join(lines)
    
    # -------------------------------------------------------------------------
    # Plugin Path Management
    # -------------------------------------------------------------------------
    
    def add_plugin_path(self, path: str):
        """Add a path to search for plugins"""
        if os.path.exists(path) and path not in self._plugin_paths:
            self._plugin_paths.append(path)
            logger.info(f"Added plugin path: {path}")
    
    def remove_plugin_path(self, path: str):
        """Remove a plugin search path"""
        if path in self._plugin_paths:
            self._plugin_paths.remove(path)
    
    # -------------------------------------------------------------------------
    # Plugin Discovery
    # -------------------------------------------------------------------------
    
    def discover_plugins(self, force: bool = False) -> List[str]:
        """
        Discover all available plugins.
        
        Returns list of discovered plugin IDs.
        """
        if not force and self.discovery.get_discovered():
            return list(self.discovery.get_discovered().keys())
        
        discovered = []
        for path in self._plugin_paths:
            found = self.discovery.discover_directory(path)
            discovered.extend(found)
        
        logger.info(f"Discovered {len(discovered)} plugins")
        return discovered
    
    # -------------------------------------------------------------------------
    # Dependency Resolution
    # -------------------------------------------------------------------------
    
    def resolve_dependencies(self, plugin_ids: List[str]) -> Tuple[List[str], List[str]]:
        """
        Resolve dependencies and return proper load order.
        
        Returns (ordered_list, missing_dependencies)
        """
        resolved = []
        unresolved = set()
        missing = []
        
        def resolve(plugin_id: str):
            if plugin_id in resolved:
                return
            
            if plugin_id in unresolved:
                # Circular dependency
                logger.warning(f"Circular dependency detected: {plugin_id}")
                return
            
            unresolved.add(plugin_id)
            
            # Get dependencies
            info = self._plugin_info.get(plugin_id)
            if not info:
                # Check discovered plugins
                discovered = self.discovery.get_discovered().get(plugin_id)
                if discovered and discovered.info:
                    info = discovered.info
            
            if info:
                for dep in info.dependencies:
                    if dep not in resolved:
                        if dep not in self._plugins and dep not in self.discovery.get_discovered():
                            missing.append(dep)
                        else:
                            resolve(dep)
            
            unresolved.remove(plugin_id)
            resolved.append(plugin_id)
        
        for plugin_id in sorted(plugin_ids, key=lambda x: self._plugin_info.get(x, PluginInfo(id=x, name="", version="", author="", description="", priority=100)).priority):
            resolve(plugin_id)
        
        return resolved, missing
    
    def check_conflicts(self, plugin_id: str) -> List[str]:
        """Check if plugin conflicts with any loaded plugins"""
        info = self._plugin_info.get(plugin_id)
        if not info:
            return []
        
        conflicts = []
        for loaded_id, loaded_info in self._plugin_info.items():
            if loaded_id == plugin_id:
                continue
            
            # Check direct conflicts
            if plugin_id in loaded_info.conflicts or loaded_id in info.conflicts:
                conflicts.append(loaded_id)
            
            # Check provides conflicts
            for provided in info.provides:
                if provided in loaded_info.provides:
                    conflicts.append(loaded_id)
        
        return conflicts
    
    # -------------------------------------------------------------------------
    # Plugin Loading
    # -------------------------------------------------------------------------
    
    def load_plugin(self, plugin_id: str) -> bool:
        """
        Load a single plugin.
        
        Returns True if successful.
        """
        if plugin_id in self._plugins:
            logger.warning(f"Plugin '{plugin_id}' already loaded")
            return False
        
        self._plugin_states[plugin_id] = PluginState.LOADING
        
        try:
            # Get discovered plugin info
            discovered = self.discovery.get_discovered().get(plugin_id)
            if not discovered:
                logger.error(f"Plugin '{plugin_id}' not found")
                self._plugin_states[plugin_id] = PluginState.ERROR
                return False
            
            if not discovered.loadable:
                logger.error(f"Plugin '{plugin_id}' not loadable: {discovered.error}")
                self._plugin_states[plugin_id] = PluginState.ERROR
                return False
            
            # Load the plugin
            plugin_instance, info = self.loader.load(
                plugin_id, 
                discovered.path, 
                discovered.plugin_type
            )
            
            # Check dependencies
            self._plugin_states[plugin_id] = PluginState.RESOLVING
            missing = [d for d in info.dependencies if d not in self._plugins]
            if missing:
                logger.error(f"Plugin '{plugin_id}' missing dependencies: {missing}")
                self._plugin_states[plugin_id] = PluginState.ERROR
                return False
            
            # Check conflicts
            conflicts = self.check_conflicts(plugin_id)
            if conflicts:
                logger.error(f"Plugin '{plugin_id}' conflicts with: {conflicts}")
                self._plugin_states[plugin_id] = PluginState.ERROR
                return False
            
            # Store plugin
            self._plugins[plugin_id] = plugin_instance
            self._plugin_info[plugin_id] = info
            
            # Build dependency graph
            for dep in info.dependencies:
                self._dependency_graph[plugin_id].add(dep)
                self._dependents[dep].add(plugin_id)
            
            # Initialize plugin
            self._plugin_states[plugin_id] = PluginState.INITIALIZING
            
            # Call on_load
            if hasattr(plugin_instance, 'on_load'):
                plugin_instance.on_load(self.game)
            
            # Register event hooks
            if hasattr(plugin_instance, 'register_hooks'):
                hooks = plugin_instance.register_hooks(self.event_system)
                for event_type, handler in hooks.items():
                    # Handle tuple format (handler, priority) or just handler
                    if isinstance(handler, tuple):
                        handler_func, priority = handler
                        self.event_system.subscribe(event_type, handler_func, 
                                                   priority=priority, plugin_id=plugin_id)
                    else:
                        self.event_system.subscribe(event_type, handler, plugin_id=plugin_id)
            elif hasattr(plugin_instance, 'get_event_subscriptions'):
                subscriptions = plugin_instance.get_event_subscriptions()
                for event_type, handler in subscriptions.items():
                    # Handle tuple format (handler, priority) or just handler
                    if isinstance(handler, tuple):
                        handler_func, priority = handler
                        self.event_system.subscribe(event_type, handler_func,
                                                   priority=priority, plugin_id=plugin_id)
                    else:
                        self.event_system.subscribe(event_type, handler, plugin_id=plugin_id)
            
            # Register commands
            if hasattr(plugin_instance, 'register_commands'):
                commands = plugin_instance.register_commands(self.command_system)
                for cmd_name, cmd_info in commands.items():
                    # Handle dict format {"handler": ..., "help": ..., "category": ...}
                    if isinstance(cmd_info, dict):
                        self.command_system.register(
                            cmd_name, 
                            cmd_info.get("handler"),
                            help_text=cmd_info.get("help", ""),
                            category=cmd_info.get("category", "general"),
                            plugin_id=plugin_id
                        )
                    else:
                        # Plain callable
                        self.command_system.register(cmd_name, cmd_info, plugin_id=plugin_id)
            elif hasattr(plugin_instance, 'get_commands'):
                commands = plugin_instance.get_commands()
                for cmd_name, cmd_info in commands.items():
                    # Handle dict format
                    if isinstance(cmd_info, dict):
                        self.command_system.register(
                            cmd_name,
                            cmd_info.get("handler"),
                            help_text=cmd_info.get("help", ""),
                            category=cmd_info.get("category", "general"),
                            plugin_id=plugin_id
                        )
                    else:
                        self.command_system.register(cmd_name, cmd_info, plugin_id=plugin_id)
            
            # Register content
            self._register_plugin_content(plugin_id, plugin_instance)
            
            # Call on_enable
            if hasattr(plugin_instance, 'on_enable'):
                plugin_instance.on_enable(self.game)
            
            # Mark as enabled
            self._plugin_states[plugin_id] = PluginState.ENABLED
            
            # Emit event
            self.event_system.emit(EventType.PLUGIN_LOAD, {"plugin_id": plugin_id})
            
            logger.info(f"Plugin '{info.name}' v{info.version} loaded")
            return True
            
        except Exception as e:
            logger.error(f"Error loading plugin '{plugin_id}': {e}")
            self._plugin_states[plugin_id] = PluginState.ERROR
            return False
    
    def _register_plugin_content(self, plugin_id: str, plugin_instance: Any):
        """Register all content from a plugin"""
        
        # Generic content registration
        if hasattr(plugin_instance, 'register_content'):
            content = plugin_instance.register_content(self.content_registry)
            for content_type, items in content.items():
                count = self.content_registry.register_batch(content_type, items, plugin_id)
                if count:
                    logger.debug(f"Registered {count} {content_type} from {plugin_id}")
        
        # IContentProvider protocol
        elif isinstance(plugin_instance, IContentProvider):
            for content_type in plugin_instance.get_content_types():
                content = plugin_instance.get_content(content_type)
                count = self.content_registry.register_batch(content_type, content, plugin_id)
                if count:
                    logger.debug(f"Registered {count} {content_type} from {plugin_id}")
        
        # Legacy registration methods
        self._register_legacy_content(plugin_id, plugin_instance)
    
    def _register_legacy_content(self, plugin_id: str, plugin_instance: Any):
        """Register content using legacy methods"""
        
        # Items
        if hasattr(plugin_instance, 'register_items'):
            items = plugin_instance.register_items({})
            if items:
                count = self.content_registry.register_batch("items", items, plugin_id)
                logger.debug(f"Registered {count} items from {plugin_id}")
        
        # Enemies
        if hasattr(plugin_instance, 'register_enemies'):
            enemies = plugin_instance.register_enemies({})
            if enemies:
                count = self.content_registry.register_batch("enemies", enemies, plugin_id)
                logger.debug(f"Registered {count} enemies from {plugin_id}")
        
        # Locations
        if hasattr(plugin_instance, 'get_new_locations'):
            locations = plugin_instance.get_new_locations()
        elif hasattr(plugin_instance, 'register_locations'):
            locations = plugin_instance.register_locations(None)
        else:
            locations = {}
        
        if locations:
            count = self.content_registry.register_batch("locations", locations, plugin_id)
            if count and hasattr(self.game, 'world') and hasattr(self.game.world, 'register_locations'):
                self.game.world.register_locations(locations)
            logger.debug(f"Registered {count} locations from {plugin_id}")
        
        # NPCs
        if hasattr(plugin_instance, 'get_new_npcs'):
            npcs = plugin_instance.get_new_npcs()
            if npcs:
                count = self.content_registry.register_batch("npcs", npcs, plugin_id)
                if hasattr(self.game, 'npc_manager') and hasattr(self.game.npc_manager, 'register_npcs'):
                    self.game.npc_manager.register_npcs(npcs)
                logger.debug(f"Registered {count} NPCs from {plugin_id}")
        
        # Quests
        if hasattr(plugin_instance, 'get_new_quests'):
            quests = plugin_instance.get_new_quests()
        elif hasattr(plugin_instance, 'register_quests'):
            quests = plugin_instance.register_quests(None)
        else:
            quests = {}
        
        if quests:
            count = self.content_registry.register_batch("quests", quests, plugin_id)
            self._load_quests(quests)
            logger.debug(f"Registered {count} quests from {plugin_id}")
        
        # Recipes
        if hasattr(plugin_instance, 'register_recipes'):
            recipes = plugin_instance.register_recipes(None)
            if recipes:
                count = self.content_registry.register_batch("recipes", recipes, plugin_id)
                logger.debug(f"Registered {count} recipes from {plugin_id}")
    
    def _load_quests(self, quests: Dict):
        """Load quests into the quest manager"""
        if not hasattr(self.game, 'quest_manager'):
            return
        
        try:
            from systems.quests import Quest, QuestObjective, QuestReward, QuestType, ObjectiveType
            
            for quest_id, quest_data in quests.items():
                objectives = []
                for obj_data in quest_data.get("objectives", []):
                    objectives.append(QuestObjective(
                        objective_type=ObjectiveType(obj_data.get("type", "kill")),
                        target=obj_data.get("target", ""),
                        required=obj_data.get("required", 1),
                        description=obj_data.get("description", "")
                    ))
                
                rewards_data = quest_data.get("rewards", {})
                rewards = QuestReward(
                    experience=rewards_data.get("experience", 0),
                    gold=rewards_data.get("gold", 0),
                    items=rewards_data.get("items", [])
                )
                
                quest = Quest(
                    id=quest_id,
                    name=quest_data.get("name", quest_id),
                    description=quest_data.get("description", ""),
                    quest_type=QuestType(quest_data.get("quest_type", "side")),
                    objectives=objectives,
                    rewards=rewards,
                    giver=quest_data.get("giver", ""),
                    location=quest_data.get("location", ""),
                    level_required=quest_data.get("level_required", 1)
                )
                
                self.game.quest_manager.quests[quest_id] = quest
                
        except Exception as e:
            logger.error(f"Error loading quests: {e}")
    
    # -------------------------------------------------------------------------
    # Plugin Unloading
    # -------------------------------------------------------------------------
    
    def unload_plugin(self, plugin_id: str) -> bool:
        """Unload a plugin"""
        if plugin_id not in self._plugins:
            return False
        
        self._plugin_states[plugin_id] = PluginState.UNLOADING
        plugin = self._plugins[plugin_id]
        
        try:
            # Check dependents
            dependents = self._dependents.get(plugin_id, set())
            if dependents:
                # Unload dependents first
                for dep_id in list(dependents):
                    if dep_id in self._plugins:
                        self.unload_plugin(dep_id)
            
            # Call lifecycle methods
            if hasattr(plugin, 'on_disable'):
                plugin.on_disable(self.game)
            
            if hasattr(plugin, 'on_unload'):
                plugin.on_unload(self.game)
            
            # Unregister event handlers
            self.event_system.unsubscribe_plugin(plugin_id)
            
            # Unregister commands
            self.command_system.unregister_plugin(plugin_id)
            
            # Unregister content
            self.content_registry.unregister_plugin(plugin_id)
            
            # Clean up dependency graph
            for dep in self._dependency_graph.get(plugin_id, set()):
                self._dependents[dep].discard(plugin_id)
            del self._dependency_graph[plugin_id]
            del self._dependents[plugin_id]
            
            # Remove plugin
            del self._plugins[plugin_id]
            del self._plugin_info[plugin_id]
            self._plugin_states[plugin_id] = PluginState.DISABLED
            
            # Emit event
            self.event_system.emit(EventType.PLUGIN_UNLOAD, {"plugin_id": plugin_id})
            
            logger.info(f"Plugin '{plugin_id}' unloaded")
            return True
            
        except Exception as e:
            logger.error(f"Error unloading plugin '{plugin_id}': {e}")
            self._plugin_states[plugin_id] = PluginState.ERROR
            return False
    
    # -------------------------------------------------------------------------
    # Plugin Enable/Disable
    # -------------------------------------------------------------------------
    
    def enable_plugin(self, plugin_id: str) -> bool:
        """Enable a disabled plugin"""
        if plugin_id not in self._plugins:
            return False
        
        if self._plugin_states.get(plugin_id) == PluginState.ENABLED:
            return True
        
        plugin = self._plugins[plugin_id]
        
        try:
            if hasattr(plugin, 'on_enable'):
                plugin.on_enable(self.game)
            
            self._plugin_states[plugin_id] = PluginState.ENABLED
            logger.info(f"Plugin '{plugin_id}' enabled")
            return True
            
        except Exception as e:
            logger.error(f"Error enabling plugin '{plugin_id}': {e}")
            return False
    
    def disable_plugin(self, plugin_id: str) -> bool:
        """Disable an enabled plugin"""
        if plugin_id not in self._plugins:
            return False
        
        if self._plugin_states.get(plugin_id) != PluginState.ENABLED:
            return True
        
        plugin = self._plugins[plugin_id]
        
        try:
            if hasattr(plugin, 'on_disable'):
                plugin.on_disable(self.game)
            
            self._plugin_states[plugin_id] = PluginState.DISABLED
            logger.info(f"Plugin '{plugin_id}' disabled")
            return True
            
        except Exception as e:
            logger.error(f"Error disabling plugin '{plugin_id}': {e}")
            return False
    
    # -------------------------------------------------------------------------
    # Plugin Reload
    # -------------------------------------------------------------------------
    
    def reload_plugin(self, plugin_id: str) -> str:
        """Reload a plugin (hot reload if supported)"""
        if plugin_id not in self._plugins:
            return f"Plugin '{plugin_id}' not loaded"
        
        plugin = self._plugins[plugin_id]
        info = self._plugin_info[plugin_id]
        
        # Save state if hot reload supported
        state = {}
        if info.supports_hot_reload and hasattr(plugin, 'on_before_reload'):
            try:
                state = plugin.on_before_reload(self.game)
            except Exception as e:
                logger.warning(f"Error saving plugin state: {e}")
        
        # Unload and reload
        if self.unload_plugin(plugin_id):
            if self.load_plugin(plugin_id):
                # Restore state if hot reload supported
                if state and info.supports_hot_reload:
                    new_plugin = self._plugins[plugin_id]
                    if hasattr(new_plugin, 'on_after_reload'):
                        try:
                            new_plugin.on_after_reload(self.game, state)
                        except Exception as e:
                            logger.warning(f"Error restoring plugin state: {e}")
                
                return f"Plugin '{plugin_id}' reloaded successfully"
        
        return f"Failed to reload plugin '{plugin_id}'"
    
    # -------------------------------------------------------------------------
    # Hot Reload Monitoring
    # -------------------------------------------------------------------------
    
    def start_hot_reload(self, interval: float = 2.0):
        """Start hot reload monitoring"""
        if self._hot_reload_enabled:
            return
        
        self._hot_reload_enabled = True
        self._stop_hot_reload.clear()
        
        def monitor():
            while not self._stop_hot_reload.is_set():
                changes = self.discovery.check_changes()
                for plugin_id, change_type in changes.items():
                    if change_type == 'modified':
                        info = self._plugin_info.get(plugin_id)
                        if info and info.supports_hot_reload:
                            logger.info(f"Hot reloading plugin '{plugin_id}'")
                            self.reload_plugin(plugin_id)
                
                self._stop_hot_reload.wait(interval)
        
        self._hot_reload_thread = threading.Thread(target=monitor, daemon=True)
        self._hot_reload_thread.start()
        logger.info("Hot reload monitoring started")
    
    def stop_hot_reload(self):
        """Stop hot reload monitoring"""
        if not self._hot_reload_enabled:
            return
        
        self._stop_hot_reload.set()
        self._hot_reload_enabled = False
        logger.info("Hot reload monitoring stopped")
    
    # -------------------------------------------------------------------------
    # Batch Operations
    # -------------------------------------------------------------------------
    
    def load_all_plugins(self) -> Tuple[int, int]:
        """Load all discovered plugins. Returns (success, fail)"""
        discovered = self.discover_plugins()
        
        # Resolve dependencies
        ordered, missing = self.resolve_dependencies(discovered)
        
        if missing:
            logger.warning(f"Missing dependencies: {missing}")
        
        success = 0
        fail = 0
        
        for plugin_id in ordered:
            if self.load_plugin(plugin_id):
                success += 1
            else:
                fail += 1
        
        return success, fail
    
    def unload_all_plugins(self) -> int:
        """Unload all plugins. Returns count unloaded."""
        count = 0
        # Unload in reverse dependency order
        plugin_ids = list(self._plugins.keys())
        while plugin_ids:
            for plugin_id in list(plugin_ids):
                # Check if any other plugins depend on this one
                if not self._dependents.get(plugin_id):
                    if self.unload_plugin(plugin_id):
                        count += 1
                    plugin_ids.remove(plugin_id)
                    break
            else:
                # Circular dependency - force unload
                if plugin_ids:
                    self.unload_plugin(plugin_ids[0])
                    count += 1
                    plugin_ids.pop(0)
        
        return count
    
    # -------------------------------------------------------------------------
    # Plugin Queries
    # -------------------------------------------------------------------------
    
    def get_plugin(self, plugin_id: str) -> Optional[Any]:
        """Get a plugin instance"""
        return self._plugins.get(plugin_id)
    
    def get_plugin_info(self, plugin_id: str) -> Optional[PluginInfo]:
        """Get plugin information"""
        return self._plugin_info.get(plugin_id)
    
    def get_plugin_state(self, plugin_id: str) -> PluginState:
        """Get plugin state"""
        return self._plugin_states.get(plugin_id, PluginState.UNDISCOVERED)
    
    def get_plugins_by_tag(self, tag: str) -> List[str]:
        """Get plugins with a specific tag"""
        return [
            plugin_id for plugin_id, info in self._plugin_info.items()
            if tag in info.tags
        ]
    
    def get_plugins_by_priority(self, priority: int) -> List[str]:
        """Get plugins with a specific priority"""
        return [
            plugin_id for plugin_id, info in self._plugin_info.items()
            if info.priority == priority
        ]
    
    def get_loaded_plugins(self) -> List[str]:
        """Get list of loaded plugin IDs"""
        return list(self._plugins.keys())
    
    def get_enabled_plugins(self) -> List[str]:
        """Get list of enabled plugin IDs"""
        return [
            plugin_id for plugin_id, state in self._plugin_states.items()
            if state == PluginState.ENABLED
        ]
    
    # -------------------------------------------------------------------------
    # Plugin Data Storage
    # -------------------------------------------------------------------------
    
    def set_plugin_data(self, plugin_id: str, key: str, value: Any):
        """Store custom data for a plugin"""
        if plugin_id not in self._plugin_data:
            self._plugin_data[plugin_id] = {}
        self._plugin_data[plugin_id][key] = value
    
    def get_plugin_data(self, plugin_id: str, key: str = None) -> Any:
        """Get custom data for a plugin"""
        if plugin_id not in self._plugin_data:
            return None
        if key:
            return self._plugin_data[plugin_id].get(key)
        return self._plugin_data[plugin_id].copy()
    
    # -------------------------------------------------------------------------
    # Configuration
    # -------------------------------------------------------------------------
    
    def get_config(self, plugin_id: str) -> Dict[str, Any]:
        """Get plugin configuration"""
        return self._plugin_configs.get(plugin_id, {}).copy()
    
    def set_config(self, plugin_id: str, config: Dict[str, Any]) -> bool:
        """Set plugin configuration"""
        if plugin_id not in self._plugins:
            return False
        
        plugin = self._plugins[plugin_id]
        self._plugin_configs[plugin_id] = config.copy()
        
        # Update plugin
        if hasattr(plugin, 'set_config'):
            plugin.set_config(config)
        
        return True
    
    # -------------------------------------------------------------------------
    # Statistics and Info
    # -------------------------------------------------------------------------
    
    def get_stats(self) -> Dict[str, Any]:
        """Get plugin system statistics"""
        return {
            "total_plugins": len(self._plugins),
            "enabled_plugins": len([p for p in self._plugin_states.values() if p == PluginState.ENABLED]),
            "disabled_plugins": len([p for p in self._plugin_states.values() if p == PluginState.DISABLED]),
            "error_plugins": len([p for p in self._plugin_states.values() if p == PluginState.ERROR]),
            "content_types": len(self.content_registry.get_types()),
            "total_content": sum(self.content_registry.get_stats().values()),
            "event_handlers": self.event_system.get_handlers()["total_handlers"],
            "commands": len(self.command_system.get_commands()),
            "hot_reload_enabled": self._hot_reload_enabled
        }


# =============================================================================
# DECORATORS FOR FUNCTIONAL PLUGINS
# =============================================================================

def plugin(info: Union[PluginInfo, Dict]):
    """
    Decorator to create a functional plugin from functions.
    
    Usage:
        @plugin(PluginInfo(id="my_plugin", ...))
        class MyPlugin:
            @hook(EventType.COMBAT_END)
            def on_combat_end(self, data):
                pass
    """
    def decorator(cls):
        plugin_info = info if isinstance(info, PluginInfo) else PluginInfo.from_dict(info)
        
        # Collect hooks
        hooks = {}
        for name, method in inspect.getmembers(cls, predicate=inspect.isfunction):
            if hasattr(method, '_event_hook'):
                hooks[method._event_hook] = method
        
        # Collect commands
        commands = {}
        for name, method in inspect.getmembers(cls, predicate=inspect.isfunction):
            if hasattr(method, '_command_name'):
                commands[method._command_name] = method
        
        # Create functional plugin
        instance = cls()
        
        return FunctionalPlugin(
            info=plugin_info,
            on_load_func=getattr(instance, 'on_load', None),
            on_unload_func=getattr(instance, 'on_unload', None),
            hooks={k: v.__get__(instance) for k, v in hooks.items()},
            commands={k: v.__get__(instance) for k, v in commands.items()}
        )
    
    return decorator


def hook(event_type: Any, priority: EventPriority = EventPriority.NORMAL):
    """Decorator to mark a method as an event hook"""
    def decorator(func):
        func._event_hook = event_type
        func._event_priority = priority
        return func
    return decorator


def command(name: str, help_text: str = "", aliases: List[str] = None):
    """Decorator to mark a method as a command"""
    def decorator(func):
        func._command_name = name
        func._command_help = help_text
        func._command_aliases = aliases or []
        return func
    return decorator


# =============================================================================
# PLUGIN BUILDER (Fluent API)
# =============================================================================

class PluginBuilder:
    """
    Fluent API for building plugins programmatically.
    
    Usage:
        plugin = (PluginBuilder("my_plugin")
            .name("My Plugin")
            .version("1.0.0")
            .author("Developer")
            .description("A cool plugin")
            .on_load(lambda game: print("Loaded!"))
            .hook(EventType.COMBAT_END, on_combat_end)
            .command("test", cmd_test, "Test command")
            .build())
    """
    
    def __init__(self, plugin_id: str):
        self._id = plugin_id
        self._name = plugin_id
        self._version = "1.0.0"
        self._author = "Unknown"
        self._description = ""
        self._dependencies = []
        self._conflicts = []
        self._priority = 100
        self._tags = []
        self._on_load = None
        self._on_unload = None
        self._on_enable = None
        self._on_disable = None
        self._hooks = {}
        self._commands = {}
        self._content = {}
    
    def name(self, name: str) -> 'PluginBuilder':
        self._name = name
        return self
    
    def version(self, version: str) -> 'PluginBuilder':
        self._version = version
        return self
    
    def author(self, author: str) -> 'PluginBuilder':
        self._author = author
        return self
    
    def description(self, desc: str) -> 'PluginBuilder':
        self._description = desc
        return self
    
    def depends_on(self, *plugin_ids: str) -> 'PluginBuilder':
        self._dependencies.extend(plugin_ids)
        return self
    
    def conflicts_with(self, *plugin_ids: str) -> 'PluginBuilder':
        self._conflicts.extend(plugin_ids)
        return self
    
    def priority(self, priority: int) -> 'PluginBuilder':
        self._priority = priority
        return self
    
    def tags(self, *tags: str) -> 'PluginBuilder':
        self._tags.extend(tags)
        return self
    
    def on_load(self, callback: Callable) -> 'PluginBuilder':
        self._on_load = callback
        return self
    
    def on_unload(self, callback: Callable) -> 'PluginBuilder':
        self._on_unload = callback
        return self
    
    def on_enable(self, callback: Callable) -> 'PluginBuilder':
        self._on_enable = callback
        return self
    
    def on_disable(self, callback: Callable) -> 'PluginBuilder':
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
        
        return FunctionalPlugin(
            info=info,
            on_load_func=self._on_load,
            on_unload_func=self._on_unload,
            on_enable_func=self._on_enable,
            on_disable_func=self._on_disable,
            hooks=self._hooks,
            commands=self._commands,
            content=self._content
        )


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

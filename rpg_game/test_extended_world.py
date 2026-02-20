#!/usr/bin/env python3
"""Debug script for extended_world plugin"""

import sys
import os
import traceback

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    print("Attempting to load extended_world plugin...")
    
    # Try importing the module directly
    import importlib.util
    path = os.path.join(os.path.dirname(__file__), 'plugins', 'extended_world.py')
    module_name = 'extended_world'
    spec = importlib.util.spec_from_file_location(module_name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    
    print('Module loaded successfully')
    print(f'Has plugin attr: {hasattr(module, "plugin")}')
    if hasattr(module, 'plugin'):
        print(f'Plugin instance: {module.plugin}')
        print(f'Plugin type: {type(module.plugin)}')
    else:
        print('No plugin attribute found!')
        
except Exception as e:
    print(f'Error: {e}')
    traceback.print_exc()

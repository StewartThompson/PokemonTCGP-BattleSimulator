"""
Deck package for Pokemon TCG Pocket Battle Simulator.
This module provides access to predefined deck configurations.
"""

import os
import importlib
from typing import Dict, List, Any, Optional

# Dictionary to store loaded decks
_decks = {}

def load_all_decks() -> Dict[str, Dict[str, Any]]:
    """
    Load all available decks from the decks directory.
    Returns a dictionary mapping deck names to their descriptions.
    """
    global _decks
    _decks.clear()
    
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Find all Python files in the directory (excluding __init__.py)
    for filename in os.listdir(current_dir):
        if filename.endswith(".py") and filename != "__init__.py":
            module_name = filename[:-3]  # Remove .py extension
            
            try:
                # Import the module
                module = importlib.import_module(f"decks.{module_name}")
                
                # Verify the module has required functions
                if hasattr(module, "get_deck") and hasattr(module, "get_description"):
                    deck_description = module.get_description()
                    _decks[module_name] = {
                        "module": module,
                        "description": deck_description
                    }
            except Exception as e:
                print(f"Warning: Failed to load deck {module_name}: {e}")
    
    return {name: info["description"] for name, info in _decks.items()}

def get_deck(deck_name: str) -> Optional[List]:
    """
    Get the specified deck by name.
    
    Args:
        deck_name: The name of the deck module (filename without .py)
        
    Returns:
        A list of cards representing the deck, or None if deck not found
    """
    if not _decks:
        load_all_decks()
        
    if deck_name not in _decks:
        available = list(_decks.keys())
        print(f"Error: Deck '{deck_name}' not found. Available decks: {available}")
        return None
    
    try:
        return _decks[deck_name]["module"].get_deck()
    except Exception as e:
        print(f"Error loading deck '{deck_name}': {e}")
        return None

def get_deck_description(deck_name: str) -> Optional[Dict[str, str]]:
    """
    Get the description of the specified deck.
    
    Args:
        deck_name: The name of the deck module (filename without .py)
        
    Returns:
        A dictionary with deck information, or None if deck not found
    """
    if not _decks:
        load_all_decks()
        
    if deck_name not in _decks:
        return None
    
    return _decks[deck_name]["description"]

def list_available_decks() -> List[str]:
    """
    Get a list of all available deck names.
    
    Returns:
        List of deck names
    """
    if not _decks:
        load_all_decks()
    
    return list(_decks.keys())

# Initialize by loading all decks when the module is imported
load_all_decks() 
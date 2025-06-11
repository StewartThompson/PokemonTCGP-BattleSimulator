#!/usr/bin/env python3
"""
Utility functions for Pokemon TCG Pocket Battle Simulator
This module provides various utility functions needed throughout the application.
"""

import os
import pandas as pd
from typing import Dict, List, Any, Optional
from collections import Counter

# Global card database - will store the imported objects directly
card_database = None

def parse_energy_cost(cost_str: str) -> Dict[str, int]:
    """
    Parse energy cost string into dictionary.
    
    Args:
        cost_str: String like "water:2|normal:1" or "fire:1"
        
    Returns:
        Dictionary with energy types as keys and amounts as values
    """
    if pd.isna(cost_str) or not cost_str:
        return {}
    
    energy_cost = {
        'fire': 0, 'water': 0, 'rock': 0, 'grass': 0, 'normal': 0,
        'electric': 0, 'psychic': 0, 'dark': 0, 'metal': 0, 'dragon': 0, 'fairy': 0
    }
    
    parts = str(cost_str).split('|')
    for part in parts:
        if ':' in part:
            energy_type, amount = part.split(':', 1)
            energy_type = energy_type.strip()
            try:
                amount = int(amount.strip())
                if energy_type in energy_cost:
                    energy_cost[energy_type] = amount
            except ValueError:
                continue
    
    return energy_cost

def parse_pipe_separated(value: str) -> List[str]:
    """
    Parse pipe-separated string into list.
    
    Args:
        value: String like "value1|value2|value3"
        
    Returns:
        List of individual values
    """
    if pd.isna(value) or not value:
        return []
    
    return [item.strip() for item in str(value).split('|') if item.strip()]

def contains_trainer(deck_counts: Dict, id_to_obj: Dict) -> bool:
    """
    Check if deck contains trainer cards.
    
    Args:
        deck_counts: Dictionary of card counts
        id_to_obj: Dictionary mapping card keys to objects
        
    Returns:
        True if deck contains trainer cards
    """
    for key in deck_counts:
        if key[1] == "trainer":
            return True
    return False

def contains_item(deck_counts: Dict, id_to_obj: Dict) -> bool:
    """
    Check if deck contains item cards.
    
    Args:
        deck_counts: Dictionary of card counts
        id_to_obj: Dictionary mapping card keys to objects
        
    Returns:
        True if deck contains item cards
    """
    for key in deck_counts:
        if key[1] == "item":
            return True
    return False

def contains_hand_pokemon(hand: List, pokemon_name: str) -> bool:
    """
    Check if hand contains a specific Pokemon.
    
    Args:
        hand: List of cards in hand
        pokemon_name: Name of the Pokemon to look for
        
    Returns:
        True if hand contains the Pokemon
    """
    for card in hand:
        if hasattr(card, 'name') and hasattr(card, 'card_type'):
            if card.card_type == "pokemon" and card.name == pokemon_name:
                return True
    return False

def satisfies_pre_evolution_rule(deck_counts: Dict, id_to_obj: Dict) -> bool:
    """
    Check if deck satisfies pre-evolution rules.
    For every evolution Pokemon, there must be at least as many of its pre-evolution.
    
    Args:
        deck_counts: Dictionary of card counts
        id_to_obj: Dictionary mapping card keys to objects
        
    Returns:
        True if all evolution rules are satisfied
    """
    # Count Pokemon by name
    pokemon_counts = {}
    
    for key, count in deck_counts.items():
        if key[1] == "pokemon":
            obj = id_to_obj[key]
            if hasattr(obj, 'name'):
                name = obj.name
                pokemon_counts[name] = pokemon_counts.get(name, 0) + count
    
    # Check evolution rules
    for key, count in deck_counts.items():
        if key[1] == "pokemon":
            obj = id_to_obj[key]
            if hasattr(obj, 'pre_evolution_name') and obj.pre_evolution_name:
                pre_evo_count = pokemon_counts.get(obj.pre_evolution_name, 0)
                if pre_evo_count < count:
                    return False
    
    return True

def load_default_database():
    """
    Load the default card database from JSON files using the JsonCardImporter.
    This function initializes the global card database.
    """
    global card_database
    
    try:
        from json_card_importer import JsonCardImporter
        
        print("Loading card database from JSON files...")
        importer = JsonCardImporter()
        
        # Determine the database path
        current_dir = os.path.dirname(os.path.abspath(__file__))
        database_path = os.path.join(current_dir, 'assets', 'database', 'pokemon')
        
        if os.path.exists(database_path):
            print(f"Loading database from: {database_path}")
            card_database = importer.initialize_from_folder(database_path)
            print("Database loaded successfully!")
            
            # Print summary
            print("\n=== DATABASE SUMMARY ===")
            for obj_type, objects in card_database.items():
                print(f"{obj_type.capitalize()}: {len(objects)}")
        else:
            print(f"Warning: Database path not found: {database_path}")
            card_database = {}
            
    except ImportError as e:
        print(f"Error importing JsonCardImporter: {e}")
        card_database = {}
    except Exception as e:
        print(f"Error loading database: {e}")
        card_database = {}

def get_card_database():
    """
    Get the global card database instance.
    
    Returns:
        Dictionary containing all card objects, or None if not loaded
    """
    return card_database

# Global accessors for different card types
def get_basic_pokemons(deck=None):
    """Get all basic Pokemon from the database or from a specific deck."""
    if deck is not None:
        # Filter basic Pokemon from the provided deck
        basic_pokemon = []
        for card in deck:
            if hasattr(card, 'stage') and hasattr(card, 'card_type'):
                if card.card_type == "pokemon" and card.stage in ['basic', 'basic_ex']:
                    basic_pokemon.append(card)
        return basic_pokemon
    
    # If no deck provided, return all basic Pokemon from database
    if not card_database:
        return []
    
    basic_pokemon = []
    for pokemon in card_database.get('pokemon', {}).values():
        if hasattr(pokemon, 'stage') and pokemon.stage in ['basic', 'basic_ex']:
            basic_pokemon.append(pokemon)
    return basic_pokemon

def all_pokemons():
    """Get all Pokemon from the database."""
    if not card_database:
        return []
    return list(card_database.get('pokemon', {}).values())

def all_attacks():
    """Get all attacks from the database."""
    if not card_database:
        return []
    return list(card_database.get('attacks', {}).values())

def all_abilities():
    """Get all abilities from the database."""
    if not card_database:
        return []
    return list(card_database.get('abilities', {}).values())

def all_trainers():
    """Get all trainers from the database."""
    if not card_database:
        return []
    return list(card_database.get('trainers', {}).values())

def all_items():
    """Get all items from the database."""
    if not card_database:
        return []
    return list(card_database.get('items', {}).values())

def all_tools():
    """Get all tools from the database."""
    if not card_database:
        return []
    return list(card_database.get('tools', {}).values())

# Specific trainer lists (these might need to be populated based on actual data)
def koga_list():
    """Get Koga-related cards."""
    if not card_database:
        return []
    
    koga_cards = []
    for trainer in card_database.get('trainers', {}).values():
        if hasattr(trainer, 'name') and 'koga' in trainer.name.lower():
            koga_cards.append(trainer)
    return koga_cards

def brock_list():
    """Get Brock-related cards."""
    if not card_database:
        return []
    
    brock_cards = []
    for trainer in card_database.get('trainers', {}).values():
        if hasattr(trainer, 'name') and 'brock' in trainer.name.lower():
            brock_cards.append(trainer)
    return brock_cards

def surge_list():
    """Get Lt. Surge-related cards."""
    if not card_database:
        return []
    
    surge_cards = []
    for trainer in card_database.get('trainers', {}).values():
        if hasattr(trainer, 'name') and 'surge' in trainer.name.lower():
            surge_cards.append(trainer)
    return surge_cards

def blaine_list():
    """Get Blaine-related cards."""
    if not card_database:
        return []
    
    blaine_cards = []
    for trainer in card_database.get('trainers', {}).values():
        if hasattr(trainer, 'name') and 'blaine' in trainer.name.lower():
            blaine_cards.append(trainer)
    return blaine_cards 
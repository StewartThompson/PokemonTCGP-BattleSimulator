import os
from json_card_importer import JsonCardImporter
from typing import Dict, List, Optional, Any
import copy

class CardLoader:
    """Loads and manages all cards from the JSON import system for easy deck building."""
    
    def __init__(self):
        self.importer = JsonCardImporter()
        self.all_objects = None
        self._pokemon_by_name = {}
        self._trainers_by_name = {}
        self._items_by_name = {}
        self._tools_by_name = {}
        self._fossils_by_name = {}
        self._loaded = False
    
    def load_all_cards(self):
        """Load all cards from JSON files and organize them by name for easy access."""
        if self._loaded:
            return
            
        print("Loading all cards from JSON files...")
        
        # Use the new initialize_from_folder function
        pokemon_dir = 'assets/database/pokemon'
        self.all_objects = self.importer.initialize_from_folder(pokemon_dir)
        
        # Create name-based lookups for easy access
        self._create_name_lookups()
        self._loaded = True
        
        print(f"✅ Successfully loaded {len(self.all_objects['pokemon'])} Pokemon, {len(self.all_objects['trainers'])} trainers, {len(self.all_objects['items'])} items, {len(self.all_objects['tools'])} tools, {len(self.all_objects['fossils'])} fossils")
    
    def _create_name_lookups(self):
        """Create name-based lookups for easy card access."""
        # Group Pokemon by name (multiple variants possible)
        for pokemon in self.all_objects['pokemon'].values():
            name = pokemon.name
            if name not in self._pokemon_by_name:
                self._pokemon_by_name[name] = []
            self._pokemon_by_name[name].append(pokemon)
        
        # Group trainers by name
        for trainer in self.all_objects['trainers'].values():
            name = trainer.name
            if name not in self._trainers_by_name:
                self._trainers_by_name[name] = []
            self._trainers_by_name[name].append(trainer)
        
        # Group items by name
        for item in self.all_objects['items'].values():
            name = item.name
            if name not in self._items_by_name:
                self._items_by_name[name] = []
            self._items_by_name[name].append(item)
        
        # Group tools by name
        for tool in self.all_objects['tools'].values():
            name = tool.name
            if name not in self._tools_by_name:
                self._tools_by_name[name] = []
            self._tools_by_name[name].append(tool)
        
        # Group fossils by name
        for fossil in self.all_objects['fossils'].values():
            name = fossil.name
            if name not in self._fossils_by_name:
                self._fossils_by_name[name] = []
            self._fossils_by_name[name].append(fossil)
    
    def get_pokemon_by_name(self, name: str, variant: int = 0) -> Optional[Any]:
        """Get a Pokemon by name. If multiple variants exist, specify which one."""
        if not self._loaded:
            self.load_all_cards()
        
        variants = self._pokemon_by_name.get(name, [])
        if not variants:
            return None
        
        # Return a deep copy of the specified variant
        pokemon = variants[min(variant, len(variants) - 1)]
        return copy.deepcopy(pokemon)
    
    def get_card_by_id(self, card_id: str) -> Optional[Any]:
        """Get any card by its ID, regardless of type."""
        if not self._loaded:
            self.load_all_cards()
        
        # Check each card type and return a deep copy
        if card_id in self.all_objects['pokemon']:
            return copy.deepcopy(self.all_objects['pokemon'][card_id])
        elif card_id in self.all_objects['trainers']:
            return copy.deepcopy(self.all_objects['trainers'][card_id])
        elif card_id in self.all_objects['items']:
            return copy.deepcopy(self.all_objects['items'][card_id])
        elif card_id in self.all_objects['tools']:
            return copy.deepcopy(self.all_objects['tools'][card_id])
        elif card_id in self.all_objects['fossils']:
            return copy.deepcopy(self.all_objects['fossils'][card_id])
        
        return None
    
    def get_pokemon_by_id(self, card_id: str) -> Optional[Any]:
        """Get a Pokemon by its card ID."""
        if not self._loaded:
            self.load_all_cards()
        
        # Return a deep copy so each card instance is independent
        pokemon = self.all_objects['pokemon'].get(card_id, None)
        return copy.deepcopy(pokemon) if pokemon else None
    
    def get_trainer_by_name(self, name: str, variant: int = 0) -> Optional[Any]:
        """Get a trainer by name. If multiple variants exist, specify which one."""
        if not self._loaded:
            self.load_all_cards()
        
        variants = self._trainers_by_name.get(name, [])
        if not variants:
            return None
        
        trainer = variants[min(variant, len(variants) - 1)]
        return copy.deepcopy(trainer)
    
    def get_item_by_name(self, name: str, variant: int = 0) -> Optional[Any]:
        """Get an item by name. If multiple variants exist, specify which one."""
        if not self._loaded:
            self.load_all_cards()
        
        variants = self._items_by_name.get(name, [])
        if not variants:
            return None
        
        item = variants[min(variant, len(variants) - 1)]
        return copy.deepcopy(item)
    
    def get_tool_by_name(self, name: str, variant: int = 0) -> Optional[Any]:
        """Get a tool by name. If multiple variants exist, specify which one."""
        if not self._loaded:
            self.load_all_cards()
        
        variants = self._tools_by_name.get(name, [])
        if not variants:
            return None
        
        tool = variants[min(variant, len(variants) - 1)]
        return copy.deepcopy(tool)
    
    def get_fossil_by_name(self, name: str, variant: int = 0) -> Optional[Any]:
        """Get a fossil by name. If multiple variants exist, specify which one."""
        if not self._loaded:
            self.load_all_cards()
        
        variants = self._fossils_by_name.get(name, [])
        if not variants:
            return None
        
        fossil = variants[min(variant, len(variants) - 1)]
        return copy.deepcopy(fossil)
    
    def list_pokemon_names(self) -> List[str]:
        """Get a list of all available Pokemon names."""
        if not self._loaded:
            self.load_all_cards()
        return sorted(self._pokemon_by_name.keys())
    
    def list_trainer_names(self) -> List[str]:
        """Get a list of all available trainer names."""
        if not self._loaded:
            self.load_all_cards()
        return sorted(self._trainers_by_name.keys())
    
    def list_item_names(self) -> List[str]:
        """Get a list of all available item names."""
        if not self._loaded:
            self.load_all_cards()
        return sorted(self._items_by_name.keys())
    
    def list_tool_names(self) -> List[str]:
        """Get a list of all available tool names."""
        if not self._loaded:
            self.load_all_cards()
        return sorted(self._tools_by_name.keys())
    
    def list_fossil_names(self) -> List[str]:
        """Get a list of all available fossil names."""
        if not self._loaded:
            self.load_all_cards()
        return sorted(self._fossils_by_name.keys())
    
    def find_pokemon_variants(self, name: str) -> List[str]:
        """Find all variants of a Pokemon (e.g., regular vs ex versions)."""
        if not self._loaded:
            self.load_all_cards()
        
        variants = self._pokemon_by_name.get(name, [])
        return [f"{p.name} (ID: {p.card_id}, HP: {p.max_hp})" for p in variants]

# # Create a global instance for easy access
# card_loader = CardLoader()

# Convenience functions for backward compatibility
def get_card_by_id(card_id: str):
    """Get any card by its ID, regardless of type."""
    return card_loader.get_card_by_id(card_id)

def get_pokemon(name: str, variant: int = 0):
    """Get a Pokemon by name."""
    return card_loader.get_pokemon_by_name(name, variant)

def get_pokemon_by_id(card_id: str):
    """Get a Pokemon by its card ID."""
    return card_loader.get_pokemon_by_id(card_id)

def get_trainer(name: str, variant: int = 0):
    """Get a trainer by name."""
    return card_loader.get_trainer_by_name(name, variant)

def get_item(name: str, variant: int = 0):
    """Get an item by name."""
    return card_loader.get_item_by_name(name, variant)

def get_tool(name: str, variant: int = 0):
    """Get a tool by name."""
    return card_loader.get_tool_by_name(name, variant)

def get_fossil(name: str, variant: int = 0):
    """Get a fossil by name."""
    return card_loader.get_fossil_by_name(name, variant)

if __name__ == "__main__":
    # Test the card loader
    card_loader.load_all_cards()
    
    print("\nSample Pokemon:")
    for name in card_loader.list_pokemon_names()[:10]:
        pokemon = card_loader.get_pokemon_by_name(name)
        print(f"  {pokemon.name} - {pokemon.max_hp} HP")
    
    print("\nSample Trainers:")
    for name in card_loader.list_trainer_names()[:5]:
        trainer = card_loader.get_trainer_by_name(name)
        print(f"  {trainer.name}")
    
    print("\nSample Items:")
    for name in card_loader.list_item_names()[:5]:
        item = card_loader.get_item_by_name(name)
        print(f"  {item.name}") 
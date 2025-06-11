from card_loader import card_loader

def get_deck():
    """Returns a Dialga-themed metal deck (20 cards)"""
    
    # Build deck with metal Pokemon
    deck = [
        # Dialga x2 (legendary steel type)
        card_loader.get_pokemon_by_id('a2-123'),  # Dialga
        card_loader.get_pokemon_by_id('a2-123'),
        
        # Metal Pokemon x8
        card_loader.get_pokemon_by_id('a1-081'),  # Magnemite
        card_loader.get_pokemon_by_id('a1-081'),
        card_loader.get_pokemon_by_id('a1-082'),  # Magneton
        card_loader.get_pokemon_by_id('a1-082'),
        card_loader.get_pokemon_by_id('a2-065'),  # Skarmory
        card_loader.get_pokemon_by_id('a2-065'),
        card_loader.get_pokemon_by_id('a1-208'),  # Steelix
        card_loader.get_pokemon_by_id('a1-208'),
        
        # Support Pokemon x2
        card_loader.get_pokemon_by_id('a1-074'),  # Geodude (rock support)
        card_loader.get_pokemon_by_id('a1-074'),
        
        # Trainers x4
        card_loader.get_trainer_by_name("Professor's Research"),
        card_loader.get_trainer_by_name("Professor's Research"),
        card_loader.get_trainer_by_name("Brock"),
        card_loader.get_trainer_by_name("Brock"),
        
        # Items x4
        card_loader.get_item_by_name("Poké Ball"),
        card_loader.get_item_by_name("Poké Ball"),
        card_loader.get_item_by_name("Potion"),
        card_loader.get_item_by_name("Potion"),
    ]
    
    # Remove any None values (in case some cards weren't found)
    deck = [card for card in deck if card is not None]
    
    return deck

def get_description():
    """Returns a description of the deck"""
    return {
        "name": "Dialga Deck",
        "type": "Metal",
        "strategy": "Heavy metal deck with Dialga and steel-type Pokemon"
    } 
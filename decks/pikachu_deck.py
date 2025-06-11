from card_loader import card_loader

def get_deck():
    """Returns a Pikachu-themed electric deck (20 cards)"""
    
    # Build deck with electric Pokemon
    deck = [
        # Pikachu line x6
        card_loader.get_pokemon_by_id('a1-025'),  # Pikachu
        card_loader.get_pokemon_by_id('a1-025'),
        card_loader.get_pokemon_by_id('a1-025'),
        card_loader.get_pokemon_by_id('a1-026'),  # Raichu
        card_loader.get_pokemon_by_id('a1-026'),
        card_loader.get_pokemon_by_id('a1-026'),
        
        # Additional Electric Pokemon x6
        card_loader.get_pokemon_by_id('a1-081'),  # Magnemite
        card_loader.get_pokemon_by_id('a1-081'),
        card_loader.get_pokemon_by_id('a1-082'),  # Magneton
        card_loader.get_pokemon_by_id('a1-082'),
        card_loader.get_pokemon_by_id('a1-100'),  # Voltorb
        card_loader.get_pokemon_by_id('a1-100'),
        
        # Trainers x4
        card_loader.get_trainer_by_name("Professor's Research"),
        card_loader.get_trainer_by_name("Professor's Research"),
        card_loader.get_trainer_by_name("Lt. Surge"),
        card_loader.get_trainer_by_name("Lt. Surge"),
        
        # Items x4
        card_loader.get_item_by_name("Poké Ball"),
        card_loader.get_item_by_name("Poké Ball"),
        card_loader.get_item_by_name("X Speed"),
        card_loader.get_item_by_name("X Speed"),
    ]
    
    # Remove any None values (in case some cards weren't found)
    deck = [card for card in deck if card is not None]
    
    return deck

def get_description():
    """Returns a description of the deck"""
    return {
        "name": "Pikachu Deck",
        "type": "Electric",
        "strategy": "Fast electric deck with Pikachu and lightning Pokemon"
    } 
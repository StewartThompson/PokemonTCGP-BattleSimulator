from card_loader import card_loader

def get_deck():
    """Returns a Mewtwo-themed psychic deck (20 cards)"""
    
    # Build deck with Mewtwo evolution line
    deck = [
        # Mewtwo x2 (using known card IDs)
        card_loader.get_pokemon_by_id('a1-150'),  # Mewtwo
        card_loader.get_pokemon_by_id('a1-150'),
        
        # Ralts x2
        card_loader.get_pokemon_by_id('a1-096'),  # Ralts
        card_loader.get_pokemon_by_id('a1-096'),
        
        # Kirlia x2
        card_loader.get_pokemon_by_id('a1-097'),  # Kirlia
        card_loader.get_pokemon_by_id('a1-097'),
        
        # Gardevoir x2
        card_loader.get_pokemon_by_id('a1-098'),  # Gardevoir
        card_loader.get_pokemon_by_id('a1-098'),
        
        # Additional Psychic Pokemon x4
        card_loader.get_pokemon_by_id('a1-063'),  # Abra
        card_loader.get_pokemon_by_id('a1-063'),
        card_loader.get_pokemon_by_id('a1-079'),  # Slowpoke
        card_loader.get_pokemon_by_id('a1-079'),
        
        # Trainers x4
        card_loader.get_trainer_by_name("Professor's Research"),
        card_loader.get_trainer_by_name("Professor's Research"),
        card_loader.get_trainer_by_name("Sabrina"),
        card_loader.get_trainer_by_name("Sabrina"),
        
        # Items x4
        card_loader.get_item_by_name("Potion"),
        card_loader.get_item_by_name("Potion"),
        card_loader.get_item_by_name("Poké Ball"),
        card_loader.get_item_by_name("Poké Ball"),
    ]
    
    # Remove any None values (in case some cards weren't found)
    deck = [card for card in deck if card is not None]
    
    return deck

def get_description():
    """Returns a description of the deck"""
    return {
        "name": "Mewtwo Deck",
        "type": "Psychic",
        "strategy": "Powerful psychic deck with Mewtwo and evolution lines"
    } 
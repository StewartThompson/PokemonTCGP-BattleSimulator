from card_loader import card_loader

# THIS FILE SHOULD NOT CHANGE
def get_deck():
    """Returns a Water Basic Pokemon only deck (20 cards)"""
    
    # Build deck with water basic Pokemon
    deck = [
        # Squirtle x2
        card_loader.get_pokemon_by_id('a1-053'),
        card_loader.get_pokemon_by_id('a1-053'),
        
        # Wartortle x2
        card_loader.get_pokemon_by_id('a1-054'),
        card_loader.get_pokemon_by_id('a1-054'),
        
        # Seel x2
        card_loader.get_pokemon_by_id('a1-064'),
        card_loader.get_pokemon_by_id('a1-064'),
        
        # Dewgong x2
        card_loader.get_pokemon_by_id('a1-065'),
        card_loader.get_pokemon_by_id('a1-065'),
        
        # Staryu x2
        card_loader.get_pokemon_by_id('a1-074'),
        card_loader.get_pokemon_by_id('a1-074'),
        
        # Starmie Ex x2
        card_loader.get_pokemon_by_id('a1-076'),
        card_loader.get_pokemon_by_id('a1-076'),
        
        # Pyukumuku
        card_loader.get_pokemon_by_id('a1-090'),
        card_loader.get_pokemon_by_id('a1-090'),
        
        # Potion x2
        card_loader.get_card_by_id('pa-001'),
        card_loader.get_card_by_id('pa-001'),

        # Pokeball x2
        card_loader.get_card_by_id('pa-005'),
        card_loader.get_card_by_id('pa-005'),
        
        # Professor's Research x2
        card_loader.get_card_by_id('pa-007'),
        card_loader.get_card_by_id('pa-007'),
    ]

    return deck

def get_description():
    """Returns a description of the deck"""
    return {
        "name": "Basic Water Deck",
        "type": "Water",
        "strategy": "Basic water Pokemon focused deck for testing battles"
    } 
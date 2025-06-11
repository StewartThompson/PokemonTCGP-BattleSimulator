from card_loader import card_loader

# THIS FILE SHOULD NOT CHANGE
def get_deck():
    """Returns a Grass Basic Pokemon only deck (20 cards)"""
    
    # Build deck with grass basic Pokemon
    deck = [
        # Potion x2
        card_loader.get_card_by_id('pa-001'),
        card_loader.get_card_by_id('pa-001'),

        # Bulbasaur x2
        card_loader.get_pokemon_by_id('a1-001'),
        card_loader.get_pokemon_by_id('a1-001'),
        
        # Ivysaur x2
        card_loader.get_pokemon_by_id('a1-002'),
        card_loader.get_pokemon_by_id('a1-002'),

        # Venusaur ex x1
        card_loader.get_pokemon_by_id('a1-004'),
        card_loader.get_pokemon_by_id('a1-004'),
        
        # Weedle x2
        card_loader.get_pokemon_by_id('a1-008'),
        card_loader.get_pokemon_by_id('a1-008'),
        
        # Kakuna x2
        card_loader.get_pokemon_by_id('a1-009'),
        card_loader.get_pokemon_by_id('a1-009'),
        
        
        # Pokeball x2
        card_loader.get_card_by_id('pa-005'),
        card_loader.get_card_by_id('pa-005'),
        
        # Professor's Research x2
        card_loader.get_card_by_id('pa-007'),
        card_loader.get_card_by_id('pa-007'),
        
        # Paras x2
        card_loader.get_pokemon_by_id('a1-014'),
        card_loader.get_pokemon_by_id('a1-014'),
        
        # Parasect x2
        card_loader.get_pokemon_by_id('a1-015'),
        card_loader.get_pokemon_by_id('a1-015'),
    ]

    return deck

def get_description():
    """Returns a description of the deck"""
    return {
        "name": "Basic Grass Deck",
        "type": "Grass",
        "strategy": "Basic grass Pokemon focused deck for testing battles"
    } 
from card_loader import card_loader

# THIS FILE SHOULD NOT CHANGE
def get_deck():
    """Returns a basic lightning deck (20 cards)"""
    
    # Build deck with electric Pokemon
    deck = [
       # Voltorb x2
        card_loader.get_pokemon_by_id('a1-099'),
        card_loader.get_pokemon_by_id('a1-099'),

        # Electrode x2
        card_loader.get_pokemon_by_id('a1-100'),
        card_loader.get_pokemon_by_id('a1-100'),

        # Tynamo x2
        card_loader.get_pokemon_by_id('a1-107'),
        card_loader.get_pokemon_by_id('a1-107'),

        # Eelektrik x2
        card_loader.get_pokemon_by_id('a1-108'),
        card_loader.get_pokemon_by_id('a1-108'),

        # Eelektross x2
        card_loader.get_pokemon_by_id('a1-109'),
        card_loader.get_pokemon_by_id('a1-109'),

        # Magnemite x2
        card_loader.get_pokemon_by_id('a2-051'),
        card_loader.get_pokemon_by_id('a2-051'),

        # Magneton x2
        card_loader.get_pokemon_by_id('a2-052'),
        card_loader.get_pokemon_by_id('a2-052'),

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
    
    # Remove any None values (in case some cards weren't found)
    deck = [card for card in deck if card is not None]
    
    return deck

def get_description():
    """Returns a description of the deck"""
    return {
        "name": "Basic Lightning Deck",
        "type": "Electric",
        "strategy": "Fast electric deck with lightning Pokemon"
    } 
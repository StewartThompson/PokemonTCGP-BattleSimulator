from .base_deck import BaseDeck

class BasicWaterDeck(BaseDeck):
    """Basic Water Pokemon deck (20 cards)"""

    def get_deck(self):
    """Returns a Water Basic Pokemon only deck (20 cards)"""
    
    # Build deck with water basic Pokemon
    deck = [
        # Squirtle x2
            self.get_card_by_id('a1-053'),
            self.get_card_by_id('a1-053'),
        
        # Wartortle x2
            self.get_card_by_id('a1-054'),
            self.get_card_by_id('a1-054'),
        
        # Seel x2
            self.get_card_by_id('a1-064'),
            self.get_card_by_id('a1-064'),
        
        # Dewgong x2
            self.get_card_by_id('a1-065'),
            self.get_card_by_id('a1-065'),
        
        # Staryu x2
            self.get_card_by_id('a1-074'),
            self.get_card_by_id('a1-074'),
        
        # Starmie Ex x2
            self.get_card_by_id('a1-076'),
            self.get_card_by_id('a1-076'),
        
        # Pyukumuku
            self.get_card_by_id('a1-090'),
            self.get_card_by_id('a1-090'),
        
        # Potion x2
            self.get_card_by_id('pa-001'),
            self.get_card_by_id('pa-001'),

        # Pokeball x2
            self.get_card_by_id('pa-005'),
            self.get_card_by_id('pa-005'),
        
        # Professor's Research x2
            self.get_card_by_id('pa-007'),
            self.get_card_by_id('pa-007'),
    ]

    return deck

    def get_description(self):
    """Returns a description of the deck"""
    return {
        "name": "Basic Water Deck",
        "type": "Water",
        "strategy": "Basic water Pokemon focused deck for testing battles"
    } 
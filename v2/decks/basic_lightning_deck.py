from .base_deck import BaseDeck

class BasicLightningDeck(BaseDeck):
    """Basic Lightning Pokemon deck (20 cards)"""
    
    def get_deck(self):
        """Returns a basic lightning deck (20 cards)"""
        
        # Build deck with electric Pokemon
        deck = [
           # Voltorb x2
            self.get_card_by_id('a1-099'),
            self.get_card_by_id('a1-099'),

            # Electrode x2
            self.get_card_by_id('a1-100'),
            self.get_card_by_id('a1-100'),

            # Tynamo x2
            self.get_card_by_id('a1-107'),
            self.get_card_by_id('a1-107'),

            # Eelektrik x2
            self.get_card_by_id('a1-108'),
            self.get_card_by_id('a1-108'),

            # Eelektross x2
            self.get_card_by_id('a1-109'),
            self.get_card_by_id('a1-109'),

            # Magnemite x2
            self.get_card_by_id('a2-051'),
            self.get_card_by_id('a2-051'),

            # Magneton x2
            self.get_card_by_id('a2-052'),
            self.get_card_by_id('a2-052'),

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
        
        # Remove any None values (in case some cards weren't found)
        deck = [card for card in deck if card is not None]
        
        return deck

    def get_description(self):
        """Returns a description of the deck"""
        return {
            "name": "Basic Lightning Deck",
            "type": "Electric",
            "strategy": "Fast electric deck with lightning Pokemon"
        } 
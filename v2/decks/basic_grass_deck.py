from .base_deck import BaseDeck

class BasicGrassDeck(BaseDeck):
    """Basic Grass Pokemon deck (20 cards)"""
    
    def get_deck(self):
        """Returns a Grass Basic Pokemon only deck (20 cards)"""
        
        # Build deck with grass basic Pokemon
        deck = [
            # Potion x2
            self.get_card_by_id('pa-001'),
            self.get_card_by_id('pa-001'),

            # Bulbasaur x2
            self.get_card_by_id('a1-001'),
            self.get_card_by_id('a1-001'),
            
            # Ivysaur x2
            self.get_card_by_id('a1-002'),
            self.get_card_by_id('a1-002'),

            # Venusaur ex x1
            self.get_card_by_id('a1-004'),
            self.get_card_by_id('a1-004'),
            
            # Weedle x2
            self.get_card_by_id('a1-008'),
            self.get_card_by_id('a1-008'),
            
            # Kakuna x2
            self.get_card_by_id('a1-009'),
            self.get_card_by_id('a1-009'),
            
            # Pokeball x2
            self.get_card_by_id('pa-005'),
            self.get_card_by_id('pa-005'),
            
            # Professor's Research x2
            self.get_card_by_id('pa-007'),
            self.get_card_by_id('pa-007'),
            
            # Paras x2
            self.get_card_by_id('a1-014'),
            self.get_card_by_id('a1-014'),
            
            # Parasect x2
            self.get_card_by_id('a1-015'),
            self.get_card_by_id('a1-015'),
        ]

        return deck

    def get_description(self):
        """Returns a description of the deck"""
        return {
            "name": "Basic Grass Deck",
            "type": "Grass",
            "strategy": "Basic grass Pokemon focused deck for testing battles"
        }
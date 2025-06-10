# This is the item card class; for example Poké Ball, Potion, Red Card, etc.
from .card import Card

class Item(Card):
    def __init__(self, id, name, type, subtype, set, pack, rarity, abilities):
        # Call the parent Card constructor
        super().__init__(id, name, type, subtype, set, pack, rarity)
        
        # If abilities exist, set the first one as the main ability
        if abilities:
            self.ability = abilities[0]

    def __str__(self):
        return f"{self.name}"

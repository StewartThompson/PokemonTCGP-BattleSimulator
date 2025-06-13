# This is the supporter card class; for example Professor's Research, Sabrina, ect.
from .card import Card

class Supporter(Card):
    def __init__(self, id, name, type, subtype, set, pack, rarity, abilities, action_ids):
        # Call the parent Card constructor
        super().__init__(id, name, type, subtype, set, pack, rarity, action_ids)

        # If abilities exist, set the first one as the main ability
        if abilities:
            self.ability = abilities[0]

    def __str__(self):
        return f"{self.name}"



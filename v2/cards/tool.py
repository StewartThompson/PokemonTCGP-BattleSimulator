# This is the tool card class; for example, the Cape, Poison Barb, etc.
from .card import Card

class Tool(Card):
    def __init__(self, id, name, type, subtype, set, pack, rarity, abilities):
        super().__init__(id, name, type, subtype, set, pack, rarity)

        # If abilities exist, set the first one as the main ability
        if abilities:
            self.ability = abilities[0]

    def __str__(self):
        return f"{self.name}"

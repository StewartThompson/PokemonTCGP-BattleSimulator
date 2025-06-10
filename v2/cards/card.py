# This is the superclass for all cards

class Card:
    def __init__(self, id, name, type, subtype, set, pack, rarity):
        self.id = id
        self.name = name
        self.type = type
        self.subtype = subtype
        self.set = set
        self.pack = pack
        self.rarity = rarity

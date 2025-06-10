# These are the attacks that a pokemon can use
class Ability:
    def __init__(self, name, effect, handler=None):
        self.name = name
        self.effect = effect
        self.handler = handler

    def __str__(self):
        return f"{self.name} ({self.effect})"
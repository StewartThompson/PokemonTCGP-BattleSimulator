from .card import Card
# These are the attacks that a pokemon can use
class Ability:
    class Target:
        PLAYER_ACTIVE = "pactive"
        PLAYER_BENCH = "pbench"
        PLAYER_ALL = "pall"
        OPPONENT_ACTIVE = "oactive"
        OPPONENT_BENCH = "obench"
        OPPONENT_ALL = "oall"
        ALL = "all"
    
    Position = Card.Position

    def __init__(self, name: str, effect: str, target : Target, position : Card.Position):
        self.name: str = name
        self.effect: str = effect
        self.target: Ability.Target = target
        self.position: Card.Position = position
from moteur.core.match import Match
from moteur.core.turn_state import TurnState
from moteur.core.player_extensions import player_extensions
from moteur.handlers.card_effect_handler import CardEffectHandler

# Apply player extensions
from moteur.player import Player
player_extensions(Player)
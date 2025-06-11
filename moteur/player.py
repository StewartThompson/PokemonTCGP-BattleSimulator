from agents.agent import Agent
from moteur.cartes.item import Item
from moteur.cartes.pokemon import Pokemon
import random
from agents import random_agent
from moteur.cartes.trainer import Trainer

dragon_type_energies = ["water", "electric"]
class Player:
    def __init__(self, name, deck=None, chosen_energies=None, agent=None):
        self.name = name
        self.deck = [] if not deck else deck
        self.points = 0
        self.remaining_cards = list(self.deck)
        self.cards_in_hand = []
        self.active_pokemon: Pokemon = None
        self.bench_pokemons = []
        self.discard_pile = []
        self.prize_points = 0
        self.can_play_trainer = True
        self.energy_points = 10
        if chosen_energies:
            self.chosen_energies = chosen_energies
        else:
            self.chosen_energies = []

        self.energy_pile = []
        self.energy_zone = []  # Energy Zone for PTCGP mechanics
        self.deck_energy_types = []  # Energy types available for this player's deck
        self.agent: Agent = agent(self) if agent else random_agent.RandomAgent(self)
        
    def reset_deck(self):
        deck_reset = []
        for card in self.deck:
            if card.card_type == "pokemon":
                card.current_hp = card.max_hp
                card.attached_tool = None
                for energy_type in card.equipped_energies:
                    card.equipped_energies[energy_type] = 0
                card.effect_status = []
                card.used_ability_this_turn = False
                card.damage_nerf = 0
                card.hiding = False
                card.can_retreat = True
                card.ability_used = False
                card.turn_since_placement = 1
                deck_reset.append(card)
            else:
                deck_reset.append(card)
        self.deck = deck_reset
        self.cards_in_hand = []
        self.discard_pile = []
        self.bench_pokemons = []
        self.active_pokemon = None
        self.prize_points = 0

    def set_deck(self, deck):
        # Filter out None values from the deck
        valid_deck = [card for card in deck if card is not None]
        none_count = len(deck) - len(valid_deck)
        
        if none_count > 0:
            print(f"Warning: Removed {none_count} None cards from {self.name}'s deck")
        
        self.deck = valid_deck
        self.chosen_energies = []
        for card in self.deck:
            if type(card) is Pokemon and card.pokemon_type != "normal":
                if card.pokemon_type == "dragon":
                    for energy in dragon_type_energies:
                        self.chosen_energies.append(energy)
                else:
                    self.chosen_energies.append(card.pokemon_type)
        self.chosen_energies = list(set(self.chosen_energies))

    def reset(self):
        self.reset_deck()
        self.points = 0
        self.remaining_cards = list(self.deck)
        random.shuffle(self.remaining_cards)
        self.cards_in_hand = []
        self.active_pokemon = None
        self.bench_pokemons = []
        self.energy_pile = []
        for i in range(1000):
            self.energy_pile.append(random.choice(self.chosen_energies))

    def draw(self, n):
        for i in range(int(n)):
            if len(self.remaining_cards) == 0 or len(self.cards_in_hand) > 9:
                return False

            self.cards_in_hand.append(self.remaining_cards[0])
            self.remaining_cards = self.remaining_cards[1:]
        return True

    def __str__(self):
        return f"Player {self.name} - Points: {self.points}, Remaining Cards: {self.remaining_cards}, Hand: {self.cards_in_hand}, Active Pokemon: {self.active_pokemon}, Bench: {self.bench_pokemons}, \nDeck: {len(self.deck)}"

    def __repr__(self):
        return str(self)

    def refill_energy(self):
        for i in range(100):
            self.energy_pile.append(random.choice(self.chosen_energies))

    def all_pokemons(self):
        """Return a list of all active and bench Pokémon belonging to this player."""
        pokemons = []
        if self.active_pokemon:
            pokemons.append(self.active_pokemon)
        if self.bench_pokemons:
            pokemons.extend(self.bench_pokemons)
        return pokemons

    def has_pokemons(self):
        """Check if player has any Pokémon left."""
        return self.active_pokemon is not None or len(self.bench_pokemons) > 0

    def reset_effects(self):
        """Reset temporary effects on all Pokémon."""
        for pokemon in self.all_pokemons():
            # Reset any temporary effects
            pokemon.damage_nerf = 0
            pokemon.hiding = False
            if hasattr(pokemon, 'used_ability_this_turn'):
                pokemon.used_ability_this_turn = False



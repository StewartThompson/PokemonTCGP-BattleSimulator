from v2.agents.random_agent import RandomAgent

import random
from v2.agents import bot_agent
from cards.pokemon import Pokemon
from cards.fossil import Fossil

class Player:
    def __init__(self, name, deck, chosen_energies=None, agent=None):
        self.name = name
        self.deck = deck
        self.chosen_energies = []
        self.agent = agent(self) if agent else bot_agent.RandomAgent(self)

        # These values are game values for the player
        self.points = 0
        self.cards_in_hand = []
        self.active_pokemon: Pokemon | Fossil = None
        self.bench_pokemons: list[Pokemon | Fossil] = [None, None, None]
        self.discard_pile = []
        self.prize_points = 0
        self.can_play_trainer = True
        self.energy_points = 10

        self.energy_pile = []  # This is the next two energies to be used
        self.energy_zone = []  # Energy Zone for PTCGP mechanics

        # These values are used to help the bot know the composition of the deck for strategy
        self._original_deck = deck 
        self._original_deck_energy_types = [] 

        # Methods to be called at the start of the game
        self._initialize_deck(deck)
        self._set_original_deck_energy_types()
    
    # Refill energy to be performed at the start of the players turn
    def refill_energy(self):
        self.energy_pile.append(random.choice(self.chosen_energies))

    def pokemon_field(self):
        """Return a list of all active and bench Pokémon belonging to this player."""
        pokemons = []
        if self.active_pokemon:
            pokemons.append(self.active_pokemon)
        if self.bench_pokemons:
            pokemons.extend(self.bench_pokemons)
        return pokemons

    # If player has no pokemon left, they lose the game
    def has_pokemon_left(self):
        """Check if player has any Pokémon left."""
        return self.active_pokemon is not None and len(self.bench_pokemons) > 0

    # Draws inital hand and checks for basic pokemon
    def draw_inital_hand(self):
        while True:
            self.shuffle_deck()
            self.draw(5)
            if self._check_for_basic_pokemon(self.cards_in_hand) == True:
                return
            else:
                # If no basic pokemon is drawn, reset the deck and draw again
                self.deck = self._original_deck
                self.cards_in_hand = []

    def get_basic_pokemon(self):
        return [card for card in self.cards_in_hand if card.subtype == "Basic"]

    def shuffle_deck(self):
        random.shuffle(self.deck)

    def draw(self, n):
        for i in range(int(n)):
            if len(self.deck) == 0 or len(self.cards_in_hand) > 10:
                return False

            self.cards_in_hand.append(self.deck[0])
            self.deck.pop(0)
        return True

    def __str__(self):
        return f"Player {self.name} - Points: {self.points}, Hand: {len(self.cards_in_hand)}, Active Pokemon: {self.active_pokemon}, Bench: {self.bench_pokemons}, \nDeck: {len(self.deck)}"

    # PRIVATE METHODS STARTING HERE

    # Initalize 
    def _initialize_deck(self, deck):
        # Filter out None values from the deck
        valid_deck = [card for card in deck if card is not None]
        
        if len(valid_deck) != 20:
            raise ValueError("Deck must contain 20 cards")
        
        if self._check_for_basic_pokemon(valid_deck) == False:
            raise ValueError("Deck must contain at least one basic pokemon")
        
        self.deck = valid_deck
        self._original_deck = valid_deck

    def _check_for_basic_pokemon(self, deck):
        for card in deck:
            if type(card) is Pokemon and card.subtype == "Basic":
                return True
        return False

    def _set_original_deck_energy_types(self):
        # Set the expected energy types for the deck
        energy_types = set()
        for card in self.deck:
            if isinstance(card, Pokemon):
                for attack in card.attacks:
                    energy_types.update(attack.cost)
        self._original_deck_energy_types = list(energy_types)



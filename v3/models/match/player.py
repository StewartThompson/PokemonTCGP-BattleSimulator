from v3.models.agents.random_agent import RandomAgent

import random
from v3.models.agents import bot_agent
from v3.models.agents.agent import Agent
from cards.pokemon import Pokemon
from cards.card import Card
from cards.energy import Energy

class Player:
    def __init__(self, name: str, deck: list[Card], chosen_energies: list[Energy.Type] = None, agent: Agent = None):
        self.name: str = name # Name of the player
        self.deck: list[Card] = deck # Original deck that the player has
        self.chosen_energies: list[Energy.Type] = chosen_energies # Chosen energies for the player
        self.agent: Agent = agent(self) if agent else bot_agent.RandomAgent(self) # Controls the player's actions

        # These values are game values for the player
        self.points: int = 0
        self.energy_zone: Energy.Type = None  # This is the next two energies to be used

        # Tracking the player's cards
        self.cards_in_hand: list[Card] = []
        self.active_pokemon: Pokemon = None
        self.bench_pokemons: list[Pokemon] = [None, None, None]
        self.discard_pile: list[Card] = []
        
        # Additional game values to track statuses
        self.can_play_trainer = True

        # Methods to be called at the start of the game
        self._initialize_deck(deck)
        self._add_energies_to_energy_zone()

    # Draws inital hand and checks for basic pokemon
    def draw_inital_hand(self):
        while True:
            self._shuffle_deck()
            self.draw(5)
            if self._check_for_basic_pokemon(self.cards_in_hand) == True:
                return
            else:
                # If no basic pokemon is drawn, reset the deck and draw again
                self.put_cards_back_in_deck()

    def can_draw(self):
        return len(self.deck) > 0 and len(self.cards_in_hand) < 10

    def draw(self, n):
        for _ in range(int(n)):
            if not self.can_draw():
                raise ValueError("Check if can draw before drawing")
            
            card = self.deck.pop(0)
            card.card_position = Card.Position.HAND
            self.cards_in_hand.append(card)
    
    def put_cards_back_in_deck(self):
        for card in self.cards_in_hand:
            card.card_position = Card.Position.DECK
        self.deck = self.deck + self.cards_in_hand
        self.cards_in_hand = []

    ########################################################
    #            PRIVATE METHODS STARTING HERE             #
    ########################################################

    # Initialize the deck
    # Initalize 
    def _initialize_deck(self, deck):
        # Filter out None values from the deck
        if None in deck:
            raise ValueError("Deck cannot contain None values")
        if self._check_for_basic_pokemon(deck) == False:
            raise ValueError("Deck must contain at least one basic pokemon")
        if len(deck) != 20:
            raise ValueError("Deck must contain 20 cards")
        # Check for duplicate cards (max 2 copies allowed)
        for card in deck:
            if deck.count(card.name) > 2:
                raise ValueError(f"Deck cannot contain more than 2 copies of {card.name}")
        
        # Set all cards in deck to DECK position
        for card in deck:
            card.card_position = Card.Position.DECK

    # Refill energy to be performed at the start of the players turn
    def _add_energies_to_energy_zone(self):
        # Add energy to the energy zone if it is not already full
        if not self._can_add_energy_to_pokemon():
            self.energy_zone = random.choice(self.chosen_energies)
    
    def _can_add_energy_to_pokemon(self):
        # Check if the pokemon can add energy to its energy zone
        return self.energy_zone is not None
    
    def _add_energy_to_pokemon(self, pokemon: Pokemon):
        # Add energy to the pokemon
        if self._can_add_energy_to_pokemon():
            pokemon.energy_zone.append(self.energy_zone)
            self.energy_zone = None
        else:
            raise ValueError("Should have checked if energy zone is not None")

    def _check_for_basic_pokemon(self, deck):
        for card in deck:
            if type(card) is Pokemon and card.subtype == "Basic":
                return True
        return False

    def _shuffle_deck(self):
        # Ensure all cards in deck have DECK position
        random.shuffle(self.deck)




    ########################################################
    #           Still need to implement these              #
    ########################################################

    def set_active_pokemon(self, pokemon):
        """Set a Pokemon as the active Pokemon."""
        if pokemon:
            pokemon.card_position = Card.Position.ACTIVE
        self.active_pokemon = pokemon

    def add_to_bench(self, pokemon, position):
        """Add a Pokemon to the bench at a specific position."""
        if pokemon and 0 <= position < len(self.bench_pokemons):
            pokemon.card_position = Card.Position.BENCH
            self.bench_pokemons[position] = pokemon

    def discard_card(self, card):
        """Add a card to the discard pile."""
        if card:
            card.card_position = Card.Position.DISCARD
            self.discard_pile.append(card)


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
        if chosen_energies:
            self.chosen_energies = chosen_energies
        else:
            self.chosen_energies = []

        self.energy_pile = []
        self.agent: Agent = agent(self) if agent else random_agent.RandomAgent(self)
    def reset_deck(self):
        deck_reset = []
        for card in self.deck:
            if card.card_type == "pokemon":
                card.current_hp = card.max_hp
                card.tool_id = None
                for energy_type in card.equipped_energies:
                    card.equipped_energies[energy_type] = 0
                card.effect_status = []
                card.turn_since_placement = 1
                card.used_ability_this_turn = False
                card.damage_nerf = 0
                card.hiding = False
                new_card = Pokemon(card.card_id, card.name, card.stage, card.attack_ids, card.ability_id, card.max_hp, card.pre_evolution_name, card.evolutions_name, card.pokemon_type, card.weakness, card.retreat_cost)
                deck_reset.append(new_card)
            elif card.card_type == "item":
                deck_reset.append(Item(card.item_id, card.name, card.effect, card.special_values))
            else:
                deck_reset.append(Trainer(card.trainer_id, card.name, card.effect, card.special_values))
        self.deck = deck_reset


    def set_deck(self, deck):
        self.deck = deck
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



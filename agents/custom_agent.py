import random

from agents.agent import Agent
from utils import all_attacks, contains_trainer, contains_hand_pokemon, contains_item


class CustomAgent(Agent):
    def __init__(self, player):
        super().__init__(player)

    def most_damaging_attacks(self, attacks):
        max_damaging_attack = None
        max_damage = 0
        for attack_id in attacks:
            attack = all_attacks[attack_id]
            if attack.damage > max_damage:
                max_damage = attack.damage
                max_damaging_attack = attack_id
        return max_damaging_attack

    def get_action(self, action_list, match, action_type=None):
        if action_type == "turn_action":
            possible_evolutions = match.get_possible_evolutions(self.player)
            if possible_evolutions:
                return "play_card"
            if "attach_energy" in action_list:
                return "attach_energy"
            else:
                return random.choice(action_list)
        elif action_type == "precise_action":
            possible_attacks = [action for action in action_list if action.startswith("attack_")]
            if possible_attacks:
                return random.choice(possible_attacks)
            else:
                return random.choice(action_list)
        else:
            return random.choice(action_list)

    def get_chosen_card(self, cards, match, chosing_type=None):
        possible_evolutions = match.get_possible_evolutions(self.player)
        if possible_evolutions and chosing_type == "playing_card":
            return random.choice(possible_evolutions)[0]
        elif chosing_type == "attaching_energy":
            all_attacks_active = match.get_possible_attacks(match.player1.active_pokemon, self.player)

            if (self.player.energy_pile[0] == self.player.active_pokemon.pokemon_type or self.player.active_pokemon.pokemon_type == "normal") and self.most_damaging_attacks(self.player.active_pokemon.attack_ids) not in all_attacks_active:
                return self.player.active_pokemon
            other_targets = []
            for pokemon in self.player.bench_pokemons:
                if pokemon.pokemon_type == self.player.energy_pile[0] or pokemon.pokemon_type == "normal":
                    all_attacks_pokemon = match.get_possible_attacks(pokemon, self.player)
                    if self.most_damaging_attacks(pokemon.attack_ids) not in all_attacks_pokemon:
                        other_targets.append(pokemon)
            if other_targets:
                return random.choice(other_targets)
            return self.player.active_pokemon
        elif chosing_type == "playing_card":
            hand_pokemons = contains_hand_pokemon(cards, self.player.cards_in_hand)
            if not match.played_trainer_this_turn and contains_trainer(cards):
                return random.choice([card for card in cards if card and card.card_type == "trainer"])
            elif hand_pokemons:
                return random.choice(hand_pokemons)
            elif contains_item(cards):
                return random.choice([card for card in cards if card and card.card_type == "item"])
            elif self.player.active_pokemon in cards:
                return self.player.active_pokemon
            else:
                return random.choice(cards)
        else:
            return random.choice(cards)



import random

from moteur.cartes.pokemon import Pokemon
from moteur.cartes.trainer import Trainer
from moteur.cartes.item import Item
from moteur.cartes.tool import Tool
from moteur.player import Player
from utils import get_basic_pokemons, koga_list, brock_list, surge_list, blaine_list, all_attacks, all_abilities


def get_chosen_card(cards, who_choose="player"):
    print("Choose Card Options :")
    for e in cards:
        print(f"{cards.index(e)}: {e}")
    return cards[int(input("Choose a card by index: "))]
    #return random.choice(cards)


def get_action(action_list, action_type=None):
    print("action_type", action_type)
    print("Choose Action Options :")
    for e in action_list:
        print(f"{action_list.index(e)}: {e}")
    return action_list[int(input("Choose an action by index: "))]
    #return random.choice(action_list)


class Match:
    def __init__(self, player1, player2):
        self.player1: Player = player1
        self.player2: Player = player2
        self.current_player = 1
        self.turn = 0
        self.result = False
        self.played_trainer_this_turn = False
        self.played_pokemon_this_turn = False

    def start_battle(self):

        if not len(self.player1.deck) == 20:
            raise ValueError("Deck 1 must have 20 cards")
        if not len(self.player2.deck) == 20:
            raise ValueError("Deck 2 must have 20 cards")
        self.player1.reset()
        self.player2.reset()

        random_player1_basic_pokemon = random.choice(get_basic_pokemons(self.player1.remaining_cards))
        self.player1.cards_in_hand.append(random_player1_basic_pokemon)
        self.player1.remaining_cards.remove(random_player1_basic_pokemon)
        self.player1.draw(4)

        basic_pokemons = get_basic_pokemons(self.player1.cards_in_hand)
        self.player1.active_pokemon = get_chosen_card(basic_pokemons)
        basic_pokemons.remove(self.player1.active_pokemon)
        self.player1.cards_in_hand.remove(self.player1.active_pokemon)
        new_bench_pokemon = get_chosen_card(basic_pokemons+ [None])
        while new_bench_pokemon is not None and len(self.player1.bench_pokemons) < 3:
            self.player1.bench_pokemons.append(new_bench_pokemon)
            basic_pokemons.remove(new_bench_pokemon)
            self.player1.cards_in_hand.remove(new_bench_pokemon)
            new_bench_pokemon = get_chosen_card(basic_pokemons + [None])

        random_player2_basic_pokemon = random.choice(get_basic_pokemons(self.player2.remaining_cards))
        self.player2.cards_in_hand.append(random_player2_basic_pokemon)
        self.player2.remaining_cards.remove(random_player2_basic_pokemon)
        self.player2.draw(4)

        basic_pokemons = get_basic_pokemons(self.player2.cards_in_hand)
        self.player2.active_pokemon = get_chosen_card(basic_pokemons)
        basic_pokemons.remove(self.player2.active_pokemon)
        self.player2.cards_in_hand.remove(self.player2.active_pokemon)
        new_bench_pokemon = get_chosen_card(basic_pokemons + [None])
        while new_bench_pokemon is not None and len(self.player2.bench_pokemons) < 3:
            self.player2.bench_pokemons.append(new_bench_pokemon)
            basic_pokemons.remove(new_bench_pokemon)
            self.player2.cards_in_hand.remove(new_bench_pokemon)
            new_bench_pokemon = get_chosen_card(basic_pokemons + [None])



        attack_prevention = (False, None)
        supporter_prevention = (False, None)
        retreat_prevention = (False, None)
        shield = (0, None)
        while self.result is False:
            print(self.player1.points, self.player2.points)
            self.turn += 1

            current_player = self.player1 if self.current_player == 1 else self.player2
            opponent = self.player2 if self.current_player == 1 else self.player1
            current_player.draw(1)
            playing = True
            self.played_trainer_this_turn = False
            attached_energy_this_turn = False
            if self.turn == 1:
                attached_energy_this_turn = True
            for pokemon in opponent.bench_pokemons:
                if pokemon.ability_id:
                    ability = all_abilities[pokemon.ability_id]
                    if ability.effect_type == "block_supporter":
                        self.played_trainer_this_turn = True
            if opponent.active_pokemon and opponent.active_pokemon.ability_id:
                ability = all_abilities[opponent.active_pokemon.ability_id]
                if ability.effect_type == "block_supporter":
                    self.played_trainer_this_turn = True
            if supporter_prevention[0] and supporter_prevention[1] == current_player:
                self.played_trainer_this_turn = True


            retreat_cost_reduction = 0
            bonus_damage_effect = (0, "")

            while playing:
                if current_player.active_pokemon in current_player.cards_in_hand + current_player.remaining_cards + current_player.bench_pokemons:
                    print(self.turn, "alert")
                    print(current_player)
                    raise IndexError
                playable_cards = self.get_playable_cards(current_player, opponent, retreat_cost_reduction, attack_prevention, retreat_prevention)
                possible_actions = ["end_turn"]
                if len(playable_cards) > 0:
                    possible_actions.append("play_card")

                if not attached_energy_this_turn:
                    possible_actions.append("attach_energy")
                print("Hand :", current_player.cards_in_hand)
                chosen_action = get_action(possible_actions+[None], "turn_action")
                if chosen_action is None:
                    continue
                if chosen_action == "end_turn":
                    break

                elif chosen_action == "attach_energy":
                    pokemons_to_attach_to = current_player.bench_pokemons + [current_player.active_pokemon]
                    pokemon_to_attach_to = get_chosen_card(pokemons_to_attach_to+[None])
                    if pokemon_to_attach_to is None:
                        continue
                    attached_energy_this_turn = True
                    try:
                        energy = current_player.energy_pile.pop(0)
                    except IndexError:
                        current_player.refill_energy()
                        energy = current_player.energy_pile.pop(0)
                    pokemon_to_attach_to.equipped_energies[energy] += 1

                elif chosen_action == "play_card":
                    chosen_card = get_chosen_card(playable_cards+[None])
                    if chosen_card is None:
                        continue
                    if chosen_card.card_type == "pokemon":
                        if chosen_card in current_player.cards_in_hand:
                            if "basic" in chosen_card.stage:
                                if not current_player.active_pokemon:
                                    current_player.active_pokemon = chosen_card
                                else:
                                    current_player.bench_pokemons.append(chosen_card)
                            else:
                                pre_evolution = chosen_card.pre_evolution_name
                                evolvable_pokemons = []
                                for bench_pokemon in current_player.bench_pokemons:
                                    if bench_pokemon.name == pre_evolution and "ex" not in bench_pokemon.stage and bench_pokemon.turn_since_placement > 1:
                                        evolvable_pokemons.append(bench_pokemon)
                                if current_player.active_pokemon and current_player.active_pokemon.name == pre_evolution and "ex" not in current_player.active_pokemon.stage and current_player.active_pokemon.turn_since_placement > 1:
                                    evolvable_pokemons.append(current_player.active_pokemon)
                                if not evolvable_pokemons:
                                    raise ValueError("No pokemon can evolve into", chosen_card.name)
                                evolving_pokemon = get_chosen_card(evolvable_pokemons) if len(
                                    evolvable_pokemons) > 1 else evolvable_pokemons[0]
                                chosen_card.current_hp -= (evolving_pokemon.max_hp - evolving_pokemon.current_hp)
                                chosen_card.equipped_energies = evolving_pokemon.equipped_energies.copy()
                                chosen_card.tool_id = evolving_pokemon.tool_id
                                if evolving_pokemon == current_player.active_pokemon:
                                    current_player.active_pokemon = chosen_card
                                else:
                                    current_player.bench_pokemons[current_player.bench_pokemons.index(evolving_pokemon)] = chosen_card
                            current_player.cards_in_hand.remove(chosen_card)

                        elif chosen_card in current_player.bench_pokemons:
                            if chosen_card.ability_id:
                                ability = all_abilities[chosen_card.ability_id]
                                if ability.effect_type == "heal_all":
                                    heal_amount = ability.special_values[0]
                                    for pokemon in current_player.bench_pokemons:
                                        if pokemon.current_hp + heal_amount <= pokemon.max_hp:
                                            pokemon.current_hp += heal_amount
                                    if current_player.active_pokemon.current_hp + heal_amount <= current_player.active_pokemon.max_hp:
                                        current_player.active_pokemon.current_hp += heal_amount

                                elif ability.effect_type == "self_discard":
                                    current_player.bench_pokemons.remove(chosen_card)

                                elif ability.effect_type == "switch_active":
                                    target_player = ability.special_values[0]
                                    who_choses_new = ability.special_values[1]
                                    if target_player == "enemy":
                                        current_active_pokemon = opponent.active_pokemon
                                        current_active_pokemon.hiding = False
                                        current_active_pokemon.damage_nerf = 0
                                        if who_choses_new == "opponent":
                                            opponent.active_pokemon = get_chosen_card(opponent.bench_pokemons,
                                                                                      "opponent")
                                            opponent.bench_pokemons.remove(opponent.active_pokemon)
                                            opponent.bench_pokemons.append(current_active_pokemon)

                                        elif who_choses_new == "self":
                                            opponent.active_pokemon = get_chosen_card(opponent.bench_pokemons)
                                            opponent.bench_pokemons.remove(opponent.active_pokemon)
                                            opponent.bench_pokemons.append(current_active_pokemon)
                                    elif target_player == "self":
                                        current_active_pokemon = current_player.active_pokemon
                                        current_active_pokemon.hiding = False
                                        current_active_pokemon.damage_nerf = 0
                                        if who_choses_new == "opponent":
                                            current_player.active_pokemon = get_chosen_card(current_player.bench_pokemons, "opponent")
                                            current_player.bench_pokemons.remove(current_player.active_pokemon)
                                            current_player.bench_pokemons.append(current_active_pokemon)

                                        elif who_choses_new == "self":
                                            current_player.active_pokemon = get_chosen_card(current_player.bench_pokemons)
                                            current_player.bench_pokemons.remove(current_player.active_pokemon)
                                            current_player.bench_pokemons.append(current_active_pokemon)

                                elif ability.effect_type == "damage_enemy":
                                    targets = ability.special_values[0]
                                    damage_amount = max(0, ability.special_values[1])
                                    target = None
                                    if targets == "active":
                                        target = opponent.active_pokemon
                                    elif targets == "bench":
                                        target = get_chosen_card(opponent.bench_pokemons)
                                    elif targets == "any":
                                        target = get_chosen_card(opponent.bench_pokemons + [opponent.active_pokemon])
                                    target.current_hp -= max(0, damage_amount)
                                    if target.current_hp <= 0:
                                        if 'ex' in target.stage:
                                            current_player.points += 2
                                        else:
                                            current_player.points += 1
                                        if target in opponent.bench_pokemons:
                                            opponent.bench_pokemons.remove(target)
                                        else:
                                            opponent.active_pokemon = None
                                            if not opponent.bench_pokemons:
                                                self.result = current_player
                                                break
                                            else:
                                                opponent.active_pokemon = get_chosen_card(opponent.bench_pokemons)
                                                opponent.bench_pokemons.remove(opponent.active_pokemon)
                                        if current_player.points >= 3:
                                            if opponent.points >= 3:
                                                if current_player.points > opponent.points:
                                                    self.result = current_player
                                                elif current_player.points < opponent.points:
                                                    self.result = opponent
                                                else:
                                                    self.result = None
                                            else:
                                                self.result = current_player
                                            break
                                elif ability.effect_type == "gain_energy":
                                    pokemon_gaining_energy = ability.special_values[0]
                                    gained_energy_type = ability.special_values[1]
                                    pokemon_gaining_energy_type = ability.special_values[2]
                                    gained_energy_amount = ability.special_values[3]
                                    if pokemon_gaining_energy == "self":
                                        chosen_card.equipped_energies[gained_energy_type] += gained_energy_amount
                                    elif pokemon_gaining_energy == "active":
                                        if pokemon_gaining_energy_type == "any" or current_player.active_pokemon.pokemon_type == pokemon_gaining_energy_type:
                                            current_player.active_pokemon.equipped_energies[
                                                gained_energy_type] += gained_energy_amount

                                    elif pokemon_gaining_energy == "bench":
                                        possible_targets = []
                                        for pokemon in current_player.bench_pokemons:
                                            if pokemon.pokemon_type == pokemon_gaining_energy_type or pokemon_gaining_energy_type == "any":
                                                possible_targets.append(pokemon)
                                        get_chosen_card(possible_targets).equipped_energies[
                                            gained_energy_type] += gained_energy_amount

                                elif ability.effect_type == "sleep":
                                    coins_to_flip = ability.special_values[0]
                                    if coins_to_flip == 0:
                                        opponent.active_pokemon.effect_status.append("asleep")
                                        if "paralyzed" in opponent.active_pokemon.effect_status:
                                            opponent.active_pokemon.effect_status.remove("paralyzed")
                                        if "confused" in opponent.active_pokemon.effect_status:
                                            opponent.active_pokemon.effect_status.remove("confused")
                                    else:
                                        if random.choice([True, False]):
                                            opponent.active_pokemon.effect_status.append("asleep")
                                            if "paralyzed" in opponent.active_pokemon.effect_status:
                                                opponent.active_pokemon.effect_status.remove("paralyzed")
                                            if "confused" in opponent.active_pokemon.effect_status:
                                                opponent.active_pokemon.effect_status.remove("confused")

                                elif ability.effect_type == "poison":
                                    poison_damage = ability.special_values[0]
                                    from_where_pokemon_must_be = ability.special_values[1]
                                    target = ability.special_values[2]
                                    resulting_poison = "poisoned" if poison_damage == 10 else "super_poisoned"
                                    if (
                                            from_where_pokemon_must_be == "active" and chosen_card == current_player.active_pokemon) or (
                                            from_where_pokemon_must_be == "bench" and chosen_card in current_player.bench_pokemons):
                                        if target == "active" and resulting_poison not in opponent.active_pokemon.effect_status:
                                            if resulting_poison == "poisoned":
                                                if resulting_poison not in opponent.active_pokemon.effect_status and "super_poisoned" not in opponent.active_pokemon.effect_status:
                                                    opponent.active_pokemon.effect_status.append(resulting_poison)
                                            else:
                                                if resulting_poison not in opponent.active_pokemon.effect_status:
                                                    opponent.active_pokemon.effect_status.append(resulting_poison)
                                                if "poisoned" in opponent.active_pokemon.effect_status:
                                                    opponent.active_pokemon.effect_status.remove("poisoned")
                                        elif target == "any":
                                            possible_targets = []
                                            if opponent.active_pokemon and resulting_poison not in opponent.active_pokemon.effect_status:
                                                possible_targets.append(opponent.active_pokemon)
                                            for pokemon in opponent.bench_pokemons:
                                                if resulting_poison not in pokemon.effect_status and "super_poisoned" not in pokemon.effect_status:
                                                    possible_targets.append(pokemon)

                                            chosen_target = get_chosen_card(possible_targets)
                                            if resulting_poison == "poisoned":
                                                chosen_target.effect_status.append(resulting_poison)
                                            else:
                                                chosen_target.effect_status.append(resulting_poison)
                                                if "poisoned" in chosen_target.effect_status:
                                                    chosen_target.effect_status.remove("poisoned")

                                        elif target == "bench":
                                            possible_targets = []
                                            for pokemon in opponent.bench_pokemons:
                                                if resulting_poison not in pokemon.effect_status and "super_poisoned" not in pokemon.effect_status:
                                                    possible_targets.append(pokemon)

                                            chosen_target = get_chosen_card(possible_targets)
                                            if resulting_poison == "poisoned":
                                                chosen_target.effect_status.append(resulting_poison)

                                            else:
                                                chosen_target.effect_status.append(resulting_poison)
                                                if "poisoned" in chosen_target.effect_status:
                                                    chosen_target.effect_status.remove("poisoned")
                                elif ability.effect_type == "look_at_deck":
                                    # todo
                                    pass
                                chosen_card.used_ability_this_turn = True
                            else:
                                raise ValueError("how is a benched pokemon with no ability playable ?", chosen_card, current_player)

                        elif chosen_card == current_player.active_pokemon:
                            precise_possible_actions = []

                            if chosen_card.ability_id and self.is_ability_conditions_met(chosen_card, current_player,
                                                                                         opponent):
                                precise_possible_actions.append("use_ability")
                            if sum(chosen_card.equipped_energies.values()) >= chosen_card.retreat_cost - retreat_cost_reduction:
                                if "paralyzed" not in chosen_card.effect_status and "asleep" not in chosen_card.effect_status and len(current_player.bench_pokemons) > 0:
                                    precise_possible_actions.append("retreat")
                            if chosen_card.attack_ids:
                                if (not attack_prevention[0] or attack_prevention[1] != current_player) and "paralyzed" not in chosen_card.effect_status and "asleep" not in chosen_card.effect_status:
                                    for attack_id in chosen_card.attack_ids:
                                        has_energies = True
                                        attack = all_attacks[attack_id]
                                        energies_used = 0
                                        for energy_type, cost in attack.energy_cost.items():
                                            if energy_type != "normal":
                                                if chosen_card.equipped_energies[energy_type] < cost:
                                                    has_energies = False
                                                    break
                                                else:
                                                    energies_used += cost
                                        if has_energies:
                                            if attack.energy_cost["normal"] > 0:
                                                if sum(chosen_card.equipped_energies.values()) - energies_used >= \
                                                        attack.energy_cost["normal"]:
                                                    precise_possible_actions.append(f"attack_{attack_id}")
                            try:
                                chosen_precise_action = get_action(precise_possible_actions, "precise_action")
                            except Exception as e:
                                print(sum(chosen_card.equipped_energies.values()), chosen_card.retreat_cost, retreat_cost_reduction, len(current_player.bench_pokemons))
                                print(chosen_card)
                                print(current_player)
                                raise e
                            if chosen_precise_action == "use_ability":
                                ability = all_abilities[chosen_card.ability_id]
                                if ability.effect_type == "heal_all":
                                    heal_amount = ability.special_values[0]
                                    for pokemon in current_player.bench_pokemons:
                                        if pokemon.current_hp + heal_amount <= pokemon.max_hp:
                                            pokemon.current_hp += heal_amount
                                    if current_player.active_pokemon.current_hp + heal_amount <= current_player.active_pokemon.max_hp:
                                        current_player.active_pokemon.current_hp += heal_amount

                                elif ability.effect_type == "self_discard":
                                    current_player.active_pokemon = None
                                    if not current_player.bench_pokemons:
                                        self.result = opponent
                                        break
                                    else:
                                        current_player.active_pokemon = get_chosen_card(current_player.bench_pokemons)
                                        current_player.bench_pokemons.remove(current_player.active_pokemon)

                                elif ability.effect_type == "switch_active":
                                    target_player = ability.special_values[0]
                                    who_choses_new = ability.special_values[1]
                                    if target_player == "enemy":
                                        current_active_pokemon = opponent.active_pokemon
                                        current_active_pokemon.hiding = False
                                        current_active_pokemon.damage_nerf = 0
                                        if who_choses_new == "opponent":
                                            opponent.active_pokemon = get_chosen_card(opponent.bench_pokemons, "opponent")
                                            opponent.bench_pokemons.remove(opponent.active_pokemon)
                                            opponent.bench_pokemons.append(current_active_pokemon)

                                        elif who_choses_new == "self":
                                            opponent.active_pokemon = get_chosen_card(opponent.bench_pokemons)
                                            opponent.bench_pokemons.remove(opponent.active_pokemon)
                                            opponent.bench_pokemons.append(current_active_pokemon)

                                    elif target_player == "self":
                                        current_active_pokemon = current_player.active_pokemon
                                        current_active_pokemon.hiding = False
                                        current_active_pokemon.damage_nerf = 0
                                        if who_choses_new == "opponent":
                                            current_player.active_pokemon = get_chosen_card(current_player.bench_pokemons, "opponent")
                                            current_player.bench_pokemons.append(current_active_pokemon)
                                            current_player.bench_pokemons.remove(current_player.active_pokemon)
                                        elif who_choses_new == "self":
                                            current_player.active_pokemon = get_chosen_card(current_player.bench_pokemons)
                                            current_player.bench_pokemons.append(current_active_pokemon)
                                            current_player.bench_pokemons.remove(current_player.active_pokemon)
                                elif ability.effect_type == "damage_enemy":
                                    targets = ability.special_values[0]
                                    damage_amount = max(0, ability.special_values[1])
                                    target = None
                                    if targets == "active":
                                        target = opponent.active_pokemon
                                    elif targets == "bench":
                                        target = get_chosen_card(opponent.bench_pokemons)
                                    elif targets == "any":
                                        target = get_chosen_card(opponent.bench_pokemons + [opponent.active_pokemon])
                                    target.current_hp -= max(damage_amount, 0)
                                    if target.current_hp <= 0:
                                        if 'ex' in target.stage:
                                            current_player.points += 2
                                        else:
                                            current_player.points += 1
                                        if target in opponent.bench_pokemons:
                                            opponent.bench_pokemons.remove(target)
                                        else:
                                            opponent.active_pokemon = None
                                            if not opponent.bench_pokemons:
                                                self.result = current_player
                                                break
                                            else:
                                                opponent.active_pokemon = get_chosen_card(opponent.bench_pokemons)
                                                opponent.bench_pokemons.remove(opponent.active_pokemon)
                                        if current_player.points >= 3:
                                            if opponent.points >= 3:
                                                if current_player.points > opponent.points:
                                                    self.result = current_player
                                                elif current_player.points < opponent.points:
                                                    self.result = opponent
                                                else:
                                                    self.result = None
                                            else:
                                                self.result = current_player
                                            break
                                elif ability.effect_type == "gain_energy":
                                    pokemon_gaining_energy = ability.special_values[0]
                                    gained_energy_type = ability.special_values[1]
                                    pokemon_gaining_energy_type = ability.special_values[2]
                                    gained_energy_amount = ability.special_values[3]
                                    if pokemon_gaining_energy == "self":
                                        chosen_card.equipped_energies[gained_energy_type] += gained_energy_amount
                                    elif pokemon_gaining_energy == "active":
                                        if pokemon_gaining_energy_type == "any" or current_player.active_pokemon.pokemon_type == pokemon_gaining_energy_type:
                                            current_player.active_pokemon.equipped_energies[
                                                gained_energy_type] += gained_energy_amount

                                    elif pokemon_gaining_energy == "bench":
                                        possible_targets = []
                                        for pokemon in current_player.bench_pokemons:
                                            if pokemon.pokemon_type == pokemon_gaining_energy_type or pokemon_gaining_energy_type == "any":
                                                possible_targets.append(pokemon)
                                        get_chosen_card(possible_targets).equipped_energies[
                                            gained_energy_type] += gained_energy_amount

                                elif ability.effect_type == "sleep":
                                    coins_to_flip = ability.special_values[0]
                                    if coins_to_flip == 0:
                                        opponent.active_pokemon.effect_status.append("asleep")
                                        if "paralyzed" in opponent.active_pokemon.effect_status:
                                            opponent.active_pokemon.effect_status.remove("paralyzed")
                                        if "confused" in opponent.active_pokemon.effect_status:
                                            opponent.active_pokemon.effect_status.remove("confused")

                                    else:
                                        if random.choice([True, False]):
                                            opponent.active_pokemon.effect_status.append("asleep")
                                            if "paralyzed" in opponent.active_pokemon.effect_status:
                                                opponent.active_pokemon.effect_status.remove("paralyzed")
                                            if "confused" in opponent.active_pokemon.effect_status:
                                                opponent.active_pokemon.effect_status.remove("confused")
                                elif ability.effect_type == "poison":
                                    poison_damage = ability.special_values[0]
                                    from_where_pokemon_must_be = ability.special_values[1]
                                    target = ability.special_values[2]
                                    resulting_poison = "poisoned" if poison_damage == 10 else "super_poisoned"
                                    if (
                                            from_where_pokemon_must_be == "active" and chosen_card == current_player.active_pokemon) or (
                                            from_where_pokemon_must_be == "bench" and chosen_card in current_player.bench_pokemons):
                                        if target == "active" and resulting_poison not in opponent.active_pokemon.effect_status:
                                            if resulting_poison == "poisoned":
                                                if resulting_poison not in opponent.active_pokemon.effect_status and "super_poisoned" not in opponent.active_pokemon.effect_status:
                                                    opponent.active_pokemon.effect_status.append(resulting_poison)
                                            else:
                                                if resulting_poison not in opponent.active_pokemon.effect_status:
                                                    opponent.active_pokemon.effect_status.append(resulting_poison)
                                                if "poisoned" in opponent.active_pokemon.effect_status:
                                                    opponent.active_pokemon.effect_status.remove("poisoned")
                                        elif target == "any":
                                            possible_targets = []
                                            if opponent.active_pokemon and resulting_poison not in opponent.active_pokemon.effect_status:
                                                possible_targets.append(opponent.active_pokemon)
                                            for pokemon in opponent.bench_pokemons:
                                                if resulting_poison not in pokemon.effect_status and "super_poisoned" not in pokemon.effect_status:
                                                    possible_targets.append(pokemon)
                                            chosen_target = get_chosen_card(possible_targets)
                                            if resulting_poison == "poisoned":
                                                chosen_target.effect_status.append(resulting_poison)
                                            else:
                                                chosen_target.effect_status.append(resulting_poison)
                                                if "poisoned" in chosen_target.effect_status:
                                                    chosen_target.effect_status.remove("poisoned")
                                        elif target == "bench":
                                            possible_targets = []
                                            for pokemon in opponent.bench_pokemons:
                                                if resulting_poison not in pokemon.effect_status and "super_poisoned" not in pokemon.effect_status:
                                                    possible_targets.append(pokemon)
                                            chosen_target = get_chosen_card(possible_targets)
                                            if resulting_poison == "poisoned":
                                                chosen_target.effect_status.append(resulting_poison)
                                            else:
                                                chosen_target.effect_status.append(resulting_poison)
                                                if "poisoned" in chosen_target.effect_status:
                                                    chosen_target.effect_status.remove("poisoned")
                                elif ability.effect_type == "look_at_deck":
                                    # todo
                                    pass
                                chosen_card.used_ability_this_turn = True
                            elif chosen_precise_action == "retreat":
                                attack_prevention = (False, None)
                                chosen_card.effect_status = []
                                chosen_card.hiding = False
                                chosen_card.damage_nerf = 0
                                retreat_cost = max(0, chosen_card.retreat_cost - retreat_cost_reduction)
                                most_energies = sorted(chosen_card.equipped_energies.values(), reverse=True)[0]
                                if most_energies == sum(chosen_card.equipped_energies.values()):
                                    def find_energy():
                                        for e_type, k in chosen_card.equipped_energies.items():
                                            if k == most_energies:
                                                return e_type

                                    chosen_card.equipped_energies[find_energy()] -= retreat_cost
                                else:
                                    while retreat_cost > 0:
                                        energies_removable = [energy_type for energy_type, amount in chosen_card.equipped_energies.items() if amount > 0]
                                        chosen_energy = get_action(energies_removable)
                                        chosen_card.equipped_energies[chosen_energy] -= 1
                                        retreat_cost -= 1
                                pokemon_to_replace_with = get_chosen_card(current_player.bench_pokemons)
                                current_player.bench_pokemons.append(chosen_card)
                                current_player.bench_pokemons.remove(pokemon_to_replace_with)
                                current_player.active_pokemon = pokemon_to_replace_with
                            elif chosen_precise_action.startswith("attack"):
                                attack_id = int(chosen_precise_action.split("_")[1])
                                attack = all_attacks[attack_id]
                                already_damaged = False
                                if attack.effect_type is not None and attack.effect_type == "copy_attack":
                                    copiable_attacks = []
                                    # get list of attacks from opponent active pokemon
                                    for attack_id in opponent.active_pokemon.attack_ids:
                                        if attack_id in all_attacks:
                                            copiable_attacks.append(all_attacks[attack_id])
                                    if copiable_attacks:
                                        chosen_attack = get_action(copiable_attacks, "copiable_attack")
                                        # check if the pokemon has the required energy to do this attack
                                        has_energies = True
                                        energies_used = 0
                                        for energy_type, cost in chosen_attack.energy_cost.items():
                                            if energy_type != "normal":
                                                if chosen_card.equipped_energies[energy_type] < cost:
                                                    has_energies = False
                                                    break
                                                else:
                                                    energies_used += cost
                                        if has_energies:
                                            if chosen_attack.energy_cost["normal"] > 0:
                                                if sum(chosen_card.equipped_energies.values()) - energies_used >= \
                                                        chosen_attack.energy_cost["normal"]:
                                                    attack = chosen_attack
                                if attack.effect_type is None:
                                    damage = attack.damage
                                    if bonus_damage_effect != (0, ""):
                                        if bonus_damage_effect[1] == "any":
                                            damage += bonus_damage_effect[0]
                                        elif bonus_damage_effect[1] == "blaine_list":
                                            if chosen_card.card_id in blaine_list:
                                                damage += bonus_damage_effect[0]
                                    active_opponent = opponent.active_pokemon
                                    if active_opponent.weakness == chosen_card.pokemon_type:
                                        damage += 20
                                    if active_opponent.ability_id:
                                        ability = all_abilities[active_opponent.ability_id]
                                        if ability.effect_type == "shield":
                                            amount_shielded = ability.special_values[0]
                                            damage -= amount_shielded
                                        elif ability.effect_type == "thorns":
                                            damage_reflected = ability.special_values[0]
                                            current_player.active_pokemon.current_hp -= damage_reflected
                                            if current_player.active_pokemon.current_hp <= 0:
                                                if not current_player.bench_pokemons:
                                                    self.result = opponent
                                                    break
                                                else:
                                                    current_player.active_pokemon = get_chosen_card(current_player.bench_pokemons)
                                                    current_player.bench_pokemons.remove(current_player.active_pokemon)
                                                if 'ex' in chosen_card.stage:
                                                    opponent.points += 2
                                                else:
                                                    opponent.points += 1
                                                if opponent.points >= 3:
                                                    if current_player.points >= 3:
                                                        if current_player.points > opponent.points:
                                                            self.result = current_player
                                                        elif current_player.points < opponent.points:
                                                            self.result = opponent
                                                        else:
                                                            self.result = None
                                                    else:
                                                        self.result = opponent
                                                    break
                                    active_opponent.current_hp -= max(0, damage)
                                    if active_opponent.current_hp <= 0:
                                        if 'ex' in active_opponent.stage:
                                            current_player.points += 2
                                        else:
                                            current_player.points += 1
                                        opponent.active_pokemon = None
                                        if not opponent.bench_pokemons:
                                            self.result = current_player
                                            break
                                        else:
                                            opponent.active_pokemon = get_chosen_card(opponent.bench_pokemons)
                                            opponent.bench_pokemons.remove(opponent.active_pokemon)
                                        if current_player.points >= 3:
                                            if opponent.points >= 3:
                                                if current_player.points > opponent.points:
                                                    self.result = current_player
                                                elif current_player.points < opponent.points:
                                                    self.result = opponent
                                                else:
                                                    self.result = None
                                            else:
                                                self.result = current_player
                                            break
                                else:
                                    damage = attack.damage
                                    lifesteal = False
                                    chosen_card: Pokemon
                                    if attack.effect_type == "self_heal":
                                        heal_amount = attack.special_values[0]
                                        chosen_card.current_hp = min(chosen_card.current_hp + heal_amount,
                                                                     chosen_card.max_hp)
                                    elif attack.effect_type == "switch_active":
                                        target = attack.special_values[0]
                                        who_choose_new_active = attack.special_values[1]
                                        if target == "enemy":
                                            current_active_pokemon = opponent.active_pokemon
                                            current_active_pokemon.hiding = False
                                            current_active_pokemon.damage_nerf = 0
                                            if who_choose_new_active == "opponent":
                                                opponent.active_pokemon = get_chosen_card(opponent.bench_pokemons, "opponent")
                                                opponent.bench_pokemons.remove(opponent.active_pokemon)
                                                opponent.bench_pokemons.append(current_active_pokemon)

                                            elif who_choose_new_active == "self":
                                                opponent.active_pokemon = get_chosen_card(opponent.bench_pokemons)
                                                opponent.bench_pokemons.remove(opponent.active_pokemon)
                                                opponent.bench_pokemons.append(current_active_pokemon)
                                            else:
                                                raise IndexError("not any ?")
                                        elif target == "self":
                                            current_active_pokemon = current_player.active_pokemon
                                            current_active_pokemon.hiding = False
                                            current_active_pokemon.damage_nerf = 0
                                            if who_choose_new_active == "opponent":
                                                current_player.active_pokemon = get_chosen_card(current_player.bench_pokemons, "opponent")
                                                current_player.bench_pokemons.remove(current_player.active_pokemon)
                                                current_player.bench_pokemons.append(current_active_pokemon)

                                            elif who_choose_new_active == "self":
                                                current_player.active_pokemon = get_chosen_card(current_player.bench_pokemons)
                                                current_player.bench_pokemons.remove(current_player.active_pokemon)
                                                current_player.bench_pokemons.append(current_active_pokemon)
                                            else:
                                                raise IndexError("not any ?")
                                        else:
                                            raise IndexError("not any ?")
                                    elif attack.effect_type == "find_random_typed_pokemon_in_deck":
                                        target_type = attack.special_values[0]
                                        amount = attack.special_values[1]
                                        if not len(current_player.cards_in_hand) + amount > 10:
                                            pokemons_of_type_in_deck = [pokemon for pokemon in
                                                                        current_player.remaining_cards if
                                                                        pokemon.card_type == "pokemon" and pokemon.pokemon_type == target_type]
                                            random.shuffle(pokemons_of_type_in_deck)
                                            if pokemons_of_type_in_deck:
                                                for i in range(amount):
                                                    if len(pokemons_of_type_in_deck) == 0:
                                                        break
                                                    current_player.cards_in_hand.append(random.choice(pokemons_of_type_in_deck))
                                                    pokemons_of_type_in_deck.remove(current_player.cards_in_hand[-1])
                                                    current_player.remaining_cards.remove(current_player.cards_in_hand[-1])
                                    elif attack.effect_type == "poison" and not opponent.active_pokemon.hiding:
                                        poison_damage = attack.special_values[0]
                                        resulting_poison = "poisoned" if poison_damage == 10 else "super_poisoned"
                                        if resulting_poison not in opponent.active_pokemon.effect_status and "super_poisoned" not in opponent.active_pokemon.effect_status:
                                            opponent.active_pokemon.effect_status.append(resulting_poison)
                                        if resulting_poison == "super_poisoned" and "poisoned" in opponent.active_pokemon.effect_status:
                                            opponent.active_pokemon.effect_status.remove("poisoned")
                                    elif attack.effect_type == "sum":
                                        bonus_damage = attack.special_values[0]
                                        coins_to_flip = attack.special_values[1]
                                        bonus_applies = attack.special_values[2]
                                        amount_of_yes = 0
                                        for i in range(coins_to_flip):
                                            if random.choice([True, False]):
                                                amount_of_yes += 1
                                        if bonus_applies == "foreach":
                                            damage += bonus_damage * amount_of_yes
                                        elif bonus_applies == "exact":
                                            if amount_of_yes == coins_to_flip:
                                                damage += bonus_damage
                                    elif attack.effect_type == "multiply":
                                        coins_to_flip = attack.special_values[0]
                                        amount_of_yes = 0
                                        for i in range(coins_to_flip):
                                            if random.choice([True, False]):
                                                amount_of_yes += 1
                                        damage *= amount_of_yes
                                    elif attack.effect_type == "bonus_energy":
                                        amount_of_energy = attack.special_values[0]
                                        target = attack.special_values[1]
                                        energy_type_given = attack.special_values[2]
                                        type_of_target_pokemon = attack.special_values[3]
                                        for i in range(amount_of_energy):
                                            if target == "active":
                                                if type_of_target_pokemon == "any" or current_player.active_pokemon.pokemon_type == type_of_target_pokemon:
                                                    current_player.active_pokemon.equipped_energies[energy_type_given] += 1
                                            elif target == "bench":
                                                possible_targets = []
                                                for pokemon in current_player.bench_pokemons:
                                                    if pokemon.pokemon_type == type_of_target_pokemon or type_of_target_pokemon == "any":
                                                        possible_targets.append(pokemon)
                                                get_chosen_card(possible_targets).equipped_energies[energy_type_given] += 1
                                    elif attack.effect_type == "discard_energy":
                                        energy_type_to_discard = attack.special_values[0]
                                        amount_of_energy_to_discard = attack.special_values[1]
                                        if amount_of_energy_to_discard == "all":
                                            amount_of_energy_to_discard = sum(chosen_card.equipped_energies.values())
                                        if energy_type_to_discard == "any":
                                            possible_energies_to_discard = []
                                            for energy_type, amount in chosen_card.equipped_energies.items():
                                                if amount > 0:
                                                    possible_energies_to_discard.append(energy_type)
                                            for i in range(amount_of_energy_to_discard):
                                                if len(possible_energies_to_discard) == 0:
                                                    break
                                                energy_type = random.choice(possible_energies_to_discard)
                                                chosen_card.equipped_energies[energy_type] -= 1
                                                if chosen_card.equipped_energies[energy_type] == 0:
                                                    possible_energies_to_discard.remove(energy_type)
                                        else:
                                            for i in range(amount_of_energy_to_discard):
                                                if chosen_card.equipped_energies[energy_type_to_discard] == 0:
                                                    break
                                                chosen_card.equipped_energies[energy_type_to_discard] -= 1
                                                if chosen_card.equipped_energies[energy_type_to_discard] == 0:
                                                    break
                                    elif attack.effect_type == "prevent_attack":
                                        coins_to_flip = attack.special_values[0]
                                        if coins_to_flip == 0 or random.choice([True, False]):
                                            attack_prevention = (True, opponent)
                                    elif attack.effect_type == "damage_self":
                                        amount_of_damage = attack.special_values[0]
                                        chosen_card.current_hp -= max(amount_of_damage, 0)
                                        if chosen_card.current_hp <= 0:
                                            if not current_player.bench_pokemons:
                                                self.result = opponent
                                                break
                                            else:
                                                current_player.active_pokemon = get_chosen_card(current_player.bench_pokemons)
                                                current_player.bench_pokemons.remove(current_player.active_pokemon)
                                            if 'ex' in chosen_card.stage:
                                                opponent.points += 2
                                            else:
                                                opponent.points += 1
                                            if opponent.points >= 3:
                                                if current_player.points >= 3:
                                                    if current_player.points > opponent.points:
                                                        self.result = current_player
                                                    elif current_player.points < opponent.points:
                                                        self.result = opponent
                                                    else:
                                                        self.result = None
                                                else:
                                                    self.result = opponent
                                                break
                                    elif attack.effect_type == "bonus_energy_flip":
                                        coins_to_flip = attack.special_values[0]
                                        target = attack.special_values[1]
                                        energy_type_given = attack.special_values[2]
                                        type_of_target_pokemon = attack.special_values[3]
                                        for i in range(coins_to_flip):
                                            if random.choice([True, False]):
                                                if target == "active":
                                                    if type_of_target_pokemon == "any" or current_player.active_pokemon.pokemon_type == type_of_target_pokemon:
                                                        current_player.active_pokemon.equipped_energies[energy_type_given] += 1
                                                elif target == "bench":
                                                    possible_targets = []
                                                    for pokemon in current_player.bench_pokemons:
                                                        if pokemon.pokemon_type == type_of_target_pokemon or type_of_target_pokemon == "any":
                                                            possible_targets.append(pokemon)
                                                    get_chosen_card(possible_targets).equipped_energies[energy_type_given] += 1
                                    elif attack.effect_type == "bonus_damage_with_bonus_energy":
                                        additional_energies_needed = attack.special_values[0]
                                        additional_energy_type = attack.special_values[1]
                                        bonus_damage = attack.special_values[2]
                                        if chosen_card.equipped_energies[additional_energy_type] >= additional_energies_needed + attack.energy_cost[additional_energy_type]:
                                            damage += bonus_damage
                                    elif attack.effect_type == "block_supporter_next_turn":
                                        supporter_prevention = (True, opponent)
                                    elif attack.effect_type == "shield":
                                        shield_amount = attack.special_values[0]
                                        shield = (shield_amount, opponent)
                                    elif attack.effect_type == "bonus_damage_foreach_enemy_energy":
                                        additional_damage = attack.special_values[0]

                                        total_enemy_energies = 0
                                        for energy_type, amount in opponent.active_pokemon.equipped_energies.items():
                                            total_enemy_energies += amount
                                        additional_damage = additional_damage * total_enemy_energies
                                        damage += additional_damage
                                    elif attack.effect_type == "hiding":
                                        coins_to_flip = attack.special_values[0]
                                        if coins_to_flip == 0:
                                            chosen_card.hiding = True
                                        elif random.choice([True, False]):
                                            chosen_card.hiding = True
                                    elif attack.effect_type == "reduce_enemy_damage":
                                        damage_nerf = attack.special_values[0]
                                        if damage_nerf > opponent.active_pokemon.damage_nerf:
                                            opponent.active_pokemon.damage_nerf = damage_nerf
                                    elif attack.effect_type == "damage_target":
                                        damage_done = attack.special_values[0]
                                        target = attack.special_values[1]
                                        possible_targets = []
                                        if target == "any":
                                            if opponent.active_pokemon and not opponent.active_pokemon.hiding:
                                                possible_targets.append(opponent.active_pokemon)
                                            possible_targets.append(*opponent.bench_pokemons)
                                        elif target == "benched":
                                            possible_targets.append(*opponent.bench_pokemons)
                                        if possible_targets:
                                            chosen_target = get_chosen_card(possible_targets)
                                            if chosen_target == opponent.active_pokemon:
                                                damage = damage_done
                                            else:
                                                already_damaged = True
                                                active_opponent = chosen_target
                                                damage_done -= chosen_card.damage_nerf
                                                chosen_card.damage_nerf = 0
                                                if active_opponent.ability_id:
                                                    ability = all_abilities[active_opponent.ability_id]
                                                    if ability.effect_type == "shield":
                                                        amount_shielded = ability.special_values[0]
                                                        damage_done -= amount_shielded
                                                    elif ability.effect_type == "thorns" and active_opponent == opponent.active_pokemon:
                                                        damage_reflected = ability.special_values[0]
                                                        current_player.active_pokemon.current_hp -= damage_reflected
                                                        if current_player.active_pokemon.current_hp <= 0:
                                                            if not current_player.bench_pokemons:
                                                                self.result = opponent
                                                                break
                                                            else:
                                                                current_player.active_pokemon = get_chosen_card(
                                                                    current_player.bench_pokemons)
                                                                current_player.bench_pokemons.remove(
                                                                    current_player.active_pokemon)
                                                            if 'ex' in chosen_card.stage:
                                                                opponent.points += 2
                                                            else:
                                                                opponent.points += 1
                                                            if opponent.points >= 3:
                                                                if current_player.points >= 3:
                                                                    if current_player.points > opponent.points:
                                                                        self.result = current_player
                                                                    elif current_player.points < opponent.points:
                                                                        self.result = opponent
                                                                    else:
                                                                        self.result = None
                                                                else:
                                                                    self.result = opponent
                                                                break
                                                active_opponent.current_hp -= max(damage_done, 0)

                                                if active_opponent.current_hp <= 0:
                                                    if 'ex' in active_opponent.stage:
                                                        current_player.points += 2
                                                    else:
                                                        current_player.points += 1
                                                    opponent.bench_pokemons.remove(active_opponent)

                                                    if current_player.points >= 3:
                                                        if opponent.points >= 3:
                                                            if current_player.points > opponent.points:
                                                                self.result = current_player
                                                            elif current_player.points < opponent.points:
                                                                self.result = opponent
                                                            else:
                                                                self.result = None
                                                        else:
                                                            self.result = current_player
                                                        break
                                    elif attack.effect_type == "discard_opponent_energy" and not opponent.active_pokemon.hiding:
                                        coins_to_flip = attack.special_values[0]
                                        amount_of_energies = attack.special_values[1]
                                        if coins_to_flip == 0 or random.choice([True, False]):
                                            possible_energies_to_discard = []
                                            for energy_type, amount in opponent.active_pokemon.equipped_energies.items():
                                                if amount > 0:
                                                    possible_energies_to_discard.append(energy_type)
                                            for i in range(amount_of_energies):
                                                if len(possible_energies_to_discard) == 0:
                                                    break
                                                energy_type = random.choice(possible_energies_to_discard)
                                                opponent.active_pokemon.equipped_energies[energy_type] -= 1
                                                if opponent.active_pokemon.equipped_energies[energy_type] == 0:
                                                    possible_energies_to_discard.remove(energy_type)
                                    elif attack.effect_type == "paralyze" and not opponent.active_pokemon.hiding:
                                        coins_to_flip = attack.special_values[0]
                                        if coins_to_flip == 0:
                                            opponent.active_pokemon.effect_status.append("paralyzed")
                                            if "asleep" in opponent.active_pokemon.effect_status:
                                                opponent.active_pokemon.effect_status.remove("asleep")
                                            if "confused" in opponent.active_pokemon.effect_status:
                                                opponent.active_pokemon.effect_status.remove("confused")
                                        elif random.choice([True, False]):
                                            opponent.active_pokemon.effect_status.append("paralyzed")
                                            if "asleep" in opponent.active_pokemon.effect_status:
                                                opponent.active_pokemon.effect_status.remove("asleep")
                                            if "confused" in opponent.active_pokemon.effect_status:
                                                opponent.active_pokemon.effect_status.remove("confused")
                                    elif attack.effect_type == "damaged_benched_pokemon":
                                        bench_pokemon_damage = attack.special_values[0]
                                        amount_of_targets = attack.special_values[1] # 0 = all
                                        target = attack.special_values[2] # ally or enemy
                                        if amount_of_targets == 0:
                                            if target == "enemy":
                                                possible_targets = opponent.bench_pokemons
                                            elif target == "ally":
                                                possible_targets = current_player.bench_pokemons
                                            else:
                                                raise ValueError("invalid target")
                                            for pokemon in possible_targets:
                                                protection_amount = 0
                                                if pokemon.ability_id:
                                                    ability = all_abilities[pokemon.ability_id]
                                                    if ability.effect_type == "shield":
                                                        protection_amount = ability.special_values[0]
                                                if pokemon.current_hp + protection_amount - bench_pokemon_damage <= 0:
                                                    if 'ex' in pokemon.stage:
                                                        current_player.points += 2
                                                    else:
                                                        current_player.points += 1
                                                    if pokemon in opponent.bench_pokemons:
                                                        opponent.bench_pokemons.remove(pokemon)
                                                    else:
                                                        current_player.bench_pokemons.remove(pokemon)
                                                else:
                                                    pokemon.current_hp -= max((bench_pokemon_damage - protection_amount), 0)
                                        else:
                                            possible_targets = []
                                            if target == "enemy":
                                                for pokemon in opponent.bench_pokemons:
                                                    possible_targets.append(pokemon)

                                            elif target == "ally":
                                                for pokemon in current_player.bench_pokemons:
                                                    possible_targets.append(pokemon)
                                            if possible_targets:
                                                chosen_target = get_chosen_card(possible_targets)
                                                protection_amount = 0
                                                if chosen_target.ability_id:
                                                    ability = all_abilities[chosen_target.ability_id]
                                                    if ability.effect_type == "shield":
                                                        protection_amount = ability.special_values[0]
                                                if chosen_target.current_hp + protection_amount - bench_pokemon_damage <= 0:
                                                    if 'ex' in chosen_target.stage:
                                                        current_player.points += 2
                                                    else:
                                                        current_player.points += 1
                                                    if chosen_target in opponent.bench_pokemons:
                                                        opponent.bench_pokemons.remove(chosen_target)
                                                    else:
                                                        current_player.bench_pokemons.remove(chosen_target)
                                                else:
                                                    chosen_target.current_hp -= max(0, (bench_pokemon_damage - protection_amount))
                                    elif attack.effect_type == "bonus_damage_if_damaged":
                                        bonus_damage = attack.special_values[0]
                                        target = attack.special_values[1]  # ally or enemy
                                        if target == "enemy":
                                            if opponent.active_pokemon.current_hp < opponent.active_pokemon.max_hp:
                                                damage += bonus_damage
                                        elif target == "self":
                                            if current_player.active_pokemon.current_hp < current_player.active_pokemon.max_hp:
                                                damage += bonus_damage
                                    elif attack.effect_type == "multiply_benched":
                                        target = attack.special_values[0]
                                        target_type = attack.special_values[1]
                                        valid_target = 0
                                        if target == "ally":
                                            for pokemon in current_player.bench_pokemons:
                                                if pokemon.pokemon_type == target_type:
                                                    valid_target += 1
                                        elif target == "enemy":
                                            for pokemon in opponent.bench_pokemons:
                                                if pokemon.pokemon_type == target_type:
                                                    valid_target += 1
                                        damage *= valid_target
                                    elif attack.effect_type == "either_bonus_damage_or_self_damage":
                                        coins_to_flip = attack.special_values[0] #need all coins to be heads for it to work
                                        bonus_damage_if_success = attack.special_values[1]
                                        recoin_damage_if_fail = attack.special_values[2]
                                        success = True
                                        for i in range(coins_to_flip):
                                            if not random.choice([True, False]):
                                                success = False
                                        if success:
                                            damage += bonus_damage_if_success
                                        else:
                                            chosen_card.current_hp -= recoin_damage_if_fail
                                            if chosen_card.current_hp <= 0:
                                                if not current_player.bench_pokemons:
                                                    self.result = opponent
                                                    break
                                                else:
                                                    current_player.active_pokemon = get_chosen_card(current_player.bench_pokemons)
                                                    current_player.bench_pokemons.remove(current_player.active_pokemon)
                                                if 'ex' in chosen_card.stage:
                                                    opponent.points += 2
                                                else:
                                                    opponent.points += 1
                                                if opponent.points >= 3:
                                                    if current_player.points >= 3:
                                                        if current_player.points > opponent.points:
                                                            self.result = current_player
                                                        elif current_player.points < opponent.points:
                                                            self.result = opponent
                                                        else:
                                                            self.result = None
                                                    else:
                                                        self.result = opponent
                                                    break
                                    elif attack.effect_type == "switch_self_with_benched":
                                        valid_targets = current_player.bench_pokemons
                                        if len(valid_targets) > 0:
                                            chosen_card.hiding = False
                                            chosen_card.damage_nerf = 0
                                            current_player.active_pokemon = get_chosen_card(valid_targets)
                                            current_player.bench_pokemons.remove(current_player.active_pokemon)
                                            current_player.bench_pokemons.append(chosen_card)
                                    elif attack.effect_type == "lifesteal":
                                        lifesteal = True
                                    elif attack.effect_type == "no_retreat":
                                        retreat_prevention = (True, opponent)
                                    elif attack.effect_type == "place_pokemon_on_bench":
                                        if len(current_player.bench_pokemons) < 3:
                                            pokemon_name = attack.special_values[0]
                                            pokemons = []
                                            for pokemon in current_player.remaining_cards:
                                                if pokemon.name == pokemon_name:
                                                    pokemons.append(pokemon)
                                            random.shuffle(pokemons)
                                            if pokemons:
                                                current_player.bench_pokemons.append(pokemons[0])
                                                current_player.remaining_cards.remove(pokemons[0])
                                    elif attack.effect_type == "bonus_specific_pokemon_benched":
                                        bonus_damage = attack.special_values[0]
                                        pokemon_name = attack.special_values[1]

                                        for pokemon in current_player.bench_pokemons:
                                            if pokemon.name == pokemon_name:
                                                damage += bonus_damage
                                    elif attack.effect_type == "bonus_if_poisoned":
                                        bonus_damage = attack.special_values[0]
                                        target = attack.special_values[1]  # self or enemy
                                        if target == "enemy":
                                            if "poisoned" in opponent.active_pokemon.effect_status or "super_poisoned" in opponent.active_pokemon.effect_status:
                                                damage += bonus_damage
                                        elif target == "self":
                                            if "poisoned" in current_player.active_pokemon.effect_status or "super_poisoned" in current_player.active_pokemon.effect_status:
                                                damage += bonus_damage
                                    elif attack.effect_type == "gain_self_energy":
                                        energy_type = attack.special_values[0]
                                        amount = attack.special_values[1]
                                        chosen_card.equipped_energies[energy_type] += amount
                                    elif attack.effect_type == "opponent_reveal_hand":
                                        #todo
                                        pass
                                    elif attack.effect_type == "sleep":
                                        opponent.active_pokemon.effect_status.append("asleep")
                                        if "paralyzed" in opponent.active_pokemon.effect_status:
                                            opponent.active_pokemon.effect_status.remove("paralyzed")
                                        if "confused" in opponent.active_pokemon.effect_status:
                                            opponent.active_pokemon.effect_status.remove("confused")
                                    elif attack.effect_type == "draw":
                                        amount_draw = attack.special_values[0]
                                        for i in range(amount_draw):
                                            if not current_player.draw(1):
                                                break
                                    elif attack.effect_type == "discard_from_hand":
                                        coins_to_flip = attack.special_values[0]
                                        target = attack.special_values[1]  # ally or enemy
                                        way_of_selection = attack.special_values[2]  # random or chosen
                                        amount_to_discord = attack.special_values[3]
                                        if coins_to_flip == 0 or random.choice([True, False]):
                                            if target == "ally":
                                                possible_targets = current_player.cards_in_hand
                                            elif target == "enemy":
                                                possible_targets = opponent.cards_in_hand
                                            else:
                                                raise ValueError("invalid target")
                                            for i in range(amount_to_discord):
                                                if len(possible_targets) == 0:
                                                    break
                                                if way_of_selection == "random":
                                                    card_to_remove = random.choice(possible_targets)
                                                elif way_of_selection == "chosen":
                                                    card_to_remove = get_chosen_card(possible_targets)
                                                else:
                                                    raise ValueError("wrong way of selection")

                                                if target == "ally":
                                                    current_player.cards_in_hand.remove(card_to_remove)
                                                elif target == "enemy":
                                                    opponent.cards_in_hand.remove(card_to_remove)
                                    elif attack.effect_type == "send_active_to_deck":
                                        coins_to_flip = attack.special_values[0]
                                        target = attack.special_values[1]  # ally or enemy
                                        if coins_to_flip == 0 or random.choice([True, False]):
                                            if target == "ally":
                                                current_player.active_pokemon.hiding = False
                                                current_player.active_pokemon.damage_nerf = 0
                                                current_player.active_pokemon.effect_status = []
                                                current_player.active_pokemon.turn_since_placement = 1
                                                current_player.remaining_cards.append(current_player.active_pokemon)
                                                current_player.active_pokemon = None
                                                if not current_player.bench_pokemons:
                                                    self.result = opponent
                                                    break
                                                else:
                                                    current_player.active_pokemon = get_chosen_card(current_player.bench_pokemons)
                                                    current_player.bench_pokemons.remove(current_player.active_pokemon)
                                            elif target == "enemy":
                                                opponent.active_pokemon.hiding = False
                                                opponent.active_pokemon.damage_nerf = 0
                                                opponent.active_pokemon.effect_status = []
                                                opponent.active_pokemon.turn_since_placement = 1
                                                opponent.remaining_cards.append(opponent.active_pokemon)
                                                opponent.active_pokemon = None
                                                if not opponent.bench_pokemons:
                                                    self.result = current_player
                                                    break
                                                else:
                                                    opponent.active_pokemon = get_chosen_card(opponent.bench_pokemons)
                                                    opponent.bench_pokemons.remove(opponent.active_pokemon)
                                    else:

                                        if attack.effect_type != "copy_attack": raise IndexError("Forgot effect or typo", attack.effect_type)

                                    if not already_damaged:
                                        if bonus_damage_effect != (0, ""):
                                            if bonus_damage_effect[1] == "any":
                                                damage += bonus_damage_effect[0]
                                            elif bonus_damage_effect[1] == "blaine_list":
                                                if chosen_card.card_id in blaine_list:
                                                    damage += bonus_damage_effect[0]
                                        active_opponent = opponent.active_pokemon
                                        if active_opponent.weakness == chosen_card.pokemon_type:
                                            damage += 20
                                        if shield[0] > 0 and shield[1] == current_player:
                                            damage -= shield[0]
                                            shield = (0, None)
                                        damage -= chosen_card.damage_nerf
                                        chosen_card.damage_nerf = 0
                                        if active_opponent.ability_id:
                                            ability = all_abilities[active_opponent.ability_id]
                                            if ability.effect_type == "shield":
                                                protection_amount = ability.special_values[0]
                                                damage -= protection_amount
                                            elif ability.effect_type == "thorns":
                                                damage_reflected = ability.special_values[0]
                                                current_player.active_pokemon.current_hp -= damage_reflected
                                                if current_player.active_pokemon.current_hp <= 0:
                                                    if not current_player.bench_pokemons:
                                                        self.result = opponent
                                                        break
                                                    else:
                                                        current_player.active_pokemon = get_chosen_card(
                                                            current_player.bench_pokemons)
                                                        current_player.bench_pokemons.remove(
                                                            current_player.active_pokemon)
                                                    if 'ex' in chosen_card.stage:
                                                        opponent.points += 2
                                                    else:
                                                        opponent.points += 1
                                                    if opponent.points >= 3:
                                                        if current_player.points >= 3:
                                                            if current_player.points > opponent.points:
                                                                self.result = current_player
                                                            elif current_player.points < opponent.points:
                                                                self.result = opponent
                                                            else:
                                                                self.result = None
                                                        else:
                                                            self.result = opponent
                                                        break

                                        if not active_opponent.hiding:
                                            active_opponent.current_hp -= max(damage, 0)
                                            if lifesteal:
                                                chosen_card.current_hp = min(chosen_card.current_hp + damage, chosen_card.max_hp)
                                        active_opponent.hiding = False
                                        if active_opponent.current_hp <= 0:
                                            if not opponent.bench_pokemons:
                                                self.result = current_player
                                                break
                                            else:
                                                opponent.active_pokemon = get_chosen_card(opponent.bench_pokemons)
                                                opponent.bench_pokemons.remove(opponent.active_pokemon)
                                            if 'ex' in active_opponent.stage:
                                                current_player.points += 2
                                            else:
                                                current_player.points += 1
                                            if current_player.points >= 3:
                                                if opponent.points >= 3:
                                                    if current_player.points > opponent.points:
                                                        self.result = current_player
                                                    elif current_player.points < opponent.points:
                                                        self.result = opponent
                                                    else:
                                                        self.result = None
                                                else:
                                                    self.result = current_player
                                                break

                        else:
                            raise ValueError("how is a card not in hand or bench playable ?")
                    elif chosen_card.card_type == "trainer":
                        chosen_card: Trainer
                        trainer = chosen_card
                        if trainer.effect == "heal":
                            heal_amount = trainer.special_values[0]
                            target_type = trainer.special_values[1]
                            targets = trainer.special_values[2]
                            if targets == "any":
                                possible_targets = []
                                for pokemon in current_player.bench_pokemons:
                                    if pokemon.pokemon_type == target_type and pokemon.current_hp + heal_amount <= pokemon.max_hp:
                                        possible_targets.append(pokemon)
                                if current_player.active_pokemon.pokemon_type == target_type and current_player.active_pokemon.current_hp + heal_amount <= current_player.active_pokemon.max_hp:
                                    possible_targets.append(current_player.active_pokemon)
                                get_chosen_card(possible_targets).current_hp += heal_amount
                            elif targets == "active":
                                current_player.active_pokemon.current_hp += heal_amount
                            elif targets == "bench":
                                possible_targets = []
                                for pokemon in current_player.bench_pokemons:
                                    if pokemon.pokemon_type == target_type and pokemon.current_hp + heal_amount <= pokemon.max_hp:
                                        possible_targets.append(pokemon)
                                get_chosen_card(possible_targets).current_hp += heal_amount

                        elif trainer.effect == "draw":
                            amount_draw = trainer.special_values[0]
                            for i in range(amount_draw):
                                if not current_player.draw(1):
                                    break

                        elif trainer.effect == "energy_bonus":
                            coins_to_flip = trainer.special_values[0]
                            target_type = trainer.special_values[1]
                            targets = trainer.special_values[2]
                            possible_targets = []
                            for pokemon in current_player.bench_pokemons:
                                if pokemon.pokemon_type == target_type:
                                    if targets == "any":
                                        possible_targets.append(pokemon)
                                    elif targets == "brock_list":
                                        if pokemon.card_id in brock_list:
                                            possible_targets.append(pokemon)
                            if current_player.active_pokemon.pokemon_type == target_type:
                                if targets == "any":
                                    possible_targets.append(current_player.active_pokemon)
                                elif targets == "brock_list":
                                    if current_player.active_pokemon.card_id in brock_list:
                                        possible_targets.append(current_player.active_pokemon)
                            if coins_to_flip == 0:
                                get_chosen_card(possible_targets).equipped_energies[target_type] += 1
                            elif coins_to_flip == -1:
                                chosen_target = get_chosen_card(possible_targets)
                                while True:
                                    if random.choice([True, False]):
                                        chosen_target.equipped_energies[target_type] += 1
                                    else:
                                        break
                            else:
                                for i in range(coins_to_flip):
                                    if random.choice([True, False]):
                                        get_chosen_card(possible_targets).equipped_energies[target_type] += 1

                        elif trainer.effect == "bonus_damage":
                            bonus_damage_effect = (trainer.special_values[0], trainer.special_values[1])

                        elif trainer.effect == "send_active_to_hand":
                            coins_to_flip = trainer.special_values[0]
                            targets = trainer.special_values[1]
                            restrictions = trainer.special_values[2]
                            if coins_to_flip == 0:
                                if targets == "ally":
                                    if restrictions == "any" or (restrictions == "koga_list" and current_player.active_pokemon.card_id in koga_list):
                                        current_player.active_pokemon.reset()
                                        current_player.cards_in_hand.append(current_player.active_pokemon)
                                        current_player.active_pokemon = get_chosen_card(current_player.bench_pokemons)
                                        current_player.bench_pokemons.remove(current_player.active_pokemon)

                                elif targets == "enemy":
                                    if restrictions == "any" or (restrictions == "koga_list" and opponent.active_pokemon.card_id in koga_list):

                                        opponent.active_pokemon.reset()
                                        opponent.cards_in_hand.append(opponent.active_pokemon)
                                        opponent.active_pokemon = get_chosen_card(opponent.bench_pokemons)
                                        opponent.bench_pokemons.remove(opponent.active_pokemon)

                            elif coins_to_flip == 1:
                                if random.choice([True, False]):
                                    if targets == "ally":
                                        if restrictions == "any" or (
                                                restrictions == "koga_list" and current_player.active_pokemon.card_id in koga_list):
                                            current_player.active_pokemon.reset()
                                            current_player.cards_in_hand.append(current_player.active_pokemon)
                                            current_player.active_pokemon = get_chosen_card(current_player.bench_pokemons)
                                            current_player.bench_pokemons.remove(current_player.active_pokemon)

                                    elif targets == "enemy":
                                        if restrictions == "any" or (
                                                restrictions == "koga_list" and opponent.active_pokemon.card_id in koga_list):
                                            opponent.active_pokemon.hiding = False
                                            opponent.active_pokemon.damage_nerf = 0
                                            opponent.active_pokemon.effect_status = []
                                            opponent.active_pokemon.turn_since_placement = 1
                                            opponent.equipped_energies = {'fire': 0, 'water': 0, 'rock': 0, 'grass': 0,
                                                                          'electric': 0, 'psychic': 0, 'dark': 0,
                                                                          'metal': 0, 'dragon': 0, 'fairy': 0}
                                            opponent.active_pokemon.current_hp = opponent.active_pokemon.max_hp
                                            opponent.cards_in_hand.append(opponent.active_pokemon)
                                            opponent.active_pokemon = get_chosen_card(opponent.bench_pokemons)
                                            opponent.bench_pokemons.remove(opponent.active_pokemon)

                            else:
                                raise ValueError("Invalid value for coins_to_flip ?")

                        elif trainer.effect == "switch_active":
                            target = trainer.special_values[0]
                            who_choses_new = trainer.special_values[1]
                            if target == "enemy":
                                if who_choses_new == "opponent":
                                    current_active_pokemon = opponent.active_pokemon
                                    opponent.active_pokemon.hiding = False
                                    opponent.active_pokemon = get_chosen_card(opponent.bench_pokemons, "opponent")
                                    opponent.bench_pokemons.remove(opponent.active_pokemon)
                                    opponent.bench_pokemons.append(current_active_pokemon)

                                elif who_choses_new == "self":
                                    current_active_pokemon = opponent.active_pokemon
                                    opponent.active_pokemon.hiding = False
                                    opponent.active_pokemon = get_chosen_card(opponent.bench_pokemons)
                                    opponent.bench_pokemons.remove(opponent.active_pokemon)
                                    opponent.bench_pokemons.append(current_active_pokemon)

                            elif target == "ally":
                                if who_choses_new == "opponent":
                                    current_active_pokemon = current_player.active_pokemon
                                    current_player.active_pokemon.hiding = False
                                    current_player.active_pokemon = get_chosen_card(current_player.bench_pokemons,
                                                                                    "opponent")
                                    current_player.bench_pokemons.remove(current_player.active_pokemon)
                                    current_player.bench_pokemons.append(current_active_pokemon)

                                elif who_choses_new == "self":
                                    current_active_pokemon = current_player.active_pokemon
                                    current_player.active_pokemon.hiding = False
                                    current_player.active_pokemon = get_chosen_card(current_player.bench_pokemons)
                                    current_player.bench_pokemons.remove(current_player.active_pokemon)
                                    current_player.bench_pokemons.append(current_active_pokemon)

                        elif trainer.effect == "move_all_energy_to_active":
                            target_type = trainer.special_values[0]
                            for pokemon in current_player.bench_pokemons:
                                for energy_type, energy_amount in pokemon.equipped_energies.items():
                                    if energy_amount > 0 and energy_type == target_type:
                                        current_player.active_pokemon.equipped_energies[target_type] += energy_amount
                                        pokemon.equipped_energies[target_type] = 0
                        current_player.cards_in_hand.remove(chosen_card)
                        self.played_trainer_this_turn = True

                    elif chosen_card.card_type == "item":
                        chosen_card: Item
                        item = chosen_card
                        if item.effect == "heal":
                            targets = item.special_values[1]
                            heal_amount = item.special_values[0]
                            if targets == "active":
                                current_player.active_pokemon.current_hp += heal_amount

                            elif targets == "bench":
                                possible_targets = []
                                for pokemon in current_player.bench_pokemons:
                                    if pokemon.current_hp + heal_amount <= pokemon.max_hp:
                                        possible_targets.append(pokemon)
                                get_chosen_card(possible_targets).current_hp += heal_amount

                            elif targets == "any":
                                possible_targets = []
                                if current_player.active_pokemon.current_hp + heal_amount <= current_player.active_pokemon.max_hp:
                                    possible_targets.append(current_player.active_pokemon)
                                for pokemon in current_player.bench_pokemons:
                                    if pokemon.current_hp + heal_amount <= pokemon.max_hp:
                                        possible_targets.append(pokemon)
                                get_chosen_card(possible_targets).current_hp += heal_amount

                        elif item.effect == "retreat_reduced_cost":
                            retreat_cost_reduction = item.special_values[0]

                        elif item.effect == "opponent_reveal_hand":
                            # todo
                            pass

                        elif item.effect == "look_at_deck":
                            # todo
                            pass

                        elif item.effect == "find_random_pokemon_at_stage":
                            stage = item.special_values[0]
                            amount = item.special_values[1]
                            pokemons_at_stage = []
                            for card in current_player.remaining_cards:
                                if card.card_type == "pokemon" and card.stage == stage:
                                    pokemons_at_stage.append(card)
                            for i in range(amount):
                                if len(pokemons_at_stage) == 0 or len(current_player.cards_in_hand) > 9:
                                    break
                                random_card = random.choice(pokemons_at_stage)
                                current_player.cards_in_hand.append(random_card)
                                current_player.remaining_cards.remove(random_card)

                        elif item.effect == "shuffle_hand_and_draw":
                            cards_to_draw = item.special_values[0]
                            target = item.special_values[1]

                            if target == "enemy":
                                for i in range(len(opponent.cards_in_hand)):
                                    random_index = random.randint(0, len(opponent.remaining_cards) - 1)

                                    opponent.remaining_cards.insert(random_index, opponent.cards_in_hand.pop(0))
                                opponent.draw(cards_to_draw)
                            else:
                                for i in range(len(current_player.cards_in_hand)):
                                    random_index = random.randint(0, len(current_player.remaining_cards) - 1)
                                    current_player.remaining_cards.insert(random_index,
                                                                          current_player.cards_in_hand.pop(0))
                                current_player.draw(cards_to_draw)
                        current_player.cards_in_hand.remove(chosen_card)


            for bench_pokemon in current_player.bench_pokemons:
                bench_pokemon.turn_since_placement += 1
            if current_player.active_pokemon:
                current_player.active_pokemon.turn_since_placement += 1


            if ((not current_player.active_pokemon and not current_player.bench_pokemons) and (not opponent.active_pokemon and not opponent.bench_pokemons)):
                self.result = None
                break
            if not current_player.active_pokemon and not current_player.bench_pokemons:
                self.result = opponent
                break
            if not opponent.active_pokemon and not opponent.bench_pokemons:
                self.result = current_player
                break
            self.current_player = 1 if self.current_player == 2 else 2
            if attack_prevention[1] == current_player:
                attack_prevention = (False, None)
            if supporter_prevention[1] == current_player:
                supporter_prevention = (False, None)
            if retreat_prevention[1] == current_player:
                retreat_prevention = (False, None)
            if shield[1] == current_player:
                shield = (0, None)
            opponent.active_pokemon.hiding = False
            retreat_cost_reduction = 0
            for pokemon in opponent.bench_pokemons + [opponent.active_pokemon]:
                pokemon.used_ability_this_turn = False
                if "asleep" in pokemon.effect_status:
                    if random.choice([True, False]):
                        pokemon.effect_status.remove("asleep")
                if "poisoned" in pokemon.effect_status:
                    pokemon.current_hp -= 10
                    if pokemon.current_hp <= 0:
                        if 'ex' in pokemon.stage:
                            current_player.points += 2
                        else:
                            current_player.points += 1
                        if pokemon in opponent.bench_pokemons:
                            opponent.bench_pokemons.remove(pokemon)
                        elif pokemon == opponent.active_pokemon:
                            if not opponent.bench_pokemons:
                                self.result = current_player
                                break
                            else:
                                opponent.active_pokemon = get_chosen_card(opponent.bench_pokemons)
                                opponent.bench_pokemons.remove(opponent.active_pokemon)

                elif "super_poisoned" in pokemon.effect_status:
                    pokemon.current_hp -= 20
                    if pokemon.current_hp <= 0:
                        if 'ex' in pokemon.stage:
                            current_player.points += 2
                        else:
                            current_player.points += 1
                        if pokemon in opponent.bench_pokemons:
                            opponent.bench_pokemons.remove(pokemon)
                        elif pokemon == opponent.active_pokemon:
                            if not opponent.bench_pokemons:
                                self.result = current_player
                                break
                            else:
                                opponent.active_pokemon = get_chosen_card(opponent.bench_pokemons)
                                opponent.bench_pokemons.remove(opponent.active_pokemon)
            for pokemon in current_player.bench_pokemons + [current_player.active_pokemon]:
                pokemon.used_ability_this_turn = False
                if "asleep" in pokemon.effect_status:
                    if random.choice([True, False]):
                        pokemon.effect_status.remove("asleep")
                elif "paralyzed" in pokemon.effect_status:
                    pokemon.effect_status.remove("paralyzed")
                if "poisoned" in pokemon.effect_status:
                    pokemon.current_hp -= 10
                    if pokemon.current_hp <= 0:
                        if 'ex' in pokemon.stage:
                            opponent.points += 2
                        else:
                            opponent.points += 1
                        if pokemon in current_player.bench_pokemons:
                            current_player.bench_pokemons.remove(pokemon)
                        elif pokemon == current_player.active_pokemon:
                            if not current_player.bench_pokemons:
                                self.result = current_player
                                break
                            else:
                                current_player.active_pokemon = get_chosen_card(current_player.bench_pokemons)
                                current_player.bench_pokemons.remove(current_player.active_pokemon)

                elif "super_poisoned" in pokemon.effect_status:
                    pokemon.current_hp -= 20
                    if pokemon.current_hp <= 0:
                        if 'ex' in pokemon.stage:
                            opponent.points += 2
                        else:
                            opponent.points += 1
                        if pokemon in current_player.bench_pokemons:
                            current_player.bench_pokemons.remove(pokemon)
                        elif pokemon == current_player.active_pokemon:
                            if not current_player.bench_pokemons:
                                self.result = current_player
                                break
                            else:
                                current_player.active_pokemon = get_chosen_card(current_player.bench_pokemons)
                                current_player.bench_pokemons.remove(current_player.active_pokemon)

            if current_player.points >= 3:
                if opponent.points >= 3:
                    if current_player.points > opponent.points:
                        self.result = current_player
                    elif current_player.points < opponent.points:
                        self.result = opponent
                    else:
                        self.result = None
                else:
                    self.result = current_player
                break
            if opponent.points >= 3:
                self.result = opponent
                break
        return self.result

    def get_playable_cards(self, current_player, opponent, retreat_cost_reduction= 0, attack_prevention=None, retreat_prevention=None):
        playable_cards = []
        for card in current_player.cards_in_hand:
            if card.card_type == "pokemon":
                if len(current_player.bench_pokemons) < 3 or not current_player.active_pokemon:
                    if card.stage == 'basic' or card.stage == 'basic_ex':
                        playable_cards.append(card)
                    else:
                        pre_evolution = card.pre_evolution_name
                        pre_evolution_on_bench_or_active = False
                        for bench_pokemon in current_player.bench_pokemons:
                            # if name is same and stage doesn't contain "ex"
                            if bench_pokemon.name == pre_evolution and "ex" not in bench_pokemon.stage and bench_pokemon.turn_since_placement > 1:
                                pre_evolution_on_bench_or_active = True
                                break
                        if current_player.active_pokemon and current_player.active_pokemon.name == pre_evolution and "ex" not in current_player.active_pokemon.stage and current_player.active_pokemon.turn_since_placement > 1:
                            pre_evolution_on_bench_or_active = True
                        if pre_evolution_on_bench_or_active:
                            playable_cards.append(card)
            elif card.card_type == "trainer":
                if not self.played_trainer_this_turn and self.conditions_are_met(card, "trainer", current_player,
                                                                                 opponent):
                    playable_cards.append(card)
            elif card.card_type == "item":
                if self.conditions_are_met(card, "item", current_player, opponent):
                    playable_cards.append(card)
        for card in current_player.bench_pokemons + [current_player.active_pokemon]:
            if card:
                if self.conditions_are_met(card, "pokemon", current_player, opponent, retreat_cost_reduction, attack_prevention, retreat_prevention):
                    playable_cards.append(card)
        return playable_cards

    def conditions_are_met(self, card, card_type, player, opponent, retreat_cost_reduction= 0, attack_prevention=None, retreat_prevention=None):
        if card_type == "trainer":
            if card.effect == "heal":
                target_type = card.special_values[1]
                heal_amount = card.special_values[0]
                targets = card.special_values[2]
                check_bench = False
                check_active = False
                if targets == "any":
                    check_bench = True
                    check_active = True
                elif targets == "active":
                    check_active = True
                elif targets == "bench":
                    check_bench = True
                # check if any pokemon on either bench or active has the type
                if check_bench:
                    for pokemon in player.bench_pokemons:
                        if pokemon.pokemon_type == target_type and pokemon.current_hp + heal_amount <= pokemon.max_hp:
                            return True
                if check_active:
                    if player.active_pokemon.pokemon_type == target_type and player.active_pokemon.current_hp + heal_amount <= player.active_pokemon.max_hp:
                        return True
            elif card.effect == "draw":
                amount_draw = card.special_values[0]
                if len(player.cards_in_hand) + amount_draw <= 10:
                    return True
            elif card.effect == "energy_bonus":
                target_type = card.special_values[1]
                targets = card.special_values[2]
                for pokemon in player.bench_pokemons:
                    if pokemon.pokemon_type == target_type:
                        if targets == "any":
                            return True
                        elif targets == "brock_list":
                            if pokemon.card_id in brock_list:
                                return True
                if player.active_pokemon.pokemon_type == target_type:
                    if targets == "any":
                        return True
                    elif targets == "brock_list":
                        if player.active_pokemon.card_id in brock_list:
                            return True
            elif card.effect == "bonus_damage":
                restrictions = card.special_values[1]
                if restrictions == "any":
                    return True
                elif restrictions == "blaine_list":
                    for pokemon in player.bench_pokemons:
                        if pokemon.card_id in blaine_list:
                            return True
                    if player.active_pokemon.card_id in blaine_list:
                        return True
            elif card.effect == "send_active_to_deck":
                targets = card.special_values[1]
                restrictions = card.special_values[2]
                if restrictions == "any":
                    if targets == "ally":
                        return len(player.bench_pokemons) > 0
                    elif targets == "enemy":
                        return len(opponent.bench_pokemons) > 0
            elif card.effect == "send_active_to_hand":
                target = card.special_values[1]
                restrictions = card.special_values[2]
                if restrictions == "any":
                    if target == "ally":
                        return len(player.cards_in_hand) < 10
                    elif target == "enemy":
                        return len(opponent.cards_in_hand) < 10
                elif restrictions == "koga_list":
                    if target == "ally":
                        if player.active_pokemon.card_id in koga_list:
                            return len(player.cards_in_hand) < 10
                    elif target == "enemy":
                        if opponent.active_pokemon.card_id in koga_list:
                            return len(opponent.cards_in_hand) < 10

            elif card.effect == "switch_active":
                target = card.special_values[0]
                if target == "enemy":
                    return len(opponent.bench_pokemons) > 0
                elif target == "ally":
                    return len(player.bench_pokemons) > 0
                else:
                    raise ValueError("Invalid target for switch_active")
            elif card.effect == "move_all_energy_to_active":
                target_type = card.special_values[0]
                restrictions = card.special_values[1]
                for pokemon in player.bench_pokemons:
                    for energy_type, energy_amount in pokemon.equipped_energies.items():
                        if energy_amount > 0 and energy_type == target_type:
                            if restrictions == "surge_list":
                                if player.active_pokemon.card_id in surge_list:
                                    return True
                            elif restrictions == "any":
                                return True
        elif card_type == "item":
            if card.effect == "heal":
                heal_amount = card.special_values[0]
                target_type = card.special_values[1]
                for pokemon in player.bench_pokemons:
                    if (
                            target_type == "any" or pokemon.pokemon_type == target_type) and pokemon.current_hp + heal_amount <= pokemon.max_hp:
                        return True
                if (
                        target_type == "any" or player.active_pokemon.pokemon_type == target_type) and player.active_pokemon.current_hp + heal_amount <= player.active_pokemon.max_hp:
                    return True
            elif card.effect == "retreat_reduced_cost":
                return True
            elif card.effect == "opponent_reveal_hand":
                return True
            elif card.effect == "look_at_deck":
                return True
            elif card.effect == "find_random_pokemon_at_stage":
                target_stage = card.special_values[0]
                # check if there's at least 1 pokemon in the deck of the target stage
                for card in player.remaining_cards:
                    if card.card_type == "pokemon" and card.stage == target_stage:
                        return True
            elif card.effect == "shuffle_hand_and_draw":
                return True
        elif card_type == "pokemon":
            if card == player.active_pokemon and sum(card.equipped_energies.values()) >= card.retreat_cost-retreat_cost_reduction and "paralyzed" not in card.effect_status and "asleep" not in card.effect_status and len(player.bench_pokemons) > 0 and retreat_prevention[1] != player:
                return True
            if card == player.active_pokemon and "paralyzed" not in card.effect_status and "asleep" not in card.effect_status and attack_prevention[1] != player:
                for attack_id in card.attack_ids:
                    has_energies = True
                    attack = all_attacks[attack_id]
                    energies_used = 0
                    for energy_type, cost in attack.energy_cost.items():
                        if energy_type != "normal":
                            if card.equipped_energies[energy_type] < cost:
                                has_energies = False
                                break
                            else:
                                energies_used += cost
                    if has_energies:
                        if attack.energy_cost["normal"] > 0:
                            if sum(card.equipped_energies.values()) - energies_used >= attack.energy_cost["normal"]:
                                return True

            if card.ability_id:
                is_ability_conditions_met = self.is_ability_conditions_met(card, player, opponent)
                if is_ability_conditions_met:
                    return True

    def is_ability_conditions_met(self, card, player, opponent):
        ability = all_abilities[card.ability_id]
        if ability.effect_type == "self_discard":
            return True
        if ability.amount_of_times == "once" and not card.used_ability_this_turn:
            if ability.effect_type == "heal_all":
                heal_amount = ability.special_values[0]
                for pokemon in player.bench_pokemons:
                    if pokemon.current_hp + heal_amount <= pokemon.max_hp:
                        return True
                if player.active_pokemon.current_hp + heal_amount <= player.active_pokemon.max_hp:
                    return True
            elif ability.effect_type == "switch_active":
                if ability.ability_id == 2 and not player.active_pokemon == card:
                    return False
                target_player = ability.special_values[0]
                if target_player == "opponent":
                    return len(opponent.bench_pokemons) > 0
                elif target_player == "self":
                    return len(player.bench_pokemons) > 0
            elif ability.effect_type == "damage_enemy":
                targets = ability.special_values[0]
                if targets == "active":
                    return opponent.active_pokemon is not None
                elif targets == "bench":
                    return len(opponent.bench_pokemons) > 0
                elif targets == "any":
                    return opponent.active_pokemon is not None or len(opponent.bench_pokemons) > 0
                elif ability.effect_type == "gain_energy":
                    target = ability.special_values[0]
                    target_type = ability.special_values[2]
                    if target_type == "any":
                        return True
                    else:
                        if target == "active":
                            return player.active_pokemon.pokemon_type == target_type
                        else:
                            return True
                elif ability.effect_type == "sleep":
                    return opponent.active_pokemon is not None
                elif ability.effect_type == "poison":
                    from_where_pokemon_must_be = ability.special_values[1]
                    target = ability.special_values[2]
                    if from_where_pokemon_must_be == "active":
                        if player.active_pokemon == card:
                            if target == "opponent":
                                return opponent.active_pokemon is not None
                            elif target == "bench":
                                return len(opponent.bench_pokemons) > 0
                            elif target == "any":
                                return opponent.active_pokemon is not None or len(opponent.bench_pokemons) > 0
                    elif from_where_pokemon_must_be == "any":
                        if target == "opponent":
                            return opponent.active_pokemon is not None
                        elif target == "bench":
                            return len(opponent.bench_pokemons) > 0
                        elif target == "any":
                            return opponent.active_pokemon is not None or len(opponent.bench_pokemons) > 0
                    else:
                        if card in player.bench_pokemons:
                            if target == "opponent":
                                return opponent.active_pokemon is not None
                            elif target == "bench":
                                return len(opponent.bench_pokemons) > 0
                            elif target == "any":
                                return opponent.active_pokemon is not None or len(opponent.bench_pokemons) > 0
                elif ability.effect_type == "look_at_deck":
                    return True

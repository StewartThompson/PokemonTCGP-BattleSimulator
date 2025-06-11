import random
from typing import List, Dict, Optional, Tuple, Union, TYPE_CHECKING

from moteur.cartes.pokemon import Pokemon
from moteur.player import Player

if TYPE_CHECKING:
    from moteur.core.match import Match

class CardEffectHandler:
    """Handles effects for abilities, attacks, trainers, and items."""
    def __init__(self, match: 'Match'):
        self.match = match
        self.ability_handlers = {
            "heal_all": self.handle_heal_all,
            "self_discard": self.handle_self_discard,
            "switch_active": self.handle_switch_active,
            "damage_enemy": self.handle_damage_enemy,
            "gain_energy": self.handle_gain_energy,
            "sleep": self.handle_sleep,
            "poison": self.handle_poison,
            "look_at_deck": self.handle_look_at_deck,
            "energy_double": self.handle_energy_double,
            "move_energy": self.handle_move_energy_ability,
            "prevent_evolution": self.handle_prevent_evolution,
            "thorns": self.handle_thorns,
            "retreat_cost_reduction": self.handle_retreat_cost_reduction,
            "status_immunity": self.handle_status_immunity,
            "checkup": self.handle_checkup_damage,
            "bonus_damage_arceus": self.handle_bonus_damage_arceus,
            "retreat_cost_arceus": self.handle_retreat_cost_arceus,
            "energy_cost_reduction_arceus": self.handle_energy_cost_reduction_arceus,
            "checkup_damage_active": self.handle_checkup_damage_active,
            "retreat_cost_reduction_bench": self.handle_retreat_cost_reduction_bench,
            "fabled_luster": self.handle_fabled_luster,
        }
        self.attack_handlers = {
            "self_heal": self.handle_self_heal,
            "switch_active": self.handle_switch_active_attack,
            "find_random_typed_pokemon_in_deck": self.handle_find_pokemon,
            "poison": self.handle_poison_attack,
            "sum": self.handle_sum,
            "multiply": self.handle_multiply,
            "bonus_energy": self.handle_bonus_energy,
            "discard_energy": self.handle_discard_energy,
            "prevent_attack": self.handle_prevent_attack,
            "damage_self": self.handle_damage_self,
            "bonus_energy_flip": self.handle_bonus_energy_flip,
            "bonus_damage_with_bonus_energy": self.handle_bonus_damage_energy,
            "block_supporter_next_turn": self.handle_block_supporter,
            "shield": self.handle_shield_attack,
            "bonus_damage_foreach_enemy_energy": self.handle_bonus_energy_count,
            "hiding": self.handle_hiding,
            "reduce_enemy_damage": self.handle_reduce_damage,
            "damage_target": self.handle_damage_target,
            "discard_opponent_energy": self.handle_discard_opponent_energy,
            "paralyze": self.handle_paralyze,
            "damaged_benched_pokemon": self.handle_damage_benched,
            "bonus_damage_if_damaged": self.handle_bonus_if_damaged,
            "multiply_benched": self.handle_multiply_benched,
            "either_bonus_damage_or_self_damage": self.handle_either_bonus_or_damage,
            "switch_self_with_benched": self.handle_switch_self_benched,
            "lifesteal": self.handle_lifesteal,
            "no_retreat": self.handle_no_retreat,
            "place_pokemon_on_bench": self.handle_place_pokemon,
            "bonus_specific_pokemon_benched": self.handle_bonus_specific_benched,
            "bonus_if_poisoned": self.handle_bonus_if_poisoned,
            "gain_self_energy": self.handle_gain_self_energy,
            "opponent_reveal_hand": self.handle_opponent_reveal_hand,
            "sleep_attack": self.handle_sleep_attack,
            "draw_attack": self.handle_draw_attack,
            "discard_from_hand": self.handle_discard_from_hand,
            "send_active_to_deck": self.handle_send_active_to_deck,
            "discard_energy_and_damage_target": self.handle_discard_energy_and_damage_target,
            "discard_random_energy_all": self.handle_discard_random_energy_all,
            "bonus_damage_to_ex": self.handle_bonus_damage_to_ex_attack,
            "bonus_damage_if_knocked_out": self.handle_bonus_damage_if_knocked_out,
            "shuffle_hand_draw": self.handle_shuffle_hand_draw_attack,
            "copy_attack": self.handle_copy_attack_effect,
            "coin_multiply": self.handle_coin_multipy,
            "poison_enhanced": self.handle_poison_enhanced,
            "prevent_next_turn_attack": self.handle_prevent_next_turn_attack,
            "sleep_self": self.handle_sleep_self,
            "burn": self.handle_burn,
            "bonus_type_damage": self.handle_bonus_type_damage,
            "damage_random_benched": self.handle_damage_random_benched,
            "multiply_with_condition": self.handle_multiply_with_condition,
            "bonus_damage_with_tool": self.handle_bonus_damage_with_tool,
            "multiply_bonus": self.handle_multiply_bonus,
            "send_active_to_hand": self.handle_send_active_to_hand,
            "bonus_damage_per_damage": self.handle_bonus_damage_per_damage,
            "discard_energy_and_damage_benched": self.handle_discard_energy_and_damage_benched,
            "attach_energy_to_benched": self.handle_attach_energy_to_benched,
            "next_turn_damage_boost": self.handle_next_turn_damage_boost,
            "conditional_energy_attach": self.handle_conditional_energy_attach,
            "confuse": self.handle_confuse,
            "coin_either_bonus_or_self_damage": self.handle_coin_either_bonus_or_self_damage,
            "coin_bonus": self.handle_coin_bonus,
            "rage_damage": self.handle_rage_damage,
        }
        self.trainer_handlers = {
            "return_to_hand": self.handle_return_to_hand,
            "damage_reduction": self.handle_damage_reduction,
            "retreat_cost_reduction": self.handle_retreat_cost_reduction,
            "switch_opponent_damaged": self.handle_switch_opponent_damaged,
            "search_deck": self.handle_search_deck,
            "bonus_damage": self.handle_bonus_damage,
            "attach_energy_from_discard": self.handle_attach_energy_from_discard,
            "move_energy": self.handle_move_energy,
            "shuffle_opponent_hand": self.handle_shuffle_opponent_hand,
            "heal": self.handle_heal,
            "retrieve_from_discard": self.handle_retrieve_from_discard,
            "energy_cost_reduction": self.handle_energy_cost_reduction,
            "shuffle_hand_draw": self.handle_shuffle_hand_draw,
            "heal_and_remove_conditions": self.handle_heal_and_remove_conditions,
            "bonus_damage_to_ex": self.handle_bonus_damage_to_ex,
            "discard_energy_coin_flip": self.handle_discard_energy_coin_flip,
            "move_damage": self.handle_move_damage,
            "attach_energy_end_turn": self.handle_attach_energy_end_turn,
            "discard_all_tools": self.handle_discard_all_tools,
            "switch_opponent_benched": self.handle_switch_opponent_benched,
            "heal_all_and_discard_energy": self.handle_heal_all_and_discard_energy,
            "reveal_supporters": self.handle_reveal_supporters,
            "attach_random_energy": self.handle_attach_random_energy,
            "draw_cards": self.handle_draw_cards,
        }
        self.item_handlers = {
            "heal": self.handle_item_heal,
            "draw_basic_pokemon": self.handle_draw_basic_pokemon,
        }

    # Ability Handlers
    def handle_heal_all(self, player: Player, opponent: Player, ability, pokemon: Pokemon) -> None:
        heal_amount = ability.special_values[0]
        for p in player.all_pokemons():
            if p.current_hp + heal_amount <= p.max_hp:
                p.current_hp += heal_amount

    def handle_self_discard(self, player: Player, opponent: Player, ability, pokemon: Pokemon) -> None:
        if pokemon in player.bench_pokemons:
            player.bench_pokemons.remove(pokemon)
        elif pokemon == player.active_pokemon:
            player.active_pokemon = None
            self.match.check_game_end()

    def handle_switch_active(self, player: Player, opponent: Player, ability, pokemon: Pokemon) -> None:
        target, who_chooses = ability.special_values
        target_player = opponent if target == "enemy" else player
        chooser = opponent.agent if who_chooses == "opponent" else player.agent
        if target_player.bench_pokemons:
            current = target_player.active_pokemon
            new_active = chooser.get_chosen_card(target_player.bench_pokemons, self.match, f"choose_new_active_{target}")
            target_player.swap_active(new_active)

    def handle_damage_enemy(self, player: Player, opponent: Player, ability, pokemon: Pokemon) -> None:
        targets, damage_amount = ability.special_values
        target = self.match.select_target(player, opponent, targets, "damage_enemy")
        if target:
            self.match.apply_damage(target, damage_amount, player)

    def handle_gain_energy(self, player: Player, opponent: Player, ability, pokemon: Pokemon) -> None:
        target, energy_type, pokemon_type, amount = ability.special_values
        if target == "self":
            pokemon.equipped_energies[energy_type] += amount
        elif target == "active" and (pokemon_type == "any" or player.active_pokemon.pokemon_type == pokemon_type):
            player.active_pokemon.equipped_energies[energy_type] += amount
        elif target == "bench":
            targets = [p for p in player.bench_pokemons if p.pokemon_type == pokemon_type or pokemon_type == "any"]
            if targets:
                player.agent.get_chosen_card(targets, self.match, "gain_energy").equipped_energies[energy_type] += amount

    def handle_sleep(self, player: Player, opponent: Player, ability, pokemon: Pokemon) -> None:
        coins = ability.special_values[0]
        if coins == 0 or random.choice([True, False]):
            self.match.apply_status(opponent.active_pokemon, "asleep")

    def handle_poison(self, player: Player, opponent: Player, ability, pokemon: Pokemon) -> None:
        poison_damage, from_where, target = ability.special_values
        if (from_where == "active" and pokemon == player.active_pokemon) or (from_where == "bench" and pokemon in player.bench_pokemons):
            poison_type = "poisoned" if poison_damage == 10 else "super_poisoned"
            targets = self.match.get_targets(opponent, target, poison_type)
            if targets:
                chosen = player.agent.get_chosen_card(targets, self.match, "ability_poison") if target != "active" else opponent.active_pokemon
                self.match.apply_status(chosen, poison_type)

    def handle_look_at_deck(self, player: Player, opponent: Player, ability, pokemon: Pokemon) -> None:
        """Handle looking at the top card(s) of deck."""
        # Allow the player to look at the top cards of their deck
        # The actual implementation would involve showing cards to the player
        pass

    def handle_thorns(self, player: Player, opponent: Player, ability, pokemon: Pokemon) -> None:
        """Handle thorns abilities that deal damage back to attackers."""
        # This effect is handled in the apply_damage method when the Pokemon is attacked
        # The actual damage reflection logic should be implemented in the match's damage application
        pass

    def handle_retreat_cost_reduction(self, player: Player, opponent: Player, ability, pokemon: Pokemon) -> None:
        """Handle abilities that reduce retreat cost."""
        # This is a passive ability that affects retreat cost calculation
        # The actual implementation should be in the retreat cost calculation method
        pass

    def handle_status_immunity(self, player: Player, opponent: Player, ability, pokemon: Pokemon) -> None:
        """Handle abilities that provide immunity to status conditions."""
        # This is a passive ability that prevents status conditions
        # The actual implementation should be in the status application method
        pass

    def handle_checkup_damage(self, player: Player, opponent: Player, ability, pokemon: Pokemon) -> None:
        """Handle abilities that deal damage during Pokemon checkup."""
        damage_amount = ability.special_values[1] if len(ability.special_values) > 1 else 10
        target = ability.special_values[0] if ability.special_values else "active"
        
        if pokemon == player.active_pokemon and target == "active":
            self.match.apply_damage(opponent.active_pokemon, damage_amount, player)

    # Attack Handlers
    def handle_self_heal(self, attacker: Pokemon, defender: Pokemon, attack, player: Player, opponent: Player) -> int:
        heal_amount = attack.special_values[0]
        attacker.current_hp = min(attacker.current_hp + heal_amount, attacker.max_hp)
        return attack.damage

    def handle_switch_active_attack(self, attacker: Pokemon, defender: Pokemon, attack, player: Player, opponent: Player) -> int:
        target, who_chooses = attack.special_values
        target_player = opponent if target == "enemy" else player
        chooser = opponent.agent if who_chooses == "opponent" else player.agent
        if target_player.bench_pokemons:
            current = target_player.active_pokemon
            new_active = chooser.get_chosen_card(target_player.bench_pokemons, self.match, f"choose_new_active_{target}")
            target_player.swap_active(new_active)
        return attack.damage

    def handle_find_pokemon(self, attacker: Pokemon, defender: Pokemon, attack, player: Player, opponent: Player) -> int:
        target_type, amount = attack.special_values
        if len(player.cards_in_hand) + amount <= 10:
            pokemons = [p for p in player.remaining_cards if p.card_type == "pokemon" and p.pokemon_type == target_type]
            random.shuffle(pokemons)
            for _ in range(min(amount, len(pokemons))):
                card = pokemons.pop()
                player.cards_in_hand.append(card)
                player.remaining_cards.remove(card)
        return attack.damage

    def handle_poison_attack(self, attacker: Pokemon, defender: Pokemon, attack, player: Player, opponent: Player) -> int:
        poison_damage = attack.special_values[0]
        poison_type = "poisoned" if poison_damage == 10 else "super_poisoned"
        if not defender.hiding and poison_type not in defender.effect_status:
            self.match.apply_status(defender, poison_type)
        return attack.damage

    def handle_sum(self, attacker: Pokemon, defender: Pokemon, attack, player: Player, opponent: Player) -> int:
        bonus_damage, coins, applies = attack.special_values
        yes_count = sum(1 for _ in range(coins) if random.choice([True, False]))
        return attack.damage + (bonus_damage * yes_count if applies == "foreach" else bonus_damage if yes_count == coins else 0)

    def handle_multiply(self, attacker: Pokemon, defender: Pokemon, attack, player: Player, opponent: Player) -> int:
        coins = attack.special_values[0]
        yes_count = sum(1 for _ in range(coins) if random.choice([True, False]))
        return attack.damage * yes_count

    def handle_bonus_energy(self, attacker: Pokemon, defender: Pokemon, attack, player: Player, opponent: Player) -> int:
        amount, target, energy_type, pokemon_type = attack.special_values
        for _ in range(amount):
            if target == "active" and (pokemon_type == "any" or player.active_pokemon.pokemon_type == pokemon_type):
                player.active_pokemon.equipped_energies[energy_type] += 1
            elif target == "bench":
                targets = [p for p in player.bench_pokemons if p.pokemon_type == pokemon_type or pokemon_type == "any"]
                if targets:
                    player.agent.get_chosen_card(targets, self.match, "gain_energy").equipped_energies[energy_type] += 1
        return attack.damage

    def handle_discard_energy(self, attacker: Pokemon, defender: Pokemon, attack, player: Player, opponent: Player) -> int:
        energy_type, amount = attack.special_values
        if amount == "all":
            amount = sum(attacker.equipped_energies.values())
        if energy_type == "any":
            energies = [et for et, qty in attacker.equipped_energies.items() if qty > 0]
            for _ in range(min(amount, len(energies))):
                et = random.choice(energies)
                attacker.equipped_energies[et] -= 1
                if attacker.equipped_energies[et] == 0:
                    energies.remove(et)
        else:
            attacker.equipped_energies[energy_type] = max(0, attacker.equipped_energies[energy_type] - amount)
        return attack.damage

    def handle_prevent_attack(self, attacker: Pokemon, defender: Pokemon, attack, player: Player, opponent: Player) -> int:
        coins = attack.special_values[0]
        if coins == 0 or random.choice([True, False]):
            self.match.attack_prevention = (True, opponent)
        return attack.damage

    def handle_damage_self(self, attacker: Pokemon, defender: Pokemon, attack, player: Player, opponent: Player) -> int:
        amount = attack.special_values[0]
        self.match.apply_damage(attacker, amount, opponent)
        return attack.damage

    def handle_bonus_energy_flip(self, attacker: Pokemon, defender: Pokemon, attack, player: Player, opponent: Player) -> int:
        coins, target, energy_type, pokemon_type = attack.special_values
        for _ in range(coins):
            if random.choice([True, False]):
                if target == "active" and (pokemon_type == "any" or player.active_pokemon.pokemon_type == pokemon_type):
                    player.active_pokemon.equipped_energies[energy_type] += 1
                elif target == "bench":
                    targets = [p for p in player.bench_pokemons if p.pokemon_type == pokemon_type or pokemon_type == "any"]
                    if targets:
                        player.agent.get_chosen_card(targets, self.match, "gain_energy").equipped_energies[energy_type] += 1
        return attack.damage

    def handle_bonus_damage_energy(self, attacker: Pokemon, defender: Pokemon, attack, player: Player, opponent: Player) -> int:
        needed, energy_type, bonus = attack.special_values
        if attacker.equipped_energies[energy_type] >= needed + attack.energy_cost.get(energy_type, 0):
            return attack.damage + bonus
        return attack.damage

    def handle_block_supporter(self, attacker: Pokemon, defender: Pokemon, attack, player: Player, opponent: Player) -> int:
        self.match.supporter_prevention = (True, opponent)
        return attack.damage

    def handle_shield_attack(self, attacker: Pokemon, defender: Pokemon, attack, player: Player, opponent: Player) -> int:
        self.match.shield = (attack.special_values[0], opponent)
        return attack.damage

    def handle_bonus_energy_count(self, attacker: Pokemon, defender: Pokemon, attack, player: Player, opponent: Player) -> int:
        additional = attack.special_values[0] * sum(defender.equipped_energies.values())
        return attack.damage + additional

    def handle_hiding(self, attacker: Pokemon, defender: Pokemon, attack, player: Player, opponent: Player) -> int:
        coins = attack.special_values[0]
        if coins == 0 or random.choice([True, False]):
            attacker.hiding = True
        return attack.damage

    def handle_reduce_damage(self, attacker: Pokemon, defender: Pokemon, attack, player: Player, opponent: Player) -> int:
        self.match.damage_reduction = (attack.special_values[0], player)
        return attack.damage

    def handle_damage_target(self, attacker: Pokemon, defender: Pokemon, attack, player: Player, opponent: Player) -> int:
        targets, damage = attack.special_values
        target = self.match.select_target(player, opponent, targets, "attack_damage_target")
        if target:
            self.match.apply_damage(target, damage, player)
        return attack.damage

    def handle_discard_opponent_energy(self, attacker: Pokemon, defender: Pokemon, attack, player: Player, opponent: Player) -> int:
        energy_type, amount = attack.special_values
        if amount == "all" and defender.equipped_energies[energy_type] > 0:
            defender.equipped_energies[energy_type] = 0
        elif amount == "random":
            energies = [et for et, qty in defender.equipped_energies.items() if qty > 0]
            if energies:
                et = random.choice(energies)
                defender.equipped_energies[et] -= 1
        else:
            defender.equipped_energies[energy_type] = max(0, defender.equipped_energies[energy_type] - amount)
        return attack.damage

    def handle_paralyze(self, attacker: Pokemon, defender: Pokemon, attack, player: Player, opponent: Player) -> int:
        coins = attack.special_values[0]
        if coins == 0 or random.choice([True, False]):
            self.match.apply_status(defender, "paralyzed")
        return attack.damage

    def handle_damage_benched(self, attacker: Pokemon, defender: Pokemon, attack, player: Player, opponent: Player) -> int:
        damage, target = attack.special_values
        if target == "opponent" and opponent.bench_pokemons:
            for pokemon in opponent.bench_pokemons:
                self.match.apply_damage(pokemon, damage, player)
        elif target == "all" and (opponent.bench_pokemons or player.bench_pokemons):
            for pokemon in opponent.bench_pokemons + player.bench_pokemons:
                self.match.apply_damage(pokemon, damage, player)
        return attack.damage

    def handle_bonus_if_damaged(self, attacker: Pokemon, defender: Pokemon, attack, player: Player, opponent: Player) -> int:
        bonus = attack.special_values[0]
        if attacker.current_hp < attacker.max_hp:
            return attack.damage + bonus
        return attack.damage

    def handle_multiply_benched(self, attacker: Pokemon, defender: Pokemon, attack, player: Player, opponent: Player) -> int:
        # Handle different possible formats of special_values
        if len(attack.special_values) == 2:
            multiplier, target = attack.special_values
            # Ensure multiplier is an integer
            if isinstance(multiplier, str):
                try:
                    multiplier = int(multiplier)
                except ValueError:
                    # If conversion fails, default to 1
                    multiplier = 1
                    
            if target == "self":
                return attack.damage * (1 + len(player.bench_pokemons) * multiplier)
            return attack.damage * (1 + len(opponent.bench_pokemons) * multiplier)
        elif len(attack.special_values) == 1:
            # If only one value, assume it's the multiplier and target is opponent
            try:
                multiplier = int(attack.special_values[0])
            except (ValueError, TypeError):
                multiplier = 1
            return attack.damage * (1 + len(opponent.bench_pokemons) * multiplier)
        else:
            # Default case, just return the base damage
            return attack.damage

    def handle_either_bonus_or_damage(self, attacker: Pokemon, defender: Pokemon, attack, player: Player, opponent: Player) -> int:
        bonus, damage = attack.special_values
        action = player.agent.get_action(["bonus", "damage"], self.match, "choose_attack_option")
        if action == "bonus":
            return attack.damage + bonus
        self.match.apply_damage(attacker, damage, opponent)
        return attack.damage

    def handle_switch_self_benched(self, attacker: Pokemon, defender: Pokemon, attack, player: Player, opponent: Player) -> int:
        if player.bench_pokemons:
            new_active = player.agent.get_chosen_card(player.bench_pokemons, self.match, "choose_new_active_self")
            player.swap_active(new_active)
        return attack.damage

    def handle_lifesteal(self, attacker: Pokemon, defender: Pokemon, attack, player: Player, opponent: Player) -> int:
        return attack.damage  # The lifesteal effect is handled in the perform_attack method

    def handle_no_retreat(self, attacker: Pokemon, defender: Pokemon, attack, player: Player, opponent: Player) -> int:
        opponent.active_pokemon.can_retreat = False
        return attack.damage

    def handle_place_pokemon(self, attacker: Pokemon, defender: Pokemon, attack, player: Player, opponent: Player) -> int:
        if len(player.bench_pokemons) < self.match.MAX_BENCH_SIZE:
            pokemon_type = attack.special_values[0]
            matching_pokemons = [p for p in player.cards_in_hand if p.card_type == "pokemon" and 
                                 p.pokemon_type == pokemon_type and p.stage == "basic"]
            if matching_pokemons:
                choice = player.agent.get_chosen_card(matching_pokemons, self.match, "place_on_bench")
                
                # Find and remove the Pokemon from hand by matching properties
                removed = False
                for i, hand_card in enumerate(player.cards_in_hand):
                    if (hasattr(hand_card, 'card_id') and hasattr(choice, 'card_id') and 
                        hand_card.card_id == choice.card_id and 
                        hasattr(hand_card, 'name') and hasattr(choice, 'name') and 
                        hand_card.name == choice.name):
                        player.cards_in_hand.pop(i)
                        choice = hand_card  # Use the actual card from the hand
                        removed = True
                        break
                
                if not removed:
                    # Fallback: try to find by name and type
                    for i, hand_card in enumerate(player.cards_in_hand):
                        if (hasattr(hand_card, 'name') and hasattr(choice, 'name') and 
                            hand_card.name == choice.name and 
                            hasattr(hand_card, 'card_type') and hand_card.card_type == "pokemon"):
                            player.cards_in_hand.pop(i)
                            choice = hand_card  # Use the actual card from the hand
                            removed = True
                            break
                
                if not removed:
                    # Final fallback: try the original method
                    try:
                        player.cards_in_hand.remove(choice)
                    except ValueError:
                        # If we can't find it, just return without placing
                        return attack.damage
                
                player.bench_pokemons.append(choice)
        return attack.damage

    def handle_bonus_specific_benched(self, attacker: Pokemon, defender: Pokemon, attack, player: Player, opponent: Player) -> int:
        pokemon_name, bonus = attack.special_values
        for p in player.bench_pokemons:
            if p.name == pokemon_name:
                return attack.damage + bonus
        return attack.damage

    def handle_bonus_if_poisoned(self, attacker: Pokemon, defender: Pokemon, attack, player: Player, opponent: Player) -> int:
        bonus = attack.special_values[0]
        if "poisoned" in defender.effect_status or "super_poisoned" in defender.effect_status:
            return attack.damage + bonus
        return attack.damage

    def handle_gain_self_energy(self, attacker: Pokemon, defender: Pokemon, attack, player: Player, opponent: Player) -> int:
        energy_type, amount = attack.special_values
        attacker.equipped_energies[energy_type] += amount
        return attack.damage

    def handle_opponent_reveal_hand(self, attacker: Pokemon, defender: Pokemon, attack, player: Player, opponent: Player) -> int:
        # No actual implementation needed as the hand is always visible in this simulator
        return attack.damage

    def handle_sleep_attack(self, attacker: Pokemon, defender: Pokemon, attack, player: Player, opponent: Player) -> int:
        self.match.apply_status(defender, "asleep")
        return attack.damage

    def handle_draw_attack(self, attacker: Pokemon, defender: Pokemon, attack, player: Player, opponent: Player) -> int:
        amount = attack.special_values[0]
        for _ in range(amount):
            if player.remaining_cards:
                player.cards_in_hand.append(player.remaining_cards.pop())
        return attack.damage

    def handle_discard_from_hand(self, attacker: Pokemon, defender: Pokemon, attack, player: Player, opponent: Player) -> int:
        amount, method, card_type = attack.special_values
        cards_of_type = [c for c in opponent.cards_in_hand if c.card_type == card_type] if card_type != "any" else opponent.cards_in_hand
        
        if method == "random" and cards_of_type:
            for _ in range(min(amount, len(cards_of_type))):
                card = random.choice(cards_of_type)
                opponent.cards_in_hand.remove(card)
                opponent.discard_pile.append(card)
                cards_of_type.remove(card)
        return attack.damage

    def handle_send_active_to_deck(self, attacker: Pokemon, defender: Pokemon, attack, player: Player, opponent: Player) -> int:
        if random.choice([True, False]):
            active = opponent.active_pokemon
            opponent.active_pokemon = None
            
            # Insert active Pokémon back into deck
            opponent.remaining_cards.append(active)
            random.shuffle(opponent.remaining_cards)
            
            # Replace active if possible
            if opponent.bench_pokemons:
                new_active = opponent.agent.get_chosen_card(opponent.bench_pokemons, self.match, "choose_new_active_forced")
                opponent.bench_pokemons.remove(new_active)
                opponent.active_pokemon = new_active
                
            self.match.check_game_end()
        return attack.damage

    # Trainer Handlers
    def handle_return_to_hand(self, player, opponent, trainer, pokemon=None):
        pokemon_name, condition = trainer.special_values.split("|")
        if condition == "active" and player.active_pokemon and player.active_pokemon.name == pokemon_name:
            player.cards_in_hand.append(player.active_pokemon)
            player.active_pokemon = None
            if player.bench_pokemons:
                new_active = player.agent.get_chosen_card(player.bench_pokemons, self.match, "choose_new_active")
                player.bench_pokemons.remove(new_active)
                player.active_pokemon = new_active
        elif condition == "damaged":
            damaged_normals = [p for p in player.all_pokemons() if p.current_hp < p.max_hp and "normal" in p.types]
            if damaged_normals:
                target = player.agent.get_chosen_card(damaged_normals, self.match, "choose_damaged_normal")
                if target == player.active_pokemon:
                    player.active_pokemon = None
                else:
                    player.bench_pokemons.remove(target)
                player.cards_in_hand.append(target)

    def handle_damage_reduction(self, player, opponent, trainer, pokemon=None):
        amount, target_type, duration = trainer.special_values.split("|")
        amount = int(amount)
        if duration == "opponent_turn":
            self.match.turn_state.damage_reduction = (amount, target_type, player)

    def handle_retreat_cost_reduction(self, player, opponent, trainer, pokemon=None):
        amount, target, duration = trainer.special_values.split("|")
        amount = int(amount)
        if duration == "this_turn" and player.active_pokemon:
            player.active_pokemon.retreat_cost = max(0, player.active_pokemon.retreat_cost - amount)
            self.match.turn_state.retreat_cost_reduction = (player.active_pokemon, amount)

    def handle_switch_opponent_damaged(self, player, opponent, trainer, pokemon=None):
        damaged_pokemons = [p for p in opponent.all_pokemons() if p.current_hp < p.max_hp]
        if damaged_pokemons:
            target = player.agent.get_chosen_card(damaged_pokemons, self.match, "choose_opponent_damaged_pokemon")
            if target != opponent.active_pokemon:
                opponent.bench_pokemons.append(opponent.active_pokemon)
                opponent.active_pokemon = target
                opponent.bench_pokemons.remove(target)

    def handle_search_deck(self, player, opponent, trainer, pokemon=None):
        pokemon_names = trainer.special_values.split("|")[:-1]
        selection_type = trainer.special_values.split("|")[-1]
        matching_pokemons = [p for p in player.remaining_cards if p.card_type == "pokemon" and p.name in pokemon_names]
        if matching_pokemons:
            if selection_type == "random":
                chosen = random.choice(matching_pokemons)
            else:
                chosen = player.agent.get_chosen_card(matching_pokemons, self.match, "choose_pokemon_from_deck")
            player.cards_in_hand.append(chosen)
            player.remaining_cards.remove(chosen)
            random.shuffle(player.remaining_cards)

    def handle_bonus_damage(self, player, opponent, trainer, pokemon=None):
        amount, *pokemon_names = trainer.special_values.split("|")
        amount = int(amount)
        self.match.turn_state.bonus_damage_effect = (amount, pokemon_names)

    def handle_attach_energy_from_discard(self, player, opponent, trainer, pokemon=None):
        amount, energy_type, *pokemon_names = trainer.special_values.split("|")
        amount = int(amount)
        eligible_pokemons = [p for p in player.all_pokemons() if p.name in pokemon_names]
        if eligible_pokemons:
            target = player.agent.get_chosen_card(eligible_pokemons, self.match, "choose_pokemon_for_energy")
            energy_cards = [e for e in player.discard_pile if e.card_type == "energy" and energy_type in e.name][:amount]
            for energy in energy_cards:
                target.equipped_energies[energy_type] = target.equipped_energies.get(energy_type, 0) + 1
                player.discard_pile.remove(energy)

    def handle_move_energy(self, player, opponent, trainer, pokemon=None):
        if player.bench_pokemons and player.active_pokemon:
            source = player.agent.get_chosen_card(player.bench_pokemons, self.match, "choose_benched_pokemon")
            for energy_type, count in source.equipped_energies.items():
                if count > 0:
                    player.active_pokemon.equipped_energies[energy_type] = player.active_pokemon.equipped_energies.get(energy_type, 0) + 1
                    source.equipped_energies[energy_type] -= 1
                    break

    def handle_shuffle_opponent_hand(self, player, opponent, trainer, pokemon=None):
        remaining_points = self.match.WINNING_POINTS - opponent.prize_points
        opponent.remaining_cards += opponent.cards_in_hand
        opponent.cards_in_hand = []
        random.shuffle(opponent.remaining_cards)
        for _ in range(remaining_points):
            if opponent.remaining_cards:
                opponent.cards_in_hand.append(opponent.remaining_cards.pop())

    def handle_heal(self, player, opponent, trainer, pokemon=None):
        amount, condition = trainer.special_values.split("|")
        amount = int(amount)
        if condition == "water_energy_attached":
            for p in player.all_pokemons():
                if any(p.equipped_energies.get("water", 0) > 0):
                    p.current_hp = min(p.current_hp + amount, p.max_hp)
        elif condition == "stage2":
            stage2_pokemons = [p for p in player.all_pokemons() if p.stage == "stage2"]
            if stage2_pokemons:
                target = player.agent.get_chosen_card(stage2_pokemons, self.match, "choose_pokemon_to_heal")
                target.current_hp = min(target.current_hp + amount, target.max_hp)

    def handle_retrieve_from_discard(self, player, opponent, trainer, pokemon=None):
        basic_pokemons = [p for p in player.discard_pile if p.card_type == "pokemon" and p.stage == "basic"]
        if basic_pokemons:
            chosen = random.choice(basic_pokemons)
            player.cards_in_hand.append(chosen)
            player.discard_pile.remove(chosen)

    def handle_energy_cost_reduction(self, player, opponent, trainer, pokemon=None):
        amount, energy_type, *pokemon_names = trainer.special_values.split("|")
        amount = int(amount)
        self.match.turn_state.energy_cost_reduction = (amount, energy_type, pokemon_names)

    def handle_shuffle_hand_draw(self, player, opponent, trainer, pokemon=None):
        player_hand_size = len(player.cards_in_hand)
        opponent_hand_size = len(opponent.cards_in_hand)
        player.remaining_cards += player.cards_in_hand
        opponent.remaining_cards += opponent.cards_in_hand
        player.cards_in_hand = []
        opponent.cards_in_hand = []
        random.shuffle(player.remaining_cards)
        random.shuffle(opponent.remaining_cards)
        for _ in range(player_hand_size):
            if player.remaining_cards:
                player.cards_in_hand.append(player.remaining_cards.pop())
        for _ in range(opponent_hand_size):
            if opponent.remaining_cards:
                opponent.cards_in_hand.append(opponent.remaining_cards.pop())

    def handle_heal_and_remove_conditions(self, player, opponent, trainer, pokemon=None):
        amount = int(trainer.special_values)
        target = player.agent.get_chosen_card(player.all_pokemons(), self.match, "choose_pokemon_to_heal")
        if target:
            target.current_hp = min(target.current_hp + amount, target.max_hp)
            target.special_conditions.clear()

    def handle_bonus_damage_to_ex(self, player, opponent, trainer, pokemon=None):
        amount = int(trainer.special_values)
        self.match.turn_state.bonus_damage_to_ex = amount

    def handle_discard_energy_coin_flip(self, player, opponent, trainer, pokemon=None):
        if opponent.active_pokemon:
            while random.choice([True, False]):  # Heads
                if opponent.active_pokemon.equipped_energies:
                    energy_type = random.choice(list(opponent.active_pokemon.equipped_energies.keys()))
                    if opponent.active_pokemon.equipped_energies[energy_type] > 0:
                        opponent.active_pokemon.equipped_energies[energy_type] -= 1
                else:
                    break

    def handle_move_damage(self, player, opponent, trainer, pokemon=None):
        amount, *pokemon_names = trainer.special_values.split("|")
        amount = int(amount[:-len("|opponent_active")])
        eligible_pokemons = [p for p in player.all_pokemons() if p.name in pokemon_names and p.current_hp < p.max_hp]
        if eligible_pokemons and opponent.active_pokemon:
            target = player.agent.get_chosen_card(eligible_pokemons, self.match, "choose_pokemon_to_move_damage")
            damage_moved = min(amount, target.max_hp - target.current_hp)
            target.current_hp += damage_moved
            opponent.active_pokemon.current_hp = max(0, opponent.active_pokemon.current_hp - damage_moved)

    def handle_attach_energy_end_turn(self, player, opponent, trainer, pokemon=None):
        amount, energy_type, *pokemon_names = trainer.special_values.split("|")
        amount = int(amount)
        eligible_pokemons = [p for p in player.all_pokemons() if p.name in pokemon_names]
        if eligible_pokemons:
            target = player.agent.get_chosen_card(eligible_pokemons, self.match, "choose_pokemon_for_energy")
            # Assuming Energy Zone is implemented as a list in player.energy_zone
            fire_energies = [e for e in player.energy_zone if "fire" in e.name][:amount]
            for energy in fire_energies:
                target.equipped_energies[energy_type] = target.equipped_energies.get(energy_type, 0) + 1
                player.energy_zone.remove(energy)
            self.match.end_turn(player)

    def handle_discard_all_tools(self, player, opponent, trainer, pokemon=None):
        for p in opponent.all_pokemons():
            if p.attached_tool:
                self.match.detach_tool(p, opponent)

    def handle_switch_opponent_benched(self, player, opponent, trainer, pokemon=None):
        if any(p.name == "Araquanid" for p in player.all_pokemons()) and opponent.bench_pokemons:
            target = player.agent.get_chosen_card(opponent.bench_pokemons, self.match, "choose_opponent_benched_pokemon")
            opponent.bench_pokemons.append(opponent.active_pokemon)
            opponent.active_pokemon = target
            opponent.bench_pokemons.remove(target)

    def handle_heal_all_and_discard_energy(self, player, opponent, trainer, pokemon=None):
        pokemon_names = trainer.special_values.split("|")
        eligible_pokemons = [p for p in player.all_pokemons() if p.name in pokemon_names]
        if eligible_pokemons:
            target = player.agent.get_chosen_card(eligible_pokemons, self.match, "choose_pokemon_to_heal")
            target.current_hp = target.max_hp
            target.equipped_energies.clear()

    def handle_reveal_supporters(self, player, opponent, trainer, pokemon=None):
        supporters = [c for c in opponent.remaining_cards if c.card_type == "supporter"]
        # Assuming a reveal mechanism exists; otherwise, this could log or notify the player
        player.agent.reveal_cards(supporters, self.match, "opponent_supporters")

    def handle_attach_random_energy(self, player, opponent, trainer, pokemon=None):
        amount, category, condition = trainer.special_values.split("|")
        amount = int(amount)
        if opponent.prize_points >= 1:
            ultra_beasts = [p for p in player.all_pokemons() if "ultra beast" in p.categories]
            if ultra_beasts:
                target = player.agent.get_chosen_card(ultra_beasts, self.match, "choose_ultra_beast")
                energy_cards = [e for e in player.discard_pile if e.card_type == "energy"][:amount]
                for energy in energy_cards:
                    energy_type = energy.name.split()[0].lower()
                    target.equipped_energies[energy_type] = target.equipped_energies.get(energy_type, 0) + 1
                    player.discard_pile.remove(energy)

    # New Ability Handlers
    def handle_energy_double(self, player: Player, opponent: Player, ability, pokemon: Pokemon) -> None:
        """Handle energy doubling abilities like Serperior's Jungle Totem."""
        # This effect is handled during energy cost calculation and energy attachment
        # The actual doubling logic should be implemented in the match's energy checking methods
        pass

    def handle_move_energy_ability(self, player: Player, opponent: Player, ability, pokemon: Pokemon) -> None:
        """Handle abilities that allow moving energy between Pokemon."""
        if pokemon.pokemon_type != "water" or pokemon != player.active_pokemon:
            return
        
        water_bench = [p for p in player.bench_pokemons if p.pokemon_type == "water" and p.equipped_energies.get("water", 0) > 0]
        if water_bench:
            source = player.agent.get_chosen_card(water_bench, self.match, "choose_energy_source")
            if source and source.equipped_energies.get("water", 0) > 0:
                source.equipped_energies["water"] -= 1
                pokemon.equipped_energies["water"] = pokemon.equipped_energies.get("water", 0) + 1

    def handle_prevent_evolution(self, player: Player, opponent: Player, ability, pokemon: Pokemon) -> None:
        """Handle abilities that prevent evolution like Aerodactyl ex's Primeval Law."""
        # This effect is handled when checking evolution conditions in the match
        # The actual prevention logic should be implemented in the match's evolution checking methods
        pass

    # New Attack Handlers
    def handle_discard_energy_and_damage_target(self, attacker: Pokemon, defender: Pokemon, attack, player: Player, opponent: Player) -> int:
        """Handle attacks that discard energy and damage a target."""
        energy_type, amount, damage, target_type = attack.special_values
        amount = int(amount)
        damage = int(damage)
        
        # Discard energy from attacker
        available = attacker.equipped_energies.get(energy_type, 0)
        discard_amount = min(amount, available)
        attacker.equipped_energies[energy_type] -= discard_amount
        
        # Damage target
        target = self.match.select_target(player, opponent, target_type, "attack_damage_target")
        if target:
            self.match.apply_damage(target, damage, attacker, player)
        
        return 0

    def handle_discard_random_energy_all(self, attacker: Pokemon, defender: Pokemon, attack, player: Player, opponent: Player) -> int:
        """Handle attacks that discard random energy from all Pokemon."""
        all_pokemons = player.all_pokemons() + opponent.all_pokemons()
        for p in all_pokemons:
            if p.equipped_energies:
                energy_types = [et for et, qty in p.equipped_energies.items() if qty > 0]
                if energy_types:
                    energy_type = random.choice(energy_types)
                    p.equipped_energies[energy_type] -= 1
        return attack.damage

    def handle_bonus_damage_to_ex_attack(self, attacker: Pokemon, defender: Pokemon, attack, player: Player, opponent: Player) -> int:
        """Handle attacks that do bonus damage to ex Pokemon."""
        bonus = int(attack.special_values[0])
        if "ex" in defender.stage:
            return attack.damage + bonus
        return attack.damage

    def handle_bonus_damage_if_knocked_out(self, attacker: Pokemon, defender: Pokemon, attack, player: Player, opponent: Player) -> int:
        """Handle attacks that do bonus damage if a Pokemon was knocked out last turn."""
        bonus = int(attack.special_values[0])
        if hasattr(player, 'last_turn_knockout') and player.last_turn_knockout:
            return attack.damage + bonus
        return attack.damage

    def handle_shuffle_hand_draw_attack(self, attacker: Pokemon, defender: Pokemon, attack, player: Player, opponent: Player) -> int:
        """Handle attacks that shuffle hand and draw new cards."""
        hand_size = attack.special_values[0]
        if hand_size == "opponent_hand_size":
            draw_amount = len(opponent.cards_in_hand)
        else:
            draw_amount = int(hand_size)
        
        # Shuffle hand back into deck
        player.remaining_cards += player.cards_in_hand
        player.cards_in_hand = []
        random.shuffle(player.remaining_cards)
        
        # Draw new cards
        for _ in range(min(draw_amount, len(player.remaining_cards))):
            player.cards_in_hand.append(player.remaining_cards.pop())
        
        return 0

    def handle_copy_attack_effect(self, attacker: Pokemon, defender: Pokemon, attack, player: Player, opponent: Player) -> int:
        """Handle attacks that copy another Pokemon's attack."""
        if defender.attack_ids:
            from utils import all_attacks
            available_attacks = [all_attacks[attack_id] for attack_id in defender.attack_ids if attack_id in all_attacks]
            if available_attacks:
                chosen_attack = player.agent.get_chosen_card(available_attacks, self.match, "choose_attack_to_copy")
                
                # Check if attacker has sufficient energy for the chosen attack
                if self.match.has_sufficient_energy(attacker, chosen_attack):
                    # Calculate and return the damage of the copied attack
                    damage = self.match.calculate_attack_damage(chosen_attack, attacker, defender, player, opponent)
                    
                    # Handle the copied attack's effects
                    if chosen_attack.effect_type in self.attack_handlers:
                        handler = self.attack_handlers[chosen_attack.effect_type]
                        return handler(attacker, defender, chosen_attack, player, opponent)
                    
                    return damage
        return 0

    def handle_coin_multipy(self, attacker: Pokemon, defender: Pokemon, attack, player: Player, opponent: Player) -> int:
        """Handle attacks that multiply damage based on coin flip."""
        multiplier = 2 if random.choice([True, False]) else 1
        return attack.damage * multiplier

    def handle_poison_enhanced(self, attacker: Pokemon, defender: Pokemon, attack, player: Player, opponent: Player) -> int:
        """Handle poison attacks with enhanced damage."""
        damage_amount = attack.special_values[0] if attack.special_values else 20
        self.match.apply_status(defender, "poisoned")
        # Set the enhanced poison damage for this specific poison
        if hasattr(defender, 'poison_damage'):
            defender.poison_damage = damage_amount
        else:
            # Default poison behavior if poison_damage attribute doesn't exist
            pass
        return attack.damage

    def handle_prevent_next_turn_attack(self, attacker: Pokemon, defender: Pokemon, attack, player: Player, opponent: Player) -> int:
        """Handle attacks that prevent the Pokemon from attacking next turn based on coin flip."""
        if random.choice([True, False]):  # Flip coin
            # Prevent this Pokemon from attacking next turn
            attacker.attack_prevented_next_turn = True
        return attack.damage

    def handle_sleep_self(self, attacker: Pokemon, defender: Pokemon, attack, player: Player, opponent: Player) -> int:
        """Handle attacks that put the attacker to sleep."""
        self.match.apply_status(attacker, "asleep")
        return attack.damage

    def handle_burn(self, attacker: Pokemon, defender: Pokemon, attack, player: Player, opponent: Player) -> int:
        """Handle burn status effect."""
        self.match.apply_status(defender, "burned")
        return attack.damage

    def handle_bonus_type_damage(self, attacker: Pokemon, defender: Pokemon, attack, player: Player, opponent: Player) -> int:
        """Handle attacks that do bonus damage against specific types."""
        bonus_damage, target_type = attack.special_values
        if defender.pokemon_type == target_type:
            return attack.damage + int(bonus_damage)
        return attack.damage

    def handle_damage_random_benched(self, attacker: Pokemon, defender: Pokemon, attack, player: Player, opponent: Player) -> int:
        """Handle attacks that damage random benched Pokemon multiple times."""
        times, damage = attack.special_values
        times = int(times)
        damage = int(damage)
        
        for _ in range(times):
            if opponent.bench_pokemons:
                target = random.choice(opponent.bench_pokemons)
                self.match.apply_damage(target, damage, attacker, player)
        return attack.damage

    def handle_multiply_with_condition(self, attacker: Pokemon, defender: Pokemon, attack, player: Player, opponent: Player) -> int:
        """Handle attacks that multiply damage and apply conditions based on coin flips."""
        coins, condition_threshold, condition = attack.special_values
        coins = int(coins)
        threshold = int(condition_threshold)
        
        heads = sum(1 for _ in range(coins) if random.choice([True, False]))
        damage = attack.damage * heads
        
        if heads >= threshold and condition == "poison":
            self.match.apply_status(defender, "poisoned")
        
        return damage

    def handle_bonus_damage_with_tool(self, attacker: Pokemon, defender: Pokemon, attack, player: Player, opponent: Player) -> int:
        """Handle attacks with bonus damage if Pokemon has a tool attached."""
        bonus_damage = int(attack.special_values[0])
        if attacker.attached_tool:
            return attack.damage + bonus_damage
        return attack.damage

    def handle_multiply_bonus(self, attacker: Pokemon, defender: Pokemon, attack, player: Player, opponent: Player) -> int:
        """Handle attacks that add bonus damage based on coin flips."""
        coins, bonus_per_head = attack.special_values
        coins = int(coins)
        bonus_per_head = int(bonus_per_head)
        
        heads = sum(1 for _ in range(coins) if random.choice([True, False]))
        return attack.damage + (bonus_per_head * heads)

    def handle_send_active_to_hand(self, attacker: Pokemon, defender: Pokemon, attack, player: Player, opponent: Player) -> int:
        """Handle attacks that send opponent's active Pokemon to hand."""
        coins = int(attack.special_values[0])
        if coins == 0 or random.choice([True, False]):
            # Add the active Pokemon back to hand
            opponent.cards_in_hand.append(defender)
            # Promote a new active Pokemon if possible
            if opponent.bench_pokemons:
                new_active = opponent.agent.get_chosen_card(opponent.bench_pokemons, self.match, "choose_new_active")
                opponent.swap_active(new_active)
            else:
                # Game ends if no bench Pokemon
                self.match.result = player
        return attack.damage

    def handle_bonus_damage_per_damage(self, attacker: Pokemon, defender: Pokemon, attack, player: Player, opponent: Player) -> int:
        """Handle attacks that do bonus damage per damage counter on the attacker."""
        bonus_per_damage = int(attack.special_values[0])
        damage_counters = attacker.max_hp - attacker.current_hp
        bonus_damage = (damage_counters // 10) * bonus_per_damage  # Each 10 HP is one damage counter
        return attack.damage + bonus_damage

    def handle_discard_energy_and_damage_benched(self, attacker: Pokemon, defender: Pokemon, attack, player: Player, opponent: Player) -> int:
        """Handle attacks that discard energy and damage all benched Pokemon."""
        energy_type, amount, damage, target = attack.special_values
        amount = int(amount)
        damage = int(damage)
        
        # Discard energy
        attacker.equipped_energies[energy_type] = max(0, attacker.equipped_energies[energy_type] - amount)
        
        # Damage benched Pokemon
        target_player = opponent if target == "enemy" else player
        for pokemon in target_player.bench_pokemons:
            self.match.apply_damage(pokemon, damage, attacker, player)
        
        return attack.damage

    def handle_attach_energy_to_benched(self, attacker: Pokemon, defender: Pokemon, attack, player: Player, opponent: Player) -> int:
        """Handle attacks that attach energy to benched Pokemon."""
        energy_type, amount, num_pokemon = attack.special_values
        amount = int(amount)
        num_pokemon = int(num_pokemon)
        
        if player.bench_pokemons:
            target = player.agent.get_chosen_card(player.bench_pokemons, self.match, "attach_energy")
            target.equipped_energies[energy_type] += amount
        
        return attack.damage

    def handle_next_turn_damage_boost(self, attacker: Pokemon, defender: Pokemon, attack, player: Player, opponent: Player) -> int:
        """Handle attacks that boost damage for next turn."""
        boost_amount = int(attack.special_values[0])
        attacker.next_turn_damage_boost = boost_amount
        return attack.damage

    def handle_conditional_energy_attach(self, attacker: Pokemon, defender: Pokemon, attack, player: Player, opponent: Player) -> int:
        """Handle attacks that attach energy if specific Pokemon are on bench."""
        required_pokemon1, required_pokemon2 = attack.special_values
        
        bench_names = [pokemon.name for pokemon in player.bench_pokemons]
        if required_pokemon1 in bench_names and required_pokemon2 in bench_names:
            # Attach one energy from Energy Zone (implementation depends on energy zone structure)
            # This is a simplified implementation
            attacker.equipped_energies["psychic"] += 1
        
        return attack.damage

    def handle_confuse(self, attacker: Pokemon, defender: Pokemon, attack, player: Player, opponent: Player) -> int:
        """Handle confusion status effect."""
        self.match.apply_status(defender, "confused")
        return attack.damage

    def handle_coin_either_bonus_or_self_damage(self, attacker: Pokemon, defender: Pokemon, attack, player: Player, opponent: Player) -> int:
        """Handle attacks that do bonus damage or self damage based on coin flip."""
        bonus, damage = attack.special_values
        action = player.agent.get_action(["bonus", "damage"], self.match, "choose_attack_option")
        if action == "bonus":
            return attack.damage + bonus
        self.match.apply_damage(attacker, damage, opponent)
        return attack.damage

    def handle_coin_bonus(self, attacker: Pokemon, defender: Pokemon, attack, player: Player, opponent: Player) -> int:
        """Handle attacks that do bonus damage based on coin flip."""
        multiplier = 2 if random.choice([True, False]) else 1
        return attack.damage * multiplier

    def handle_bonus_damage_arceus(self, player: Player, opponent: Player, ability, pokemon: Pokemon) -> None:
        """Handle bonus damage Arceus abilities."""
        # This effect is handled during damage calculation
        # The actual implementation should be in the damage calculation method
        pass

    def handle_retreat_cost_arceus(self, player: Player, opponent: Player, ability, pokemon: Pokemon) -> None:
        """Handle retreat cost Arceus abilities."""
        # This effect is handled during retreat cost calculation
        # The actual implementation should be in the retreat cost calculation method
        pass

    def handle_energy_cost_reduction_arceus(self, player: Player, opponent: Player, ability, pokemon: Pokemon) -> None:
        """Handle energy cost reduction Arceus abilities."""
        # This effect is handled during energy cost calculation
        # The actual implementation should be in the energy cost calculation method
        pass

    def handle_checkup_damage_active(self, player: Player, opponent: Player, ability, pokemon: Pokemon) -> None:
        """Handle checkup damage Arceus abilities."""
        # This effect is handled during damage calculation
        # The actual implementation should be in the damage calculation method
        pass

    def handle_retreat_cost_reduction_bench(self, player: Player, opponent: Player, ability, pokemon: Pokemon) -> None:
        """Handle retreat cost reduction bench Arceus abilities."""
        # This effect is handled during retreat cost calculation
        # The actual implementation should be in the retreat cost calculation method
        pass

    def handle_fabled_luster(self, player: Player, opponent: Player, ability, pokemon: Pokemon) -> None:
        """Handle Fabled Luster abilities - prevents special conditions."""
        # This effect prevents special conditions from being applied
        # The actual implementation should be in the status application method
        pass

    def handle_rage_damage(self, attacker: Pokemon, defender: Pokemon, attack, player: Player, opponent: Player) -> int:
        """Handle rage damage Arceus abilities."""
        # This effect is handled during damage calculation
        # The actual implementation should be in the damage calculation method
        bonus = int(attack.special_values[0])
        if "rage" in defender.effect_status:
            return attack.damage + bonus
        return attack.damage

    def handle_heal_self(self, attacker: Pokemon, defender: Pokemon, attack, player: Player, opponent: Player) -> int:
        heal_amount = int(attack.special_values[0])
        # Healing removes damage counters
        healed = min(heal_amount, attacker.damage_taken)
        attacker.damage_taken = max(0, attacker.damage_taken - heal_amount)
        if self.match.debug:
            self.match.log(f"{attacker.name} heals {healed} damage")
        return attack.damage

    # Item Handlers
    def handle_item_heal(self, player: Player, opponent: Player, item, heal_amount: int) -> None:
        """Handle item healing effects like Potion."""
        # Get only Pokemon that have damage (healing items only work on damaged Pokemon)
        damaged_pokemon = [p for p in player.all_pokemons() if p.damage_taken > 0]
        
        if not damaged_pokemon:
            if self.match.debug:
                self.match.log(f"No damaged Pokemon to heal with {item.name}")
            return
        
        # Let the player choose which damaged Pokemon to heal
        target = player.agent.get_chosen_card(damaged_pokemon, self.match, f"choose_pokemon_to_heal_with_{item.name}")
        
        # Apply healing
        healed = min(heal_amount, target.damage_taken)
        target.damage_taken = max(0, target.damage_taken - heal_amount)
        
        if self.match.debug:
            self.match.log(f"{player.name} uses {item.name} to heal {healed} damage from {target.name}")
            if target.damage_taken > 0:
                self.match.log(f"{target.name} still has {target.damage_taken} damage remaining")
            else:
                self.match.log(f"{target.name} is fully healed")

    def handle_draw_basic_pokemon(self, player: Player, opponent: Player, item, special_values) -> None:
        """Handle drawing a basic Pokemon card from deck like Pokeball."""
        # Get all basic Pokemon in the player's deck
        basic_pokemons = [p for p in player.remaining_cards if p.card_type == "pokemon" and p.stage == "basic"]
        
        if not basic_pokemons:
            if self.match.debug:
                self.match.log(f"No basic Pokemon in deck for {item.name}")
            return
        
        # Randomly select a basic Pokemon (Pokeball doesn't let you choose)
        chosen = random.choice(basic_pokemons)
        
        # Add to hand and remove from deck
        player.cards_in_hand.append(chosen)
        player.remaining_cards.remove(chosen)
        
        # Shuffle deck
        random.shuffle(player.remaining_cards)
        
        if self.match.debug:
            self.match.log(f"{player.name} uses {item.name} to randomly draw {chosen.name} from deck")

    def handle_draw_cards(self, player: Player, opponent: Player, trainer, amount: int) -> None:
        """Handle drawing cards from deck like Professor's Research."""
        drawn_count = 0
        
        # Draw the specified number of cards
        for _ in range(amount):
            if player.remaining_cards:
                card = player.remaining_cards.pop()
                self.match.log(f"{player.name} draws {card.name} from deck")
                player.cards_in_hand.append(card)
                drawn_count += 1
            else:
                break
        
        if self.match.debug:
            if drawn_count > 0:
                # Output the player's hand
                hand_names = [card.name for card in player.cards_in_hand if card is not None]
                self.match.log(f"{player.name} hand: {hand_names}")
            else:
                self.match.log(f"{player.name} uses {trainer.name} but no cards left to draw") 
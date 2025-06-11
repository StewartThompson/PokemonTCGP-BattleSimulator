from agents.agent import Agent
import random

class RandomAgent(Agent):

    def __init__(self, player):
        super().__init__(player)

    def get_action(self, action_list, match, action_type=None):
        """Make strategic action choices instead of pure random."""
        
        if action_type == "turn_action":
            # Prioritize strategic actions
            
            # If we can attack and have pokemon that can attack, strongly prefer attacking
            if "pokemon_action" in action_list:
                # Check if we have pokemon that can actually attack
                can_attack = False
                if match.current_player.active_pokemon:
                    possible_attacks = match.get_possible_attacks(match.current_player.active_pokemon)
                    if possible_attacks:
                        can_attack = True
                
                if can_attack:
                    # 80% chance to prioritize pokemon action (which includes attacking)
                    if random.random() < 0.8:
                        return "pokemon_action"
            
            # If we can attach energy and don't have good attacks yet, prioritize energy
            if "attach_energy" in action_list:
                # Check if our active pokemon needs more energy for attacks
                needs_energy = True
                if match.current_player.active_pokemon:
                    possible_attacks = match.get_possible_attacks(match.current_player.active_pokemon)
                    if possible_attacks:
                        needs_energy = False  # Already has attacks available
                
                if needs_energy:
                    # 70% chance to attach energy when needed
                    if random.random() < 0.7:
                        return "attach_energy"
            
            # If we can evolve, it's usually good
            if "evolve" in action_list and random.random() < 0.6:
                return "evolve"
            
            # If we can play cards, sometimes do it
            if "play_card" in action_list and random.random() < 0.4:
                return "play_card"
                
        elif action_type == "precise_action":
            # When choosing specific pokemon actions, prioritize attacks
            attack_actions = [action for action in action_list if action.startswith("use_attack_")]
            if attack_actions:
                # 90% chance to attack if possible
                if random.random() < 0.9:
                    return random.choice(attack_actions)
        
        # Default to random choice
        return random.choice(action_list)

    def get_chosen_card(self, cards, match, choosing_type=None):
        """Make strategic card choices instead of pure random."""
        if not cards:
            return None
            
        if choosing_type == "choose_evolution":
            # For evolution choices, cards is a list of tuples (evolution, targets)
            # Return the selected tuple directly
            return random.choice(cards)
            
        elif choosing_type == "choose_energy_target":
            # Prioritize active pokemon for energy, then pokemon that need energy for attacks
            active = match.current_player.active_pokemon
            if active and active in cards:
                # Check if active pokemon still needs energy
                possible_attacks = match.get_possible_attacks(active)
                if not possible_attacks:  # Needs more energy
                    return active
            
            # Otherwise prioritize pokemon with the fewest energy attached
            cards_with_energy = [(card, sum(card.equipped_energies.values())) for card in cards]
            cards_with_energy.sort(key=lambda x: x[1])  # Sort by energy count
            return cards_with_energy[0][0]
            
        elif choosing_type == "choose_pokemon_for_action":
            # Prioritize active pokemon for actions
            active = match.current_player.active_pokemon
            if active and active in cards:
                return active
                
        elif choosing_type == "choose_new_active" or choosing_type == "choose_new_active_knockout":
            # Choose pokemon with the most HP or best attacks available
            best_pokemon = None
            best_score = -1
            
            for pokemon in cards:
                # Score based on HP and available attacks
                score = pokemon.current_hp
                possible_attacks = match.get_possible_attacks(pokemon)
                score += len(possible_attacks) * 10  # Bonus for having attacks available
                
                if score > best_score:
                    best_score = score
                    best_pokemon = pokemon
                    
            return best_pokemon if best_pokemon else random.choice(cards)
        
        # Default to random choice
        return random.choice(cards)
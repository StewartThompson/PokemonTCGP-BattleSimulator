import random
from typing import Optional, List, Any
from utils import get_card_database

class CustomAgent:
    """Custom AI agent for Pokemon TCG Pocket battles with improved strategy"""

    def __init__(self, player):
        self.player = player

    def get_action(self, possible_actions, match, context):
        """Get the best action to take"""
        
        # Handle precise Pokemon actions (attack, ability, retreat)
        if context == "precise_action":
            # Prioritize attacks over other actions
            attack_actions = [action for action in possible_actions if action.startswith("use_attack_")]
            if attack_actions:
                # Choose the first available attack (could be improved to choose best attack)
                return attack_actions[0]
            
            # Then abilities
            if "use_ability" in possible_actions:
                return "use_ability"
                
            # Retreat only as last resort
            if "retreat" in possible_actions:
                return "retreat"
                
            return possible_actions[0] if possible_actions else None
        
        # Always prioritize attacking if we can
        active_pokemon = self.player.active_pokemon
        if 'pokemon_action' in possible_actions:
            if active_pokemon and self._can_pokemon_attack(active_pokemon, match):
                return 'pokemon_action'
                
        # Then prioritize energy attachment to get closer to attacking  
        if 'attach_energy' in possible_actions:
            return 'attach_energy'
            
        # Play cards to improve board state
        if 'play_card' in possible_actions:
            return 'play_card'
            
        # Use Pokemon actions (evolution, abilities, retreat)
        if 'pokemon_action' in possible_actions:
            return 'pokemon_action'
            
        # End turn if nothing else to do
        if 'end_turn' in possible_actions:
            return 'end_turn'
            
        # Default to first option
        return possible_actions[0] if possible_actions else None

    def _can_pokemon_attack(self, pokemon, match):
        """Check if a Pokemon can use any of its attacks"""
        if not pokemon or not hasattr(pokemon, 'attack_ids') or not pokemon.attack_ids:
            return False
            
        # Get the card database to look up attacks
        from utils import get_card_database
        db = get_card_database()
        if not db or 'attacks' not in db:
            return False
            
        for attack_id in pokemon.attack_ids:
            # Build full attack ID if needed
            full_attack_id = f"attack_{attack_id}" if not attack_id.startswith("attack_") else attack_id
            if full_attack_id in db['attacks']:
                attack = db['attacks'][full_attack_id]
                if self._has_sufficient_energy(pokemon, attack.energy_cost):
                    return True
        return False

    def _has_sufficient_energy(self, pokemon, energy_cost):
        """Check if Pokemon has sufficient energy for an attack"""
        if not energy_cost:
            return True
            
        pokemon_energy = pokemon.equipped_energies.copy()
        
        for energy_type, required_amount in energy_cost.items():
            if energy_type == 'normal':
                # Normal energy can be satisfied by any energy type
                total_available = sum(pokemon_energy.values())
                if total_available < required_amount:
                    return False
                # Remove normal energy requirement from total pool
                remaining = required_amount
                for e_type in list(pokemon_energy.keys()):
                    if pokemon_energy[e_type] > 0 and remaining > 0:
                        taken = min(pokemon_energy[e_type], remaining)
                        pokemon_energy[e_type] -= taken
                        remaining -= taken
            else:
                # Specific energy type required
                if pokemon_energy.get(energy_type, 0) < required_amount:
                    return False
                pokemon_energy[energy_type] -= required_amount
                
        return True

    def _can_pokemon_attack_soon(self, pokemon, match):
        """Check if Pokemon could attack with 1-2 more energy"""
        if not pokemon or not hasattr(pokemon, 'attack_ids') or not pokemon.attack_ids:
            return False
            
        from utils import get_card_database
        db = get_card_database()
        if not db or 'attacks' not in db:
            return False
            
        for attack_id in pokemon.attack_ids:
            full_attack_id = f"attack_{attack_id}" if not attack_id.startswith("attack_") else attack_id
            if full_attack_id in db['attacks']:
                attack = db['attacks'][full_attack_id]
                needed_energy = self._calculate_energy_still_needed(pokemon, attack)
                total_needed = sum(needed_energy.values())
                if total_needed <= 2:  # Can attack within 1-2 turns
                    return True
        return False

    def get_chosen_card(self, options: List[Any], match, context: str) -> Optional[Any]:
        """Choose the best card/Pokemon from available options"""
        
        if not options:
            return None
            
        if context == "pokemon_action":
            return self._choose_pokemon_for_action(options, match)
        elif context == "energy_attachment":
            return self._choose_best_energy_target(options, match)
        elif context == "energy_type":
            return self._choose_best_energy_type(options, match)
        elif context == "card_to_play":
            return self._choose_best_card_to_play(options, match)
        elif context == "initial_active":
            return self._choose_best_active_pokemon(options, match)
        elif context == "initial_bench":
            return self._choose_best_bench_pokemon(options, match)
        elif context == "evolution":
            return self._choose_evolution_target_for_energy(options, match)
        elif context == "heal_target":
            return self._choose_best_heal_target(options, match)
        elif context == "retreat_choice":
            # Only retreat if active Pokemon is in serious danger or can't contribute
            active = self.player.active_pokemon
            if active:
                # Don't retreat if we can attack!
                if self._can_pokemon_attack(active, match):
                    return None  # Don't retreat
                # Only retreat if heavily damaged and can't attack soon
                damage_percent = (active.damage / active.hp) if active.hp > 0 else 1.0
                if damage_percent > 0.7 and not self._can_pokemon_attack_soon(active, match):
                    # Choose best replacement from bench
                    bench_options = [p for p in options if p != active]
                    for pokemon in bench_options:
                        if self._can_pokemon_attack(pokemon, match):
                            return pokemon
                    # If no one can attack, choose highest HP
                    if bench_options:
                        return max(bench_options, key=lambda p: p.hp - p.damage)
            return None  # Default: don't retreat
        else:
            # Generic selection - choose the first viable option
            return options[0] if options else None

    def _choose_pokemon_for_action(self, options, match):
        """Choose Pokemon for action - ALWAYS prioritize attacking with active Pokemon"""
        active_pokemon = self.player.active_pokemon
        
        # If active Pokemon can attack, choose it!
        if active_pokemon and active_pokemon in options and self._can_pokemon_attack(active_pokemon, match):
            return active_pokemon
            
        # Otherwise, look for other Pokemon that can attack
        for pokemon in options:
            if self._can_pokemon_attack(pokemon, match):
                return pokemon
        
        # If no one can attack, prioritize evolution or Pokemon close to attacking
        for pokemon in options:
            if self._can_pokemon_attack_soon(pokemon, match):
                return pokemon
                
        # Last resort - choose active Pokemon to avoid unnecessary retreats
        if active_pokemon and active_pokemon in options:
            return active_pokemon
            
        return options[0] if options else None

    def _choose_pokemon_for_energy_focus(self, options, match):
        """Choose Pokemon to focus energy on"""
        
        from utils import get_card_database
        db = get_card_database()
        if not db or 'attacks' not in db:
            return options[0] if options else None
        
        # Priority 1: Pokemon that can attack with just one more energy
        for pokemon in options:
            if not self._can_pokemon_attack(pokemon, match):
                if hasattr(pokemon, 'attack_ids') and pokemon.attack_ids:
                    for attack_id in pokemon.attack_ids:
                        full_attack_id = f"attack_{attack_id}" if not attack_id.startswith("attack_") else attack_id
                        if full_attack_id in db['attacks']:
                            attack = db['attacks'][full_attack_id]
                            needed_energy = self._calculate_energy_still_needed(pokemon, attack)
                            total_needed = sum(needed_energy.values())
                            if total_needed == 1:
                                return pokemon
        
        # Priority 2: Active Pokemon (to enable immediate attacks)
        active_pokemon = self.player.active_pokemon
        if active_pokemon and active_pokemon in options:
            return active_pokemon
            
        # Priority 3: Pokemon with lowest energy requirements
        def energy_priority(pokemon):
            if not hasattr(pokemon, 'attack_ids') or not pokemon.attack_ids:
                return 999
            min_cost = 999
            for attack_id in pokemon.attack_ids:
                full_attack_id = f"attack_{attack_id}" if not attack_id.startswith("attack_") else attack_id
                if full_attack_id in db['attacks']:
                    attack = db['attacks'][full_attack_id]
                    cost = sum(attack.energy_cost.values())
                    min_cost = min(min_cost, cost)
            return min_cost
            
        return min(options, key=energy_priority)

    def _choose_best_active_pokemon(self, options, match):
        """Choose best Pokemon for initial active position - prioritize higher HP"""
        if not options:
            return None
            
        from utils import get_card_database
        db = get_card_database()
        
        # Choose Pokemon with highest HP that can potentially attack
        def active_priority(pokemon):
            hp_score = pokemon.max_hp * 10  # Heavily weight HP
            attack_score = 50 if hasattr(pokemon, 'attack_ids') and pokemon.attack_ids else 0
            energy_score = 0
            if hasattr(pokemon, 'attack_ids') and pokemon.attack_ids and db and 'attacks' in db:
                min_energy_cost = 999
                for attack_id in pokemon.attack_ids:
                    full_attack_id = f"attack_{attack_id}" if not attack_id.startswith("attack_") else attack_id
                    if full_attack_id in db['attacks']:
                        attack = db['attacks'][full_attack_id]
                        cost = sum(attack.energy_cost.values())
                        min_energy_cost = min(min_energy_cost, cost)
                if min_energy_cost < 999:
                    energy_score = max(0, 30 - min_energy_cost * 5)  # Lower cost = higher score
            return hp_score + attack_score + energy_score
            
        return max(options, key=active_priority)

    def _choose_best_bench_pokemon(self, options, match):
        """Choose best Pokemon for bench"""
        return options[0] if options else None

    def _choose_evolution_target_for_energy(self, options, match):
        """Choose Pokemon to evolve - prioritize those with energy"""
        
        # Prioritize Pokemon that already have energy
        options_with_energy = [p for p in options if sum(p.equipped_energies.values()) > 0]
        if options_with_energy:
            return options_with_energy[0]
            
        return options[0] if options else None

    def _choose_best_card_to_play(self, cards, match):
        """Choose best card to play with improved priority"""
        
        if not cards:
            return None
        
        # HIGHEST PRIORITY: Basic Pokemon for bench (if we have space)
        if len(self.player.bench_pokemons) < 3:  # MAX_BENCH_SIZE is 3
            basic_pokemon = [card for card in cards if 
                           hasattr(card, 'card_type') and card.card_type == "pokemon" and 
                           hasattr(card, 'stage') and card.stage == "basic"]
            if basic_pokemon:
                # Prioritize Pokemon that can attack or have higher HP
                def pokemon_priority(pokemon):
                    hp_score = getattr(pokemon, 'max_hp', 0) * 2  # HP is important
                    attack_score = 20 if hasattr(pokemon, 'attack_ids') and pokemon.attack_ids else 0
                    return hp_score + attack_score
                
                return max(basic_pokemon, key=pokemon_priority)
        
        # SECOND PRIORITY: Evolution Pokemon if we can evolve
        evolution_pokemon = [card for card in cards if 
                           hasattr(card, 'card_type') and card.card_type == "pokemon" and 
                           hasattr(card, 'evolves_from') and card.evolves_from]
        
        for card in evolution_pokemon:
            # Check if we have the pre-evolution in play
            all_pokemon = [self.player.active_pokemon] + self.player.bench_pokemons
            for pokemon in all_pokemon:
                if pokemon and hasattr(pokemon, 'name') and pokemon.name == card.evolves_from:
                    return card
        
        # THIRD PRIORITY: Useful items/trainers
        priority_order = [
            'Poké Ball',      # High priority - deck search  
            "Professor's Research",  # Card draw
            'Potion',         # Healing
        ]
        
        for priority in priority_order:
            for card in cards:
                card_name = getattr(card, 'name', str(card))
                if priority in card_name:
                    return card
        
        # FOURTH PRIORITY: Any other items/trainers
        other_cards = [card for card in cards if 
                      hasattr(card, 'card_type') and card.card_type in ['item', 'trainer']]
        if other_cards:
            return other_cards[0]
        
        # DEFAULT: First card
        return cards[0]

    def _choose_best_energy_type(self, options, match):
        """Choose the best energy type to attach"""
        if not options:
            return None
            
        from utils import get_card_database
        db = get_card_database()
        if not db or 'attacks' not in db:
            return options[0]
            
        # Count what energy types we need most
        energy_needs = {}
        all_pokemon = [self.player.active_pokemon] + self.player.bench_pokemons
        
        for pokemon in all_pokemon:
            if pokemon and hasattr(pokemon, 'attack_ids') and pokemon.attack_ids:
                for attack_id in pokemon.attack_ids:
                    full_attack_id = f"attack_{attack_id}" if not attack_id.startswith("attack_") else attack_id
                    if full_attack_id in db['attacks']:
                        attack = db['attacks'][full_attack_id]
                        needed = self._calculate_energy_still_needed(pokemon, attack)
                        for energy_type, amount in needed.items():
                            energy_needs[energy_type] = energy_needs.get(energy_type, 0) + amount
        
        # Choose the energy type we need most
        if energy_needs:
            most_needed = max(energy_needs.items(), key=lambda x: x[1])
            if most_needed[0] in options:
                return most_needed[0]
                
        return options[0]

    def _choose_best_energy_target(self, options, match):
        """Choose best Pokemon to attach energy to"""
        if not options:
            return None
            
        return self._choose_pokemon_for_energy_focus(options, match)

    def _calculate_total_energy_needed(self, attack):
        """Calculate total energy needed for an attack"""
        if not attack or not attack.energy_cost:
            return 0
        return sum(attack.energy_cost.values())

    def _calculate_energy_still_needed(self, pokemon, attack):
        """Calculate what energy is still needed for a Pokemon to use an attack"""
        if not attack or not attack.energy_cost:
            return {}
            
        needed = {}
        pokemon_energy = pokemon.equipped_energies.copy()
        
        for energy_type, required_amount in attack.energy_cost.items():
            if energy_type == 'normal':
                # Normal energy can be satisfied by any type
                total_available = sum(pokemon_energy.values())
                if total_available < required_amount:
                    needed['normal'] = required_amount - total_available
                else:
                    # Remove energy from pool
                    remaining = required_amount
                    for e_type in list(pokemon_energy.keys()):
                        if pokemon_energy[e_type] > 0 and remaining > 0:
                            taken = min(pokemon_energy[e_type], remaining)
                            pokemon_energy[e_type] -= taken
                            remaining -= taken
            else:
                # Specific energy type
                available = pokemon_energy.get(energy_type, 0)
                if available < required_amount:
                    needed[energy_type] = required_amount - available
                    pokemon_energy[energy_type] = 0
                else:
                    pokemon_energy[energy_type] -= required_amount
                    
        return needed

    def _choose_best_heal_target(self, options, match):
        """Choose best Pokemon to heal"""
        if not options:
            return None
            
        # Heal the most valuable damaged Pokemon
        damaged_pokemon = [p for p in options if p.current_hp < p.max_hp]
        if not damaged_pokemon:
            return None
            
        def heal_priority(pokemon):
            damage_ratio = (pokemon.max_hp - pokemon.current_hp) / pokemon.max_hp if pokemon.max_hp > 0 else 0
            # Prioritize Pokemon that are close to being knocked out but still valuable
            if damage_ratio > 0.7:  # Severely damaged
                return pokemon.max_hp * 2  # High priority for high HP Pokemon
            elif damage_ratio > 0.3:  # Moderately damaged
                return pokemon.max_hp
            else:
                return 0  # Low priority for lightly damaged
                
        return max(damaged_pokemon, key=heal_priority)



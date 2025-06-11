import random
from typing import Optional, List, Any
from utils import get_card_database

class OpponentAgent:
    """Effective aggressive agent that properly handles energy and attacks"""
    
    def __init__(self, player):
        self.player = player
        
    def get_action(self, possible_actions, match, context):
        """Smart action selection focused on winning."""
        
        # Always prioritize actions over ending turn unless no good options
        available_actions = [action for action in possible_actions if action != "end_turn"]
        if not available_actions:
            return "end_turn"
        
        our_player = match.current_player
        opponent = match.get_opponent()
        
        # PRIORITY 1: Attack if we can do meaningful damage
        attack_actions = [action for action in available_actions if "attack" in action.lower()]
        if attack_actions and our_player.active_pokemon:
            # Be aggressive - attack whenever possible
            return attack_actions[0]
        
        # PRIORITY 2: Evolve to get stronger Pokemon
        if "evolve" in available_actions:
            return "evolve"
        
        # PRIORITY 3: Attach energy strategically
        if "attach_energy" in available_actions:
            return "attach_energy"
        
        # PRIORITY 4: Play helpful cards
        if "play_card" in available_actions:
            return "play_card"
        
        # PRIORITY 5: Use Pokemon abilities if beneficial
        if "pokemon_action" in available_actions:
            return "pokemon_action"
        
        # PRIORITY 6: Retreat if current Pokemon is in bad shape
        if "retreat" in available_actions and our_player.active_pokemon:
            # Only retreat if current Pokemon is badly damaged and we have better options
            current_hp_percent = our_player.active_pokemon.current_hp / our_player.active_pokemon.max_hp
            if current_hp_percent < 0.4 and len(our_player.bench_pokemons) > 0:
                # Check if we have a healthier Pokemon on bench
                for bench_pokemon in our_player.bench_pokemons:
                    bench_hp_percent = bench_pokemon.current_hp / bench_pokemon.max_hp
                    if bench_hp_percent > current_hp_percent + 0.2:  # Significantly healthier
                        return "retreat"
        
        # Default: first available action or end turn
        return available_actions[0] if available_actions else "end_turn"
    
    def get_chosen_card(self, options: List[Any], match, context: str) -> Optional[Any]:
        """Smart card selection based on context."""
        if not options:
            return None
        
        if len(options) == 1:
            return options[0]
        
        our_player = match.current_player
        opponent = match.get_opponent()
        
        # Context-specific intelligent choices
        if context == "choose_active":
            # Choose strongest Pokemon for active slot
            return max(options, key=lambda p: (p.max_hp, len(p.attack_ids)))
        
        elif context == "choose_bench":
            # Fill bench with good Pokemon
            return max(options, key=lambda p: p.max_hp)
        
        elif context == "choose_evolution":
            # Always evolve for better stats and attacks
            return options[0][0] if options else None
        
        elif context == "choose_target_for_evolution":
            # Prefer active Pokemon first, then Pokemon with most HP
            if our_player.active_pokemon in options:
                return our_player.active_pokemon
            return max(options, key=lambda p: p.current_hp)
        
        elif context == "choose_card_to_play":
            # Play cards strategically
            return self._choose_best_card_to_play(options, match)
        
        elif context == "choose_pokemon_for_action":
            # Use active Pokemon if possible, otherwise strongest available
            if our_player.active_pokemon in options:
                return our_player.active_pokemon
            return max(options, key=lambda p: p.current_hp)
        
        elif context == "choose_energy_type":
            # Match active Pokemon's type if possible
            if our_player.active_pokemon and our_player.active_pokemon.pokemon_type in options:
                return our_player.active_pokemon.pokemon_type
            return options[0]
        
        elif context == "choose_pokemon_to_attach_energy":
            # Attach energy strategically to Pokemon that can use it best
            return self._choose_best_energy_target(options, match)
        
        elif "retreat" in context:
            # Choose best replacement for active Pokemon
            return self._choose_best_active_replacement(options, match)
        
        elif "heal" in context or "potion" in context:
            # Heal most damaged Pokemon
            damaged_options = [p for p in options if p.current_hp < p.max_hp]
            if damaged_options:
                return min(damaged_options, key=lambda p: p.current_hp / p.max_hp)
            return options[0]
        
        # Default: choose first option
        return options[0]
    
    def _choose_best_card_to_play(self, cards, match):
        """Choose the most beneficial card to play."""
        our_player = match.current_player
        
        # Prioritize by strategic value
        for card in cards:
            if card.card_type == "pokemon":
                if card.stage == "basic":
                    # Need basic Pokemon for active or bench
                    if not our_player.active_pokemon or len(our_player.bench_pokemons) < 5:
                        return card
                else:
                    # Evolution cards are usually valuable
                    return card
                    
            elif card.card_type in ["trainer", "supporter", "item"]:
                # These cards usually provide immediate benefits
                return card
        
        return cards[0]
    
    def _choose_best_energy_target(self, options, match):
        """Choose the best Pokemon to attach energy to."""
        our_player = match.current_player
        db = get_card_database()
        
        if not db:
            # Fallback: prefer active Pokemon
            return our_player.active_pokemon if our_player.active_pokemon in options else options[0]
        
        best_pokemon = None
        best_score = -1
        
        for pokemon in options:
            score = 0
            
            # Prefer active Pokemon (gets 50 bonus points)
            if pokemon == our_player.active_pokemon:
                score += 50
            
            # Score based on how close the Pokemon is to being able to attack
            if hasattr(pokemon, 'attack_ids') and pokemon.attack_ids:
                for attack_id in pokemon.attack_ids:
                    if attack_id in db['attacks']:
                        attack = db['attacks'][attack_id]
                        
                        # Check how much energy this Pokemon still needs
                        energy_needed = self._calculate_energy_still_needed(pokemon, attack)
                        if energy_needed == 1:  # Will be able to attack after this energy
                            score += 100
                        elif energy_needed == 2:  # Will be close to attacking
                            score += 30
                        elif energy_needed == 0:  # Can already attack
                            score += 10
                        
                        # Bonus for high damage attacks
                        try:
                            damage = int(attack.damage) if attack.damage and str(attack.damage).isdigit() else 0
                            score += damage * 0.2
                        except (ValueError, AttributeError):
                            pass
            
            # Prefer Pokemon with more HP (survival)
            score += pokemon.current_hp * 0.1
            
            if score > best_score:
                best_score = score
                best_pokemon = pokemon
        
        return best_pokemon or options[0]
    
    def _calculate_energy_still_needed(self, pokemon, attack):
        """Calculate how much more energy a Pokemon needs for an attack."""
        total_needed = 0
        total_have = sum(pokemon.equipped_energies.values())
        
        # Count specific energy requirements
        for energy_type, cost in attack.energy_cost.items():
            if cost > 0 and energy_type != 'normal':
                have = pokemon.equipped_energies.get(energy_type, 0)
                total_needed += max(0, cost - have)
        
        # Add colorless energy requirements
        colorless_needed = attack.energy_cost.get('normal', 0)
        if colorless_needed > 0:
            # Any energy can satisfy colorless requirements
            energy_used_for_specific = sum([min(pokemon.equipped_energies.get(t, 0), c) 
                                          for t, c in attack.energy_cost.items() 
                                          if t != 'normal' and c > 0])
            remaining_energy = total_have - energy_used_for_specific
            colorless_still_needed = max(0, colorless_needed - remaining_energy)
            total_needed += colorless_still_needed
        
        return total_needed
    
    def _choose_best_active_replacement(self, options, match):
        """Choose the best Pokemon to replace the active Pokemon."""
        if not options:
            return None
        
        db = get_card_database()
        if not db:
            return max(options, key=lambda p: p.current_hp)
        
        best_pokemon = None
        best_score = 0
        
        for pokemon in options:
            score = pokemon.current_hp  # Prefer healthy Pokemon
            
            # Bonus for Pokemon that can attack immediately
            if hasattr(pokemon, 'attack_ids') and pokemon.attack_ids:
                for attack_id in pokemon.attack_ids:
                    if attack_id in db['attacks']:
                        attack = db['attacks'][attack_id]
                        energy_needed = self._calculate_energy_still_needed(pokemon, attack)
                        if energy_needed == 0:  # Can attack now
                            try:
                                damage = int(attack.damage) if attack.damage and str(attack.damage).isdigit() else 0
                                score += damage
                            except (ValueError, AttributeError):
                                score += 20  # Default bonus for having an attack
                        elif energy_needed <= 2:  # Close to attacking
                            score += 30
            
            if score > best_score:
                best_score = score
                best_pokemon = pokemon
        
        return best_pokemon or options[0]



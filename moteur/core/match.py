import random
from typing import List, Dict, Optional, Tuple, Union

from moteur.cartes.pokemon import Pokemon
from moteur.cartes.trainer import Trainer
from moteur.cartes.item import Item
from moteur.cartes.tool import Tool
from moteur.player import Player
from utils import get_basic_pokemons, get_card_database, all_attacks, all_abilities
from typing import Optional

from moteur.core.turn_state import TurnState
from moteur.handlers.card_effect_handler import CardEffectHandler

class Match:
    """Manages a Pokémon TCG match between two players."""
    DECK_SIZE = 20
    MAX_BENCH_SIZE = 3
    WINNING_POINTS = 3
    MAX_TURNS = 50  # Add a maximum number of turns to prevent infinite loops

    def __init__(self, player1: Player, player2: Player, debug=False):
        self.player1 = player1
        self.player2 = player2
        self.turn = 0
        self.turn_state = TurnState()
        self.current_player = None
        self.first_player = None  # Track who went first
        self.winner = None
        self.attack_prevention = (False, None)
        self.supporter_prevention = (False, None)
        self.shield = (0, None)
        self.damage_reduction = (0, None)
        self.effect_handler = CardEffectHandler(self)
        self.debug = debug  # Whether to print debug information

    def log(self, message):
        """Print a debug message if debug mode is enabled."""
        if self.debug:
            print(f"[Turn {self.turn}] {message}")
            
    def start_battle(self) -> Optional[Player]:
        """Start and run the battle until completion."""
        self.validate_decks()
        self.setup_game()
        
        while not self.winner and self.turn < self.MAX_TURNS:
            self.log(f"Starting turn {self.turn + 1} for {self.current_player.name}")
            self.play_turn()
            
        if self.turn >= self.MAX_TURNS and not self.winner:
            self.log("Maximum number of turns reached, determining winner by prize points")
            if self.player1.prize_points > self.player2.prize_points:
                self.winner = self.player1
            elif self.player2.prize_points > self.player1.prize_points:
                self.winner = self.player2
            else:
                # Tie - use random winner for now
                self.winner = random.choice([self.player1, self.player2])
                
        self.log(f"Battle complete! Winner: {self.winner.name if self.winner else 'None'}")
        return self.winner

    def validate_decks(self) -> None:
        """Validate that both players' decks meet the requirements."""
        for player in [self.player1, self.player2]:
            if len(player.deck) != self.DECK_SIZE:
                raise ValueError(f"Deck size must be {self.DECK_SIZE} current deck size is {len(player.deck)}")
            if not get_basic_pokemons(player.deck):
                raise ValueError("Deck must contain at least one basic Pokémon")

    def setup_game(self) -> None:
        """Initialize the game state for both players."""
        # Coin flip for who goes first - happens first
        first_player = random.choice([self.player1, self.player2])
        self.first_player = first_player  # Store who went first
        self.current_player = first_player
        if self.debug:
            self.log(f"Coin flip result: {first_player.name} goes first!")
        
        for player in [self.player1, self.player2]:
            player.remaining_cards = player.deck.copy()
            random.shuffle(player.remaining_cards)
            player.cards_in_hand = []
            player.discard_pile = []
            player.active_pokemon = None
            player.bench_pokemons = []
            player.prize_points = 0
            
            # Initialize Energy Zone (replaces energy_points)
            player.energy_zone = []  # Available energy this turn
            player.deck_energy_types = []  # Energy types from deck composition
            
            # Initialize turns_in_play for all Pokemon in deck
            for card in player.deck:
                if hasattr(card, 'pokemon_type'):  # Pokemon card
                    if not hasattr(card, 'turns_in_play'):
                        card.turns_in_play = 0
            
            # Determine energy types based on deck composition
            for card in player.deck:
                if hasattr(card, 'pokemon_type') and card.pokemon_type:
                    if card.pokemon_type not in player.deck_energy_types:
                        player.deck_energy_types.append(card.pokemon_type)
            
            # Fallback to common types if no Pokemon types found
            if not player.deck_energy_types:
                player.deck_energy_types = ['grass', 'water', 'fire', 'normal']
            
            # Draw initial hand
            for _ in range(5):
                if player.remaining_cards:
                    card = player.remaining_cards.pop()
                    if card is not None:  # Only add non-None cards
                        player.cards_in_hand.append(card)
                    else:
                        print(f"Warning: Found None card in {player.name}'s deck during setup")
            
            # Remove any None values that might have slipped through
            player.cards_in_hand = [card for card in player.cards_in_hand if card is not None]
            
            # Log initial hand
            if self.debug:
                hand_names = [card.name for card in player.cards_in_hand if card is not None]
                self.log(f"{player.name} draws initial hand: {hand_names}")
                
        # Set up active Pokémon and mulligan if needed
        self.setup_active_pokemon(self.player1)
        self.setup_active_pokemon(self.player2)
        
        # Initial check for game end conditions
        self.check_game_end()

    def play_turn(self) -> None:
        """Execute a single turn of gameplay."""
        self.turn += 1
        opponent = self.get_opponent()
        
        # Display the game state at the start of each turn
        self.display_game_state_ascii()
        
        # Reset turn state - this should clear evolved Pokemon tracking
        self.turn_state.reset(is_first_turn=(self.turn == 1))
        
        # Remove any None values from hand before proceeding
        self.current_player.cards_in_hand = [card for card in self.current_player.cards_in_hand if card is not None]
        
        # Increment turn counter for all Pokemon (for evolution timing)
        for pokemon in self.current_player.all_pokemons():
            if hasattr(pokemon, 'turns_in_play'):
                pokemon.turns_in_play += 1
            else:
                pokemon.turns_in_play = 1
        
        # Generate energy for Energy Zone (except first player's first turn)
        if not (self.turn == 1 and self.current_player == self.first_player):
            energy_type = random.choice(self.current_player.deck_energy_types)
            self.current_player.energy_zone.append(energy_type)
            if self.debug:
                self.log(f"{self.current_player.name} gains {energy_type} energy in Energy Zone")
        elif self.debug:
            # First player's first turn gets no energy
            self.log(f"{self.current_player.name} gets no energy on first turn (goes first)")
        
        # Apply status effects from previous turn
        if self.current_player.active_pokemon:
            self.handle_status_effects(self.current_player.active_pokemon, opponent)
            
        # Apply supporter prevention
        self.apply_supporter_prevention(self.current_player, opponent)
        
        # Draw a card at the start of turn (first player still draws on their first turn)
        if self.current_player.remaining_cards:
            drawn_card = self.current_player.remaining_cards.pop()
            if drawn_card is not None:  # Only add non-None cards
                self.current_player.cards_in_hand.append(drawn_card)
                if self.debug:
                    hand_names = [card.name for card in self.current_player.cards_in_hand if card is not None]
                    self.log(f"{self.current_player.name} draws {drawn_card.name}. Hand size: {len(self.current_player.cards_in_hand)} - {hand_names}")
            else:
                print(f"Warning: Drew None card from {self.current_player.name}'s deck")
            
        # Main turn loop
        action = self.get_player_action(self.current_player, opponent)
        max_actions = 10  # Prevent infinite loops within a turn
        action_count = 0
        
        while action != "end_turn" and action is not None and action_count < max_actions and not self.turn_state.has_attacked:
            action_count += 1
            action = self.get_player_action(self.current_player, opponent)
            
        if action_count >= max_actions:
            self.log(f"Maximum actions reached for turn {self.turn}, forcing end turn")
            
        if self.turn_state.has_attacked:
            self.log(f"{self.current_player.name}'s turn ends after attacking")
            
        self.end_turn()

    def apply_supporter_prevention(self, player: Player, opponent: Player) -> None:
        """Apply supporter prevention effects."""
        if self.supporter_prevention[0] and self.supporter_prevention[1] == player:
            self.supporter_prevention = (False, None)
            player.can_play_trainer = False
        else:
            player.can_play_trainer = True

    def get_player_action(self, player: Player, opponent: Player) -> Optional[str]:
        """Get and execute the next action for the current player."""
        playable_cards = self.get_playable_cards(player, opponent)
        possible_actions = self.get_possible_actions(playable_cards)
        
        self.log(f"Possible actions for {player.name}: {possible_actions}")
        
        action = player.agent.get_action(possible_actions, self, "turn_action")
        self.log(f"{player.name} chose action: {action}")
        
        if action == "attach_energy":
            self.attach_energy(player)
        elif action == "play_card":
            self.play_card(player, opponent)
        elif action == "pokemon_action":
            pokemon_to_act = player.agent.get_chosen_card(player.all_pokemons(), self, "choose_pokemon_for_action")
            if pokemon_to_act:
                self.log(f"{player.name} chose Pokemon for action: {pokemon_to_act.name}")
                self.handle_pokemon_action(pokemon_to_act, player, opponent)
        elif action == "evolve":
            evolutions = self.get_possible_evolutions(player)
            if evolutions:
                chosen_evolution_option = player.agent.get_chosen_card(evolutions, self, "choose_evolution")
                evolution, targets = chosen_evolution_option
                self.log(f"{player.name} chose evolution: {evolution.name if evolution else None}")
                target = player.agent.get_chosen_card(targets, self, "choose_target_for_evolution")
                self.log(f"{player.name} chose target for evolution: {target.name if target else None}")
                self.evolve_pokemon(evolution, target, player)
                
        elif action.startswith("attack_"):
            # Attack IDs are stored as strings like 'attack_89', so we need to extract the number
            attack_id_str = action.split("_", 1)[1]  # Get everything after first underscore
            if attack_id_str.startswith("attack_"):
                # If it's in format "attack_attack_89", extract the final number
                attack_id = int(attack_id_str.split("_")[1])
            else:
                # If it's just a number, convert to int
                attack_id = int(attack_id_str)
            self.perform_attack(attack_id, player.active_pokemon, opponent.active_pokemon, player, opponent)
        elif action.startswith("use_attack_"):
            # Extract the attack ID from 'use_attack_89'
            attack_id = action.split("_")[2]  # Get the ID part after 'use_attack_'
            self.perform_attack(attack_id, player.active_pokemon, opponent.active_pokemon, player, opponent)

        return action

    def attach_energy(self, player: Player) -> None:
        """Attach an energy card to a Pokémon."""
        if self.turn_state.has_attached_energy:
            return
            
        # Check if Energy Zone has energy available
        if not player.energy_zone:
            return
            
        # Get all Pokemon that can have energy attached
        all_pokemon = player.all_pokemons()
        if not all_pokemon:
            return
            
        # Let player choose which Pokemon to attach energy to
        target = player.agent.get_chosen_card(all_pokemon, self, "choose_pokemon_to_attach_energy")
        
        # Choose energy type from Energy Zone
        if len(player.energy_zone) == 1:
            energy_type = player.energy_zone[0]
        else:
            energy_type = player.agent.get_action(player.energy_zone, self, "choose_energy_type")
        
        # Remove energy from Energy Zone and attach to Pokemon
        player.energy_zone.remove(energy_type)
        target.equipped_energies[energy_type] += 1
        self.turn_state.has_attached_energy = True
        
        if self.debug:
            self.log(f"{player.name} attached {energy_type} energy to {target.name}")

    def play_card(self, player: Player, opponent: Player) -> None:
        """Play a card from hand."""
        playable = [c for c in player.cards_in_hand if self.conditions_are_met(c, c.card_type, player, opponent)]
        if not playable:
            return
            
        card = player.agent.get_chosen_card(playable, self, "choose_card_to_play")
        
        # Find and remove the card from hand by matching properties
        # instead of relying on object identity
        removed = False
        for i, hand_card in enumerate(player.cards_in_hand):
            if (hasattr(hand_card, 'card_id') and hasattr(card, 'card_id') and 
                hand_card.card_id == card.card_id and 
                hasattr(hand_card, 'name') and hasattr(card, 'name') and 
                hand_card.name == card.name):
                player.cards_in_hand.pop(i)
                card = hand_card  # Use the actual card from the hand
                removed = True
                break
        
        if not removed:
            # Fallback: try to find by name and type
            for i, hand_card in enumerate(player.cards_in_hand):
                if (hasattr(hand_card, 'name') and hasattr(card, 'name') and 
                    hand_card.name == card.name and 
                    hasattr(hand_card, 'card_type') and hand_card.card_type == card.card_type):
                    player.cards_in_hand.pop(i)
                    card = hand_card  # Use the actual card from the hand
                    removed = True
                    break
        
        if not removed:
            # Final fallback: try the original method
            try:
                player.cards_in_hand.remove(card)
            except ValueError:
                if self.debug:
                    self.log(f"Warning: Could not find selected card {card.name} in hand")
                return
        
        if card.card_type == "pokemon":
            self.play_pokemon(card, player, opponent)
        elif card.card_type == "trainer":
            self.play_trainer(card, player, opponent)
        elif card.card_type == "item":
            self.play_item(card, player)
        elif card.card_type == "tool":
            self.play_tool(card, player)

    def play_pokemon(self, card: Pokemon, player: Player, opponent: Player) -> None:
        """Play a Pokémon card from hand."""
        # Initialize turn tracking
        card.turns_in_play = 0
        
        if card.stage == "basic" or "ex" in card.stage:
            # Place as active if no active Pokémon
            if not player.active_pokemon:
                player.active_pokemon = card
                if self.debug:
                    self.log(f"{player.name} plays {card.name} to the active spot")
            # Place on bench if space available
            elif len(player.bench_pokemons) < self.MAX_BENCH_SIZE:
                player.bench_pokemons.append(card)
                if self.debug:
                    self.log(f"{player.name} plays {card.name} to the bench")
            else:
                # No space, return to hand
                player.cards_in_hand.append(card)
                if self.debug:
                    self.log(f"{player.name} cannot play {card.name} - no space available")
        else:
            # Handle evolution
            # Pokemon TCG Rule: No evolution on the first turn of the game for either player
            if self.turn <= 2:
                # Return evolution card to hand
                player.cards_in_hand.append(card)
                if self.debug:
                    self.log(f"{player.name} cannot evolve {card.name} on turn {self.turn} (first turn rule)")
                return
                
            targets = self.get_evolvable_pokemon(card, player)
            if targets:
                target = player.agent.get_chosen_card(targets, self, "choose_evolution_target")
                self.evolve_pokemon(card, target, player)
            else:
                # No valid targets, return to hand
                player.cards_in_hand.append(card)
                if self.debug:
                    self.log(f"{player.name} cannot play {card.name} - no valid evolution targets")

    def get_evolvable_pokemon(self, evolution: Pokemon, player: Player) -> List[Pokemon]:
        """Get Pokémon that can evolve into the given evolution."""
        if not hasattr(evolution, 'pre_evolution_name') or not evolution.pre_evolution_name:
            return []
        
        targets = []
        for pokemon in player.all_pokemons():
            name_match = pokemon.name == evolution.pre_evolution_name
            turns_valid = hasattr(pokemon, 'turns_in_play') and pokemon.turns_in_play >= 1
            not_evolved_this_turn = pokemon not in self.turn_state.evolved_pokemon_this_turn
            
            if name_match and turns_valid and not_evolved_this_turn:
                targets.append(pokemon)
                
        return targets

    def handle_pokemon_action(self, pokemon: Pokemon, player: Player, opponent: Player) -> None:
        """Handle actions for a specific Pokémon."""
        actions = self.get_pokemon_actions(pokemon, player, opponent)
        if not actions:
            return
            
        action = player.agent.get_action(actions, self, "precise_action")
        
        if action == "cancel":
            # Return to main action menu
            return
        elif action == "use_ability":
            self.use_ability(pokemon, player, opponent)
        elif action == "retreat":
            self.retreat(pokemon, player)
        elif action.startswith("use_attack_"):
            # Extract the attack ID from 'use_attack_89'
            attack_id = action.split("_")[2]  # Get the ID part after 'use_attack_'
            self.perform_attack(attack_id, player.active_pokemon, opponent.active_pokemon, player, opponent)

    def get_pokemon_actions(self, pokemon: Pokemon, player: Player, opponent: Player) -> List[str]:
        """Get available actions for a Pokémon."""
        actions = []
        
        # Only active Pokémon can retreat or attack
        if pokemon == player.active_pokemon:
            # Get possible attacks
            possible_attacks = []
            if opponent.active_pokemon and not self.attack_prevention[0]:
                for attack_id in self.get_possible_attacks(pokemon, log_details=True):
                    # attack_id is already in format 'attack_89', so we use it directly
                    actions.append(f"use_{attack_id}")
                    possible_attacks.append(f"use_{attack_id}")
                
            if self.can_retreat(pokemon, player):
                actions.append("retreat")
            
            # If only retreat is available (no attacks possible), add option to cancel and go back to main menu
            if not possible_attacks and len(actions) == 1 and actions[0] == "retreat":
                actions.append("cancel")
        
        # Check for usable abilities
        if pokemon.ability_id and self.is_ability_conditions_met(pokemon, player, opponent):
            actions.append("use_ability")
            
        return actions

    def use_ability(self, pokemon: Pokemon, player: Player, opponent: Player) -> None:
        """Use a Pokémon's ability."""
        db = get_card_database()
        ability = db['abilities'][pokemon.ability_id]
        
        if ability.effect_type in self.effect_handler.ability_handlers:
            handler = self.effect_handler.ability_handlers[ability.effect_type]
            handler(player, opponent, ability, pokemon)
            
        # Mark ability as used if it has a limited number of uses
        if ability.amount_of_times == "once":
            pokemon.ability_used = True

    def can_retreat(self, pokemon: Pokemon, player: Player) -> bool:
        """Check if a Pokémon can retreat."""
        if not pokemon.can_retreat:
            return False
            
        retreat_cost = max(0, pokemon.retreat_cost - self.turn_state.retreat_cost_reduction)
        
        # Check if Pokemon has enough equipped energy to pay retreat cost
        total_energy = sum(pokemon.equipped_energies.values())
        return total_energy >= retreat_cost

    def retreat(self, pokemon: Pokemon, player: Player) -> None:
        """Retreat an active Pokémon to the bench."""
        if not player.bench_pokemons:
            return
            
        # Pay retreat cost
        retreat_cost = max(0, pokemon.retreat_cost - self.turn_state.retreat_cost_reduction)
        
        if self.debug:
            self.log(f"{player.name}'s {pokemon.name} retreats (cost: {retreat_cost} energy)")
            
        self.discard_energies(pokemon, retreat_cost, player)
        
        # Select new active Pokémon
        new_active = player.agent.get_chosen_card(player.bench_pokemons, self, "choose_new_active")
        
        if self.debug:
            self.log(f"{player.name} promotes {new_active.name} from bench to active")
        
        # Swap Pokémon
        player.bench_pokemons.remove(new_active)
        player.bench_pokemons.append(player.active_pokemon)
        player.active_pokemon = new_active

    def discard_energies(self, pokemon: Pokemon, amount: int, player: Player) -> None:
        """Discard energy cards from a Pokémon."""
        for _ in range(amount):
            energy_types = [et for et, count in pokemon.equipped_energies.items() if count > 0]
            if not energy_types:
                break
                
            energy_type = player.agent.get_action(energy_types, self, "choose_energy_to_discard")
            pokemon.equipped_energies[energy_type] -= 1

    def perform_attack(self, attack_id: str, attacker: Pokemon, defender: Pokemon, player: Player, opponent: Player) -> None:
        """Execute an attack."""
        db = get_card_database()
        if not db:
            if self.debug:
                self.log(f"Database not available for attack lookup: {attack_id}")
            return
            
        # attack_id should be in format 'attack_89'
        full_attack_id = f"attack_{attack_id}" if not attack_id.startswith("attack_") else attack_id
        
        if full_attack_id not in db['attacks']:
            if self.debug:
                self.log(f"Attack not found in database: {full_attack_id}")
            return
            
        attack = db['attacks'][full_attack_id]
        
        if not self.has_sufficient_energy(attacker, attack):
            if self.debug:
                self.log(f"{attacker.name} has insufficient energy for {attack.name}")
            return
            
        if self.debug:
            self.log(f"{attacker.name} uses {attack.name} for {attack.damage} damage!")
            
        # Handle special case for copy attack
        if attack.effect_type == "copy_attack":
            self.handle_copy_attack(attack, attacker, defender, player, opponent)
            # Set flag to end turn after attack
            self.turn_state.has_attacked = True
            return
            
        # Calculate damage
        damage = self.calculate_attack_damage(attack, attacker, defender, player, opponent)
        
        # Apply damage to defender
        lifesteal = attack.effect_type == "lifesteal"
        self.apply_damage(defender, damage, attacker, player, lifesteal)
        
        # Handle attack effects
        if attack.effect_type in self.effect_handler.attack_handlers:
            handler = self.effect_handler.attack_handlers[attack.effect_type]
            handler(attacker, defender, attack, player, opponent)
            
        # Set flag to end turn after attack
        self.turn_state.has_attacked = True
        
        # Display game state after attack in debug mode
        if self.debug:
            self.display_game_state_ascii()

    def handle_copy_attack(self, attack, attacker: Pokemon, defender: Pokemon, player: Player, opponent: Player) -> None:
        """Handle the copy attack effect."""
        # Get the opponent's last used attack
        if opponent.last_attack_used:
            db = get_card_database()
            copied_attack = db['attacks'][opponent.last_attack_used]
            
            # Calculate damage
            damage = self.calculate_attack_damage(copied_attack, attacker, defender, player, opponent)
            
            # Apply damage
            self.apply_damage(defender, damage, player)
            
            # Handle effects
            if copied_attack.effect_type in self.effect_handler.attack_handlers:
                handler = self.effect_handler.attack_handlers[copied_attack.effect_type]
                handler(attacker, defender, copied_attack, player, opponent)

    def has_sufficient_energy(self, pokemon: Pokemon, attack) -> bool:
        """Check if a Pokémon has sufficient energy for an attack."""
        # First, check specific energy requirements (non-normal)
        specific_energy_used = 0
        for energy_type, cost in attack.energy_cost.items():
            if cost > 0 and energy_type != 'normal':
                if energy_type not in pokemon.equipped_energies:
                    return False
                if pokemon.equipped_energies[energy_type] < cost:
                    return False
                specific_energy_used += cost
        
        # Then check if we have enough total energy for normal energy requirements
        normal_energy_needed = attack.energy_cost.get('normal', 0)
        if normal_energy_needed > 0:
            total_energy_available = sum(pokemon.equipped_energies.values())
            # Subtract already used specific energy
            remaining_energy = total_energy_available - specific_energy_used
            if remaining_energy < normal_energy_needed:
                return False
                
        return True

    def calculate_attack_damage(self, attack, attacker: Pokemon, defender: Pokemon, player: Player, opponent: Player) -> int:
        """Calculate the damage of an attack."""
        # Convert damage to int if it's a string
        try:
            base_damage = int(attack.damage)
        except (ValueError, TypeError):
            base_damage = 0
        
        # Apply weakness
        if defender.weakness == attacker.pokemon_type:
            base_damage += 20  # Pokemon TCG Pocket weakness adds +20 damage, not double damage
            
        # Apply resistance
        # (Not implemented in this version)
        
        # Apply shield
        if self.shield[0] > 0 and self.shield[1] == opponent:
            base_damage = max(0, base_damage - self.shield[0])
            
        # Apply damage reduction
        if self.damage_reduction[0] > 0 and self.damage_reduction[1] == opponent:
            base_damage = max(0, base_damage - self.damage_reduction[0])
            
        # Apply bonus damage effect
        if self.turn_state.bonus_damage_effect[0] > 0 and self.turn_state.bonus_damage_effect[1] == attacker.pokemon_type:
            base_damage += self.turn_state.bonus_damage_effect[0]
            
        # Handle attack effects
        if attack.effect_type in self.effect_handler.attack_handlers:
            handler = self.effect_handler.attack_handlers[attack.effect_type]
            base_damage = handler(attacker, defender, attack, player, opponent)
            
        return max(0, base_damage)

    def apply_damage(self, target: Pokemon, damage: int, attacker: Optional[Pokemon], attacker_player: Player, lifesteal: bool = False) -> None:
        """Apply damage to a Pokémon using damage counters."""
        if target.hiding:
            return
            
        # Add damage counters to the target Pokemon
        target.damage_taken += damage
        
        if self.debug:
            self.log(f"{target.name} takes {damage} damage (Total damage: {target.damage_taken}/{target.max_hp})")
        
        # Handle tool effects if damage is from an attack
        if attacker is not None and target.attached_tool:
            tool = target.attached_tool
            if tool.effect == "damage_reflect":
                amount = int(tool.special_values[0]) if isinstance(tool.special_values, list) else int(tool.special_values)
                self.apply_damage(attacker, amount, None, attacker_player, lifesteal=False)
            elif tool.effect == "poison_attacker":
                defender_player = self.player1 if target in self.player1.all_pokemons() else self.player2
                if target == defender_player.active_pokemon:
                    self.apply_status(attacker, "poisoned")
        
        # Handle lifesteal
        if lifesteal and attacker:
            heal_amount = min(damage, attacker.damage_taken)  # Can only heal up to damage taken
            attacker.damage_taken = max(0, attacker.damage_taken - heal_amount)
            if self.debug:
                self.log(f"{attacker.name} heals {heal_amount} damage (lifesteal)")
            
        # Check for knockout - Pokemon is knocked out when damage >= max_hp
        if target.damage_taken >= target.max_hp and not hasattr(target, '_knockout_processed'):
            target._knockout_processed = True  # Set flag immediately to prevent double-processing
            self.handle_knockout(target, attacker_player)
            return  # Exit immediately after knockout to prevent further processing

    def handle_knockout(self, pokemon: Pokemon, attacker_player: Player) -> None:
        """Handle a Pokémon being knocked out."""
        # Find the defender player by checking which player owns the knocked-out Pokemon
        defender_player = None
        if pokemon in self.player1.all_pokemons():
            defender_player = self.player1
        elif pokemon in self.player2.all_pokemons():
            defender_player = self.player2
        else:
            # Pokemon is not in either player's list, should not happen
            return
        
        # Award prize points - 2 for ex Pokemon (name ends with " ex"), 1 for normal Pokemon
        is_ex_pokemon = pokemon.name.endswith(" ex") if pokemon.name else False
        points_awarded = 2 if is_ex_pokemon else 1
        attacker_player.prize_points += points_awarded
        
        if self.debug:
            self.log(f"{pokemon.name} is knocked out! {attacker_player.name} gains {points_awarded} point(s)")
        
        # Detach and discard the tool if attached
        if pokemon.attached_tool:
            defender_player.discard_pile.append(pokemon.attached_tool)
            pokemon.attached_tool = None
        
        # Remove the knocked-out Pokémon
        if pokemon == defender_player.active_pokemon:
            defender_player.active_pokemon = None
            defender_player.discard_pile.append(pokemon)
            
            # Promote a bench Pokémon if available
            if defender_player.bench_pokemons:
                new_active = defender_player.agent.get_chosen_card(defender_player.bench_pokemons, self, "choose_new_active_knockout")
                defender_player.bench_pokemons.remove(new_active)
                defender_player.active_pokemon = new_active
                if self.debug:
                    self.log(f"{defender_player.name} promotes {new_active.name} from bench to active")
        elif pokemon in defender_player.bench_pokemons:
            defender_player.bench_pokemons.remove(pokemon)
            defender_player.discard_pile.append(pokemon)
            
        # Check for game end
        self.check_game_end()
        
        # Display game state after knockout in debug mode
        if self.debug:
            self.display_game_state_ascii()

    def play_trainer(self, trainer: Trainer, player: Player, opponent: Player) -> None:
        """Play a trainer card."""
        # Check if this is a Supporter
        is_supporter = getattr(trainer, 'is_supporter', True)
        
        if is_supporter and (self.turn_state.has_played_supporter or not player.can_play_trainer):
            return
            
        if is_supporter:
            self.turn_state.has_played_supporter = True
        
        if self.debug:
            self.log(f"{player.name} plays {trainer.name} (Trainer)")
        
        # Use the new handler system if the trainer has a handler
        if hasattr(trainer, 'handler') and trainer.handler:
            effect_handler = CardEffectHandler(self)
            
            if trainer.handler in effect_handler.trainer_handlers:
                handler_func = effect_handler.trainer_handlers[trainer.handler]
                # Call the handler with the trainer and its special values
                handler_func(player, opponent, trainer, trainer.special_values)
            else:
                if self.debug:
                    self.log(f"Warning: No handler found for {trainer.handler}")
        elif trainer.effect in self.effect_handler.trainer_handlers:
            # Legacy handling for trainers without handlers
            handler = self.effect_handler.trainer_handlers[trainer.effect]
            handler(player, opponent, trainer)
        else:
            # Fallback for any trainer effects not yet implemented in the handler
            if self.debug:
                self.log(f"Warning: No handler found for trainer effect '{trainer.effect}' on card '{trainer.name}'")
            
        player.discard_pile.append(trainer)

    def get_heal_targets(self, player: Player, heal_amount: int, target_type: str, targets: str) -> List[Pokemon]:
        """Get potential healing targets."""
        potential_targets = []
        
        if targets == "all":
            potential_targets = player.all_pokemons()
        elif targets == "benched":
            potential_targets = player.bench_pokemons
        elif targets == "active":
            potential_targets = [player.active_pokemon] if player.active_pokemon else []
            
        if target_type == "any":
            return [p for p in potential_targets if p.current_hp < p.max_hp]
        elif target_type == "damaged":
            return [p for p in potential_targets if p.current_hp < p.max_hp]
            
        return []

    def play_item(self, item: Item, player: Player) -> None:
        """Play an item card."""
        if self.debug:
            self.log(f"{player.name} plays {item.name} (Item)")
            
        # Use the new handler system if the item has a handler
        if hasattr(item, 'handler') and item.handler:
            from moteur.handlers.card_effect_handler import CardEffectHandler
            effect_handler = CardEffectHandler(self)
            
            if item.handler in effect_handler.item_handlers:
                handler_func = effect_handler.item_handlers[item.handler]
                # Call the handler with the item and its special values
                handler_func(player, self.get_opponent(), item, item.special_values)
            else:
                if self.debug:
                    self.log(f"Warning: No handler found for {item.handler}")
        elif item.effect == "search_pokemon":
            # Legacy handling for items without handlers
            # Search for Pokémon
            pokemon_type, amount = item.special_values
            matching_pokemon = [p for p in player.remaining_cards if p.card_type == "pokemon" and 
                               (p.pokemon_type == pokemon_type or pokemon_type == "any")]
            
            if matching_pokemon:
                for _ in range(min(amount, len(matching_pokemon))):
                    chosen = player.agent.get_chosen_card(matching_pokemon, self, "choose_pokemon_from_deck")
                    player.cards_in_hand.append(chosen)
                    player.remaining_cards.remove(chosen)
                    matching_pokemon.remove(chosen)
                    
                random.shuffle(player.remaining_cards)
        elif item.effect == "search_energy":
            # Legacy handling for items without handlers
            # Search for energy
            energy_type, amount = item.special_values
            player.energy_points[energy_type] += amount
        elif item.effect == "heal":
            # Legacy handling for items without handlers
            # Heal Pokémon
            heal_amount, target = item.special_values
            if target == "active" and player.active_pokemon:
                # Healing removes damage counters
                player.active_pokemon.damage_taken = max(0, player.active_pokemon.damage_taken - heal_amount)
                if self.debug:
                    self.log(f"{player.active_pokemon.name} heals {heal_amount} damage")
            elif target == "any":
                damaged = [p for p in player.all_pokemons() if p.damage_taken > 0]
                if damaged:
                    chosen = player.agent.get_chosen_card(damaged, self, "choose_pokemon_to_heal")
                    healed = min(heal_amount, chosen.damage_taken)
                    chosen.damage_taken = max(0, chosen.damage_taken - heal_amount)
                    if self.debug:
                        self.log(f"{chosen.name} heals {healed} damage")
                    
        player.discard_pile.append(item)
    
    def play_tool(self, tool: Tool, player: Player) -> None:
        """Attach a tool to a Pokémon."""
        eligible_pokemons = [p for p in player.all_pokemons() if p.attached_tool is None]
        if eligible_pokemons:
            target = player.agent.get_chosen_card(eligible_pokemons, self, "choose_pokemon_for_tool")
            if target:
                target.attached_tool = tool
                if self.debug:
                    self.log(f"{player.name} attaches {tool.name} (Tool) to {target.name}")
                if tool.effect == "hp_boost":
                    amount, type_condition = tool.special_values
                    amount = int(amount) if not isinstance(amount, int) else amount
                    if type_condition == "any" or target.pokemon_type == type_condition:
                        target.current_hp += amount

    def detach_tool(self, pokemon: Pokemon, causing_player: Player):
        """Detach a tool from a Pokémon and handle effects."""
        if pokemon.attached_tool:
            tool = pokemon.attached_tool
            pokemon.attached_tool = None
            owner_player = self.player1 if pokemon in self.player1.all_pokemons() else self.player2
            owner_player.discard_pile.append(tool)
            if tool.effect == "hp_boost":
                amount, type_condition = tool.special_values
                amount = int(amount) if not isinstance(amount, int) else amount
                if type_condition == "any" or pokemon.pokemon_type == type_condition:
                    pokemon.current_hp = max(pokemon.current_hp - amount, 0)
                    if pokemon.current_hp <= 0:
                        self.handle_knockout(pokemon, causing_player)

    def end_turn(self) -> None:
        """End the current turn."""
        # Discard unused energy from Energy Zone
        if self.current_player.energy_zone:
            if self.debug:
                discarded_energy = ", ".join(self.current_player.energy_zone)
                self.log(f"{self.current_player.name} discards unused energy: {discarded_energy}")
            self.current_player.energy_zone.clear()
        
        # Reset temporary effects
        self.reset_temporary_effects()
        
        # Handle status effects for active Pokémon
        player = self.current_player
        opponent = self.get_opponent()
        
        if player.active_pokemon:
            pokemon = player.active_pokemon
            if "asleep" in pokemon.effect_status:
                if random.choice([True, False]):
                    pokemon.effect_status.remove("asleep")
                    if self.debug:
                        self.log(f"{pokemon.name} wakes up from sleep")
                elif self.debug:
                    self.log(f"{pokemon.name} remains asleep")
            if "poisoned" in pokemon.effect_status:
                if self.debug:
                    self.log(f"{pokemon.name} takes 10 poison damage at end of turn")
                self.apply_damage(pokemon, 10, None, opponent)
            elif "super_poisoned" in pokemon.effect_status:
                if self.debug:
                    self.log(f"{pokemon.name} takes 20 super poison damage at end of turn")
                self.apply_damage(pokemon, 20, None, opponent)
        
        # Clean up any knocked-out Pokemon that might have been missed
        self.cleanup_knocked_out_pokemon()
        
        # Debug output: Show Pokemon status for both players with point tracking
        if self.debug:
            for p in [self.player1, self.player2]:
                if p.active_pokemon:
                    active_hp = f"{p.active_pokemon.current_hp}/{p.active_pokemon.max_hp}"
                    # Add energy information if Pokemon has energy
                    active_energy_str = ""
                    if p.active_pokemon.equipped_energies:
                        energy_info = []
                        for energy_type, count in p.active_pokemon.equipped_energies.items():
                            if count > 0:
                                energy_info.append(f"{energy_type.capitalize()}: {count}")
                        if energy_info:
                            active_energy_str = f" [{', '.join(energy_info)}]"
                    active_name = f"{p.active_pokemon.name} ({active_hp}){active_energy_str}"
                else:
                    active_name = "None"
                    
                if p.bench_pokemons:
                    bench_info = []
                    for pokemon in p.bench_pokemons:
                        bench_hp = f"{pokemon.current_hp}/{pokemon.max_hp}"
                        # Add energy information if Pokemon has energy
                        bench_energy_str = ""
                        if pokemon.equipped_energies:
                            energy_info = []
                            for energy_type, count in pokemon.equipped_energies.items():
                                if count > 0:
                                    energy_info.append(f"{energy_type.capitalize()}: {count}")
                            if energy_info:
                                bench_energy_str = f" [{', '.join(energy_info)}]"
                        bench_info.append(f"{pokemon.name} ({bench_hp}){bench_energy_str}")
                    bench_str = ", ".join(bench_info)
                else:
                    bench_str = "None"
                    
                self.log(f"    {p.name} - Active Pokemon: {active_name}; Benched Pokemon: {bench_str}; Points: {p.prize_points}")
                
                # Add hand information
                hand_names = [card.name for card in p.cards_in_hand if card is not None]
                hand_str = ", ".join(hand_names) if hand_names else "None"
                self.log(f"    {p.name} - Hand: {hand_str}")
                
        # Switch current player
        self.current_player = opponent

    def cleanup_knocked_out_pokemon(self) -> None:
        """Clean up any Pokemon with 0 or negative HP that should be knocked out."""
        for player in [self.player1, self.player2]:
            opponent = self.player2 if player == self.player1 else self.player1
            
            # Check active Pokemon
            if player.active_pokemon and player.active_pokemon.current_hp <= 0 and not hasattr(player.active_pokemon, '_knockout_processed'):
                player.active_pokemon._knockout_processed = True
                self.handle_knockout(player.active_pokemon, opponent)
                
            # Check bench Pokemon
            knocked_out_bench = []
            for pokemon in player.bench_pokemons:
                if pokemon.current_hp <= 0 and not hasattr(pokemon, '_knockout_processed'):
                    pokemon._knockout_processed = True
                    knocked_out_bench.append(pokemon)
                    
            for pokemon in knocked_out_bench:
                self.handle_knockout(pokemon, opponent)

    def handle_status_effects(self, pokemon: Pokemon, opponent: Player) -> None:
        """Handle status effects at the start of a turn."""
        # Check if Pokémon is paralyzed
        if "paralyzed" in pokemon.effect_status:
            pokemon.effect_status.remove("paralyzed")
            return True  # Skip this Pokémon's actions
            
        # Check if Pokémon is asleep
        if "asleep" in pokemon.effect_status:
            return True  # Skip this Pokémon's actions
            
        return False

    def reset_temporary_effects(self) -> None:
        """Reset temporary effects at the end of a turn."""
        # Reset shield
        self.shield = (0, None)
        
        # Reset damage reduction
        self.damage_reduction = (0, None)
        
        # Reset attack prevention
        if self.attack_prevention[0]:
            self.attack_prevention = (False, None)
            
        # Reset Pokémon effects
        self.current_player.reset_effects()
        self.get_opponent().reset_effects()

    def check_game_end(self) -> None:
        """Check if the game has ended."""
        # Check for win by prize points or tie
        if self.player1.prize_points >= self.WINNING_POINTS and self.player2.prize_points >= self.WINNING_POINTS:
            # Both players have 3+ points - it's a tie
            self.winner = "tie"
            if self.debug:
                self.log("Game ends in a tie - both players reached 3 points")
        elif self.player1.prize_points >= self.WINNING_POINTS:
            self.winner = self.player1
        elif self.player2.prize_points >= self.WINNING_POINTS:
            self.winner = self.player2
            
        # Check for win by opponent having no Pokémon
        if not self.player1.has_pokemons():
            self.winner = self.player2
        elif not self.player2.has_pokemons():
            self.winner = self.player1
            
        # Note: No deck-out loss conditions in Pokemon TCG Pocket

    def get_playable_cards(self, player: Player, opponent: Player) -> List[Union[Pokemon, Trainer, Item]]:
        """Get cards that can be played from hand."""
        playable = []
        for card in player.cards_in_hand:
            is_playable = self.conditions_are_met(card, card.card_type, player, opponent)
            if self.debug and card.card_type == "pokemon" and hasattr(card, 'evolves_from') and card.evolves_from:
                targets = self.get_evolvable_pokemon(card, player)
                self.log(f"Evolution check for {card.name} (evolves from {card.evolves_from}): found {len(targets)} targets, playable: {is_playable}")
                for pokemon in player.all_pokemons():
                    turns_info = getattr(pokemon, 'turns_in_play', 'unknown')
                    self.log(f"  - {pokemon.name}: turns_in_play={turns_info}, matches evolves_from={pokemon.name == card.evolves_from}")
            if is_playable:
                playable.append(card)
        return playable

    def conditions_are_met(self, card, card_type: str, player: Player, opponent: Player) -> bool:
        """Check if conditions are met to play a card."""
        if card_type == "pokemon":
            return self.check_pokemon_conditions(card, player, opponent)
        elif card_type == "trainer":
            return self.check_trainer_conditions(card, player, opponent)
        elif card_type == "item":
            return self.check_item_conditions(card, player, opponent)
        elif card_type == "tool":
            return any(p.attached_tool is None for p in player.all_pokemons())
        return False
    

    def check_trainer_conditions(self, trainer: Trainer, player: Player, opponent: Player) -> bool:
        """Check if conditions are met to play a trainer card."""
        if not player.can_play_trainer:
            return False
        
        # Check if this is a Supporter and if we've already played one
        is_supporter = getattr(trainer, 'is_supporter', True)  # Most trainers are supporters by default
        if is_supporter and self.turn_state.has_played_supporter:
            return False
            
        # Check conditions based on trainer effect
        if trainer.effect == "heal":
            # Healing cards - check if there are damaged Pokémon to heal
            heal_amount, target_type, targets = trainer.special_values
            heal_targets = self.get_heal_targets(player, heal_amount, target_type, targets)
            return bool(heal_targets)
        elif trainer.effect in ["poison", "sleep", "paralyze"]:
            # Status effect cards - need opponent's active Pokémon
            return opponent.active_pokemon is not None
        elif trainer.effect in ["attach_energy_from_discard", "attach_energy_end_turn", "attach_random_energy"]:
            # Energy cards - always playable
            return True
        elif trainer.effect == "bonus_damage":
            # Damage bonus cards - need own active Pokémon
            return player.active_pokemon is not None
        elif trainer.effect == "send_to_hand":
            # Card recovery
            target_type, max_amount, target_player = trainer.special_values
            target = player if target_player == "self" else opponent
            eligible_cards = [c for c in target.discard_pile if c.card_type == target_type]
            return bool(eligible_cards)
        elif trainer.effect == "draw":
            # Draw cards
            return bool(player.remaining_cards)
        elif trainer.effect in self.effect_handler.trainer_handlers:
            # For other effects handled by the effect handler, assume they're playable
            # Individual handlers can implement their own condition checking if needed
            return True
            
        return True

    def check_item_conditions(self, item: Item, player: Player, opponent: Player) -> bool:
        """Check if conditions are met to play an item card."""
        if item.effect == "search_pokemon":
            pokemon_type, amount = item.special_values
            matching_pokemon = [p for p in player.remaining_cards if p.card_type == "pokemon" and 
                               (p.pokemon_type == pokemon_type or pokemon_type == "any")]
            return bool(matching_pokemon)
        elif item.effect == "heal":
            heal_amount, target = item.special_values
            if target == "active":
                return player.active_pokemon and player.active_pokemon.damage_taken > 0
            elif target == "any":
                return any(p.damage_taken > 0 for p in player.all_pokemons())
                
        return True

    def check_pokemon_conditions(self, pokemon: Pokemon, player: Player, opponent: Player) -> bool:
        """Check if conditions are met to play a Pokémon card."""
        if pokemon.stage == "basic" or "ex" in pokemon.stage or pokemon.stage == "fossil":
            return not player.active_pokemon or len(player.bench_pokemons) < self.MAX_BENCH_SIZE
        else:
            return bool(self.get_evolvable_pokemon(pokemon, player))

    def is_ability_conditions_met(self, pokemon: Pokemon, player: Player, opponent: Player) -> bool:
        """Check if conditions are met to use an ability."""
        db = get_card_database()
        ability = db['abilities'][pokemon.ability_id]
        
        # Check if ability has already been used this turn
        if ability.amount_of_times == "once" and pokemon.ability_used:
            return False
            
        if ability.effect_type == "heal_all":
            return any(p.current_hp < p.max_hp for p in player.all_pokemons())
        elif ability.effect_type == "switch_active":
            target, who_chooses = ability.special_values
            target_player = opponent if target == "enemy" else player
            return bool(target_player.bench_pokemons)
        elif ability.effect_type == "damage_enemy":
            targets, _ = ability.special_values
            return bool(self.get_targets(opponent, targets, "damage"))
        elif ability.effect_type == "gain_energy":
            target, _, pokemon_type, _ = ability.special_values
            if target == "self":
                return True
            elif target == "active":
                return player.active_pokemon and (pokemon_type == "any" or player.active_pokemon.pokemon_type == pokemon_type)
            elif target == "bench":
                return any(p.pokemon_type == pokemon_type or pokemon_type == "any" for p in player.bench_pokemons)
        elif ability.effect_type == "sleep":
            return opponent.active_pokemon is not None
        elif ability.effect_type == "poison":
            _, from_where, target = ability.special_values
            if from_where == "active" and pokemon != player.active_pokemon:
                return False
            if from_where == "bench" and pokemon not in player.bench_pokemons:
                return False
            return bool(self.get_targets(opponent, target, "poison"))
            
        return True

    def get_possible_attacks(self, pokemon: Pokemon, log_details: bool = False) -> List[str]:
        """Get list of attacks that can be used."""
        possible_attacks = []
        
        # Safety check: ensure Pokemon is still in play and has positive HP
        if pokemon.current_hp <= 0:
            return possible_attacks
            
        # Safety check: ensure Pokemon is still owned by a player
        if pokemon not in self.player1.all_pokemons() and pokemon not in self.player2.all_pokemons():
            return possible_attacks
        
        db = get_card_database()
        
        if not db:
            if self.debug and log_details:
                self.log(f"Database not available for {pokemon.name}")
            return possible_attacks
        
        for attack_id in pokemon.attack_ids:
            if attack_id not in db['attacks']:
                if self.debug and log_details:
                    self.log(f"Attack {attack_id} not found in database for {pokemon.name}")
                continue
                
            attack = db['attacks'][attack_id]

            if self.has_sufficient_energy(pokemon, attack):
                possible_attacks.append(attack_id)
                if self.debug and log_details:
                    self.log(f"{pokemon.name} can use {attack.name} (has sufficient energy)")
            elif self.debug and log_details:
                # Filter energy requirements and current energies to only show non-zero values
                needed_energy = {k: v for k, v in attack.energy_cost.items() if v > 0}
                current_energy = {k: v for k, v in pokemon.equipped_energies.items() if v > 0}
                self.log(f"{pokemon.name} cannot use {attack.name} - needs {needed_energy}, has {current_energy}")
                
        return possible_attacks

    def get_possible_actions(self, playable_cards: List) -> List[str]:
        """Get list of possible actions for the current player."""
        actions = ["end_turn"]
        
        # Check for energy attachment from Energy Zone
        if not self.turn_state.has_attached_energy and self.current_player.energy_zone:
            actions.append("attach_energy")
            
        if playable_cards:
            actions.append("play_card")
            
        if any(self.get_pokemon_actions(p, self.current_player, self.get_opponent()) for p in self.current_player.all_pokemons()):
            actions.append("pokemon_action")
            
        # Allow evolution if there are any Pokemon that can evolve (not restricted by turn limit)
        if self.get_possible_evolutions(self.current_player):
            actions.append("evolve")
            
        return actions

    def evolve_pokemon(self, evolution: Pokemon, target: Pokemon, player: Player) -> None:
        """Evolve a Pokémon into its next stage."""
        # Track that this specific Pokemon has evolved this turn (not just any Pokemon)
        evolution.evolved_this_turn = True
        
        # Transfer damage counters and other status
        damage_transferred = target.damage_taken
        evolution.damage_taken = damage_transferred
        evolution.equipped_energies = target.equipped_energies.copy()
        evolution.effect_status = target.effect_status[:]
        evolution.attached_tool = target.attached_tool
        
        # Remove evolved Pokemon from turn tracking if it was there
        if target in self.turn_state.evolved_pokemon_this_turn:
            self.turn_state.evolved_pokemon_this_turn.remove(target)
        
        # Add the new evolution to tracking
        self.turn_state.evolved_pokemon_this_turn.append(evolution)
        
        if target == player.active_pokemon:
            player.active_pokemon = evolution
            if self.debug:
                message = f"{player.name} evolves {target.name} into {evolution.name} on active"
                if damage_transferred > 0:
                    message += f" with {damage_transferred} damage"
                self.log(message)
        else:
            for i, pokemon in enumerate(player.bench_pokemons):
                if pokemon == target:
                    player.bench_pokemons[i] = evolution
                    if self.debug:
                        message = f"{player.name} evolves {target.name} into {evolution.name} on bench"
                        if damage_transferred > 0:
                            message += f" with {damage_transferred} damage"
                        self.log(message)
                    break
        
        player.remaining_cards.append(evolution)

    def get_possible_evolutions(self, player: Player) -> List[Tuple[Pokemon, List[Pokemon]]]:
        """Get possible evolution cards and their targets."""
        evolutions = []
        
        # Pokemon TCG Rule: No evolution on the first turn of the game for either player
        if self.turn <= 2:
            if self.debug:
                self.log(f"No evolution allowed on turn {self.turn} (first turn rule)")
            return evolutions
        
        for card in player.cards_in_hand:
            if card.card_type == "pokemon" and card.stage != "basic" and "ex" not in card.stage:
                targets = self.get_evolvable_pokemon(card, player)
                if targets:
                    evolutions.append((card, targets))
                    
        if self.debug and evolutions:
            evolved_count = len(self.turn_state.evolved_pokemon_this_turn)
            self.log(f"Found {len(evolutions)} possible evolutions, {evolved_count} Pokemon already evolved this turn")
            
        return evolutions

    def get_opponent(self) -> Player:
        """Get the opponent of the current player."""
        return self.player2 if self.current_player == self.player1 else self.player1

    def select_target(self, player: Player, opponent: Player, targets: str, context: str) -> Optional[Pokemon]:
        """Select a target Pokémon based on target type."""
        all_targets = self.get_targets(opponent, targets, context)
        if not all_targets:
            return None
            
        return player.agent.get_chosen_card(all_targets, self, f"select_target_{context}")

    def get_targets(self, opponent: Player, target: str, status: str) -> List[Pokemon]:
        """Get list of potential targets based on target type."""
        if target == "active" and opponent.active_pokemon:
            return [opponent.active_pokemon]
        elif target == "bench":
            return opponent.bench_pokemons
        elif target == "any":
            return opponent.all_pokemons()
            
        return []

    def apply_status(self, pokemon: Pokemon, status: str) -> None:
        """Apply a status effect to a Pokémon."""
        if not pokemon or pokemon.hiding:
            return
            
        # Clear incompatible statuses
        if status == "asleep" or status == "paralyzed":
            if "asleep" in pokemon.effect_status:
                pokemon.effect_status.remove("asleep")
            if "paralyzed" in pokemon.effect_status:
                pokemon.effect_status.remove("paralyzed")
                
        # Apply new status
        if status not in pokemon.effect_status:
            pokemon.effect_status.append(status)
            
        # Handle poisoned/super_poisoned replacement
        if status == "poisoned" and "super_poisoned" in pokemon.effect_status:
            pokemon.effect_status.remove("super_poisoned")
        elif status == "super_poisoned" and "poisoned" in pokemon.effect_status:
            pokemon.effect_status.remove("poisoned")
            
    def setup_active_pokemon(self, player: Player) -> None:
        """Set up the initial active Pokémon and handle mulligans."""
        basic_pokemons = get_basic_pokemons(player.cards_in_hand)
        
        if not basic_pokemons:
            # Mulligan: reveal hand, reshuffle, and draw a new hand
            if self.debug:
                hand_names = [card.name for card in player.cards_in_hand]
                self.log(f"{player.name} has no basic Pokemon in hand {hand_names} - taking a mulligan (redrawing until basic Pokemon found)")
            
            player.remaining_cards += player.cards_in_hand
            player.cards_in_hand = []
            random.shuffle(player.remaining_cards)
            
            for _ in range(5):
                player.cards_in_hand.append(player.remaining_cards.pop())
            
            if self.debug:
                new_hand_names = [card.name for card in player.cards_in_hand]
                self.log(f"{player.name} draws new hand after mulligan: {new_hand_names}")
                
            # Recursively try again until we get basic Pokemon
            self.setup_active_pokemon(player)
        else:
            if self.debug:
                basic_names = [pokemon.name for pokemon in basic_pokemons]
                self.log(f"{player.name} has basic Pokemon available: {basic_names}")
            
            # Choose a basic Pokémon as active
            active = player.agent.get_chosen_card(basic_pokemons, self, "choose_active")
            
            # Find and remove the active Pokemon from hand by matching properties
            # instead of relying on object identity
            removed = False
            for i, card in enumerate(player.cards_in_hand):
                if (hasattr(card, 'card_id') and hasattr(active, 'card_id') and 
                    card.card_id == active.card_id and 
                    hasattr(card, 'name') and hasattr(active, 'name') and 
                    card.name == active.name):
                    player.cards_in_hand.pop(i)
                    active = card  # Use the actual card from the hand
                    removed = True
                    break
            
            if not removed:
                # Fallback: try to find by name and type
                for i, card in enumerate(player.cards_in_hand):
                    if (hasattr(card, 'name') and hasattr(active, 'name') and 
                        card.name == active.name and 
                        hasattr(card, 'card_type') and card.card_type == "pokemon"):
                        player.cards_in_hand.pop(i)
                        active = card  # Use the actual card from the hand
                        removed = True
                        break
            
            if not removed:
                # Final fallback: try the original method
                try:
                    player.cards_in_hand.remove(active)
                except ValueError:
                    # If we still can't find it, log the error and use the first basic Pokemon
                    if self.debug:
                        self.log(f"Warning: Could not find selected Pokemon {active.name} in hand, using first basic Pokemon")
                    if basic_pokemons:
                        active = basic_pokemons[0]
                        # Try to remove it from hand
                        for i, card in enumerate(player.cards_in_hand):
                            if (hasattr(card, 'name') and card.name == active.name and 
                                hasattr(card, 'card_type') and card.card_type == "pokemon"):
                                player.cards_in_hand.pop(i)
                                active = card
                                break
            
            active.turns_in_play = 0  # Initialize turn tracking
            player.active_pokemon = active
            
            if self.debug:
                self.log(f"{player.name} places {active.name} as active Pokemon")
            
            # Ask player whether to place additional basic Pokemon on bench (up to bench limit)
            remaining_basics = get_basic_pokemons(player.cards_in_hand)
            while remaining_basics and len(player.bench_pokemons) < self.MAX_BENCH_SIZE:
                # Offer choice: place on bench or keep in hand
                bench_choice = player.agent.get_action(["place_on_bench", "keep_in_hand"], self, "initial_bench_choice")
                
                if bench_choice == "place_on_bench":
                    choice = player.agent.get_chosen_card(remaining_basics, self, "choose_bench")
                    
                    # Find and remove the bench Pokemon from hand by matching properties
                    removed = False
                    for i, card in enumerate(player.cards_in_hand):
                        if (hasattr(card, 'card_id') and hasattr(choice, 'card_id') and 
                            card.card_id == choice.card_id and 
                            hasattr(card, 'name') and hasattr(choice, 'name') and 
                            card.name == choice.name):
                            player.cards_in_hand.pop(i)
                            choice = card  # Use the actual card from the hand
                            removed = True
                            break
                    
                    if not removed:
                        # Fallback: try to find by name and type
                        for i, card in enumerate(player.cards_in_hand):
                            if (hasattr(card, 'name') and hasattr(choice, 'name') and 
                                card.name == choice.name and 
                                hasattr(card, 'card_type') and card.card_type == "pokemon"):
                                player.cards_in_hand.pop(i)
                                choice = card  # Use the actual card from the hand
                                removed = True
                                break
                    
                    if not removed:
                        # Final fallback
                        try:
                            player.cards_in_hand.remove(choice)
                        except ValueError:
                            if self.debug:
                                self.log(f"Warning: Could not find selected bench Pokemon {choice.name} in hand")
                            continue
                    
                    choice.turns_in_play = 0  # Initialize turn tracking
                    player.bench_pokemons.append(choice)
                    remaining_basics.remove(choice)
                    
                    if self.debug:
                        self.log(f"{player.name} places {choice.name} on bench (position {len(player.bench_pokemons)})")
                else:
                    # Player chooses to keep remaining basics in hand
                    break
            
            if self.debug:
                final_hand_names = [card.name for card in player.cards_in_hand]
                self.log(f"{player.name} setup complete - remaining hand: {final_hand_names}")

    def simulate_match(self) -> Player:
        """Simulate a complete match and return the winner."""
        MAX_TURNS = 50  # Prevent infinite loops
        
        # Coin flip for who goes first
        self.first_player = random.choice([self.player1, self.player2])
        if self.debug:
            self.log(f"Coin flip result: {self.first_player.name} goes first!")
        
        # Set initial active player
        self.current_player = self.first_player
        
        while not self.winner and self.turn < MAX_TURNS:
            self.simulate_turn()
            
        # If we hit max turns without a winner, declare winner based on remaining HP
        if not self.winner and self.turn >= MAX_TURNS:
            if self.debug:
                self.log(f"Maximum turns ({MAX_TURNS}) reached. Determining winner by remaining HP.")
            
            p1_total_hp = sum(p.current_hp for p in self.player1.all_pokemons())
            p2_total_hp = sum(p.current_hp for p in self.player2.all_pokemons())
            
            if p1_total_hp > p2_total_hp:
                self.winner = self.player1
            elif p2_total_hp > p1_total_hp:
                self.winner = self.player2
            else:
                # Tie - randomly choose winner
                self.winner = random.choice([self.player1, self.player2])
                
            if self.debug:
                self.log(f"Winner by HP: {self.winner.name} ({p1_total_hp} vs {p2_total_hp})")
        
        return self.winner 

    def display_game_state_ascii(self):
        """Display the current game state in ASCII art format for debug mode."""
        if not self.debug:
            return
            
        print(f"\n" + "=" * 80)
        print(f"🎮 POKEMON TCG POCKET - TURN {self.turn} 🎮")
        print(f"Current Player: {self.current_player.name}")
        print("=" * 80)
        
        opponent = self.get_opponent()
        
        # Show opponent's Pokemon (top of screen)
        print(f"\n🔴 {opponent.name}'s Pokemon:")
        print("-" * 60)
        
        # Opponent's active Pokemon
        if opponent.active_pokemon:
            active = opponent.active_pokemon
            energy_str = self._format_energy_display(active.equipped_energies)
            attacks_str = self._format_attacks_display(getattr(active, 'attacks', []))
            print(f"  🥊 Active: {active.name} ({active.current_hp}/{active.max_hp} HP) {energy_str}")
            if attacks_str:
                print(f"       Attacks: {attacks_str}")
        else:
            print(f"  🥊 Active: None")
        
        # Opponent's bench
        if opponent.bench_pokemons:
            print(f"  🪑 Bench: {len(opponent.bench_pokemons)} Pokemon")
            for i, pokemon in enumerate(opponent.bench_pokemons, 1):
                energy_str = self._format_energy_display(pokemon.equipped_energies)
                attacks_str = self._format_attacks_display(getattr(pokemon, 'attacks', []))
                print(f"    {i}. {pokemon.name} ({pokemon.current_hp}/{pokemon.max_hp} HP) {energy_str}")
                if attacks_str:
                    print(f"       Attacks: {attacks_str}")
        else:
            print(f"  🪑 Bench: Empty")
        
        print("\n" + "~" * 60)
        print("                    ⚡ BATTLE FIELD ⚡")
        print("~" * 60 + "\n")
        
        # Show current player's Pokemon (bottom of screen)
        print(f"🔵 {self.current_player.name}'s Pokemon:")
        print("-" * 60)
        
        # Current player's active Pokemon
        if self.current_player.active_pokemon:
            active = self.current_player.active_pokemon
            energy_str = self._format_energy_display(active.equipped_energies)
            attacks_str = self._format_attacks_display(getattr(active, 'attacks', []))
            print(f"  🥊 Active: {active.name} ({active.current_hp}/{active.max_hp} HP) {energy_str}")
            if attacks_str:
                print(f"       Attacks: {attacks_str}")
        else:
            print(f"  🥊 Active: None")
        
        # Current player's bench
        if self.current_player.bench_pokemons:
            print(f"  🪑 Bench: {len(self.current_player.bench_pokemons)} Pokemon")
            for i, pokemon in enumerate(self.current_player.bench_pokemons, 1):
                energy_str = self._format_energy_display(pokemon.equipped_energies)
                attacks_str = self._format_attacks_display(getattr(pokemon, 'attacks', []))
                print(f"    {i}. {pokemon.name} ({pokemon.current_hp}/{pokemon.max_hp} HP) {energy_str}")
                if attacks_str:
                    print(f"       Attacks: {attacks_str}")
        else:
            print(f"  🪑 Bench: Empty")
        
        print("\n" + "=" * 80)
        
        # Show game state information
        print(f"📊 Game Status:")
        print(f"  🔴 {opponent.name}: Hand: {len(opponent.cards_in_hand)} cards | Deck: {len(opponent.remaining_cards)} cards | Energy Zone: {len(opponent.energy_zone)}")
        print(f"  🔵 {self.current_player.name}: Hand: {len(self.current_player.cards_in_hand)} cards | Deck: {len(self.current_player.remaining_cards)} cards | Energy Zone: {len(self.current_player.energy_zone)}")
        
        # Show current player's hand (for debug purposes)
        if self.current_player.cards_in_hand:
            print(f"\n🔵 {self.current_player.name}'s Hand:")
            for i, card in enumerate(self.current_player.cards_in_hand, 1):
                card_details = self._format_card_details(card)
                print(f"  {i}. {card_details}")
        
        # Show energy zones
        if self.current_player.energy_zone:
            print(f"\n⚡ {self.current_player.name}'s Energy Zone: {', '.join(self.current_player.energy_zone)}")
        if opponent.energy_zone:
            print(f"⚡ {opponent.name}'s Energy Zone: {', '.join(opponent.energy_zone)}")
        
        print("=" * 80 + "\n")

    def _format_energy_display(self, equipped_energies):
        """Format energy display for Pokemon."""
        if not equipped_energies:
            return ""
        energies = [f"{count}x{energy}" for energy, count in equipped_energies.items() if count > 0]
        return f"⚡ {', '.join(energies)}" if energies else ""
    
    def _format_attacks_display(self, attacks):
        """Format attacks display for Pokemon."""
        if not attacks:
            return ""
        attack_strings = []
        for attack in attacks:
            cost_str = ""
            if hasattr(attack, 'energy_cost') and attack.energy_cost:
                costs = []
                for energy, count in attack.energy_cost.items():
                    if count > 0:
                        energy_abbrev = energy[0].upper()
                        costs.append(f"{count}{energy_abbrev}")
                if costs:
                    cost_str = f"[{'/'.join(costs)}] "
            damage_str = f"{attack.damage}" if hasattr(attack, 'damage') and attack.damage else "?"
            attack_strings.append(f"{attack.name} {cost_str}{damage_str}")
        return " | ".join(attack_strings)
    
    def _format_card_details(self, card):
        """Format detailed card information for debug display."""
        if not hasattr(card, 'card_type'):
            return str(card)
            
        card_type = getattr(card, 'card_type', 'unknown')
        if card_type == 'pokemon':
            hp = getattr(card, 'max_hp', '?')
            stage = getattr(card, 'stage', 'unknown')
            attacks_str = self._format_attacks_display(getattr(card, 'attacks', []))
            base_info = f"{card.name} ({stage}, {hp} HP)"
            if attacks_str:
                return f"{base_info} - Attacks: {attacks_str}"
            return base_info
        elif card_type == 'energy':
            energy_type = getattr(card, 'energy_type', 'unknown')
            return f"{card.name} ({energy_type} energy)"
        else:
            return f"{card.name} ({card_type})" 
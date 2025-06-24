import random
import sys
import os
from typing import List, Dict, Optional, Tuple, Union, Any
from dataclasses import dataclass, field
from enum import Enum

from models.match.player import Player
from models.cards.pokemon import Pokemon
from models.cards.card import Card
from models.cards.energy import Energy
from models.match.game_rules import GameRules

"""Core battle engine - simplified and modular"""
class BattleEngine:
    def __init__(self, player1: Player, player2: Player, debug: bool = False):
        self.players = [player1, player2]
        self.debug = debug

        self.current_player_index = 0
        self.turn = 0
        self.phase = GameRules.GamePhase.SETUP
    
    def start_battle(self) -> Optional[Player]:
        """Main battle execution"""
        try:
            self._setup_game()
            
            while not self._is_game_over():
                self._execute_turn()
            return self._determine_winner()
        except Exception as e:
            self.log(f"Battle error: {e}")
            return None
        


    
    def log(self, message: str):
        # TODO: Make logging correpsondant with the agent. Like if it's a human,
        # it should print to the console or maybe have more. 
        # It it's the AI it might be best to print errors or something.
        if self.debug:
            print(f"[Turn {self.turn}] {message}")
        
    #### PRIVATE METHODS ####

    def _setup_game(self):
        """Initialize game state"""
        self.log("Setting up battle...")

        self._determine_first_player()
        
        # Setup both players
        for player in self.players:
            self._setup_player(player)

        # Each player gets a turn zero
        for i in range(2):
            self._turn_zero(self._get_current_player, self._get_opponent)
            self._switch_players()
    
    def _determine_first_player(self):
        """Determine which player goes first"""
        self.players.shuffle()
        self.log(f"{self.players[0].name} goes first!")

        self.current_player_index = 0
    
    def _setup_player(self, player: Player):
        """Setup individual player by drawing initial hand and adding energies to energy zone"""
        # Draw initial hand
        player.draw_inital_hand()
        player.add_energies_to_energy_zone()

    def _switch_players(self):
        self.current_player_index = 1 - self.current_player_index

    def _get_current_player(self) -> Player:
        return self.players[self.current_player_index]
    
    def _get_opponent(self) -> Player:
        return self.players[1 - self.current_player_index]
    

    def _turn_zero(self, player: Player, opponent: Player):
        """Execute turn zero for a player"""
        player_state = self._get_player_state(player, opponent)
        self.log(f"{player_state}")
        
        # Get Actions
        actions = player._get_turn_zero_actions()

        # Play Action
        player.agent.play_action(actions)

    def _get_player_state(self, player: Player, opponent: Player) -> str:
        """Get the state for a player as a string representation of the board"""
        return self.generate_board_view(player, opponent)
    
    def generate_board_view(self, player: Player, opponent: Player) -> str:
        """Generate a complete board view from the player's perspective"""
        lines = []
        
        # Header
        lines.append("=" * 80)
        lines.append(f"POKEMON TCG BATTLE - {player.name}'s Turn")
        lines.append("=" * 80)
        lines.append("")
        
        # Opponent's section
        lines.append("OPPONENT'S FIELD:")
        lines.append("-" * 40)
        
        # Opponent's points and deck info
        lines.append(f"Opponent: {opponent.name} | Points: {opponent.points}")
        lines.append(f"Cards in deck: {len(opponent.deck)} | Cards in hand: {len(opponent.cards_in_hand)}")
        lines.append(f"Current Energy: {opponent.energy_zone_curent_energy or 'None'} | Next Energy: {opponent.energy_zone_next_energy or 'None'}")
        lines.append("")
        
        # Opponent's bench
        lines.append("Opponent's Bench:")
        for i, pokemon in enumerate(opponent.bench_pokemons):
            if pokemon:
                lines.append(f"  Bench {i+1}: {pokemon.name} [{pokemon.element.upper()}] HP: {pokemon.current_health()}/{pokemon.health}")
            else:
                lines.append(f"  Bench {i+1}: [Empty]")
        lines.append("")
        
        # Opponent's active Pokemon
        lines.append("Opponent's Active Pokemon:")
        if opponent.active_pokemon:
            lines.append(self._indent_text(opponent.active_pokemon.to_display_string(), 2))
        else:
            lines.append("  [No Active Pokemon]")
        lines.append("")
        
        # Battle zone separator
        lines.append("~" * 80)
        lines.append(" " * 35 + "BATTLE ZONE")
        lines.append("~" * 80)
        lines.append("")
        
        # Player's active Pokemon
        lines.append("Your Active Pokemon:")
        if player.active_pokemon:
            lines.append(self._indent_text(player.active_pokemon.to_display_string(), 2))
        else:
            lines.append("  [No Active Pokemon]")
        lines.append("")
        
        # Player's bench
        lines.append("Your Bench:")
        for i, pokemon in enumerate(player.bench_pokemons):
            if pokemon:
                lines.append(f"  Bench {i+1}: {pokemon.name} [{pokemon.element.upper()}] HP: {pokemon.current_health()}/{pokemon.health}")
            else:
                lines.append(f"  Bench {i+1}: [Empty]")
        lines.append("")
        
        # Player's section
        lines.append("YOUR FIELD:")
        lines.append("-" * 40)
        
        # Player's points and deck info
        lines.append(f"You: {player.name} | Points: {player.points}")
        lines.append(f"Cards in deck: {len(player.deck)} | Cards in hand: {len(player.cards_in_hand)}")
        lines.append(f"Current Energy: {player.energy_zone_curent_energy or 'None'} | Next Energy: {player.energy_zone_next_energy or 'None'}")
        lines.append("")
        
        # Player's hand
        lines.append("Your Hand:")
        if player.cards_in_hand:
            for i, card in enumerate(player.cards_in_hand):
                lines.append(f"  {i+1}. {card.to_display_string()}")
        else:
            lines.append("  [No cards in hand]")
        lines.append("")
        
        # Available actions (placeholder)
        lines.append("AVAILABLE ACTIONS:")
        lines.append("-" * 40)
        lines.append("1. Play a card from hand")
        lines.append("2. Attack with active Pokemon")
        lines.append("3. Switch active Pokemon")
        lines.append("4. Use Pokemon ability")
        lines.append("5. End turn")
        lines.append("")
        
        lines.append("=" * 80)
        
        return "\n".join(lines)
    
    def _indent_text(self, text: str, spaces: int) -> str:
        """Helper method to indent multi-line text"""
        indent = " " * spaces
        return "\n".join(indent + line for line in text.split("\n"))




########################################################
#            Still need to implement these             #
########################################################

    def _execute_turn(self):
        """Execute a complete turn"""
        self.turn += 1
        current = self.current_player
        
        self.log(f"Turn {self.turn} - {current.name}")
        
        # Turn start procedures
        self._start_turn_effects(current)
        self._draw_phase(current)
        self._main_phase(current)
        self._end_turn()

    def _create_empty_state(self) -> List[float]:
        """Create an empty state array initialized with zeros"""
        return [0.0] * STATE_SIZE
    
    # This is a function that gets the state for the human player or for the AI
    def _get_state(self, player: Player, opponent: Player) -> Dict[str, Any]:
        # If the player is human, get the state from the human player
        if player.agent.is_human:
            #return player._get_human_state()
            return []
        # If the player is AI, get the state from the AI
        else:
            return self.get_ai_state(player, opponent)
        
    def _get_actions(self, player: Player) -> List[str]:
        """Get all possible actions for the player"""

        # Get the actions from the player
        opponent_pokemon_locations = self._get_opponent_pokemon_locations(player, self.opponent)
        return player._get_actions(opponent_pokemon_locations)

    def _start_turn_effects(self, player: Player):
        """Handle start-of-turn effects"""
        return
    
    def _draw_phase(self, player: Player):
        """Draw phase"""
        return
    
    def _main_phase(self, player: Player):
        """Main phase with player actions"""
        return
    
    def _get_player_action(self, player: Player, has_attacked: bool) -> Optional[str]:
        """Get and execute player action"""
        return
    
    def _default_ai_action(self, player: Player, has_attacked: bool) -> str:
        """Simple default AI logic"""
        # Try to attack
        return
    
    def _get_playable_cards(self, player: Player) -> List[Card]:
        """Get cards that can be played this turn"""
        return
    
    def _can_evolve_any(self, evolution: Pokemon, player: Player) -> bool:
        """Check if evolution can be played on any Pokemon"""
        return
    
    def _play_card(self, card: Card, player: Player):
        """Play a card from hand"""
        return
    
    def _evolve_pokemon(self, evolution: Pokemon, player: Player):
        """Handle Pokemon evolution"""
        return
    
    def _execute_attack(self, attacker: Pokemon, attack_index: int):
        """Execute an attack"""
        return
    
    def _calculate_damage(self, attacker: Pokemon, defender: Pokemon, base_damage: int) -> int:
        """Calculate final damage (can be extended for type effectiveness, etc.)"""
        return
    
    def _handle_knockout(self, knocked_out: Pokemon):
        """Handle Pokemon knockout"""
        return
    
    def _force_active_replacement(self):
        """Force opponent to replace active Pokemon"""
        return
    
    def _process_status_effects(self, player: Player):
        """Handle status effects at turn start"""
        return
    
    def _end_turn(self):
        """End current turn and switch players"""
        return
    
    def _is_game_over(self) -> bool:
        """Check if game should end"""
        return
    
    def _determine_winner(self) -> Optional[Player]:
        """Determine final winner"""
        return
    
    def _get_human_state(self, player: Player, opponent: Player) -> List[float]:
        """Get the state for the human player"""
        # This will be the GUI state that the human player sees
        return
    
    def _get_opponent_pokemon_locations(self, player: Player, opponent: Player) -> int:
        """Get the location of the opponent's active pokemon"""
        pokemon_locations = [0] * 3
        if opponent.active_pokemon:
            pokemon_locations[0] = 1
        if opponent.bench_pokemons[0]:
            pokemon_locations[1] = 1
        if opponent.bench_pokemons[1]:
            pokemon_locations[2] = 1
        if opponent.bench_pokemons[2]:
            pokemon_locations[3] = 1
        return pokemon_locations

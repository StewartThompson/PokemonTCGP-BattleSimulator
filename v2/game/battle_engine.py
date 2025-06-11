import random
from typing import List, Dict, Optional, Tuple, Union, Any
from dataclasses import dataclass, field
from enum import Enum
from game.game_rules import GameRules
from import_files.card_loader import CardLoader
from game.player import Player

class CardType(Enum):
    POKEMON = "pokemon"
    TRAINER = "trainer"
    ITEM = "item"
    TOOL = "tool"

class GamePhase(Enum):
    SETUP = "setup"
    MAIN = "main"
    END = "end"

class BattleEngine:
    """Core battle engine - simplified and modular"""
    
    def __init__(self, player1: Player, player2: Player, debug: bool = False):
        self.players = [player1, player2]
        self.debug = debug

        self.current_player_index = 0
        self.turn = 0
        self.phase = GamePhase.SETUP
        self.winner = None
        self.turn_actions = 0
    
    def log(self, message: str):
        if self.debug:
            print(f"[Turn {self.turn}] {message}")
    
    @property
    def current_player(self) -> Player:
        return self.players[self.current_player_index]
    
    @property
    def opponent(self) -> Player:
        return self.players[1 - self.current_player_index]
    
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
    
    def _setup_game(self):
        """Initialize game state"""
        self.log("Setting up battle...")
        
        # Determine first player
        self.current_player_index = random.randint(0, 1)
        self.log(f"{self.current_player.name} goes first!")
        
        # Setup both players
        for player in self.players:
            self._setup_player(player)
        
        self.phase = GamePhase.MAIN
    
    def _setup_player(self, player: Player):
        """Setup individual player with mulligan handling"""
        # Draw initial hand
        player.draw_inital_hand()  
        
        # Set active Pokemon
        basic_pokemon = player.get_basic_pokemon()
        
        active = basic_pokemon[0]
        player.play_card_to_location(active, "active")
        self.log(f"{player.name} sets {active.name} as active")
    
    def _execute_turn(self):
        """Execute a complete turn"""
        self.turn += 1
        self.turn_actions = 0
        current = self.current_player
        
        self.log(f"Turn {self.turn} - {current.name}")
        
        # Turn start procedures
        self._start_turn_effects(current)
        self._draw_phase(current)
        self._main_phase(current)
        self._end_turn()
    
    def _start_turn_effects(self, player: Player):
        """Handle start-of-turn effects"""
        # Update Pokemon turn counters
        for pokemon in player.all_pokemon():
            pokemon.reset_turn_effects()
        
        # Generate energy (skip first player's first turn)
        if not (self.turn == 1 and self.current_player_index == 0):
            energy_type = random.choice(player.deck_energy_types)
            player.energy_zone.append(energy_type)
            self.log(f"{player.name} gains {energy_type} energy")
        
        # Handle status effects
        self._process_status_effects(player)
    
    def _draw_phase(self, player: Player):
        """Draw phase"""
        drawn = player.draw_card()
        if drawn:
            self.log(f"{player.name} draws {drawn.name}")
    
    def _main_phase(self, player: Player):
        """Main phase with player actions"""
        has_attacked = False
        
        while (not has_attacked and 
               self.turn_actions < GameRules.MAX_ACTIONS_PER_TURN and 
               not self._is_game_over()):
            
            action = self._get_player_action(player, has_attacked)
            
            if action == "end_turn":
                break
            elif action == "attack":
                has_attacked = True
            elif action is None:
                break
            
            self.turn_actions += 1
    
    def _get_player_action(self, player: Player, has_attacked: bool) -> Optional[str]:
        """Get and execute player action"""
        if player.agent and hasattr(player.agent, 'choose_action'):
            return player.agent.choose_action(self, player, self.opponent, has_attacked)
        return self._default_ai_action(player, has_attacked)
    
    def _default_ai_action(self, player: Player, has_attacked: bool) -> str:
        """Simple default AI logic"""
        # Try to attack
        if not has_attacked and player.active_pokemon:
            for i, attack in enumerate(player.active_pokemon.attacks):
                if player.active_pokemon.can_attack(i):
                    self._execute_attack(player.active_pokemon, i)
                    return "attack"
        
        # Try to play cards
        playable = self._get_playable_cards(player)
        if playable:
            card = random.choice(playable)
            self._play_card(card, player)
            return "play_card"
        
        # Try to attach energy
        if player.energy_zone and player.active_pokemon:
            energy_type = player.energy_zone.pop()
            player.active_pokemon.modify_energy(energy_type, 1)
            self.log(f"Attached {energy_type} energy to {player.active_pokemon.name}")
            return "attach_energy"
        
        return "end_turn"
    
    def _get_playable_cards(self, player: Player) -> List[Card]:
        """Get cards that can be played this turn"""
        playable = []
        for card in player.hand:
            if isinstance(card, Pokemon):
                if (card.stage == "basic" and 
                    len(player.bench) < GameRules.MAX_BENCH_SIZE):
                    playable.append(card)
                elif self._can_evolve_any(card, player):
                    playable.append(card)
            elif card.card_type in [CardType.TRAINER, CardType.ITEM]:
                playable.append(card)
        return playable
    
    def _can_evolve_any(self, evolution: Pokemon, player: Player) -> bool:
        """Check if evolution can be played on any Pokemon"""
        return any(GameRules.can_evolve(pokemon, evolution) 
                  for pokemon in player.all_pokemon())
    
    def _play_card(self, card: Card, player: Player):
        """Play a card from hand"""
        if isinstance(card, Pokemon):
            if card.stage == "basic":
                player.play_card_to_location(card, "bench")
                self.log(f"{player.name} plays {card.name} to bench")
            else:
                self._evolve_pokemon(card, player)
        else:
            player.play_card_to_location(card, "discard")
            self.log(f"{player.name} plays {card.name}")
    
    def _evolve_pokemon(self, evolution: Pokemon, player: Player):
        """Handle Pokemon evolution"""
        for pokemon in player.all_pokemon():
            if GameRules.can_evolve(pokemon, evolution):
                # Transfer properties
                evolution.current_hp = evolution.max_hp
                evolution.equipped_energies = pokemon.equipped_energies.copy()
                evolution.status_effects = pokemon.status_effects.copy()
                evolution.attached_tool = pokemon.attached_tool
                evolution.turns_in_play = pokemon.turns_in_play
                
                # Replace Pokemon
                if player.active_pokemon == pokemon:
                    player.active_pokemon = evolution
                else:
                    idx = player.bench.index(pokemon)
                    player.bench[idx] = evolution
                
                player.discard_pile.append(pokemon)
                player.hand.remove(evolution)
                self.log(f"{pokemon.name} evolves into {evolution.name}")
                break
    
    def _execute_attack(self, attacker: Pokemon, attack_index: int):
        """Execute an attack"""
        if not self.opponent.active_pokemon:
            return
        
        attack = attacker.attacks[attack_index]
        defender = self.opponent.active_pokemon
        
        # Pay energy cost
        cost = attack.get('cost', {})
        for energy_type, amount in cost.items():
            attacker.modify_energy(energy_type, -amount)
        
        # Calculate and apply damage
        damage = attack.get('damage', 0)
        final_damage = self._calculate_damage(attacker, defender, damage)
        
        if final_damage > 0:
            defender.current_hp -= final_damage
            self.log(f"{attacker.name} attacks {defender.name} for {final_damage} damage")
            
            if defender.is_knocked_out():
                self._handle_knockout(defender)
    
    def _calculate_damage(self, attacker: Pokemon, defender: Pokemon, base_damage: int) -> int:
        """Calculate final damage (can be extended for type effectiveness, etc.)"""
        return max(0, base_damage)
    
    def _handle_knockout(self, knocked_out: Pokemon):
        """Handle Pokemon knockout"""
        self.log(f"{knocked_out.name} is knocked out!")
        
        # Award prize points
        prize_value = GameRules.calculate_prize_value(knocked_out)
        self.current_player.prize_points += prize_value
        
        # Remove from play
        if self.opponent.active_pokemon == knocked_out:
            self.opponent.active_pokemon = None
            self._force_active_replacement()
        else:
            self.opponent.bench.remove(knocked_out)
        
        self.opponent.discard_pile.append(knocked_out)
        
        # Check win conditions
        if (self.current_player.prize_points >= GameRules.WINNING_POINTS or
            not self.opponent.has_pokemon()):
            self.winner = self.current_player
    
    def _force_active_replacement(self):
        """Force opponent to replace active Pokemon"""
        if self.opponent.bench:
            new_active = self.opponent.bench.pop(0)
            self.opponent.active_pokemon = new_active
            self.log(f"{self.opponent.name} promotes {new_active.name} to active")
        else:
            self.winner = self.current_player
    
    def _process_status_effects(self, player: Player):
        """Handle status effects at turn start"""
        if not player.active_pokemon:
            return
        
        for effect in player.active_pokemon.status_effects[:]:
            if effect == "poisoned":
                player.active_pokemon.current_hp -= 10
                self.log(f"{player.active_pokemon.name} takes 10 poison damage")
            elif effect == "burned":
                if random.choice([True, False]):
                    player.active_pokemon.current_hp -= 20
                    self.log(f"{player.active_pokemon.name} takes 20 burn damage")
                else:
                    player.active_pokemon.status_effects.remove(effect)
                    self.log(f"{player.active_pokemon.name} recovers from burn")
            
            if player.active_pokemon.is_knocked_out():
                self._handle_knockout(player.active_pokemon)
                break
    
    def _end_turn(self):
        """End current turn and switch players"""
        self.log(f"{self.current_player.name}'s turn ends")
        self.current_player_index = 1 - self.current_player_index
    
    def _is_game_over(self) -> bool:
        """Check if game should end"""
        return self.winner is not None or self.turn >= GameRules.MAX_TURNS
    
    def _determine_winner(self) -> Optional[Player]:
        """Determine final winner"""
        if self.winner:
            self.log(f"Winner: {self.winner.name}")
            return self.winner
        
        # Timeout - winner by prize points
        p1, p2 = self.players
        if p1.prize_points != p2.prize_points:
            winner = p1 if p1.prize_points > p2.prize_points else p2
            self.log(f"Time limit - {winner.name} wins by prize points")
            return winner
        
        # Random winner on tie
        winner = random.choice(self.players)
        self.log(f"Time limit - random winner: {winner.name}")
        return winner
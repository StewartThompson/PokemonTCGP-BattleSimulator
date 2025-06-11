from flask import Flask, render_template, request, jsonify, redirect, url_for
import threading
import queue
import time
from typing import Optional, List, Any
import json

class PokemonTCGWebGUI:
    """Simple web-based GUI for Pokemon TCG debugging and gameplay"""
    
    def __init__(self, port=5000):
        self.app = Flask(__name__, template_folder='templates', static_folder='static')
        self.port = port
        
        # Game state
        self.match = None
        self.human_player = None
        self.current_options = []
        self.current_context = None
        self.waiting_for_input = False
        self.user_choice = None
        self.choice_queue = queue.Queue()
        self.game_log = []
        
        # Setup routes
        self.setup_routes()
        
    def setup_routes(self):
        """Set up Flask routes"""
        
        @self.app.route('/')
        def index():
            return render_template('game.html')
            
        @self.app.route('/api/game_state')
        def get_game_state():
            """Get current game state as JSON"""
            state = {
                'match_active': self.match is not None,
                'current_player': self.match.current_player.name if self.match else None,
                'turn': getattr(self.match, 'turn', 0),
                'human_player': self.human_player.name if self.human_player else None,
                'waiting_for_input': self.waiting_for_input,
                'current_context': self.current_context,
                'game_log': self.game_log[-50:],  # Last 50 messages
                'options': self._format_options_for_web(),
                'player_info': self._get_player_info(),
                'opponent_info': self._get_opponent_info()
            }
            return jsonify(state)
            
        @self.app.route('/api/make_choice', methods=['POST'])
        def make_choice():
            """Handle user choice from web interface"""
            if not self.waiting_for_input:
                return jsonify({'error': 'Not waiting for input'}), 400
                
            choice_index = request.json.get('choice_index')
            if choice_index is None or not (0 <= choice_index < len(self.current_options)):
                return jsonify({'error': 'Invalid choice'}), 400
                
            choice = self.current_options[choice_index]
            self.choice_queue.put(choice)
            return jsonify({'success': True})
            
        @self.app.route('/api/log')
        def get_log():
            """Get game log"""
            return jsonify({'log': self.game_log})
            
    def _format_options_for_web(self):
        """Format options for web display"""
        if not self.current_options:
            return []
            
        formatted = []
        for i, option in enumerate(self.current_options):
            formatted.append({
                'index': i,
                'name': self._get_option_name(option),
                'description': self._get_option_description(option)
            })
        return formatted
        
    def _get_player_info(self):
        """Get human player information"""
        if not self.human_player:
            return None
            
        # Active Pokemon
        active_info = None
        if self.human_player.active_pokemon:
            pokemon = self.human_player.active_pokemon
            active_info = {
                'name': pokemon.name,
                'hp': f"{pokemon.current_hp}/{pokemon.max_hp}",
                'energy': self._format_energy(pokemon.equipped_energies),
                'attacks': self._format_attacks(getattr(pokemon, 'attacks', []))
            }
            
        # Bench Pokemon
        bench_info = []
        for pokemon in self.human_player.bench_pokemons:
            bench_info.append({
                'name': pokemon.name,
                'hp': f"{pokemon.current_hp}/{pokemon.max_hp}",
                'energy': self._format_energy(pokemon.equipped_energies)
            })
            
        # Hand
        hand_info = []
        for card in self.human_player.cards_in_hand:
            card_info = {
                'name': card.name,
                'type': getattr(card, 'card_type', 'unknown')
            }
            if card_info['type'] == 'pokemon':
                card_info['hp'] = getattr(card, 'max_hp', '?')
                card_info['stage'] = getattr(card, 'stage', 'unknown')
            hand_info.append(card_info)
            
        return {
            'name': self.human_player.name,
            'active': active_info,
            'bench': bench_info,
            'hand': hand_info,
            'hand_count': len(self.human_player.cards_in_hand),
            'deck_count': len(self.human_player.remaining_cards)
        }
        
    def _get_opponent_info(self):
        """Get opponent information"""
        if not self.match or not self.human_player:
            return None
            
        opponent = self.match.player1 if self.human_player == self.match.player2 else self.match.player2
        
        # Active Pokemon
        active_info = None
        if opponent.active_pokemon:
            pokemon = opponent.active_pokemon
            active_info = {
                'name': pokemon.name,
                'hp': f"{pokemon.current_hp}/{pokemon.max_hp}"
            }
            
        # Bench Pokemon (just count and names)
        bench_info = []
        for pokemon in opponent.bench_pokemons:
            bench_info.append({
                'name': pokemon.name,
                'hp': f"{pokemon.current_hp}/{pokemon.max_hp}"
            })
            
        return {
            'name': opponent.name,
            'active': active_info,
            'bench': bench_info,
            'hand_count': len(opponent.cards_in_hand),
            'deck_count': len(opponent.remaining_cards)
        }
        
    def _format_energy(self, energy_dict):
        """Format energy for display"""
        if not energy_dict:
            return ""
        energies = [f"{count}x{energy}" for energy, count in energy_dict.items() if count > 0]
        return ", ".join(energies)
        
    def _format_attacks(self, attacks):
        """Format attacks for display"""
        if not attacks:
            return []
        return [{'name': attack.name, 'damage': getattr(attack, 'damage', '?')} for attack in attacks]
        
    def _get_option_name(self, option):
        """Get a display name for an option"""
        if hasattr(option, 'name'):
            return option.name
        elif isinstance(option, str):
            return option
        else:
            return str(option)
            
    def _get_option_description(self, option):
        """Get a description for an option"""
        # You can expand this to provide more detailed descriptions
        return self._get_option_name(option)
        
    def set_match(self, match, human_player):
        """Set the current match and human player"""
        self.match = match
        self.human_player = human_player
        
    def show_options(self, options, context, callback):
        """Show options to the user and wait for selection"""
        self.current_options = options
        self.current_context = context
        self.waiting_for_input = True
        
        self.log_message(f"Choose {context}: {len(options)} options available")
        
        # Wait for user choice
        try:
            choice = self.choice_queue.get(timeout=300)  # 5 minute timeout
            self.waiting_for_input = False
            callback(choice)
        except queue.Empty:
            self.log_message("Choice timeout - using first option")
            self.waiting_for_input = False
            callback(options[0] if options else None)
            
    def log_message(self, message):
        """Add a message to the game log"""
        timestamp = time.strftime("%H:%M:%S")
        self.game_log.append(f"[{timestamp}] {message}")
        # Keep only last 100 messages
        if len(self.game_log) > 100:
            self.game_log = self.game_log[-100:]
            
    def run(self):
        """Start the web server"""
        print(f"🌐 Starting web GUI on http://localhost:{self.port}")
        self.app.run(host='0.0.0.0', port=self.port, debug=False, use_reloader=False)
        
    def run_threaded(self):
        """Run the web server in a separate thread"""
        thread = threading.Thread(target=self.run, daemon=True)
        thread.start()
        return thread 
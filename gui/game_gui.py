import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from typing import Optional, List, Any
import threading

class PokemonTCGGUI:
    """Simple Tkinter GUI for Pokemon TCG debugging and gameplay"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Pokemon TCG Pocket - Battle Simulator")
        self.root.geometry("1200x800")
        
        # Game state
        self.match = None
        self.human_player = None
        self.current_options = []
        self.current_context = None
        self.waiting_for_input = False
        self.user_choice = None
        
        # Colors
        self.colors = {
            'bg': '#f0f0f0',
            'player_bg': '#e6f3ff',
            'opponent_bg': '#ffe6e6',
            'card_bg': '#ffffff',
            'energy_fire': '#ff6b6b',
            'energy_water': '#4dabf7',
            'energy_grass': '#51cf66',
            'energy_electric': '#ffd43b',
            'energy_psychic': '#da77f2',
            'energy_rock': '#8c7853',
            'energy_normal': '#ced4da'
        }
        
        self.setup_ui()
        
    def setup_ui(self):
        """Set up the user interface layout"""
        # Main frame
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Top section - Opponent area
        self.opponent_frame = ttk.LabelFrame(main_frame, text="Opponent", padding=10)
        self.opponent_frame.pack(fill=tk.X, pady=(0, 5))
        
        # Opponent's Pokemon
        self.opponent_pokemon_frame = ttk.Frame(self.opponent_frame)
        self.opponent_pokemon_frame.pack(fill=tk.X)
        
        # Game info section
        self.game_info_frame = ttk.LabelFrame(main_frame, text="Game Info", padding=10)
        self.game_info_frame.pack(fill=tk.X, pady=5)
        
        self.game_info_text = scrolledtext.ScrolledText(self.game_info_frame, height=8, wrap=tk.WORD)
        self.game_info_text.pack(fill=tk.BOTH, expand=True)
        
        # Middle section - Actions and choices
        self.action_frame = ttk.LabelFrame(main_frame, text="Actions", padding=10)
        self.action_frame.pack(fill=tk.X, pady=5)
        
        # Player section - Bottom
        self.player_frame = ttk.LabelFrame(main_frame, text="Your Pokemon & Hand", padding=10)
        self.player_frame.pack(fill=tk.BOTH, expand=True, pady=(5, 0))
        
        # Player's Pokemon area
        self.player_pokemon_frame = ttk.Frame(self.player_frame)
        self.player_pokemon_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Player's hand area
        self.hand_frame = ttk.LabelFrame(self.player_frame, text="Your Hand", padding=5)
        self.hand_frame.pack(fill=tk.BOTH, expand=True)
        
        # Initialize empty state
        self.update_display()
        
    def set_match(self, match, human_player):
        """Set the current match and human player"""
        self.match = match
        self.human_player = human_player
        self.update_display()
        
    def update_display(self):
        """Update the entire display with current game state"""
        if not self.match or not self.human_player:
            self.game_info_text.delete(1.0, tk.END)
            self.game_info_text.insert(tk.END, "No game in progress\n")
            return
            
        # Clear existing widgets
        self._clear_frame(self.opponent_pokemon_frame)
        self._clear_frame(self.player_pokemon_frame)
        self._clear_frame(self.hand_frame)
        self._clear_frame(self.action_frame)
        
        # Update game info
        self._update_game_info()
        
        # Update opponent display
        self._update_opponent_display()
        
        # Update player display
        self._update_player_display()
        
    def _clear_frame(self, frame):
        """Clear all widgets from a frame"""
        for widget in frame.winfo_children():
            widget.destroy()
            
    def _update_game_info(self):
        """Update the game information text area"""
        self.game_info_text.delete(1.0, tk.END)
        
        if not self.match:
            return
            
        info = f"Turn: {getattr(self.match, 'turn', '?')}\n"
        info += f"Current Player: {self.match.current_player.name}\n"
        
        # Add current phase info if available
        if hasattr(self.match, 'phase'):
            info += f"Phase: {self.match.phase}\n"
            
        info += "\n"
        
        # Player stats
        opponent = self.match.player1 if self.human_player == self.match.player2 else self.match.player2
        
        info += f"🔴 {opponent.name}:\n"
        info += f"  Hand: {len(opponent.cards_in_hand)} cards\n"
        info += f"  Deck: {len(opponent.remaining_cards)} cards\n"
        info += f"  Prizes: {len(getattr(opponent, 'prize_cards', []))} remaining\n\n"
        
        info += f"🔵 {self.human_player.name}:\n"
        info += f"  Hand: {len(self.human_player.cards_in_hand)} cards\n"
        info += f"  Deck: {len(self.human_player.remaining_cards)} cards\n"
        info += f"  Prizes: {len(getattr(self.human_player, 'prize_cards', []))} remaining\n"
        
        self.game_info_text.insert(tk.END, info)
        
    def _update_opponent_display(self):
        """Update opponent's Pokemon display"""
        if not self.match:
            return
            
        opponent = self.match.player1 if self.human_player == self.match.player2 else self.match.player2
        
        # Active Pokemon
        if opponent.active_pokemon:
            active_frame = self._create_pokemon_widget(self.opponent_pokemon_frame, opponent.active_pokemon, "Active", False)
            active_frame.pack(side=tk.LEFT, padx=5)
            
        # Bench Pokemon
        if opponent.bench_pokemons:
            bench_label = ttk.Label(self.opponent_pokemon_frame, text="Bench:")
            bench_label.pack(side=tk.LEFT, padx=(20, 5))
            
            for i, pokemon in enumerate(opponent.bench_pokemons):
                bench_frame = self._create_pokemon_widget(self.opponent_pokemon_frame, pokemon, f"Bench {i+1}", False)
                bench_frame.pack(side=tk.LEFT, padx=2)
                
    def _update_player_display(self):
        """Update player's Pokemon and hand display"""
        if not self.human_player:
            return
            
        # Active Pokemon
        if self.human_player.active_pokemon:
            active_frame = self._create_pokemon_widget(self.player_pokemon_frame, self.human_player.active_pokemon, "Active", True)
            active_frame.pack(side=tk.LEFT, padx=5)
            
        # Bench Pokemon
        if self.human_player.bench_pokemons:
            bench_label = ttk.Label(self.player_pokemon_frame, text="Bench:")
            bench_label.pack(side=tk.LEFT, padx=(20, 5))
            
            for i, pokemon in enumerate(self.human_player.bench_pokemons):
                bench_frame = self._create_pokemon_widget(self.player_pokemon_frame, pokemon, f"Bench {i+1}", True)
                bench_frame.pack(side=tk.LEFT, padx=2)
                
        # Hand
        self._update_hand_display()
        
    def _create_pokemon_widget(self, parent, pokemon, position, is_player):
        """Create a widget to display a Pokemon"""
        frame = ttk.Frame(parent, relief=tk.RAISED, borderwidth=1)
        
        # Pokemon name and position
        name_label = ttk.Label(frame, text=f"{pokemon.name}\n({position})", font=('Arial', 9, 'bold'))
        name_label.pack(pady=2)
        
        # HP
        hp_label = ttk.Label(frame, text=f"HP: {pokemon.current_hp}/{pokemon.max_hp}")
        hp_label.pack()
        
        # Energy (only for player Pokemon or visible info)
        if is_player and pokemon.equipped_energies:
            energy_text = ", ".join([f"{count}x{energy}" for energy, count in pokemon.equipped_energies.items() if count > 0])
            energy_label = ttk.Label(frame, text=f"⚡ {energy_text}", font=('Arial', 8))
            energy_label.pack()
            
        # Attacks (only for player Pokemon)
        if is_player and hasattr(pokemon, 'attacks') and pokemon.attacks:
            attacks_text = " | ".join([f"{attack.name}" for attack in pokemon.attacks])
            attack_label = ttk.Label(frame, text=attacks_text, font=('Arial', 8))
            attack_label.pack()
            
        return frame
        
    def _update_hand_display(self):
        """Update the hand display"""
        if not self.human_player.cards_in_hand:
            no_cards_label = ttk.Label(self.hand_frame, text="No cards in hand")
            no_cards_label.pack()
            return
            
        # Create scrollable frame for hand
        canvas = tk.Canvas(self.hand_frame)
        scrollbar = ttk.Scrollbar(self.hand_frame, orient="horizontal", command=canvas.xview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(xscrollcommand=scrollbar.set)
        
        # Add cards to hand
        for i, card in enumerate(self.human_player.cards_in_hand):
            card_frame = self._create_card_widget(scrollable_frame, card, i)
            card_frame.pack(side=tk.LEFT, padx=2, pady=2)
            
        canvas.pack(side="top", fill="both", expand=True)
        scrollbar.pack(side="bottom", fill="x")
        
    def _create_card_widget(self, parent, card, index):
        """Create a widget to display a card"""
        frame = ttk.Frame(parent, relief=tk.RAISED, borderwidth=1)
        
        # Card name
        name_label = ttk.Label(frame, text=card.name, font=('Arial', 9, 'bold'))
        name_label.pack(pady=2)
        
        # Card type
        card_type = getattr(card, 'card_type', 'unknown')
        type_label = ttk.Label(frame, text=f"({card_type})")
        type_label.pack()
        
        # Additional info based on card type
        if card_type == 'pokemon':
            hp = getattr(card, 'max_hp', '?')
            stage = getattr(card, 'stage', 'unknown')
            info_label = ttk.Label(frame, text=f"{stage}\n{hp} HP", font=('Arial', 8))
            info_label.pack()
            
        return frame
        
    def show_options(self, options, context, callback):
        """Show options to the user and wait for selection"""
        self.current_options = options
        self.current_context = context
        self.waiting_for_input = True
        self.user_choice = None
        
        # Clear action frame
        self._clear_frame(self.action_frame)
        
        # Add title
        title_label = ttk.Label(self.action_frame, text=f"Choose {context}:", font=('Arial', 10, 'bold'))
        title_label.pack(pady=(0, 10))
        
        # Create buttons for each option
        for i, option in enumerate(options):
            option_name = self._get_option_name(option)
            btn = ttk.Button(
                self.action_frame, 
                text=f"{i+1}. {option_name}",
                command=lambda idx=i: self._on_option_selected(idx, callback)
            )
            btn.pack(fill=tk.X, pady=2)
            
    def _on_option_selected(self, index, callback):
        """Handle option selection"""
        if 0 <= index < len(self.current_options):
            self.user_choice = self.current_options[index]
            self.waiting_for_input = False
            callback(self.user_choice)
            
    def _get_option_name(self, option):
        """Get a display name for an option"""
        if hasattr(option, 'name'):
            return option.name
        elif isinstance(option, str):
            return option
        else:
            return str(option)
            
    def log_message(self, message):
        """Add a message to the game log"""
        self.game_info_text.insert(tk.END, f"\n{message}")
        self.game_info_text.see(tk.END)
        
    def run(self):
        """Start the GUI main loop"""
        self.root.mainloop()
        
    def destroy(self):
        """Close the GUI"""
        self.root.destroy()

# Example usage and testing
if __name__ == "__main__":
    gui = PokemonTCGGUI()
    gui.run() 
#!/usr/bin/env python3

import threading
import argparse
import time
import webbrowser
from gui.web_gui import PokemonTCGWebGUI
from agents.web_human_agent import WebHumanAgent
from agents.opponent_agent import OpponentAgent
from moteur.player import Player
from moteur.core.match import Match
from utils import get_card_database, load_default_database
import decks


def setup_player_gui(name: str, deck_name: str, agent_class=None, web_gui=None) -> Player:
    """Set up a player with a deck and agent for web GUI"""
    print(f"Setting up player {name} with deck {deck_name}")
    
    # Check if deck exists
    all_decks = decks.load_all_decks()
    if deck_name not in all_decks:
        print(f"❌ Deck '{deck_name}' not found!")
        available_decks = list(all_decks.keys())
        print(f"Available decks: {', '.join(available_decks)}")
        raise ValueError(f"Deck '{deck_name}' not found")
    
    # Load the actual deck cards
    deck_definition = decks.get_deck(deck_name)
    if deck_definition is None:
        raise ValueError(f"Failed to load deck '{deck_name}'")
    
    # Create player with specified agent
    if agent_class is None:
        agent_class = OpponentAgent
    
    # Create player first
    player = Player(name, deck_definition, chosen_energies=None, agent=agent_class)
    
    # If it's a WebHumanAgent, we need to set the web_gui reference
    if agent_class == WebHumanAgent and web_gui:
        player.agent.set_web_gui(web_gui)
    
    print(f"✅ Player {name} created with {len(player.deck)} cards")
    return player


def run_web_game(deck1_name: str, deck2_name: str, human_deck: str, debug: bool = False, port: int = 5000):
    """Run a game with web GUI interface"""
    
    # Initialize the card database
    load_default_database()
    db = get_card_database()
    if not db:
        print("❌ Failed to load card database!")
        return
    
    # Create web GUI
    web_gui = PokemonTCGWebGUI(port=port)
    
    # Set up players
    if human_deck == "deck1":
        player1 = setup_player_gui("You", deck1_name, agent_class=WebHumanAgent, web_gui=web_gui)
        player2 = setup_player_gui("Opponent", deck2_name, agent_class=OpponentAgent)
        human_player = player1
    else:  # deck2
        player1 = setup_player_gui("Opponent", deck1_name, agent_class=OpponentAgent)
        player2 = setup_player_gui("You", deck2_name, agent_class=WebHumanAgent, web_gui=web_gui)
        human_player = player2
    
    # Set up web GUI with match info
    web_gui.set_match(None, human_player)  # Will update when match starts
    
    # Start the web server in a separate thread
    web_thread = web_gui.run_threaded()
    
    # Give the web server a moment to start
    time.sleep(2)
    
    # Open web browser
    try:
        webbrowser.open(f'http://localhost:{port}')
        print(f"🌐 Opened web browser at http://localhost:{port}")
    except Exception as e:
        print(f"⚠️ Could not open browser automatically: {e}")
        print(f"🌐 Please open http://localhost:{port} in your browser")
    
    # Start the game in a separate thread
    def start_game():
        try:
            # Give user a moment to open the browser
            time.sleep(3)
            
            match = Match(player1, player2, debug=debug)
            web_gui.set_match(match, human_player)
            web_gui.log_message(f"🎮 Starting match: {player1.name} vs {player2.name}")
            
            winner = match.start_battle()
            
            if winner:
                if winner == human_player:
                    web_gui.log_message(f"\n🎉 Congratulations! You won!")
                else:
                    web_gui.log_message(f"\n😔 You lost. {winner.name} won this time.")
            else:
                web_gui.log_message(f"\n🤝 The match ended in a draw.")
                
        except Exception as e:
            web_gui.log_message(f"\n❌ Error during game: {str(e)}")
            print(f"Game error: {e}")
            import traceback
            traceback.print_exc()
    
    # Start game thread
    game_thread = threading.Thread(target=start_game, daemon=True)
    game_thread.start()
    
    # Keep the main thread alive and run the web server
    try:
        print("🎮 Game is running! Press Ctrl+C to quit.")
        print(f"🌐 Web interface: http://localhost:{port}")
        
        # Keep the main thread alive while the threaded server runs
        while True:
            time.sleep(1)
        
    except KeyboardInterrupt:
        print("\n👋 Shutting down...")
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()


def main():
    parser = argparse.ArgumentParser(description="Pokemon TCG Pocket Battle Simulator - Web GUI Version")
    parser.add_argument("--list-decks", action="store_true", help="List available decks")
    parser.add_argument("--deck1", type=str, default="basic_lightning_deck", help="Deck for player 1")
    parser.add_argument("--deck2", type=str, default="basic_water_deck", help="Deck for player 2")
    parser.add_argument("--human", choices=["deck1", "deck2"], default="deck1", help="Make deck1 or deck2 human-controlled")
    parser.add_argument("--debug", action="store_true", help="Enable debug logging")
    parser.add_argument("--port", type=int, default=5000, help="Port for web interface")
    
    args = parser.parse_args()
    
    # Initialize the card database
    load_default_database()
    db = get_card_database()
    if not db:
        print("❌ Failed to load card database!")
        return
    
    # List available decks if requested
    if args.list_decks:
        all_decks = decks.load_all_decks()
        print("Available decks:")
        for deck_name in sorted(all_decks.keys()):
            print(f"  - {deck_name}")
        return
    
    print(f"\n🎮 Starting Web-based Pokemon TCG Battle!")
    print(f"Human Player: {args.human}")
    print(f"Deck 1: {args.deck1}")
    print(f"Deck 2: {args.deck2}")
    print(f"Debug Mode: {args.debug}")
    print(f"Port: {args.port}")
    
    # Run the web game
    run_web_game(args.deck1, args.deck2, args.human, args.debug, args.port)


if __name__ == "__main__":
    main() 
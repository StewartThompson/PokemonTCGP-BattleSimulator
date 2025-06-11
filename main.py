#!/usr/bin/env python3

import argparse
import itertools
from typing import Dict, List, Any
from agents.human_agent import HumanAgent
from agents.random_agent import RandomAgent
from agents.custom_agent import CustomAgent
from agents.opponent_agent import OpponentAgent
from moteur.player import Player
from moteur.core.match import Match
from utils import get_card_database, load_default_database
import decks

def setup_player(name: str, deck_name: str, agent_class=None) -> Player:
    """Set up a player with a deck and agent"""
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
        agent_class = CustomAgent
    
    player = Player(name, deck_definition, chosen_energies=None, agent=agent_class)
    
    print(f"✅ Player {name} created with {len(player.deck)} cards")
    return player

def run_simulations(player1: Player, player2: Player, num_simulations: int = 10, debug: bool = False) -> Dict[str, int]:
    """Run multiple simulations and return win counts"""
    results = {}
    
    for i in range(num_simulations):
        if not debug:
            print(f"Running simulation {i+1}/{num_simulations}...", end="\r")
        
        # Create fresh player instances for each simulation
        fresh_player1 = Player(player1.name, player1.deck.copy(), player1.agent.__class__)
        fresh_player2 = Player(player2.name, player2.deck.copy(), player2.agent.__class__)
        
        match = Match(fresh_player1, fresh_player2, debug=debug)
        winner = match.start_battle()
        
        if winner:
            winner_name = winner.name
            if winner_name in results:
                results[winner_name] += 1
            else:
                results[winner_name] = 1
        else:
            # Handle draws
            if "Draw" in results:
                results["Draw"] += 1
            else:
                results["Draw"] = 1
    
    if not debug:
        print()  # New line after progress updates
    
    return results

def print_results_summary(results: Dict[str, int], num_simulations: int, deck1_name: str = None, deck2_name: str = None) -> None:
    """Print enhanced results summary"""
    print("\n===== SIMULATION RESULTS =====")
    
    if deck1_name and deck2_name:
        print(f"Matchup: {deck1_name} vs {deck2_name}")
    
    print(f"Total simulations: {num_simulations}")
    print("\nResults:")
    
    # Sort results by win count (descending)
    sorted_results = sorted(results.items(), key=lambda x: x[1], reverse=True)
    
    for result, count in sorted_results:
        percentage = (count / num_simulations) * 100
        print(f"  {result}: {count} wins ({percentage:.1f}%)")
    
    # Determine the winner
    if sorted_results:
        winner, wins = sorted_results[0]
        if len(sorted_results) > 1 and sorted_results[1][1] == wins:
            print("\n🤝 Result: Tie!")
        else:
            print(f"\n🏆 Winner: {winner}")
    
    print("================================")

def print_deck_contents(player_name: str, deck: List[Any]) -> None:
    """Print the contents of a deck in a readable format"""
    print(f"\n{player_name}'s Deck ({len(deck)} cards):")
    print("=" * 40)
    
    # Count cards by name
    card_counts = {}
    for card in deck:
        card_name = getattr(card, 'name', str(card))
        if card_name in card_counts:
            card_counts[card_name] += 1
        else:
            card_counts[card_name] = 1
    
    # Sort by card type and name
    def sort_key(item):
        card_name, count = item
        # Find a card with this name to get its type
        card = next((c for c in deck if getattr(c, 'name', str(c)) == card_name), None)
        if card and hasattr(card, 'card_type'):
            type_priority = {'pokemon': 0, 'trainer': 1, 'item': 2, 'energy': 3}
            return (type_priority.get(card.card_type, 4), card_name)
        return (5, card_name)
    
    sorted_cards = sorted(card_counts.items(), key=sort_key)
    
    for card_name, count in sorted_cards:
        # Find a card with this name to get additional info
        card = next((c for c in deck if getattr(c, 'name', str(c)) == card_name), None)
        if card and hasattr(card, 'card_type'):
            card_type = card.card_type
            if card_type == 'pokemon':
                hp = getattr(card, 'max_hp', '?')
                stage = getattr(card, 'stage', 'unknown')
                print(f"  {count}x {card_name} ({stage}, {hp} HP)")
            else:
                print(f"  {count}x {card_name} ({card_type})")
        else:
            print(f"  {count}x {card_name}")

print("\n--------------------------------")

def main():
    parser = argparse.ArgumentParser(description="Pokemon TCG Pocket Battle Simulator")
    parser.add_argument("--list-decks", action="store_true", help="List available decks")
    parser.add_argument("--deck1", type=str, help="Deck for player 1")
    parser.add_argument("--deck2", type=str, help="Deck for player 2")
    parser.add_argument("--human", choices=["deck1", "deck2"], help="Make deck1 or deck2 human-controlled")
    parser.add_argument("--simulations", type=int, default=10, help="Number of simulations to run")
    parser.add_argument("--debug", action="store_true", help="Enable debug logging")
    parser.add_argument("--all-vs-all", action="store_true", help="Run all-vs-all deck matchups")
    
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
    
    # Handle human vs AI matches
    if args.human:
        if not (args.deck1 and args.deck2):
            print("❌ Error: --human requires both --deck1 and --deck2 to be specified")
            return
        
        if args.simulations != 10:  # Check if user explicitly set simulations
            print("🎮 Human games run single matches only. Ignoring --simulations argument.")
        
        # Set up players with human control
        if args.human == "deck1":
            player1 = setup_player("You", args.deck1, agent_class=HumanAgent)
            player2 = setup_player("Opponent", args.deck2, agent_class=OpponentAgent)
        else:  # deck2
            player1 = setup_player("Opponent", args.deck1, agent_class=OpponentAgent)
            player2 = setup_player("You", args.deck2, agent_class=HumanAgent)
        
        print(f"\n🎮 Starting Human vs AI Match!")
        print(f"Human Player: {player1.name if args.human == 'deck1' else player2.name}")
        print(f"Deck: {args.deck1 if args.human == 'deck1' else args.deck2}")
        
        # Run single match
        match = Match(player1, player2, debug=args.debug)
        winner = match.start_battle()
        
        if winner:
            if ((args.human == "deck1" and winner == player1) or 
                (args.human == "deck2" and winner == player2)):
                print(f"\n🎉 Congratulations! You won with {winner.name}!")
            else:
                print(f"\n😔 You lost. {winner.name} won this time.")
        else:
            print(f"\n🤝 The match ended in a draw.")
            
        return
    
    # Run all-vs-all matchups if requested
    if args.all_vs_all:
        all_deck_names = list(decks.load_all_decks().keys())
        all_possible_combos = list(itertools.permutations(all_deck_names, 2))
        
        total_results = {}
        matchup_summaries = []
        
        for deck1_name, deck2_name in all_possible_combos:
            print(f"\nMatchup: {deck1_name} vs {deck2_name}")
            
            player1 = setup_player("Stewart", deck1_name, agent_class=CustomAgent)
            player2 = setup_player("Kimberly", deck2_name)
            
            matchup_results = run_simulations(player1, player2, args.simulations, args.debug)
            
            # Calculate win percentage for this matchup
            p1_wins = matchup_results.get("Stewart", 0)
            p2_wins = matchup_results.get("Kimberly", 0)
            p1_win_pct = (p1_wins / args.simulations) * 100
            
            # Store summary for later
            matchup_summaries.append(f"{deck1_name} vs {deck2_name}: Stewart won {p1_wins}/{args.simulations} ({p1_win_pct:.1f}%)")
            
            # Update total results
            for result, count in matchup_results.items():
                if result in total_results:
                    total_results[result] += count
                else:
                    total_results[result] = count
            
            # Print deck contents first
            print_deck_contents("Stewart", player1.deck)
            print_deck_contents("Kimberly", player2.deck)
            
            # Then print results for this matchup
            print_results_summary(matchup_results, args.simulations, deck1_name, deck2_name)
        
        # Print matchup summaries
        print("\nMatchup Summaries:")
        for summary in matchup_summaries:
            print(f"  {summary}")
            
        # Calculate total number of simulations
        total_simulations = args.simulations * len(all_possible_combos)
        
        # Print overall results
        print("\n===== OVERALL TOURNAMENT RESULTS =====")
        print(f"Total matchups: {len(all_possible_combos)}")
        print(f"Simulations per matchup: {args.simulations}")
        print(f"Total simulations: {total_simulations}")
        print("\nResults by player:")
        for player, wins in total_results.items():
            win_percentage = (wins / total_simulations) * 100
            print(f"  {player}: {wins} wins ({win_percentage:.1f}%)")
        print("=========================================")
        return
    
    # Run a single matchup if deck1 and deck2 are specified
    if args.deck1 and args.deck2:
        player1 = setup_player("Stewart", args.deck1, agent_class=CustomAgent)
        player2 = setup_player("Kimberly", args.deck2, agent_class=OpponentAgent)
        
        results = run_simulations(player1, player2, args.simulations, args.debug)
        
        # Print deck contents first
        print_deck_contents("Stewart", player1.deck)
        print_deck_contents("Kimberly", player2.deck)
        
        # Then print enhanced results
        print_results_summary(results, args.simulations, args.deck1, args.deck2)
        return
    
    # Default behavior: run pikachu_deck vs sandslash_deck
    print("No decks specified. Running default matchup: pikachu_deck vs sandslash_deck")
    player1 = setup_player("Stewart", "pikachu_deck", agent_class=CustomAgent)
    player2 = setup_player("Kimberly", "dialga_deck", agent_class=CustomAgent)
    
    results = run_simulations(player1, player2, args.simulations, args.debug)
    
    # Print deck contents first
    print_deck_contents("Stewart", player1.deck)
    print_deck_contents("Kimberly", player2.deck)
    
    # Then print enhanced results
    print_results_summary(results, args.simulations, "pikachu_deck", "sandslash_deck")


if __name__ == "__main__":
    main() 
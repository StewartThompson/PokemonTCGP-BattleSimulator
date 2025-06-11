#!/usr/bin/env python3

import argparse
import random
import sys
import os
from game.battle_engine import BattleEngine

# Add the current directory to path so we can import load_deck
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from load_deck import DeckLoader

class Match:
    """Simple match class"""
    
    def __init__(self, deck1_name: str = None, deck2_name: str = None, debug: bool = False):
        self.deck_loader = DeckLoader()
        self.deck1_name = deck1_name
        self.deck2_name = deck2_name
        self.deck1 = None
        self.deck2 = None
        self.debug = debug
        
        if deck1_name:
            self.deck1 = self.deck_loader.load_deck_by_name(deck1_name)
        if deck2_name:
            self.deck2 = self.deck_loader.load_deck_by_name(deck2_name)
    
    def start_battle(self):
        """Start battle and return winner"""
        battle_engine = BattleEngine(self.deck1, self.deck2, self.debug)
        battle_engine.start_battle()

        return battle_engine.winner
    
def main():
    parser = argparse.ArgumentParser(description="Pokemon Match Simulator")
    parser.add_argument("--deck1", nargs=2, help="Player 1: agent deck_name")
    parser.add_argument("--deck2", nargs=2, help="Player 2: agent deck_name") 
    parser.add_argument("--simulations", type=int, default=1)
    parser.add_argument("--debug", action="store_true", help="Enable debug output")
    
    args = parser.parse_args()
    
    if not args.deck1 or not args.deck2:
        print("❌ Need --deck1 and --deck2")
        return
    
    _, deck1_name = args.deck1
    _, deck2_name = args.deck2
    
    # Pass debug flag to Match constructor
    match = Match(deck1_name, deck2_name, debug=args.debug)
    
    if not match.deck1:
        print(f"❌ Deck '{deck1_name}' not found")
        return
    if not match.deck2:
        print(f"❌ Deck '{deck2_name}' not found") 
        return
    
    print(f"  {deck1_name} vs {deck2_name}")
    
    results = {"Player 1": 0, "Player 2": 0}
    for i in range(args.simulations):
        winner = match.start_battle()
        results[winner] += 1
    
    print(f"Results: Player 1: {results['Player 1']}, Player 2: {results['Player 2']}")

if __name__ == "__main__":
    main()

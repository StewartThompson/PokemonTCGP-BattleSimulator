import csv
import os
import time
from concurrent.futures import ProcessPoolExecutor, as_completed
import pandas as pd
from itertools import combinations
from collections import Counter

# Assuming these are defined in their respective modules
from moteur.cartes.pokemon import Pokemon
from moteur.combat.attack import Attack
from moteur.combat.ability import Ability
from moteur.cartes.item import Item
from moteur.cartes.trainer import Trainer
from moteur.cartes.tool import Tool

from utils import parse_energy_cost, parse_pipe_separated, contains_trainer, contains_item, satisfies_pre_evolution_rule

# Constants
TYPES_LIST = ["fire", "water", "rock", "grass", "normal", "electric", "psychic", "dark", "metal", "dragon", "fairy"]
MAX_DECKS = 10_000_000
OUTPUT = "deck_counts.csv"
FIELDNAMES = ["type", "include_normal", "deck_size", "count", "time"]
ABSOLUTE_FOLDER_PATH = os.path.dirname(os.path.abspath(__file__)) + "/"

class CardDatabase:
    """Manages all card data loaded from CSV files."""
    def __init__(self):
        self.pokemons = {}
        self.attacks = {}
        self.abilities = {}
        self.tools = {}
        self.items = {}
        self.trainers = {}

    def load_from_csv(self, folder_path):
        """Loads card data from CSV files into the database."""
        # Load abilities
        abilities_df = pd.read_csv(os.path.join(folder_path, 'abilities.csv'))
        for _, row in abilities_df.iterrows():
            self.abilities[row['ID']] = Ability(
                ability_id=row['ID'],
                name=row['Name'],
                description=row['Description'],
                effect_type=row['effect type'],
                special_values=parse_pipe_separated(row['special values']),
                amount_of_times=row['amount'] if not pd.isna(row['amount']) else None
            )

        # Load attacks
        attacks_df = pd.read_csv(os.path.join(folder_path, 'attacks.csv'))
        for _, row in attacks_df.iterrows():
            damage_str = str(row['damage']) if not pd.isna(row['damage']) else "0"
            damage_value = int(damage_str[:-1]) if damage_str.endswith('x') else int(damage_str) if damage_str.isdigit() else 0
            self.attacks[row['ID']] = Attack(
                id_attaque=row['ID'],
                name=row['Name'],
                description=row['Description'] if not pd.isna(row['Description']) else "",
                damage=damage_value,
                energy_cost=parse_energy_cost(row['energy cost']),
                effect_type=row['attack effect'] if not pd.isna(row['attack effect']) else None,
                special_values=parse_pipe_separated(row['special values'])
            )

        # Load Pokémon
        pokemons_df = pd.read_csv(os.path.join(folder_path, 'pokemons.csv'))
        for _, row in pokemons_df.iterrows():
            attack_ids = [int(aid) for aid in str(row['Attacks IDs']).split('|') if aid.strip()] if not pd.isna(row['Attacks IDs']) else []
            self.pokemons[row['ID']] = Pokemon(
                card_id=row['ID'],
                name=row['Name'],
                stage=row['Stage'],
                attack_ids=attack_ids,
                ability_id=int(row['Ability ID']) if not pd.isna(row['Ability ID']) else None,
                max_hp=int(row['hp']) if not pd.isna(row['hp']) else 0,
                pre_evolution_name=row['pre-evo name'] if not pd.isna(row['pre-evo name']) else None,
                evolutions_name=row['evo name'] if not pd.isna(row['evo name']) else None,
                pokemon_type=row['type'] if not pd.isna(row['type']) else None,
                weakness=row['weakness'] if not pd.isna(row['weakness']) else None,
                retreat_cost=int(row['retreat cost']) if not pd.isna(row['retreat cost']) else 0
            )

        # Load items
        items_df = pd.read_csv(os.path.join(folder_path, 'items.csv'))
        for _, row in items_df.iterrows():
            self.items[row['ID']] = Item(
                item_id=row['ID'],
                name=row['Name'],
                effect=row['effect_type'],
                special_values=parse_pipe_separated(row['special values'])
            )

        # Load trainers
        trainers_df = pd.read_csv(os.path.join(folder_path, 'trainers.csv'))
        for _, row in trainers_df.iterrows():
            self.trainers[row['ID']] = Trainer(
                trainer_id=row['ID'],
                name=row['Name'],
                effect=row['effect_type'],
                special_values=parse_pipe_separated(row['special values'])
            )

        # Load tools if available
        tools_path = os.path.join(folder_path, 'tools.csv')
        if os.path.exists(tools_path):
            tools_df = pd.read_csv(tools_path)
            for _, row in tools_df.iterrows():
                self.tools[row['tool_id']] = Tool(
                    tool_id=row['tool_id'],
                    name=row['name'],
                    effect=row['effect'],
                    special_values=parse_pipe_separated(row['special_values']) if 'special_values' in row else None
                )

def generate_all_decks(db, deck_size=20, pokemon_type=None, include_normal=False, include_cards=None, as_objects=False):
    """Generates all possible decks based on given parameters."""
    include_cards = include_cards or []
    pool, id_to_obj = [], {}

    # Helper to add cards to pool with optional filter
    def _add(dic, card_type, extra=lambda cid, obj: True):
        for cid, obj in dic.items():
            if extra(cid, obj):
                key = (cid, card_type)
                pool.append(key)
                id_to_obj[key] = obj

    # Populate pool
    _add(db.pokemons, "pokemon", lambda _, o: (
        pokemon_type is None or o.pokemon_type == pokemon_type or (include_normal and o.pokemon_type == "normal")
    ))
    _add(db.items, "item", lambda cid, _: cid not in (3, 4))
    _add(db.trainers, "trainer")
    _add(db.tools, "tool")

    # Add explicitly included cards
    for key in include_cards:
        if key not in id_to_obj:
            pool.append(key)
            id_to_obj[key] = (
                db.pokemons[key[0]] if key[1] == "pokemon" else
                db.items[key[0]] if key[1] == "item" else
                db.trainers[key[0]] if key[1] == "trainer" else
                db.tools[key[0]]
            )

    n = len(pool)
    must = Counter(include_cards)
    max_twos = deck_size // 2

    # Generate combinations
    for k in range(max_twos + 1):  # Number of cards included twice
        singles = deck_size - 2 * k
        if singles < 0 or singles > n - k:
            continue
        for dup_set in combinations(range(n), k):
            if any(pool[i] in must and must[pool[i]] > 2 for i in dup_set):
                continue
            dup_set = set(dup_set)
            remaining = [i for i in range(n) if i not in dup_set]
            for single_set in combinations(remaining, singles):
                counts = {pool[i]: 2 for i in dup_set}
                counts.update({pool[i]: 1 for i in single_set})
                if any(must[pool[i]] > counts.get(pool[i], 0) for i in (*dup_set, *single_set)):
                    continue
                if not satisfies_pre_evolution_rule(counts, id_to_obj):
                    continue
                if as_objects:
                    deck = [id_to_obj[pool[i]] for i in dup_set for _ in range(2)] + [id_to_obj[pool[i]] for i in single_set]
                    yield deck
                else:
                    yield counts

def _worker(args, db):
    """Counts decks for a given type and size, returning result rows."""
    pokemon_type, size = args
    start = time.time()
    count = sum(1 for _ in generate_all_decks(db, deck_size=size, pokemon_type=pokemon_type, include_normal=False, as_objects=False))
    elapsed = round(time.time() - start, 3)
    return [{"type": pokemon_type, "include_normal": False, "deck_size": size, "count": count, "time": elapsed}]

def main():
    """Main execution logic."""
    db = CardDatabase()
    db.load_from_csv(ABSOLUTE_FOLDER_PATH + 'assets/database/')

    if not os.path.exists(OUTPUT):
        with open(OUTPUT, "w", newline="") as f:
            csv.DictWriter(f, FIELDNAMES).writeheader()

    job_args = [(t, s) for t in TYPES_LIST for s in range(1, 21)]
    job_args.sort(key=lambda x: x[1])  # Sort by deck size

    with ProcessPoolExecutor() as pool, open(OUTPUT, "a", newline="") as f:
        writer = csv.DictWriter(f, FIELDNAMES)
        futures = {pool.submit(_worker, arg, db): arg for arg in job_args}
        for future in as_completed(futures):
            for row in future.result():
                writer.writerow(row)
                f.flush()
                print(f"{row['type']} | normals={row['include_normal']} | size={row['deck_size']} → {row['count']} | {row['time']} s")

if __name__ == "__main__":
    main()
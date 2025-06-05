import csv
import os
import time
from concurrent.futures import ProcessPoolExecutor, as_completed

import pandas as pd
from moteur.cartes.pokemon import Pokemon
from moteur.combat.attack import Attack
from moteur.combat.ability import Ability
from moteur.cartes.item import Item
from moteur.cartes.trainer import Trainer

types_list = ["fire", "water", "rock", "grass", "normal", "electric", "psychic", "dark", "metal", "dragon", "fairy"]
types_dict = {types_list[i]: 0 for i in range(len(types_list))}

MAX_DECKS = 10_000_000
OUTPUT     = "deck_counts.csv"
FIELDNAMES = ["type", "include_normal", "deck_size", "count", "time"]

# ---------------------------------------------------------------------------
# put this *above* so every subprocess can import it
def _worker(args):
    t, size = args
    rows = []

    start = time.time()
    cnt = 0
    for _ in generate_all_decks(deck_size=size,
                                pokemon_type=t,
                                include_normal=False,
                                as_objects=False):
        cnt += 1

    elapsed = round(time.time() - start, 3)

    rows.append(dict(type=t,
                     include_normal=False,
                     deck_size=size,
                     count=cnt,
                     time=elapsed))
    return rows
all_pokemons = {}
all_attacks = {}
all_abilities = {}
all_tools = {}
all_items = {}
all_trainers = {}

blaine_list = [38, 43, 44]
koga_list = [175, 177]
brock_list = [149, 150]
surge_list = [95, 100, 101]

def get_basic_pokemons(hand):
    basic_pokemons = []
    for card in hand:
        if isinstance(card, Pokemon):
            if card.stage == "basic" or "ex" in card.stage:
                basic_pokemons.append(card)
    return basic_pokemons


def parse_energy_cost(energy_cost_str):
    """Parse energy cost string into a dictionary."""
    if not energy_cost_str or pd.isna(energy_cost_str):
        return {energy_type: 0 for energy_type in types_list}

    energy_cost = {energy_type: 0 for energy_type in types_list}
    for cost in energy_cost_str.split('|'):
        if ':' in cost:
            energy_type, amount = cost.split(':')
            energy_cost[energy_type] = int(amount)

    return energy_cost


def parse_pipe_separated(value):
    """Parse pipe-separated values into a list, converting integer-looking strings to ints."""
    # Handle missing
    if pd.isna(value) or value == "":
        return None

    def _maybe_int(x):
        x = x.strip()
        try:
            return int(x)
        except (ValueError, TypeError):
            return x

    # If it's a pipe-separated string, return list with conversion
    if isinstance(value, str) and '|' in value:
        return [_maybe_int(item) for item in value.split('|')]
    return [_maybe_int(value)]


def load_default_database():
    global all_pokemons, all_attacks, all_abilities, all_tools, all_items, all_trainers

    # Load abilities
    abilities_df = pd.read_csv(absolute_folder_path+'assets/database/abilities.csv')
    for _, row in abilities_df.iterrows():
        ability_id = row['ID']
        all_abilities[ability_id] = Ability(
            ability_id=ability_id,
            name=row['Name'],
            description=row['Description'],
            effect_type=row['effect type'],
            special_values=parse_pipe_separated(row['special values']),
            amount_of_times=row['amount'] if not pd.isna(row['amount']) else None
        )

    # Load attacks
    attacks_df = pd.read_csv(absolute_folder_path+'assets/database/attacks.csv')
    for _, row in attacks_df.iterrows():
        attack_id = row['ID']

        all_attacks[attack_id] = Attack(
            id_attaque=attack_id,
            name=row['Name'],
            description=row['Description'] if not pd.isna(row['Description']) else "",
            damage=int(row['damage']) if not pd.isna(row['damage']) else 0,
            energy_cost=parse_energy_cost(row['energy cost']),
            effect_type=row['attack effect'] if not pd.isna(row['attack effect']) else None,
            special_values=parse_pipe_separated(row['special values'])
        )

    # Load Pokemons
    pokemons_df = pd.read_csv(absolute_folder_path+'assets/database/pokemons.csv')
    for _, row in pokemons_df.iterrows():
        pokemon_id = row['ID']

        # Parse attack IDs
        attack_ids = []
        if not pd.isna(row['Attacks IDs']):
            attack_ids = [int(a_id) for a_id in row['Attacks IDs'].split('|')]

        ability_id = None
        if 'Ability ID' in row and not pd.isna(row['Ability ID']):
            ability_id = int(row['Ability ID'])

        # Handle potential pipe-separated evolution names
        evo_name = parse_pipe_separated(row['evo name']) if not pd.isna(row['evo name']) else None

        all_pokemons[pokemon_id] = Pokemon(
            card_id=pokemon_id,
            name=row['Name'],
            stage=row['Stage'],
            attack_ids=attack_ids,
            ability_id=ability_id,
            max_hp=int(row['hp']),
            pre_evolution_name=row['pre-evo name'] if not pd.isna(row['pre-evo name']) else None,
            evolutions_name=evo_name,
            pokemon_type=row['type'] if not pd.isna(row['type']) else None,
            weakness=row['weakness'] if not pd.isna(row['weakness']) else None,
            retreat_cost=int(row['retreat cost']) if not pd.isna(row['retreat cost']) else 0,
        )

    # Load Items
    items_df = pd.read_csv(absolute_folder_path+'assets/database/items.csv')
    for _, row in items_df.iterrows():
        item_id = row['ID']
        all_items[item_id] = Item(
            item_id=item_id,
            name=row['Name'],
            effect=row['effect_type'],
            special_values=parse_pipe_separated(row['special values'])
        )

    # Load Trainers
    trainers_df = pd.read_csv(absolute_folder_path+'assets/database/trainers.csv')
    for _, row in trainers_df.iterrows():
        trainer_id = row['ID']
        all_trainers[trainer_id] = Trainer(
            trainer_id=trainer_id,
            name=row['Name'],
            effect=row['effect_type'],
            special_values=parse_pipe_separated(row['special values'])
        )

    # Initialize tools dictionary (no CSV data provided)
    all_tools = {}

def contains_trainer(cards):
    """Check if the list of cards contains any trainer cards."""
    for card in cards:
        if card and card.card_type == "trainer":
            return True
    return False

def contains_hand_pokemon(cards, player_hand):
    """Check if the player's hand contains any Pokémon cards."""
    cards_in_hand = []
    for card in cards:
        if card and card.card_type == "pokemon" and card in player_hand:
            cards_in_hand.append(card)
    return cards_in_hand

def contains_item(cards):
    """Check if the list of cards contains any item cards."""
    for card in cards:
        if card and card.card_type == "item":
            return True
    return False

absolute_folder_path = os.path.dirname(os.path.abspath(__file__)) + "/"


from itertools import combinations
from collections import Counter

def generate_all_decks(
    deck_size=20,
    pokemon_type=None,
    include_normal=False,
    include_cards=None,
    as_objects=False,
):
    include_cards = include_cards or []

    pool, id_to_obj = [], {}

    def _add(dic, card_type, extra=lambda cid, o: True):
        for cid, obj in dic.items():
            if extra(cid, obj):
                key = (cid, card_type)
                pool.append(key)
                id_to_obj[key] = obj

    _add(all_pokemons, "pokemon",
         lambda _cid, o: (
             pokemon_type is None
             or o.pokemon_type == pokemon_type
             or (include_normal and o.pokemon_type == "normal")
         ))
    _add(all_items, "item", lambda cid, _o: cid not in (3, 4))
    _add(all_trainers, "trainer")
    _add(all_tools, "tool")

    for key in include_cards:
        if key not in id_to_obj:
            id_to_obj[key] = (
                all_pokemons[key[0]] if key[1] == "pokemon" else
                all_items[key[0]] if key[1] == "item" else
                all_trainers[key[0]] if key[1] == "trainer" else
                all_tools[key[0]]
            )
            pool.append(key)

    n = len(pool)
    must = Counter(include_cards)

    # map pokémon names to keys for quick pre-evo lookup
    name_to_keys = {}
    for key in pool:
        if key[1] == "pokemon":
            name_to_keys.setdefault(id_to_obj[key].name, []).append(key)

    max_twos = deck_size // 2
    for k in range(max_twos + 1):
        singles = deck_size - 2 * k
        if singles < 0 or singles > n - k:
            continue

        for dup_set in combinations(range(n), k):
            if any(pool[i] in must and must[pool[i]] > 2 for i in dup_set):
                continue
            dup_set = set(dup_set)
            remaining = [i for i in range(n) if i not in dup_set]

            for single_set in combinations(remaining, singles):
                if any(
                    (pool[i] in must and (2 if i in dup_set else 1) < must[pool[i]])
                    for i in (*dup_set, *single_set)
                ):
                    continue

                counts = {pool[i]: 2 for i in dup_set}
                counts.update({pool[i]: 1 for i in single_set})

                # --- pre-evolution rule ------------------------------------
                names_present = {
                    id_to_obj[key].name
                    for key in counts
                    if key[1] == "pokemon"
                }
                valid = True
                for key in counts:
                    if key[1] != "pokemon":
                        continue
                    p = id_to_obj[key]
                    if p.stage != "basic" and "ex" not in p.stage:
                        prev = p.pre_evolution_name
                        if prev and prev not in names_present:
                            valid = False
                            break
                if not valid:
                    continue
                # -----------------------------------------------------------

                if as_objects:
                    deck = []
                    for i in dup_set:
                        deck.extend([id_to_obj[pool[i]]] * 2)
                    for i in single_set:
                        deck.append(id_to_obj[pool[i]])
                    yield deck
                else:
                    yield counts



load_default_database()   # make sure the main process is ready


if __name__ == "__main__":
    if not os.path.exists(OUTPUT):
        with open(OUTPUT, "w", newline="") as f:
            csv.DictWriter(f, FIELDNAMES).writeheader()


    job_args = [(t, s) for t in types_list for s in range (1, 21)]
    # sort them by smallest s first
    job_args.sort(key=lambda x: x[1])  # sort by deck size

    with ProcessPoolExecutor(max_workers=None) as pool, \
            open(OUTPUT, "a", newline="") as f:

        writer = csv.DictWriter(f, FIELDNAMES)
        futures = {pool.submit(_worker, arg): arg for arg in job_args}

        for fut in as_completed(futures):
            for row in fut.result():  # each worker returns 20 rows
                writer.writerow(row)
                f.flush()
                print(f"{row['type']} | normals={row['include_normal']} | "
                      f"size={row['deck_size']} → {row['count']} | {row['time']} s")
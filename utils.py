import os

import pandas as pd
from moteur.cartes.pokemon import Pokemon
from moteur.combat.attack import Attack
from moteur.combat.ability import Ability
from moteur.cartes.tool import Tool
from moteur.cartes.item import Item
from moteur.cartes.trainer import Trainer

types_list = ["fire", "water", "rock", "grass", "normal", "electric", "psychic", "dark", "metal", "dragon", "fairy"]
types_dict = {types_list[i]: 0 for i in range(len(types_list))}



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
        except (ValueError, TypeError) as e:
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
            attack_ids = [int(id) for id in row['Attacks IDs'].split('|')]

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

absolute_folder_path = os.path.dirname(os.path.abspath(__file__)) + "/"
# load_default_database()
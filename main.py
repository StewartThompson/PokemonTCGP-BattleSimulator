import time

import utils
utils.load_default_database()
import random
from moteur import match, player
from utils import get_basic_pokemons, all_pokemons, all_items, all_trainers
j1 = player.Player("j1")
j2 = player.Player("j2")


i = 1
results = {}
# random_deck_1 = random.sample(list(utils.all_pokemons.values()) + list(utils.all_items.values()) + list(utils.all_trainers.values()), 20)
# random_deck_2 = random.sample(list(utils.all_pokemons.values()) + list(utils.all_items.values()) + list(utils.all_trainers.values()), 20)
# while len(get_basic_pokemons(random_deck_1)) < 1 or len(get_basic_pokemons(random_deck_2)) < 1:
#     random_deck_1 = random.sample(list(utils.all_pokemons.values()) + list(utils.all_items.values()) + list(utils.all_trainers.values()), 20)
#     random_deck_2 = random.sample(list(utils.all_pokemons.values()) + list(utils.all_items.values()) + list(utils.all_trainers.values()), 20)
#     # print(get_basic_pokemons(random_deck_1))
#     # print(get_basic_pokemons(random_deck_2))
#     # print()

pikachu_deck = [
    all_pokemons[96], all_pokemons[104], all_pokemons[104], all_pokemons[99], all_pokemons[99], all_pokemons[100], all_pokemons[99],
    all_items[1], all_items[1], all_items[2], all_items[2], all_items[5], all_items[5], all_items[6],
    all_trainers[9], all_trainers[9], all_trainers[7], all_trainers[7], all_trainers[5], all_trainers[5]
]

sandlash_deck = [
    all_pokemons[137], all_pokemons[137], all_pokemons[138], all_pokemons[138], all_pokemons[139], all_pokemons[140], all_pokemons[141], all_pokemons[141], all_pokemons[142], all_pokemons[142], all_pokemons[151], all_pokemons[151], all_pokemons[153],
    all_items[1], all_items[1], all_items[5], all_items[5], all_items[2],
    all_trainers[9], all_trainers[9]
]

j1.set_deck(pikachu_deck)
j2.set_deck(sandlash_deck)

m = match.Match(j1, j2)
result = m.start_battle()
if result == j1:
    result = "j1"
elif result == j2:
    result = "j2"
if result in results:
    results[result] += 1
else:
    results[result] = 1
print(i, results)
i+=1
from utils import load_default_database, get_card_database

load_default_database()
db = get_card_database()
pokemon_dict = db.get('pokemon', {})
sample_keys = list(pokemon_dict.keys())[:5]
print('Pokemon dict keys sample:', sample_keys)

if sample_keys:
    sample_pokemon = pokemon_dict[sample_keys[0]]
    print('Sample pokemon type:', type(sample_pokemon))
    print('Sample pokemon name:', getattr(sample_pokemon, 'name', 'No name'))
    print('Sample pokemon attributes:', dir(sample_pokemon))

# Check for 'Tynamo' specifically
print('\nSearching for Tynamo:')
for key, pokemon in pokemon_dict.items():
    if hasattr(pokemon, 'name') and 'Tynamo' in pokemon.name:
        print(f'Found: {pokemon.name} (key: {key})')
        break
else:
    print('Tynamo not found')

# Check first few Pokemon names
print('\nFirst 10 Pokemon names:')
count = 0
for key, pokemon in pokemon_dict.items():
    if hasattr(pokemon, 'name'):
        print(f'{pokemon.name}')
        count += 1
        if count >= 10:
            break 
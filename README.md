# PokemonTCGP-BattleSimulator

A Python-based Pokémon TCG Pocket Battle Simulator designed for running automated battle simulations. This tool is ideal for developing and testing AI/bot strategies, analyzing deck performance, and exploring game mechanics with cards from the original TCG extension and promo sets.

## Table of Contents

- [Features](#features)
- [Project Structure](#project-structure)
- [Database](#database)
  - [Overview](#overview)
  - [File Descriptions](#file-descriptions)
    - [`abilities.csv`](#abilitiescsv)
    - [`attacks.csv`](#attackscsv)
    - [`items.csv`](#itemscsv)
    - [`pokemons.csv`](#pokemonscsv)
    - [`trainers.csv`](#trainerscsv)
- [How It Works](#how-it-works)
  - [Game Engine (`moteur/`)](#game-engine-moteur)
  - [Database Loading (`utils.py`)](#database-loading-utilspy)
- [Installation](#installation)
- [Usage](#usage)
  - [Running a Simulation](#running-a-simulation)
  - [Customizing Simulations](#customizing-simulations)
- [Extending the Simulator](#extending-the-simulator)
  - [Adding New Cards](#adding-new-cards)
  - [Modifying Game Logic](#modifying-game-logic)
  - [Developing AI/Bots](#developing-aibots)
- [Future Enhancements](#future-enhancements)
- [Contributing](#contributing)

## Features

*   **Turn-based Battle Simulation:** Emulates core Pokémon TCG Pocket battle mechanics.
*   **CSV-Powered Database:** Easily view and manage card data for Pokémon, attacks, abilities, items, and trainers.
*   **Initial Card Set:** Includes cards primarily from the first TCG extension and associated promo cards.
*   **Extensible:** Designed to allow for the addition of new cards and modification of game rules.
*   **AI/Bot Development Platform:** Provides a framework for creating and testing automated player strategies.
*   **Deck Testing:** Facilitates experimentation with different deck builds and strategies.

## Project Structure

```
PokemonTCGP-BattleSimulator/
├── main.py                 # Main script to run simulations
├── utils.py                # Utility functions, including database loading
├── assets/
│   └── database/
│       ├── abilities.csv
│       ├── attacks.csv
│       ├── items.csv
│       ├── pokemons.csv
│       └── trainers.csv
└── moteur/
    ├── match.py            # Core game logic and match orchestration
    ├── player.py           # Player class, manages player state
    ├── cartes/
    │   ├── item.py
    │   ├── pokemon.py
    │   ├── tool.py         # (Note: Tool cards are defined but not yet in CSVs/gameplay)
    │   └── trainer.py
    └── combat/
        ├── ability.py
        └── attack.py
```

## Database

### Overview

The simulator's card data is stored in CSV files located in the `assets/database/` directory. This data is loaded at runtime by `utils.py`. The `effect type` / `attack effect` and `special values` columns are crucial as they drive the game logic in `moteur/match.py`.

### File Descriptions

#### `abilities.csv`
Stores Pokémon abilities.
*   `ID`: Unique identifier.
*   `Name`: Ability name.
*   `Description`: Text description.
*   `amount`: How often it can be used (e.g., "once" per turn).
*   `effect type`: A keyword string that `match.py` uses to determine the ability's logic (e.g., `heal_all`, `switch_active`).
*   `special values`: Pipe-separated values that provide parameters for the `effect type` (e.g., `20` for `heal_all`, `enemy|self` for `switch_active`).

#### `attacks.csv`
Stores Pokémon attacks.
*   `ID`: Unique identifier.
*   `Name`: Attack name.
*   `Description`: Text description.
*   `damage`: Base damage of the attack.
*   `energy cost`: Pipe-separated string defining energy requirements (e.g., `water:2|normal:1`).
*   `attack effect`: Keyword string for the attack's additional effect (e.g., `discard_opponent_energy`, `self_heal`).
*   `special values`: Pipe-separated parameters for the `attack effect`.

#### `items.csv`
Stores Item cards.
*   `ID`: Unique identifier.
*   `Name`: Item name.
*   `Description`: Text description.
*   `effect_type`: Keyword string for the item's effect.
*   `special values`: Pipe-separated parameters for the `effect_type`.

#### `pokemons.csv`
Stores Pokémon card data.
*   `ID`: Unique identifier.
*   `Name`: Pokémon name.
*   `Stage`: Evolution stage (e.g., `basic`, `stage1`, `stage2_ex`).
*   `Attacks IDs`: Pipe-separated list of attack IDs this Pokémon can use.
*   `hp`: Maximum Hit Points.
*   `pre-evo name`: Name of the Pokémon it evolves from.
*   `evo name`: Pipe-separated list of Pokémon it can evolve into.
*   `retreat cost`: Number of energy cards to discard for retreating.
*   `type`: Pokémon's energy type (e.g., `grass`, `fire`).
*   `weakness`: Energy type this Pokémon is weak to.
*   `Ability ID`: ID of the ability this Pokémon has, if any.

#### `trainers.csv`
Stores Trainer (Supporter) cards.
*   `ID`: Unique identifier.
*   `Name`: Trainer name.
*   `Description`: Text description.
*   `effect_type`: Keyword string for the trainer's effect.
*   `special values`: Pipe-separated parameters for the `effect_type`.

## How It Works

### Game Engine (`moteur/`)

The core game logic resides in the `moteur/` directory:

*   **`match.py`**: This is the heart of the simulator. The `Match` class orchestrates the entire game flow, from setup (drawing initial hands, placing active/benched Pokémon) to turn-by-turn actions (drawing, playing cards, attaching energy, attacking, checking win conditions). It interprets the `effect type` and `special values` from the database to execute card effects.
    *   **Decision Making**: Currently, `match.py` uses `get_chosen_card()` and `get_action()` which prompt for user input via `input()`. This is the primary point for integrating AI or bot logic.
*   **`player.py`**: The `Player` class manages all aspects of a player's state, including their deck, hand, discard pile, active Pokémon, benched Pokémon, prize points, and energy pile.
*   **`cartes/`**: This sub-directory contains classes for each card type (`Pokemon`, `Item`, `Trainer`, `Tool`). These classes primarily act as data containers for card attributes loaded from the CSVs.
*   **`combat/`**: Contains classes for `Attack` and `Ability`, which also primarily store data loaded from the CSVs.

### Database Loading (`utils.py`)

The `utils.py` script is responsible for:
1.  Reading the CSV files from `assets/database/`.
2.  Parsing the data, including specialized parsing for `energy cost` and pipe-separated `special values`.
3.  Instantiating `Pokemon`, `Attack`, `Ability`, `Item`, and `Trainer` objects.
4.  Storing these objects in global dictionaries (e.g., `all_pokemons`, `all_attacks`) for easy access by the game engine.
The `load_default_database()` function must be called before a match can start.

## Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/your-username/PokemonTCGP-BattleSimulator.git
    cd PokemonTCGP-BattleSimulator
    ```
2.  **Ensure Python is installed:** Python 3.7+ is recommended.
3.  **Install dependencies:** The project uses `pandas` for reading CSV files.
    ```bash
    pip install pandas
    ```

## Usage

### Running a Simulation

The `main.py` script provides an example of how to set up and run a simulation:

1.  **Define Decks:** Decks are Python lists of card objects. `main.py` shows examples like `pikachu_deck` and `sandlash_deck`. You'll need to use card objects fetched from the `utils.all_pokemons`, `utils.all_items`, etc., dictionaries.
    ```python
    # In main.py
    import utils
    utils.load_default_database() # Crucial: Load data first
    from moteur import match, player

    # Example deck definition
    pikachu_deck = [
        utils.all_pokemons[96], utils.all_pokemons[104], # ... and so on
        utils.all_items[1], utils.all_items[1],         # ...
        utils.all_trainers[9], utils.all_trainers[9]    # ...
    ]
    ```
2.  **Create Player Instances:**
    ```python
    j1 = player.Player("j1")
    j2 = player.Player("j2")
    j1.set_deck(pikachu_deck)
    j2.set_deck(sandlash_deck) # Replace with another deck
    ```
3.  **Start the Match:**
    ```python
    m = match.Match(j1, j2)
    result = m.start_battle()
    print(f"Winner: {result.name if result else 'Draw'}")
    ```
4.  **Run the script:**
    ```bash
    python main.py
    ```
    During the simulation, you will be prompted to make decisions for each player via the console (due to the `input()` calls in `match.py`).

### Customizing Simulations

*   **Decks:** Modify the deck lists in `main.py` to test different card combinations. Ensure each deck has at least one Basic Pokémon.
*   **Number of Simulations:** Wrap the match setup and `start_battle()` call in a loop in `main.py` to run multiple simulations and gather statistics.
*   **Automated Decisions:** To run simulations without manual input, you'll need to modify `get_chosen_card()` and `get_action()` in `moteur/match.py` (see [Developing AI/Bots](#developing-aibots)).

## Extending the Simulator

### Adding New Cards

1.  **Identify Card Details:** Gather all necessary information for the new card (HP, attacks, ability, effects, etc.).
2.  **Update CSVs:**
    *   Add a new row to the relevant CSV file(s) (`pokemons.csv`, `attacks.csv`, `abilities.csv`, `items.csv`, `trainers.csv`).
    *   Ensure `ID`s are unique.
    *   For `effect type` / `attack effect` and `special values`:
        *   If the effect is similar to an existing one, reuse the `effect type` and adjust `special values`.
        *   If it's a new type of effect, you'll need to define a new `effect type` keyword and implement its logic in `moteur/match.py`.
3.  **Implement New Effects (if needed):** If you introduced a new `effect type`, add corresponding `elif` blocks in `moteur/match.py` within the card playing or attack handling sections to implement its logic.

### Modifying Game Logic

*   **Core Rules:** Changes to fundamental game rules (e.g., prize card count, hand size limits, turn phases) would primarily be made in `moteur/match.py`.
*   **Effect Implementation:** To alter how existing effects are resolved, modify the corresponding logic blocks in `moteur/match.py` that handle specific `effect type` or `attack effect` keywords.

### Developing AI/Bots

This simulator is well-suited for creating AI players. The key is to replace the manual `input()` calls in `moteur/match.py`:

1.  **Locate Decision Points:**
    *   `get_chosen_card(cards, who_choose="player")`
    *   `get_action(action_list, action_type=None)`
2.  **Modify for Programmatic Choice:** Instead of `input()`, your AI logic would analyze the `cards` or `action_list` and the current game state (accessible via `current_player` and `opponent` objects within `Match`) to return a choice.
    ```python
    # Example modification in moteur/match.py (conceptual)

    # def get_action(action_list, action_type=None, player_ai=None):
    #     if player_ai:
    #         return player_ai.choose_action(action_list, action_type, current_game_state)
    #     else:
    #         print("action_type", action_type)
    #         print("Choose Action Options :")
    #         for i, e in enumerate(action_list):
    #             print(f"{i}: {e}")
    #         return action_list[int(input("Choose an action by index: "))]
    ```
3.  **AI State Access:** Your AI will need access to the game state. This can be passed to your AI's decision-making functions. The `Match` object holds references to both `Player` objects, which in turn contain information about their hand, active/bench Pokémon, etc.
4.  **Example AI Structure (Separate File):**
    ```python
    # ai_player.py (new file)
    import random

    class SimpleAI:
        def __init__(self, player_object_in_match):
            self.player = player_object_in_match # Reference to the AI's player object

        def choose_card(self, available_cards, game_state):
            # Simple AI: pick a random card
            if not available_cards: return None
            return random.choice(available_cards)

        def choose_action(self, available_actions, action_type, game_state):
            # Simple AI: pick a random action
            if not available_actions: return None
            # Prioritize attacking if possible, otherwise random
            attack_actions = [a for a in available_actions if isinstance(a, str) and a.startswith("attack_")]
            if action_type == "precise_action" and attack_actions:
                return random.choice(attack_actions)
            if "end_turn" in available_actions and len(available_actions) > 1 and action_type == "turn_action":
                # Avoid ending turn immediately if other options exist
                options = [a for a in available_actions if a != "end_turn"]
                return random.choice(options)
            return random.choice(available_actions)

    # Then, in main.py, you might instantiate AIs and pass them to the Match,
    # or modify Match to accept AI handlers.
    ```

## Future Enhancements

*   **Graphical User Interface (GUI):** For interactive play or visualization.
*   **Expanded Card Sets:** Add data for more Pokémon TCG expansions.
*   **Tool Cards & Stadiums:** Fully implement Tool card mechanics and Stadium cards.
*   **Network Play:** Allow two human players to play over a network.

### Note (English) :
**English Version:**

Hello there ! If you're interested in this project or any of my other projects, please read this message :

I'm here to invite you to AngelFire's Stuff, my personal Discord server. Here I will share all kinds of projects I'm working on, may it be programming, statistics (I love numbers, graphs, sheets, etc.), and some writing projects (so get ready to read !). If you enjoy devlogs or just following how projects develop, you'll find plenty to explore here. You can choose which topics interest you and pick roles to receive notifications or access channels—nothing is forced upon you !

Our community is bilingual, welcoming both English and French speakers. I do my best to post every important message in both languages, though sometimes there might be a slight delay. Even if my projects don't catch your interest, you're more than welcome to share your own work, get feedback, or just chat with others who share your passions, the goal is to bring together people who share the same passions !

In the server, you'll find many categories like important information, general chatting, and specific categories for code, stats, and writing projects. There are also channels for introducing yourself, sharing your own projects, suggesting new ideas for the server and for me to post personal updates. It's a discord for mature and chill individuals who enjoy similar interests, in the goal of making a united and friendly community.

Looking forward to seeing you there, even if it's just to take a quick look !

https://discord.gg/pzd7dJS72t

---

### Note (Français)
Salut toi ! Si tu es intéressé par ce projet ou n'importe quel autre de mes projets, je te conseille de lire ce message :

Je suis ravi de t'inviter dans AngelFire's Stuff, mon serveur Discord personnel. Ici, je partage tout type de projets sur lesquels je travaille—programmation, statistiques (j'adore les chiffres, les graphiques, les tableaux, etc.), et des projets d'écriture (alors prépare-toi à bien lire !). Si tu aimes les devlogs, ou juste suivre comment les projets évoluent, tu trouveras plein de choses à explorer ici. Tu peux choisir les sujets qui t'intéressent et sélectionner les rôles pour recevoir des notifications ou accéder à certains salons—rien n'est forcé !

Cette communauté est bilingue, accueillant à la fois les anglophones et les francophones. Je fais de mon mieux pour publier les messages importants dans les deux langues, même si parfois il peut y avoir un peu de délai ou des mots laissés en anglais lorsqu'ils sont transparents. Et même si mes projets ne t'intéressent pas, tu es plus que bienvenu de partager tes propres projets, obtenir des retours ou simplement discuter avec d'autres passionnés comme toi. Le but est de rassembler des personnes ayant des intérêts similaires !

Sur le serveur, tu trouveras des catégories pour des informations importantes, des discussions générales, et des catégories spécifiques pour les projets de programmation, de stats, et d'écriture. Il y a aussi des salons pour te présenter, partager tes propres projets, suggérer de nouvelles idées pour le serveur et suivre des actualités sur ma vie. C'est un discord pour des personnes chills et matures qui ont des intérêts similaires, dans le but de faire une communauté unie et conviviale.

Au plaisir de te voir bientôt !

https://discord.gg/pzd7dJS72t

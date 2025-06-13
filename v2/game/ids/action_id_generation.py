from typing import Dict, List


# Documentation for the labeling:
# Position: where the card needs to be to use the action (pHand, pActive, pBench1, pBench2, pBench3) 
#           Supporter cards can only be played from your hand so they would be pHand
#           Default is pActive (active pokemon's attacks can only be from active spot)
# Target: where the action is targeting (pActive, pBench1, pBench2, pBench3, pDiscard, oActive, oBench1, oBench2, oBench3, oDiscard)
#           If the action doesn't target anything, it's pActive (active pokemon attacks active pokmeon)

class ActionIdGenerator:
    @staticmethod
    def _to_camel_case(text: str) -> str:
        """Convert string to lowerCamelCase, stripping spaces/underscores."""
        if not text:
            return ""
        words = text.replace("_", " ").split()
        return words[0].lower() + "".join(w.capitalize() for w in words[1:])

    @staticmethod
    def get_attack_id(card: dict, attack: dict) -> str:
        """Generate a unique ID for an attack action.
        Format: {cardId}_{pokemonName}_{attackName}_{position}_{target}
        """
        position = attack.get("position", "pActive")
        target = attack.get("target", "oActive")
        return f"{card['id']}_{ActionIdGenerator._to_camel_case(card['name'])}_{ActionIdGenerator._to_camel_case(attack['name'])}_{position}_{target}"

    @staticmethod
    def get_ability_id(card: dict, ability: dict) -> str:
        """Generate a unique ID for an ability action.
        Format: {cardId}_{pokemonName}_{abilityName}_{position}_{target}
        """
        position = ability.get("position", "pActive") 
        target = ability.get("target", "oActive")
        return f"{card['id']}_{ActionIdGenerator._to_camel_case(card['name'])}_{ActionIdGenerator._to_camel_case(ability['name'])}_{position}_{target}"

    @staticmethod
    def evolution_ids(card: dict) -> List[str]:
        """Generate the 4 evolution action IDs for a card that can be evolved into.
        Format: {cardId}_{spot}_evolve_{basePokemon}_into_{evolvedPokemon}
        Returns empty list if card is not evolvable into.
        """
        if not card.get("evolvesFrom"):
            return []
        base = f"evolve_{ActionIdGenerator._to_camel_case(card['evolvesFrom'])}_into_{ActionIdGenerator._to_camel_case(card['name'])}"
        return [
            f"{card['id']}_a_{base}",
            f"{card['id']}_b1_{base}",
            f"{card['id']}_b2_{base}",
            f"{card['id']}_b3_{base}"
        ]

    @staticmethod
    def retreat_id(card: dict) -> str:
        """Generate a unique ID for a retreat action.
        Format: {cardId}_{pokemonName}_retreat
        """
        return f"{card['id']}_{ActionIdGenerator._to_camel_case(card['name'])}_retreat"

    @staticmethod
    def play_basic_pokemon_ids(card: dict) -> List[str]:
        """Generate the 4 'play basic pokemon' action IDs for a basic pokemon card.
        Format: {cardId}_{spot}_playBasicPokemon
        Returns empty list if card is not a basic pokemon.
        """
        base = f"play_{ActionIdGenerator._to_camel_case(card['name'])}"
        # Handle both Basic Pokemon and Fossil cards that act as Basic Pokemon
        if card.get("subtype") == "Basic":
           return [
                f"{card['id']}_a_{base}",
                f"{card['id']}_b1_{base}",
                f"{card['id']}_b2_{base}",
                f"{card['id']}_b3_{base}"
            ]
        elif card.get("subtype") == "Fossil":
            return [
                f"{card['id']}_b1_{base}",
                f"{card['id']}_b2_{base}",
                f"{card['id']}_b3_{base}"
            ]
        else:
            return []
    
    @staticmethod
    def get_all_action_ids(card: dict) -> List[str]:
        """Generate all action IDs for a card."""
        ids = []

        # Add play basic pokemon IDs
        # Add evolution trigger IDs 
        if (card.get('type') == 'Pokemon'):
            ids.extend(ActionIdGenerator.play_basic_pokemon_ids(card))
            ids.extend(ActionIdGenerator.evolution_ids(card))

        # Add ability IDs
        for ability in card.get("abilities", []):
            ids.append(ActionIdGenerator.get_ability_id(card, ability))

        # Add attack IDs
        for attack in card.get("attacks", []):
            ids.append(ActionIdGenerator.get_attack_id(card, attack))

        if (card.get('type') == 'Pokemon' and card.get("subtype") != "Fossil"):
            ids.append(ActionIdGenerator.retreat_id(card))

        return ids


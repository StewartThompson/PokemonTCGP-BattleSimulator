#!/usr/bin/env python3
"""Generate/extend ID mappings for game actions (attacks, abilities, evolution triggers)
   and cards themselves.

This script scans one or more card JSON files and produces two Python files
under `v2/game/ids/`:

1. `actions.py` – contains ACTION_IDS: Dict[str, int]
   • all attack identifiers (cardId_pokemon_attack_active_active)
   • all ability identifiers (pokemon_ability_cardId_active_active)
   • evolution trigger identifiers (evolveInto_<pokemon>_<spot>) for each
     Pokémon that *can* be evolved into (i.e. has an `evolvesFrom` field).

2. `cards.py` – contains CARD_IDS: Dict[str, int] mapping every card `id` to a
   sequential integer.

Indices are persistent: if the target file already exists, its mapping is
imported so existing numbers stay fixed and only *new* keys are appended with
next indices.

Run:
    python helperFiles/generate_actions_and_cards.py \
        --cards v2/assets/cards/a1-genetic-apex.json

The default argument processes the Genetic Apex set, but you can pass multiple
`--cards` paths.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import os
from pathlib import Path
from typing import Dict, List

DEFAULT_CARDS = ["v2/assets/cards/a1-genetic-apex.json"]
IDS_DIR = Path("v2/game/ids")
ACTIONS_PY = IDS_DIR / "actions.py"
CARDS_PY = IDS_DIR / "cards.py"


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------

def to_camel_case(text: str) -> str:
    """Convert string to lowerCamelCase, stripping spaces/underscores."""
    if not text:
        return ""
    words = text.replace("_", " ").split()
    return words[0].lower() + "".join(w.capitalize() for w in words[1:])


def load_existing_mapping(py_path: Path, var_name: str) -> Dict[str, int]:
    """Import mapping variable `var_name` from `py_path` if it exists."""
    if not py_path.exists():
        return {}
    spec = importlib.util.spec_from_file_location("ids_module", str(py_path))
    module = importlib.util.module_from_spec(spec)  # type: ignore[arg-type]
    assert spec.loader is not None
    spec.loader.exec_module(module)  # type: ignore[arg-type]
    return getattr(module, var_name, {})  # type: ignore[return-value]


# ---------------------------------------------------------------------------
# ID generation per category
# ---------------------------------------------------------------------------

def attack_id(card: dict, attack: dict) -> str:
    position = attack.get("position", "active")
    target = attack.get("target", "active")
    return f"{card['id']}_{to_camel_case(card['name'])}_{to_camel_case(attack['name'])}_{position}_{target}"


def ability_id(card: dict, ability: dict) -> str:
    position = ability.get("position", "active") 
    target = ability.get("target", "active")
    return f"{card['id']}_{to_camel_case(card['name'])}_{to_camel_case(ability['name'])}_{position}_{target}"


def evolution_ids(card: dict) -> List[str]:
    """Return the 4 evolveInto ids for the given card, if it is evolvable into."""
    if not card.get("evolvesFrom"):
        return []
    base = f"evolveInto_{to_camel_case(card['name'])}"
    return [f"a_{base}", f"b1_{base}", f"b2_{base}", f"b3_{base}"]


# ---------------------------------------------------------------------------
# mapping builders
# ---------------------------------------------------------------------------

def build_actions_mapping(cards: List[dict], existing: Dict[str, int]) -> Dict[str, int]:
    """Build mapping of action IDs to sequential integers."""
    mapping = existing.copy()
    next_id = max(mapping.values()) + 1 if mapping else 0

    def add(key: str):
        nonlocal next_id
        if key not in mapping:
            mapping[key] = next_id
            next_id += 1

    # Process in sorted order for deterministic output
    for card in sorted(cards, key=lambda c: c["id"]):
        # Add attack IDs
        for attack in card.get("attacks", []):
            add(attack_id(card, attack))

        # Add ability IDs
        for ability in card.get("abilities", []):
            add(ability_id(card, ability))

        # Add evolution trigger IDs
        if card.get("evolvesFrom"):
            for evo_id in evolution_ids(card):
                add(evo_id)

    return mapping


def build_card_mapping(cards: List[dict], existing: Dict[str, int]) -> Dict[str, int]:
    mapping = dict(existing)
    next_idx = max(mapping.values(), default=-1) + 1
    for card in cards:
        cid = card["id"]
        if cid not in mapping:
            mapping[cid] = next_idx
            next_idx += 1
    return mapping


# ---------------------------------------------------------------------------
# file writers
# ---------------------------------------------------------------------------

def write_mapping(mapping: Dict[str, int], py_path: Path, var_name: str):
    py_path.parent.mkdir(parents=True, exist_ok=True)
    lines = [f'    "{k}": {v},' for k, v in sorted(mapping.items(), key=lambda kv: kv[1])]

    header = (
        "from typing import Dict\n\n"
        "# Auto-generated by helperFiles/generate_actions_and_cards.py\n"
        "# DO NOT EDIT MANUALLY.\n\n"
        f"{var_name}: Dict[str, int] = {{\n"
    )
    footer = "}\n"
    with open(py_path, "w", encoding="utf-8") as f:
        f.write(header)
        f.write("\n".join(lines))
        f.write("\n" + footer)
    print(f"[OK] Wrote {len(mapping)} entries -> {py_path}")


# ---------------------------------------------------------------------------
# main entry
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="Generate/update action & card ID mappings.")
    parser.add_argument(
        "--cards",
        nargs="*",
        default=DEFAULT_CARDS,
        help="Card JSON file(s) to process (default: Genetic Apex A1)",
    )
    args = parser.parse_args()

    # Load card data
    all_cards: List[dict] = []
    for path in args.cards:
        if not os.path.exists(path):
            print(f"[WARN] Card file not found: {path}")
            continue
        with open(path, "r", encoding="utf-8") as f:
            all_cards.extend(json.load(f))

    print(f"[INFO] Loaded {len(all_cards)} cards from {len(args.cards)} file(s)")

    # Existing mappings (if any)
    existing_actions = load_existing_mapping(ACTIONS_PY, "ACTION_IDS")
    existing_cards = load_existing_mapping(CARDS_PY, "CARD_IDS")

    # Build new mappings
    new_actions = build_actions_mapping(all_cards, existing_actions)
    new_cards = build_card_mapping(all_cards, existing_cards)

    # Write output files
    write_mapping(new_actions, ACTIONS_PY, "ACTION_IDS")
    write_mapping(new_cards, CARDS_PY, "CARD_IDS")


if __name__ == "__main__":
    main() 
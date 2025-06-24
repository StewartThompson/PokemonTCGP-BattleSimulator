import json
import os
import sys
from typing import Dict, List
from ..models.cards.energy import Energy
from ..models.cards.attack import Attack
from ..models.cards.ability import Ability
from ..models.cards.card import Card
from ..models.cards.pokemon import Pokemon
class JsonCardImporter:
    def __init__(self):
        # Card types
        self.items = {}
        self.pokemon = {}
        self.supporters = {}
        self.tools = {}

    def import_from_json(self):
        """Import cards from all JSON files in a folder"""
        folder_path = "/Users/stewartthompson/Documents/repos/PokemonTCGP-BattleSimulator/v3/assets"

        print(f"Loading cards from {folder_path}...")
        
        cards_data = []
        json_files = [f for f in os.listdir(folder_path) if f.endswith('.json')]
        
        for json_file in json_files:
            file_path = os.path.join(folder_path, json_file)
            try:
                with open(file_path, 'r', encoding='utf-8') as file:
                    file_cards = json.load(file)
                    cards_data.extend(file_cards)
                    print(f"✓ Loaded {len(file_cards)} cards from {json_file}")
            except Exception as e:
                print(f"❌ Error with {json_file}: {e}")
                continue
                
        print(f"Found {len(cards_data)} total cards to process...")
        
        # Process each card
        for card_data in cards_data:
            try:
                card_type = card_data.get('type', '').lower()
                card_subtype = card_data.get('subtype', '').lower()
                
                # Handle Pokemon cards
                if card_type == 'pokemon':
                    pokemon = self.create_pokemon(card_data)
                    self.pokemon[pokemon.id] = pokemon
                    
                # Handle Trainer cards
                elif card_type == 'trainer':
                    # Handle regular items
                    if card_subtype == 'item':
                        item = self.create_item(card_data)
                        self.items[item.id] = item
                        
                    # Handle supporters
                    elif card_subtype == 'supporter':
                        supporter = self.create_supporter(card_data)
                        self.supporters[supporter.id] = supporter
                        
                    # Handle tools
                    elif card_subtype == 'tool':
                        tool = self.create_tool(card_data)
                        self.tools[tool.id] = tool

            except Exception as e:
                print(f"⚠️ Error processing card {card_data.get('name', 'Unknown')}: {e}")
                continue
        
        # Set evolution relationships after processing all cards
        self._set_evolution_relationships()
        
        print(f"Import complete!")
        print(f"Created {len(self.pokemon)} Pokemon")
        print(f"Created {self.attack_counter} unique attacks")
        print(f"Created {self.ability_counter} unique abilities")
        print(f"Created {len(self.supporters)} supporters")
        print(f"Created {len(self.tools)} tools")
        print(f"Created {len(self.items)} items")
    
    def parse_energy_cost(self, cost_list: List[str]) -> Dict[str, int]:
        """Convert JSON energy cost array to internal energy cost dict"""
        energy = Energy.from_string_list(cost_list)
        return energy.cost

    def create_attack(self, attack_data: dict, card_data: dict) -> CardAttack:
        """Create an Attack object"""
        
        name = attack_data.get('name', '')
        if not name:
            raise ValueError(f"Attack name cannot be empty for card {card_data.get('name', 'Unknown')}")
       
        ability = self.create_ability(attack_data.get('ability', {}), card_data)
        return Attack(
            name=name,
            ability=ability,
            damage=attack_data.get('damage', '0'),
            cost=self.parse_energy_cost(attack_data.get('cost', []))
        )

    def create_ability(self, ability_data: dict, card_data: dict) -> Ability:
        """Create an Ability object"""
        name = ability_data.get('name', '')
        if not name:
            raise ValueError(f"Ability name cannot be empty for card {card_data.get('name', 'Unknown')}")
            
        effect = ability_data.get('effect', '')
        if not effect:
            raise ValueError(f"Ability effect cannot be empty for card {card_data.get('name', 'Unknown')}")
            
        return Ability(
            name=name,
            effect=effect,
            target=ability_data.get('target', Ability.Target.OPPONENT_ACTIVE),
            position=ability_data.get('position', Card.Position.ACTIVE)
        )
    
    def create_pokemon(self, card_data: dict) -> Pokemon:
        """Create a Pokemon object from JSON card data"""
        # Handle attacks
        attacks = []
        for attack_data in card_data.get('attacks', []):
            attack = self.create_attack(attack_data, card_data)
            attacks.append(attack)
        
        # Handle abilities
        abilities = []
        abilities_list = card_data.get('abilities', [])
        for ability_data in abilities_list:
            ability = self.create_ability(ability_data, card_data)
            abilities.append(ability)

        
        # Get pokemon type and weakness
        element = card_data.get('element')
        if not element:
            raise ValueError(f"Element cannot be empty for card {card_data.get('name', 'Unknown')}")

        try:
            # Convert string element to Energy.Type enum
            pokemon_type = Energy.Type[element.upper()]
        except KeyError:
            if card_data.get('subtype') != 'Fossil':
                raise ValueError(f"Unknown element type: {element}")
            pokemon_type = None
        
        weakness_type = card_data.get('weakness')
        weakness = None
        if weakness_type:
            try:
                weakness = Energy.Type[weakness_type.upper()]
            except KeyError:
                raise ValueError(f"Unknown weakness type: {weakness_type}")

        subtype = card_data.get('subtype')
        if subtype not in ['Basic', 'Stage 1', 'Stage 2', 'Fossil']:
            raise ValueError(f"Unknown stage type: {subtype}")
        stage = subtype.lower().replace(' ', '')

        action_ids = []
        for action_id in ActionIdGenerator.get_all_action_ids_for_card(card_data):
            action_ids.append(action_id)
        
        pokemon = Pokemon(
            id=card_data.get('id'),
            name=card_data.get('name'),
            element=element,
            type=pokemon_type,
            subtype=subtype,
            stage=stage,
            health=card_data.get('health'),
            set=card_data.get('set'),
            pack=card_data.get('pack'),
            attacks=attacks,
            retreat_cost=card_data.get('retreatCost'),
            weakness=weakness,
            abilities=abilities,
            evolves_from=card_data.get('evolvesFrom'),
            rarity=card_data.get('rarity'),
            action_ids=action_ids
        )
        
        return pokemon

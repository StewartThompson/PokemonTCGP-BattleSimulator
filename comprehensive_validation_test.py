#!/usr/bin/env python3
"""
Comprehensive Database Validation Test Suite

This test validates all database components:
- Pokemon (structure, references, evolution chains)
- Attacks (effects, handlers, energy costs)
- Abilities (effects, handlers, conditions)
- Trainers (effects, handlers)
- Items (effects, handlers)
- Tools (effects, handlers)

Run this after adding new content to ensure database integrity.
"""

import sys
import os
import pandas as pd
from typing import Dict, List, Tuple, Set, Any
import inspect

# Add the project root to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils import load_default_database
from moteur.handlers.card_effect_handler import CardEffectHandler
from moteur.cartes.pokemon import Pokemon
from moteur.combat.attack import Attack
from moteur.combat.ability import Ability
from moteur.cartes.trainer import Trainer
from moteur.cartes.item import Item
from moteur.cartes.tool import Tool

class DatabaseValidator:
    def __init__(self):
        self.errors = []
        self.warnings = []
        self.stats = {
            'pokemon': 0,
            'attacks': 0,
            'abilities': 0,
            'trainers': 0,
            'items': 0,
            'tools': 0
        }
        
        # Load database
        print("Loading database...")
        load_default_database()
        
        # Load CSV data directly
        base_path = 'assets/database/'
        self.pokemons_df = pd.read_csv(base_path + 'pokemons.csv')
        self.attacks_df = pd.read_csv(base_path + 'attacks.csv')
        self.abilities_df = pd.read_csv(base_path + 'abilities.csv')
        self.trainers_df = pd.read_csv(base_path + 'trainers.csv')
        self.items_df = pd.read_csv(base_path + 'items.csv')
        self.tools_df = pd.read_csv(base_path + 'tools.csv')
        
        # Update stats
        self.stats['pokemon'] = len(self.pokemons_df)
        self.stats['attacks'] = len(self.attacks_df)
        self.stats['abilities'] = len(self.abilities_df)
        self.stats['trainers'] = len(self.trainers_df)
        self.stats['items'] = len(self.items_df)
        self.stats['tools'] = len(self.tools_df)
        
        # Get handler methods
        self.handler = CardEffectHandler(None)  # Pass None as match for now
        self.attack_handlers = self._get_attack_handlers()
        self.ability_handlers = self._get_ability_handlers()
        self.trainer_handlers = self._get_trainer_handlers()
        self.item_handlers = self._get_item_handlers()
        self.tool_handlers = self._get_tool_handlers()

    def _get_attack_handlers(self) -> Set[str]:
        """Get all available attack effect handlers."""
        handlers = set()
        for name, method in inspect.getmembers(self.handler, predicate=inspect.ismethod):
            if name.startswith('handle_') and not name.startswith('handle_ability'):
                effect_name = name.replace('handle_', '')
                handlers.add(effect_name)
        return handlers

    def _get_ability_handlers(self) -> Set[str]:
        """Get all available ability effect handlers."""
        handlers = set()
        for name, method in inspect.getmembers(self.handler, predicate=inspect.ismethod):
            if name.startswith('handle_'):
                effect_name = name.replace('handle_', '')
                handlers.add(effect_name)
        return handlers

    def _get_trainer_handlers(self) -> Set[str]:
        """Get all available trainer effect handlers."""
        return self._get_ability_handlers()  # Trainers use same handler system

    def _get_item_handlers(self) -> Set[str]:
        """Get all available item effect handlers."""
        return self._get_ability_handlers()  # Items use same handler system

    def _get_tool_handlers(self) -> Set[str]:
        """Get all available tool effect handlers."""
        return self._get_ability_handlers()  # Tools use same handler system

    def error(self, message: str):
        """Add an error message."""
        self.errors.append(f"❌ ERROR: {message}")
        print(f"❌ ERROR: {message}")

    def warning(self, message: str):
        """Add a warning message."""
        self.warnings.append(f"⚠️  WARNING: {message}")
        print(f"⚠️  WARNING: {message}")

    def success(self, message: str):
        """Print a success message."""
        print(f"✅ {message}")

    def validate_pokemon_data(self):
        """Validate Pokemon database integrity."""
        print("\n🔍 Validating Pokemon Data...")
        
        for index, row in self.pokemons_df.iterrows():
            pokemon_id = row['ID']
            name = row['Name']
            stage = row['Stage']
            attack_ids = row['Attacks IDs']
            hp = row['hp']
            pre_evo = row['pre-evo name']
            evo = row['evo name']
            retreat_cost = row['retreat cost']
            pokemon_type = row['type']
            weakness = row['weakness']
            ability_id = row['Ability ID']
            
            # Validate basic structure
            if pd.isna(pokemon_id) or pokemon_id == '':
                self.error(f"Pokemon missing ID at row {index + 1}")
                continue
                
            if pd.isna(name) or name == '':
                self.error(f"Pokemon ID {pokemon_id} missing name")
                continue
            
            # Validate HP
            if pd.isna(hp) or hp == '':
                if 'Fossil' not in name:  # Fossils can have empty HP
                    self.error(f"Pokemon {name} (ID: {pokemon_id}) missing HP")
            else:
                try:
                    hp_val = int(hp)
                    if hp_val <= 0 or hp_val > 300:
                        self.warning(f"Pokemon {name} has unusual HP: {hp_val}")
                except ValueError:
                    self.error(f"Pokemon {name} has invalid HP format: {hp}")
            
            # Validate stage
            valid_stages = ['basic', 'stage1', 'stage2', 'stage1_ex', 'stage2_ex', 'basic_ex', 'fossil']
            if stage not in valid_stages:
                self.error(f"Pokemon {name} has invalid stage: {stage}")
            
            # Validate attack IDs
            if not pd.isna(attack_ids) and attack_ids != '':
                attack_list = str(attack_ids).split('|')
                for attack_id in attack_list:
                    try:
                        attack_num = int(attack_id.strip())
                        if attack_num not in self.attacks_df['ID'].values:
                            self.error(f"Pokemon {name} references non-existent attack ID: {attack_num}")
                    except ValueError:
                        self.error(f"Pokemon {name} has invalid attack ID format: {attack_id}")
            
            # Validate ability ID
            if not pd.isna(ability_id) and ability_id != '':
                try:
                    ability_num = int(ability_id)
                    if ability_num not in self.abilities_df['ID'].values:
                        self.error(f"Pokemon {name} references non-existent ability ID: {ability_num}")
                except ValueError:
                    self.error(f"Pokemon {name} has invalid ability ID format: {ability_id}")
            
            # Validate type
            valid_types = ['grass', 'fire', 'water', 'electric', 'psychic', 'fighting', 'dark', 'metal', 'dragon', 'normal', 'fairy', 'rock']
            if pokemon_type not in valid_types:
                self.error(f"Pokemon {name} has invalid type: {pokemon_type}")
            
            # Validate weakness
            if not pd.isna(weakness) and weakness != '':
                if weakness not in valid_types:
                    self.error(f"Pokemon {name} has invalid weakness: {weakness}")
            
            # Validate retreat cost
            if not pd.isna(retreat_cost) and retreat_cost != '':
                try:
                    retreat_val = int(retreat_cost)
                    if retreat_val < 0 or retreat_val > 5:
                        self.warning(f"Pokemon {name} has unusual retreat cost: {retreat_val}")
                except ValueError:
                    if retreat_cost != '999':  # Special case for fossils
                        self.error(f"Pokemon {name} has invalid retreat cost format: {retreat_cost}")
            
            # Validate evolution chains
            if stage.startswith('stage') and (pd.isna(pre_evo) or pre_evo == ''):
                self.error(f"Evolution Pokemon {name} missing pre-evolution")
            
            if not pd.isna(evo) and evo != '':
                # Check if evolution exists
                evo_names = str(evo).split('|')
                for evo_name in evo_names:
                    evo_name = evo_name.strip()
                    if evo_name not in self.pokemons_df['Name'].values:
                        self.error(f"Pokemon {name} references non-existent evolution: {evo_name}")

        self.success(f"Validated {self.stats['pokemon']} Pokemon")

    def validate_attacks_data(self):
        """Validate Attacks database integrity."""
        print("\n🔍 Validating Attacks Data...")
        
        for index, row in self.attacks_df.iterrows():
            attack_id = row['ID']
            name = row['Name']
            description = row['Description']
            damage = row['damage']
            energy_cost = row['energy cost']
            attack_effect = row['attack effect']
            special_values = row['special values']
            
            # Validate basic structure
            if pd.isna(attack_id) or attack_id == '':
                self.error(f"Attack missing ID at row {index + 1}")
                continue
                
            if pd.isna(name) or name == '':
                self.error(f"Attack ID {attack_id} missing name")
                continue
            
            # Validate damage
            if not pd.isna(damage) and damage != '':
                damage_str = str(damage)
                if damage_str.endswith('x'):
                    # Variable damage like "50x"
                    try:
                        base_damage = int(damage_str[:-1])
                        if base_damage < 0:
                            self.error(f"Attack {name} has negative base damage: {damage}")
                    except ValueError:
                        self.error(f"Attack {name} has invalid variable damage format: {damage}")
                else:
                    try:
                        damage_val = int(damage)
                        if damage_val < 0 or damage_val > 500:
                            self.warning(f"Attack {name} has unusual damage: {damage_val}")
                    except ValueError:
                        self.error(f"Attack {name} has invalid damage format: {damage}")
            
            # Validate energy cost
            if not pd.isna(energy_cost) and energy_cost != '':
                energy_parts = str(energy_cost).split('|')
                valid_energy_types = ['grass', 'fire', 'water', 'electric', 'psychic', 'fighting', 'dark', 'metal', 'dragon', 'normal', 'fairy', 'rock']
                
                for energy_part in energy_parts:
                    if ':' in energy_part:
                        energy_type, amount = energy_part.split(':')
                        if energy_type not in valid_energy_types:
                            self.error(f"Attack {name} has invalid energy type: {energy_type}")
                        try:
                            amount_val = int(amount)
                            if amount_val < 0 or amount_val > 10:
                                self.warning(f"Attack {name} has unusual energy amount: {amount_val}")
                        except ValueError:
                            self.error(f"Attack {name} has invalid energy amount: {amount}")
                    else:
                        self.error(f"Attack {name} has invalid energy cost format: {energy_part}")
            
            # Validate attack effect handlers
            if not pd.isna(attack_effect) and attack_effect != '':
                if attack_effect not in self.attack_handlers:
                    self.error(f"Attack {name} uses unknown effect handler: {attack_effect}")

        self.success(f"Validated {self.stats['attacks']} Attacks")

    def validate_abilities_data(self):
        """Validate Abilities database integrity."""
        print("\n🔍 Validating Abilities Data...")
        
        for index, row in self.abilities_df.iterrows():
            ability_id = row['ID']
            name = row['Name']
            description = row['Description']
            amount = row['amount']
            effect_type = row['effect type']
            special_values = row['special values']
            
            # Validate basic structure
            if pd.isna(ability_id) or ability_id == '':
                self.error(f"Ability missing ID at row {index + 1}")
                continue
                
            if pd.isna(name) or name == '':
                self.error(f"Ability ID {ability_id} missing name")
                continue
            
            if pd.isna(effect_type) or effect_type == '':
                self.error(f"Ability {name} missing effect type")
                continue
            
            # Validate effect type handlers
            if effect_type not in self.ability_handlers:
                self.error(f"Ability {name} uses unknown effect handler: {effect_type}")
            
            # Validate amount
            if not pd.isna(amount) and amount != '':
                valid_amounts = ['once', 'attacked', 'during_turn', 'during_enemy_turn', 'always', 'checkup']
                amount_str = str(amount)
                if amount_str not in valid_amounts:
                    try:
                        amount_val = int(amount)
                        if amount_val < 0:
                            self.error(f"Ability {name} has negative amount: {amount}")
                    except ValueError:
                        self.warning(f"Ability {name} has unusual amount format: {amount}")

        self.success(f"Validated {self.stats['abilities']} Abilities")

    def validate_trainers_data(self):
        """Validate Trainers database integrity."""
        print("\n🔍 Validating Trainers Data...")
        
        for index, row in self.trainers_df.iterrows():
            trainer_id = row['ID']
            name = row['Name']
            description = row['Description']
            effect_type = row['effect_type']
            special_values = row['special values']
            
            # Validate basic structure
            if pd.isna(trainer_id) or trainer_id == '':
                self.error(f"Trainer missing ID at row {index + 1}")
                continue
                
            if pd.isna(name) or name == '':
                self.error(f"Trainer ID {trainer_id} missing name")
                continue
            
            if pd.isna(effect_type) or effect_type == '':
                self.error(f"Trainer {name} missing effect type")
                continue
            
            # Validate effect type handlers
            if effect_type not in self.trainer_handlers:
                self.error(f"Trainer {name} uses unknown effect handler: {effect_type}")

        self.success(f"Validated {self.stats['trainers']} Trainers")

    def validate_items_data(self):
        """Validate Items database integrity."""
        print("\n🔍 Validating Items Data...")
        
        for index, row in self.items_df.iterrows():
            item_id = row['ID']
            name = row['Name']
            description = row['Description']
            effect_type = row['effect_type']
            special_values = row['special values']
            
            # Validate basic structure
            if pd.isna(item_id) or item_id == '':
                self.error(f"Item missing ID at row {index + 1}")
                continue
                
            if pd.isna(name) or name == '':
                self.error(f"Item ID {item_id} missing name")
                continue
            
            if pd.isna(effect_type) or effect_type == '':
                self.error(f"Item {name} missing effect type")
                continue
            
            # Validate effect type handlers
            if effect_type not in self.item_handlers:
                self.error(f"Item {name} uses unknown effect handler: {effect_type}")

        self.success(f"Validated {self.stats['items']} Items")

    def validate_tools_data(self):
        """Validate Tools database integrity."""
        print("\n🔍 Validating Tools Data...")
        
        for index, row in self.tools_df.iterrows():
            tool_id = row['tool_id']
            name = row['name']
            effect = row['effect']
            special_values = row['special_values']
            
            # Validate basic structure
            if pd.isna(tool_id) or tool_id == '':
                self.error(f"Tool missing ID at row {index + 1}")
                continue
                
            if pd.isna(name) or name == '':
                self.error(f"Tool ID {tool_id} missing name")
                continue
            
            if pd.isna(effect) or effect == '':
                self.error(f"Tool {name} missing effect")
                continue
            
            # Validate effect handlers
            if effect not in self.tool_handlers:
                self.error(f"Tool {name} uses unknown effect handler: {effect}")

        self.success(f"Validated {self.stats['tools']} Tools")

    def validate_cross_references(self):
        """Validate cross-references between databases."""
        print("\n🔍 Validating Cross-References...")
        
        # Check for orphaned attacks (attacks not used by any Pokemon)
        used_attacks = set()
        for index, row in self.pokemons_df.iterrows():
            attack_ids = row['Attacks IDs']
            if not pd.isna(attack_ids) and attack_ids != '':
                attack_list = str(attack_ids).split('|')
                for attack_id in attack_list:
                    try:
                        used_attacks.add(int(attack_id.strip()))
                    except ValueError:
                        pass
        
        all_attacks = set(self.attacks_df['ID'].values)
        orphaned_attacks = all_attacks - used_attacks
        if orphaned_attacks:
            self.warning(f"Found {len(orphaned_attacks)} orphaned attacks (not used by any Pokemon): {sorted(orphaned_attacks)}")
        
        # Check for orphaned abilities
        used_abilities = set()
        for index, row in self.pokemons_df.iterrows():
            ability_id = row['Ability ID']
            if not pd.isna(ability_id) and ability_id != '':
                try:
                    used_abilities.add(int(ability_id))
                except ValueError:
                    pass
        
        all_abilities = set(self.abilities_df['ID'].values)
        orphaned_abilities = all_abilities - used_abilities
        if orphaned_abilities:
            self.warning(f"Found {len(orphaned_abilities)} orphaned abilities (not used by any Pokemon): {sorted(orphaned_abilities)}")

    def validate_pokemon_instantiation(self):
        """Test that Pokemon can be instantiated correctly."""
        print("\n🔍 Testing Pokemon Instantiation...")
        
        test_count = 0
        success_count = 0
        
        for index, row in self.pokemons_df.iterrows():
            test_count += 1
            try:
                pokemon_id = row['ID']
                name = row['Name']
                stage = row['Stage']
                attack_ids = []
                if not pd.isna(row['Attacks IDs']) and row['Attacks IDs'] != '':
                    attack_ids = [int(x.strip()) for x in str(row['Attacks IDs']).split('|')]
                
                ability_id = None
                if not pd.isna(row['Ability ID']) and row['Ability ID'] != '':
                    ability_id = int(row['Ability ID'])
                
                hp = 60  # Default HP for testing
                if not pd.isna(row['hp']) and row['hp'] != '':
                    hp = int(row['hp'])
                
                pre_evo = row['pre-evo name'] if not pd.isna(row['pre-evo name']) else None
                evo = row['evo name'] if not pd.isna(row['evo name']) else None
                retreat_cost = 1
                if not pd.isna(row['retreat cost']) and row['retreat cost'] != '':
                    retreat_cost = int(row['retreat cost']) if str(row['retreat cost']) != '999' else 1
                
                pokemon_type = row['type']
                weakness = row['weakness'] if not pd.isna(row['weakness']) else None
                
                # Create Pokemon instance
                pokemon = Pokemon(
                    card_id=pokemon_id,
                    name=name,
                    stage=stage,
                    attack_ids=attack_ids,
                    ability_id=ability_id,
                    max_hp=hp,
                    pre_evolution_name=pre_evo,
                    evolutions_name=evo,
                    pokemon_type=pokemon_type,
                    weakness=weakness,
                    retreat_cost=retreat_cost
                )
                
                success_count += 1
                
            except Exception as e:
                self.error(f"Failed to instantiate Pokemon {name} (ID: {pokemon_id}): {str(e)}")
        
        self.success(f"Successfully instantiated {success_count}/{test_count} Pokemon")

    def validate_recent_additions(self):
        """Validate recently added Pokemon (Triumphant Light expansion)."""
        print("\n🔍 Validating Recent Additions (Triumphant Light)...")
        
        triumphant_light_pokemon = [
            'Heracross', 'Burmy', 'Mothim', 'Combee', 'Vespiquen',
            'Cherubi', 'Cherrim', 'Carnivine', 'Houndour', 'Houndoom',
            'Heatran', 'Marill', 'Azumarill', 'Barboach', 'Whiscash',
            'Snorunt', 'Froslass', 'Snover', 'Abomasnow', 'Origin Forme Palkia',
            'Phione', 'Pikachu', 'Raichu', 'Electrike', 'Manectric',
            'Clefairy', 'Clefable', 'Gastly', 'Haunter', 'Gengar',
            'Unown', 'Rotom', 'Sudowoodo', 'Phanpy', 'Donphan',
            'Larvitar', 'Pupitar', 'Tyranitar', 'Nosepass', 'Croagunk',
            'Toxicroak', 'Magnemite', 'Magneton', 'Magnezone', 'Mawile',
            'Probopass ex', 'Bronzor', 'Bronzong', 'Origin Forme Dialga',
            'Giratina', 'Eevee', 'Snorlax', 'Hoothoot', 'Noctowl',
            'Starly', 'Staravia', 'Staraptor', 'Shaymin', 'Arceus',
            'Arceus ex', 'Leafeon ex', 'Glaceon ex'
        ]
        
        found_pokemon = []
        missing_pokemon = []
        
        for pokemon_name in triumphant_light_pokemon:
            if pokemon_name in self.pokemons_df['Name'].values:
                found_pokemon.append(pokemon_name)
            else:
                missing_pokemon.append(pokemon_name)
        
        if missing_pokemon:
            self.error(f"Missing Triumphant Light Pokemon: {missing_pokemon}")
        else:
            self.success("All Triumphant Light Pokemon found in database")
        
        self.success(f"Found {len(found_pokemon)}/{len(triumphant_light_pokemon)} Triumphant Light Pokemon")

    def validate_pack_number_uniqueness(self):
        """Validate that all pack numbers are unique"""
        print("\n🔍 Validating Pack Number Uniqueness...")
        
        pack_numbers = {}
        duplicates = []
        
        for index, row in self.pokemons_df.iterrows():
            pack_number = row.get('pack_number', '')
            pokemon_name = row['Name']
            
            if pack_number and not pd.isna(pack_number) and pack_number != '':
                if pack_number in pack_numbers:
                    duplicates.append(f"Duplicate pack number {pack_number}: {pack_numbers[pack_number]} and {pokemon_name}")
                else:
                    pack_numbers[pack_number] = pokemon_name
        
        if duplicates:
            for duplicate in duplicates:
                self.error(f"Pack Number Duplicate: {duplicate}")
        else:
            self.success(f"All {len(pack_numbers)} pack numbers are unique")
            
        return len(duplicates) == 0

    def generate_report(self):
        """Generate a comprehensive validation report."""
        print("\n" + "="*60)
        print("📊 COMPREHENSIVE DATABASE VALIDATION REPORT")
        print("="*60)
        
        print(f"\n📈 Database Statistics:")
        print(f"   • Pokemon: {self.stats['pokemon']}")
        print(f"   • Attacks: {self.stats['attacks']}")
        print(f"   • Abilities: {self.stats['abilities']}")
        print(f"   • Trainers: {self.stats['trainers']}")
        print(f"   • Items: {self.stats['items']}")
        print(f"   • Tools: {self.stats['tools']}")
        
        total_cards = sum(self.stats.values())
        print(f"   • Total Cards: {total_cards}")
        
        print(f"\n🔍 Validation Results:")
        print(f"   • Errors: {len(self.errors)}")
        print(f"   • Warnings: {len(self.warnings)}")
        
        if self.errors:
            print(f"\n❌ ERRORS FOUND ({len(self.errors)}):")
            for error in self.errors:
                print(f"   {error}")
        
        if self.warnings:
            print(f"\n⚠️  WARNINGS ({len(self.warnings)}):")
            for warning in self.warnings:
                print(f"   {warning}")
        
        if not self.errors and not self.warnings:
            print(f"\n🎉 VALIDATION PASSED! All database components are valid.")
            return True
        elif not self.errors:
            print(f"\n✅ VALIDATION MOSTLY PASSED! Only warnings found.")
            return True
        else:
            print(f"\n💥 VALIDATION FAILED! Please fix the errors above.")
            return False

    def run_full_validation(self):
        """Run complete validation suite."""
        print("🚀 Starting Comprehensive Database Validation...")
        
        try:
            self.validate_pokemon_data()
            self.validate_attacks_data()
            self.validate_abilities_data()
            self.validate_trainers_data()
            self.validate_items_data()
            self.validate_tools_data()
            self.validate_cross_references()
            self.validate_pokemon_instantiation()
            self.validate_recent_additions()
            self.validate_pack_number_uniqueness()
            
            return self.generate_report()
            
        except Exception as e:
            self.error(f"Validation failed with exception: {str(e)}")
            return False

def main():
    """Main function to run the validation."""
    validator = DatabaseValidator()
    success = validator.run_full_validation()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main() 
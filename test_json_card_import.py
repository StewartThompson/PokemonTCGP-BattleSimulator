import unittest
import sys
import os
from collections import Counter, defaultdict
import re

# Add the project root to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from json_card_importer import JsonCardImporter
from moteur.cartes.pokemon import Pokemon
from moteur.combat.attack import Attack
from moteur.combat.ability import Ability
from moteur.cartes.trainer import Trainer
from moteur.cartes.tool import Tool
from moteur.cartes.item import Item

class TestJsonCardImport(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Set up the test class with imported card data."""
        cls.importer = JsonCardImporter()
        try:
            # Import all JSON files from pokemon folder
            pokemon_dir = 'assets/database/pokemon'
            json_files = [f for f in os.listdir(pokemon_dir) if f.endswith('.json')]
            
            cls.all_objects = {
                'pokemon': {},
                'attacks': {},
                'abilities': {},
                'trainers': {},
                'tools': {},
                'items': {},
                'fossils': {}
            }
            
            successful_imports = 0
            for json_file in json_files:
                file_path = os.path.join(pokemon_dir, json_file)
                # Check if file is not empty
                if os.path.getsize(file_path) == 0:
                    print(f"⚠️ Skipping empty file: {json_file}")
                    continue
                    
                try:
                    objects = cls.importer.import_from_json(file_path)
                    if objects:
                        # Merge objects from each file
                        for obj_type, items in objects.items():
                            if obj_type in cls.all_objects and items:
                                cls.all_objects[obj_type].update(items)
                        successful_imports += 1
                except Exception as e:
                    print(f"⚠️ Failed to import {json_file}: {e}")
                    continue
                    
            print(f"✅ Successfully imported {successful_imports} out of {len(json_files)} JSON files")
            print("✅ Import completed successfully")
        except Exception as e:
            print(f"❌ Setup failed: {e}")
            cls.all_objects = {
                'pokemon': {},
                'attacks': {},
                'abilities': {},
                'trainers': {},
                'tools': {},
                'items': {},
                'fossils': {}
            }

    def test_pokemon_objects_structure(self):
        """Test that Pokemon objects are created with correct structure."""
        print("\nPOKEMON OBJECT STRUCTURE VALIDATION")
        print("=" * 50)
        
        pokemon_dict = self.all_objects['pokemon']
        self.assertGreater(len(pokemon_dict), 0, "Should have Pokemon objects")
        
        # Test a sample of Pokemon
        sample_size = min(5, len(pokemon_dict))
        sample_pokemon = list(pokemon_dict.values())[:sample_size]
        
        print(f"   Testing structure of {sample_size} sample Pokemon...")
        
        required_attributes = [
            'card_id', 'name', 'stage', 'attack_ids', 'ability_id', 
            'max_hp', 'current_hp', 'pre_evolution_name', 'evolutions_name',
            'retreat_cost', 'pokemon_type', 'weakness', 'equipped_energies',
            'effect_status'
        ]
        
        for i, pokemon in enumerate(sample_pokemon):
            print(f"    {i+1}. {pokemon.name} ({pokemon.stage}) - {pokemon.max_hp} HP")
            
            # Check it's a Pokemon instance
            self.assertIsInstance(pokemon, Pokemon)
            
            # Check all required attributes exist
            for attr in required_attributes:
                self.assertTrue(hasattr(pokemon, attr), f"Pokemon missing attribute: {attr}")
            
            # Check types
            self.assertIsInstance(pokemon.max_hp, int)
            self.assertIsInstance(pokemon.current_hp, int)
            self.assertIsInstance(pokemon.attack_ids, list)
            self.assertIsInstance(pokemon.equipped_energies, dict)
            self.assertIsInstance(pokemon.effect_status, list)
        
        print("  ✅ All Pokemon objects have correct structure")

    def test_pokemon_data_integrity(self):
        """Test Pokemon data integrity and patterns."""
        print("\n POKEMON DATA INTEGRITY ANALYSIS")
        print("=" * 50)
        
        pokemon_dict = self.all_objects['pokemon']
        
        # Analyze HP distribution by stage
        hp_by_stage = defaultdict(list)
        type_distribution = Counter()
        weakness_distribution = Counter()
        retreat_cost_distribution = Counter()
        
        for pokemon in pokemon_dict.values():
            hp_by_stage[pokemon.stage].append(pokemon.max_hp)
            type_distribution[pokemon.pokemon_type] += 1
            weakness_distribution[pokemon.weakness] += 1
            retreat_cost_distribution[pokemon.retreat_cost] += 1
        
        print("  HP DISTRIBUTION BY STAGE:")
        for stage, hps in hp_by_stage.items():
            avg_hp = sum(hps) / len(hps)
            min_hp = min(hps)
            max_hp = max(hps)
            print(f"    {stage.capitalize()}: Avg={avg_hp:.1f}, Range={min_hp}-{max_hp} ({len(hps)} cards)")
            
            # Sanity checks for HP ranges
            if stage == "basic":
                self.assertGreaterEqual(min_hp, 30, "Basic Pokemon HP too low")
                self.assertLessEqual(max_hp, 200, "Basic Pokemon HP too high")
            elif stage == "stage1":
                self.assertGreaterEqual(min_hp, 60, "Stage 1 Pokemon HP too low")
                self.assertLessEqual(max_hp, 200, "Stage 1 Pokemon HP too high")
            elif stage == "stage2":
                self.assertGreaterEqual(min_hp, 100, "Stage 2 Pokemon HP too low")
                self.assertLessEqual(max_hp, 300, "Stage 2 Pokemon HP too high")
        
        print(f"\n  TYPE DISTRIBUTION:")
        for ptype, count in type_distribution.most_common():
            percentage = (count / len(pokemon_dict)) * 100
            print(f"    {ptype.capitalize()}: {count} cards ({percentage:.1f}%)")
        
        # Count weakness distribution
        weakness_counts = {}
        for pokemon in pokemon_dict.values():
            weakness = pokemon.weakness
            if weakness is not None:  # Handle None weakness
                weakness_counts[weakness] = weakness_counts.get(weakness, 0) + 1
        
        print("  WEAKNESS DISTRIBUTION:")
        for weakness, count in sorted(weakness_counts.items(), key=lambda x: x[1], reverse=True):
            percentage = (count / len(pokemon_dict)) * 100
            print(f"    {weakness.capitalize()}: {count} cards ({percentage:.1f}%)")
        
        print(f"\n  RETREAT COST DISTRIBUTION:")
        for cost, count in retreat_cost_distribution.most_common():
            percentage = (count / len(pokemon_dict)) * 100
            print(f"    {cost} energy: {count} cards ({percentage:.1f}%)")

    def test_attack_objects_structure(self):
        """Test that Attack objects are created with correct structure."""
        print("\nATTACK OBJECT STRUCTURE VALIDATION")
        print("=" * 50)
        
        attacks_dict = self.all_objects['attacks']
        self.assertGreater(len(attacks_dict), 0, "Should have Attack objects")
        
        # Test structure of attacks
        sample_attack = next(iter(attacks_dict.values()))
        
        required_attributes = ['id_attaque', 'name', 'description', 'damage', 'energy_cost', 'effect_type', 'special_values']
        for attr in required_attributes:
            self.assertIsInstance(sample_attack, Attack)
            self.assertTrue(hasattr(sample_attack, attr), f"Attack missing attribute: {attr}")
            
        # Check energy_cost is a dict with expected keys
        expected_energy_types = {'fire', 'water', 'rock', 'grass', 'normal', 'electric', 'psychic', 'dark', 'metal', 'dragon', 'fairy'}
        for energy_type in expected_energy_types:
            self.assertIn(energy_type, sample_attack.energy_cost)
        
        print(f"   Total unique attacks: {len(attacks_dict)}")
        
        # Analyze attack patterns
        damage_distribution = Counter()
        cost_distribution = Counter()
        effect_patterns = Counter()
        
        print(f"   Analyzing {len(attacks_dict)} attacks...")
        
        for attack in attacks_dict.values():
            # Categorize damage
            try:
                if 'x' in str(attack.damage).lower():
                    damage_distribution[str(attack.damage)] += 1
                elif '+' in str(attack.damage):
                    damage_distribution[str(attack.damage)] += 1
                else:
                    damage_val = int(attack.damage) if attack.damage.isdigit() else 0
                    if damage_val == 0:
                        damage_distribution["0-49"] += 1
                    elif damage_val < 50:
                        damage_distribution["0-49"] += 1
                    elif damage_val < 100:
                        damage_distribution["50-99"] += 1
                    elif damage_val < 150:
                        damage_distribution["100-149"] += 1
                    else:
                        damage_distribution["150-199"] += 1
            except:
                damage_distribution[str(attack.damage)] += 1
            
            # Count total energy cost
            total_cost = sum(attack.energy_cost.values())
            cost_distribution[total_cost] += 1
            
            # Effect analysis
            if attack.description and attack.description.strip():
                effect_patterns["Has Effect"] += 1
            else:
                effect_patterns["No Effect"] += 1
        
        print(f"\n  DAMAGE DISTRIBUTION:")
        for damage_range, count in damage_distribution.most_common():
            percentage = (count / len(attacks_dict)) * 100
            print(f"    {damage_range}: {count} attacks ({percentage:.1f}%)")
        
        print(f"\n  ENERGY COST DISTRIBUTION:")
        for cost, count in cost_distribution.most_common():
            percentage = (count / len(attacks_dict)) * 100
            print(f"    {cost} energy: {count} attacks ({percentage:.1f}%)")
        
        print(f"\n  EFFECT DISTRIBUTION:")
        for effect, count in effect_patterns.items():
            percentage = (count / len(attacks_dict)) * 100
            print(f"    {effect}: {count} attacks ({percentage:.1f}%)")

    def test_ability_objects_structure(self):
        """Test that Ability objects are created with correct structure."""
        print("\nABILITY OBJECT STRUCTURE VALIDATION")
        print("=" * 50)
        
        abilities_dict = self.all_objects['abilities']
        
        if len(abilities_dict) > 0:
            print(f"   Total unique abilities: {len(abilities_dict)}")
            
            sample_ability = next(iter(abilities_dict.values()))
            
            # Test structure
            required_attributes = ['ability_id', 'name', 'description', 'effect_type', 'special_values', 'amount_of_times']
            for attr in required_attributes:
                self.assertIsInstance(sample_ability, Ability)
                self.assertTrue(hasattr(sample_ability, attr), f"Ability missing attribute: {attr}")
            
            # Analyze ability patterns
            print(f"   Analyzing {len(abilities_dict)} abilities...")
            
            name_length_dist = Counter()
            description_length_dist = Counter()
            
            for ability in abilities_dict.values():
                # Name length analysis
                name_len = len(ability.name)
                if name_len < 5:
                    name_length_dist["5-9 chars"] += 1
                elif name_len < 10:
                    name_length_dist["5-9 chars"] += 1
                elif name_len < 15:
                    name_length_dist["10-14 chars"] += 1
                elif name_len < 20:
                    name_length_dist["15-19 chars"] += 1
                else:
                    name_length_dist["20+ chars"] += 1
                
                # Description length analysis  
                desc_len = len(ability.description)
                desc_len_range = (desc_len // 25) * 25
                description_length_dist[f"{desc_len_range}-{desc_len_range+24}"] += 1
                
                print(f"    {ability.name}: {len(ability.description)} chars")
            
            print(f"\n  NAME LENGTH DISTRIBUTION:")
            for length_range, count in name_length_dist.most_common():
                percentage = (count / len(abilities_dict)) * 100
                print(f"    {length_range}: {count} abilities ({percentage:.1f}%)")
        else:
            print("  No abilities found to analyze")

    def test_attack_deduplication_effectiveness(self):
        """Test the effectiveness of attack deduplication."""
        print("\nATTACK DEDUPLICATION ANALYSIS")
        print("=" * 50)
        
        attacks_dict = self.all_objects['attacks']
        pokemon_dict = self.all_objects['pokemon']
        
        # Count total attack references vs unique attacks
        total_attack_references = 0
        for pokemon in pokemon_dict.values():
            total_attack_references += len(pokemon.attack_ids)
        
        unique_attacks = len(attacks_dict)
        deduplication_ratio = total_attack_references / unique_attacks if unique_attacks > 0 else 0
        
        print(f"  DEDUPLICATION STATISTICS:")
        print(f"    Total attack references: {total_attack_references}")
        print(f"    Unique attacks created: {unique_attacks}")
        print(f"    Deduplication ratio: {deduplication_ratio:.2f}x")
        if deduplication_ratio > 1:
            memory_saved = ((total_attack_references - unique_attacks) / total_attack_references) * 100
            print(f"    Memory saved: {memory_saved:.1f}%")
        
        # Find most reused attacks
        attack_usage = Counter()
        for pokemon in pokemon_dict.values():
            for attack_id in pokemon.attack_ids:
                if attack_id in attacks_dict:
                    attack = attacks_dict[attack_id]
                    signature = f"{attack.name} ({attack.damage} dmg)"
                    attack_usage[signature] += 1
        
        print(f"\n  MOST REUSED ATTACKS:")
        for attack_sig, count in attack_usage.most_common(5):
            if count > 1:
                print(f"    {attack_sig}: Used {count} times")
        
        # Verify all attacks have unique signatures
        signatures = set()
        for attack in attacks_dict.values():
            signature = f"{attack.name}_{attack.damage}_{attack.description}"
            self.assertNotIn(signature, signatures, f"Duplicate attack signature found: {signature}")
            signatures.add(signature)
        
        print(f"  ✅ All {len(attacks_dict)} attacks have unique signatures")

    def test_ability_deduplication_effectiveness(self):
        """Test the effectiveness of ability deduplication."""
        print("\nABILITY DEDUPLICATION ANALYSIS")
        print("=" * 50)
        
        abilities_dict = self.all_objects['abilities']
        pokemon_dict = self.all_objects['pokemon']
        
        if len(abilities_dict) > 0:
            # Count total ability references vs unique abilities
            total_ability_references = 0
            for pokemon in pokemon_dict.values():
                if pokemon.ability_id:
                    total_ability_references += 1
            
            unique_abilities = len(abilities_dict)
            deduplication_ratio = total_ability_references / unique_abilities if unique_abilities > 0 else 0
            
            print(f"  DEDUPLICATION STATISTICS:")
            print(f"    Total ability references: {total_ability_references}")
            print(f"    Unique abilities created: {unique_abilities}")
            print(f"    Deduplication ratio: {deduplication_ratio:.2f}x")
            if deduplication_ratio > 1:
                memory_saved = ((total_ability_references - unique_abilities) / total_ability_references) * 100
                print(f"    Memory saved: {memory_saved:.1f}%")
            
            # Find most reused abilities
            ability_usage = Counter()
            for pokemon in pokemon_dict.values():
                if pokemon.ability_id and pokemon.ability_id in abilities_dict:
                    ability = abilities_dict[pokemon.ability_id]
                    ability_usage[ability.name] += 1
            
            print(f"\n  MOST REUSED ABILITIES:")
            for ability_name, count in ability_usage.most_common(5):
                print(f"    {ability_name}: Used {count} times")
            
            # Verify all abilities have unique descriptions
            descriptions = set()
            for ability in abilities_dict.values():
                self.assertNotIn(ability.description, descriptions, f"Duplicate ability description found: {ability.description}")
                descriptions.add(ability.description)
            
            print(f"  ✅ All {len(abilities_dict)} abilities have unique descriptions")
        else:
            print("  No abilities to analyze for deduplication")

    def test_pokemon_references_integrity(self):
        """Test that Pokemon correctly reference attacks and abilities."""
        print("\nPOKEMON REFERENCE INTEGRITY VALIDATION")
        print("=" * 50)
        
        pokemon_dict = self.all_objects['pokemon']
        attacks_dict = self.all_objects['attacks']
        abilities_dict = self.all_objects['abilities']
        
        print(f"   Validating references for {len(pokemon_dict)} Pokemon...")
        
        if len(pokemon_dict) == 0:
            print("   No Pokemon found to validate")
            return
            
        # Check references are valid
        pokemon_with_abilities = 0
        total_attack_refs = 0
        
        reference_issues = []
        
        for pokemon in pokemon_dict.values():
            # Check attack references
            for attack_id in pokemon.attack_ids:
                total_attack_refs += 1
                if attack_id not in attacks_dict:
                    reference_issues.append(f"Pokemon {pokemon.name} references non-existent attack {attack_id}")
            
            # Check ability references
            if pokemon.ability_id:
                pokemon_with_abilities += 1
                if pokemon.ability_id not in abilities_dict:
                    reference_issues.append(f"Pokemon {pokemon.name} references non-existent ability {pokemon.ability_id}")
        
        print(f"  REFERENCE STATISTICS:")
        print(f"    Pokemon with abilities: {pokemon_with_abilities}/{len(pokemon_dict)} ({(pokemon_with_abilities/len(pokemon_dict)*100):.1f}%)")
        print(f"    Total attack references: {total_attack_refs}")
        print(f"    Average attacks per Pokemon: {total_attack_refs/len(pokemon_dict):.2f}")
        
        # Report any issues
        if reference_issues:
            print(f"\n  ❌ REFERENCE ISSUES FOUND:")
            for issue in reference_issues:
                print(f"    {issue}")
            self.fail(f"Found {len(reference_issues)} reference issues")
        else:
            print(f"  ✅ All references are valid")

    def test_evolution_relationships_comprehensive(self):
        """Test evolution relationships with comprehensive analysis."""
        print("\nCOMPREHENSIVE EVOLUTION ANALYSIS")
        print("=" * 50)
        
        pokemon_dict = self.all_objects['pokemon']
        
        evolution_chains = defaultdict(list)
        ex_evolution_violations = []
        successful_evolutions = 0
        multi_form_pokemon = []
        
        print(f"   Analyzing evolution patterns for {len(pokemon_dict)} Pokemon...")
        
        for pokemon in pokemon_dict.values():
            # Build evolution chains - evolutions_name is a single string, not a list
            if pokemon.evolutions_name:
                evolution_chains[pokemon.name].append(pokemon.evolutions_name)
                successful_evolutions += 1
            
            # Check for ex evolution violations (ex Pokemon shouldn't evolve)
            if " ex" in pokemon.name and pokemon.evolutions_name:
                ex_evolution_violations.append(f"{pokemon.name} (ex) should not evolve but evolves into: {pokemon.evolutions_name}")
        
        # Find multi-form Pokemon (same base name, different versions)
        base_names = defaultdict(list)
        for pokemon in pokemon_dict.values():
            # Extract base name (remove ex, variants, etc.)
            base_name = pokemon.name.replace(" ex", "").split(" (")[0]
            base_names[base_name].append(pokemon.name)
        
        for base_name, forms in base_names.items():
            if len(forms) > 1:
                multi_form_pokemon.append(f"{base_name}: {', '.join(forms)}")
        
        print(f"  EVOLUTION STATISTICS:")
        print(f"    Total evolution relationships: {successful_evolutions}")
        print(f"    Multi-form Pokemon: {len(multi_form_pokemon)}")
        print(f"    Ex evolution violations: {len(ex_evolution_violations)}")
        
        if evolution_chains:
            print(f"\n  EVOLUTION CHAINS (showing first 10):")
            for i, (pre_evo, evolutions) in enumerate(list(evolution_chains.items())[:10]):
                print(f"    {pre_evo} -> {', '.join(evolutions)}")
                if i == 9 and len(evolution_chains) > 10:
                    print(f"    ... and {len(evolution_chains) - 10} more")
        else:
            print(f"\n  EVOLUTION CHAINS: None found")
        
        print(f"\n  MULTI-FORM POKEMON (showing first 15):")
        if multi_form_pokemon:
            for i, form_info in enumerate(multi_form_pokemon[:15]):
                print(f"    {form_info}")
                if i == 14 and len(multi_form_pokemon) > 15:
                    print(f"    ... and {len(multi_form_pokemon) - 15} more")
        else:
            print(f"    None found")
        
        # Verify no ex evolution violations
        if ex_evolution_violations:
            print(f"\n  ❌ EX EVOLUTION VIOLATIONS:")
            for violation in ex_evolution_violations:
                print(f"    {violation}")
            self.fail("Ex Pokemon should not evolve")
        else:
            print(f"  ✅ Evolution rules properly enforced")

    def test_energy_type_mapping_comprehensive(self):
        """Test comprehensive energy type mapping and usage patterns."""
        print("\nCOMPREHENSIVE ENERGY TYPE ANALYSIS")
        print("=" * 50)
        
        attacks = self.all_objects['attacks']
        pokemon_dict = self.all_objects['pokemon']
        
        # Energy type usage analysis
        energy_type_usage = Counter()
        cost_distribution = Counter()
        pokemon_type_vs_attack_cost = defaultdict(lambda: defaultdict(int))
        
        print(f"   Analyzing energy patterns across {len(attacks)} attacks...")
        
        for attack in attacks.values():
            total_cost = sum(attack.energy_cost.values())
            cost_distribution[total_cost] += 1
            
            for energy_type, cost in attack.energy_cost.items():
                if cost > 0:
                    energy_type_usage[energy_type] += cost
            
            # Validate energy cost structure
            self.assertIsInstance(attack.energy_cost, dict)
            expected_energy_types = {'fire', 'water', 'rock', 'grass', 'normal', 'electric', 'psychic', 'dark', 'metal', 'dragon', 'fairy'}
            for energy_type in expected_energy_types:
                self.assertIn(energy_type, attack.energy_cost)
                self.assertIsInstance(attack.energy_cost[energy_type], int)
                self.assertGreaterEqual(attack.energy_cost[energy_type], 0)
            
            # Check that attacks with positive total cost have at least one positive energy value
            if total_cost > 0:
                self.assertTrue(any(cost > 0 for cost in attack.energy_cost.values()),
                              f"Attack {attack.name} has total cost {total_cost} but no positive energy values")
        
        # Analyze Pokemon type vs their attack energy requirements
        for pokemon in pokemon_dict.values():
            for attack_id in pokemon.attack_ids:
                if attack_id in attacks:
                    attack = attacks[attack_id]
                    for energy_type, cost in attack.energy_cost.items():
                        if cost > 0:
                            pokemon_type_vs_attack_cost[pokemon.pokemon_type][energy_type] += cost
        
        print(f"\n  ENERGY TYPE USAGE:")
        total_energy_used = sum(energy_type_usage.values())
        for energy_type, usage in energy_type_usage.most_common():
            percentage = (usage / total_energy_used) * 100
            print(f"    {energy_type.capitalize()}: {usage} uses ({percentage:.1f}%)")
        
        print(f"\n  ATTACK COST DISTRIBUTION:")
        for cost, count in sorted(cost_distribution.items()):
            percentage = (count / len(attacks)) * 100
            print(f"    {cost} energy: {count} attacks ({percentage:.1f}%)")
        
        print(f"\n  TYPE vs ENERGY ALIGNMENT:")
        for pokemon_type, energy_usage in pokemon_type_vs_attack_cost.items():
            if energy_usage:
                most_used_energy = max(energy_usage.items(), key=lambda x: x[1])
                alignment = "✅" if most_used_energy[0] == pokemon_type else "⚠️"
                print(f"    {pokemon_type.capitalize()} Pokemon: Most used {most_used_energy[0]} ({most_used_energy[1]} uses) {alignment}")

    def test_trainer_tool_item_objects(self):
        """Test trainer, tool, and item objects with detailed analysis."""
        print("\nTRAINER/TOOL/ITEM OBJECT ANALYSIS")
        print("=" * 50)
        
        trainers = self.all_objects['trainers']
        tools = self.all_objects['tools']
        items = self.all_objects['items']
        
        # Test trainers
        if trainers:
            print(f"  TRAINERS ({len(trainers)}):")
            for trainer_id, trainer in trainers.items():
                self.assertIsInstance(trainer, Trainer)
                self.assertTrue(hasattr(trainer, 'trainer_id'))
                self.assertTrue(hasattr(trainer, 'name'))
                self.assertTrue(hasattr(trainer, 'effect'))
                print(f"    {trainer.name} (ID: {trainer_id})")
        else:
            print("  TRAINERS: None found")
        
        # Test tools
        if tools:
            print(f"\n  TOOLS ({len(tools)}):")
            for tool_id, tool in tools.items():
                self.assertIsInstance(tool, Tool)
                self.assertTrue(hasattr(tool, 'tool_id'))
                self.assertTrue(hasattr(tool, 'name'))
                self.assertTrue(hasattr(tool, 'effect'))
                print(f"    {tool.name} (ID: {tool_id})")
        else:
            print(f"\n  TOOLS: None found")
        
        # Test items
        if items:
            print(f"\n  ITEMS ({len(items)}):")
            for item_id, item in items.items():
                self.assertIsInstance(item, Item)
                self.assertTrue(hasattr(item, 'item_id'))
                self.assertTrue(hasattr(item, 'name'))
                self.assertTrue(hasattr(item, 'effect'))
                print(f"    {item.name} (ID: {item_id})")
        else:
            print(f"\n  ITEMS: None found")
        
        total_support_cards = len(trainers) + len(tools) + len(items)
        print(f"\n  Total support cards: {total_support_cards}")

    def test_card_id_format_and_uniqueness(self):
        """Test card ID formats and uniqueness across all card types."""
        print("\nCARD ID FORMAT & UNIQUENESS VALIDATION")
        print("=" * 50)
        
        all_ids = set()
        id_patterns = Counter()
        id_format_issues = []
        
        for obj_type, objects in self.all_objects.items():
            print(f"   Checking {obj_type} IDs...")
            
            for obj_id, obj in objects.items():
                # Check for duplicates
                if obj_id in all_ids:
                    id_format_issues.append(f"Duplicate ID found: {obj_id}")
                all_ids.add(obj_id)
                
                # Categorize ID patterns
                if obj_id.startswith('attack_'):
                    id_patterns["attack-generated"] += 1
                elif obj_id.startswith('ability_'):
                    id_patterns["ability-generated"] += 1
                elif re.match(r'^[a-z0-9]+[a-z]*-\d+$', obj_id):
                    # Card set IDs like a1-001, a3a-002, pa-007, etc.
                    id_patterns["card-set-id"] += 1
                else:
                    id_patterns["other-format"] += 1
                    id_format_issues.append(f"Unusual ID format: {obj_id}")
        
        print(f"\n  ID STATISTICS:")
        print(f"    Total unique IDs: {len(all_ids)}")
        for pattern, count in id_patterns.most_common():
            percentage = (count / len(all_ids)) * 100
            print(f"    {pattern}: {count} IDs ({percentage:.1f}%)")
        
        # Report any issues
        if id_format_issues:
            print(f"\n  ❌ ID FORMAT ISSUES:")
            for issue in id_format_issues:
                print(f"    {issue}")
            self.fail(f"Found {len(id_format_issues)} ID format issues")
        else:
            print(f"  ✅ All {len(all_ids)} IDs are unique and properly formatted")

    def test_specific_cards_detailed(self):
        """Test specific cards with detailed validation."""
        print("\nSPECIFIC CARD DETAILED VALIDATION")
        print("=" * 50)
        
        pokemon_dict = self.all_objects['pokemon']
        attacks_dict = self.all_objects['attacks']
        abilities_dict = self.all_objects['abilities']
        
        # Look for specific Pokemon we expect to find
        expected_pokemon = ['Petilil', 'Lilligant', 'Rowlet', 'Buzzwole ex', 'Nihilego', 'Growlithe', 'Arcanine']
        found_pokemon = {}
        
        print(f"   Searching for specific Pokemon...")
        
        for pokemon in pokemon_dict.values():
            if pokemon.name in expected_pokemon:
                if pokemon.name not in found_pokemon:
                    found_pokemon[pokemon.name] = []
                found_pokemon[pokemon.name].append(pokemon)
        
        print(f"\n  FOUND POKEMON DETAILS:")
        for name, pokemon_list in found_pokemon.items():
            print(f"     {name}: {len(pokemon_list)} variant(s)")
            for i, pokemon in enumerate(pokemon_list):
                print(f"      {i+1}. {pokemon.card_id} - {pokemon.max_hp} HP, {len(pokemon.attack_ids)} attacks")
                
                # Show attacks
                for attack_id in pokemon.attack_ids:
                    if attack_id in attacks_dict:
                        attack = attacks_dict[attack_id]
                        print(f"         {attack.name}: {attack.damage} damage")
                    else:
                        self.fail(f"Attack {attack_id} not found for {pokemon.name}")
                
                # Show ability if present
                if pokemon.ability_id:
                    if pokemon.ability_id in abilities_dict:
                        ability = abilities_dict[pokemon.ability_id]
                        print(f"         {ability.name}: {ability.description[:50]}...")
                    else:
                        self.fail(f"Ability {pokemon.ability_id} not found for {pokemon.name}")
        
        print(f"  ✅ Found {len(found_pokemon)}/{len(expected_pokemon)} expected Pokemon")
        self.assertGreaterEqual(len(found_pokemon), len(expected_pokemon) * 0.5, "Should find at least half of expected Pokemon")

    def test_data_consistency_and_balance(self):
        """Test data consistency and game balance."""
        print("\nDATA CONSISTENCY & BALANCE ANALYSIS")
        print("=" * 50)
        
        pokemon_dict = self.all_objects['pokemon']
        attacks_dict = self.all_objects['attacks']
        
        if len(pokemon_dict) > 0 and len(attacks_dict) > 0:
            # Calculate balance metrics
            total_hp = sum(pokemon.max_hp for pokemon in pokemon_dict.values())
            avg_hp = total_hp / len(pokemon_dict)
            
            # Calculate average attack damage
            attack_damages = []
            hp_damage_ratios = []
            
            for attack in attacks_dict.values():
                try:
                    if attack.damage.isdigit():
                        damage = int(attack.damage)
                        attack_damages.append(damage)
                        
                        # Calculate damage per energy
                        total_energy = sum(attack.energy_cost.values())
                        if total_energy > 0:
                            damage_per_energy = damage / total_energy
                            hp_damage_ratios.append((attack.name, damage, damage_per_energy))
                except:
                    pass  # Skip non-numeric damage values
            
            avg_damage = sum(attack_damages) / len(attack_damages)
            avg_damage_per_energy = sum(ratio[2] for ratio in hp_damage_ratios) / len(hp_damage_ratios)
            
            print(f"  BALANCE METRICS:")
            print(f"    Average Pokemon HP: {avg_hp:.1f}")
            print(f"    Average attack damage: {avg_damage:.1f}")
            print(f"    Average damage per energy: {avg_damage_per_energy:.1f}")
            
            # Find potentially underpowered attacks (low damage per energy)
            underpowered = [ratio for ratio in hp_damage_ratios if ratio[2] < avg_damage_per_energy * 0.7]
            if underpowered:
                print(f"\n  POTENTIALLY UNDERPOWERED ATTACKS ({len(underpowered)}):")
                for name, damage, dpe in underpowered[:5]:  # Show top 5
                    if dpe > 0:  # Avoid division by zero
                        expected_damage = damage * avg_damage_per_energy / dpe
                        print(f"    {name}: {damage}/{expected_damage:.0f} = {dpe:.1f} dmg/energy")
                    else:
                        print(f"    {name}: {damage}/0 = 0.0 dmg/energy (free attack)")
            
            print(f"  ✅ Balance analysis complete")
        else:
            print("  ⚠️ Insufficient data for balance analysis")
    
    def test_basic_import_stats(self):
        """Test basic import statistics and completeness."""
        print("\nBASIC IMPORT STATISTICS")
        print("=" * 50)
        
        pokemon_count = len(self.all_objects['pokemon'])
        attack_count = len(self.all_objects['attacks'])
        ability_count = len(self.all_objects['abilities'])
        trainer_count = len(self.all_objects['trainers'])
        tool_count = len(self.all_objects['tools'])
        item_count = len(self.all_objects['items'])
        fossil_count = len(self.all_objects['fossils'])
        
        print(f"   Basic import statistics:")
        print(f"   Pokemon: {pokemon_count}")
        print(f"   Attacks: {attack_count}")
        print(f"   Abilities: {ability_count}")
        print(f"   Trainers: {trainer_count}")
        print(f"   Tools: {tool_count}")
        print(f"   Items: {item_count}")
        print(f"   Fossils: {fossil_count}")
        
        # Calculate ratios
        if pokemon_count > 0:
            attacks_per_pokemon = attack_count / pokemon_count
            abilities_per_pokemon = ability_count / pokemon_count
            
            print(f"\n   Average attacks per Pokemon: {attacks_per_pokemon:.2f}")
            print(f"   Average abilities per Pokemon: {abilities_per_pokemon:.2f}")
        else:
            print(f"\n   ⚠️ No Pokemon found - cannot calculate ratios")
        
        # Ensure minimum counts
        self.assertGreater(pokemon_count, 0, "Should have imported some Pokemon")

def run_comprehensive_test():
    """Run comprehensive tests with detailed output"""
    print("\n" + "=" * 80)
    print("POKÉMON TCG POCKET JSON CARD IMPORT - COMPREHENSIVE TEST SUITE")
    print("=" * 80)
    
    # Custom test result class for more detailed output
    class VerboseTestResult(unittest.TextTestResult):
        def startTest(self, test):
            super().startTest(test)
            
        def addSuccess(self, test):
            super().addSuccess(test)
            print(f"✅ {test._testMethodName}")
            
        def addFailure(self, test, err):
            super().addFailure(test, err)
            print(f"❌ {test._testMethodName} - FAILED")
            
        def addError(self, test, err):
            super().addError(test, err)
            print(f"💥 {test._testMethodName} - ERROR")
    
    # Create test suite
    suite = unittest.TestLoader().loadTestsFromTestCase(TestJsonCardImport)
    
    # Run tests with custom result handler
    runner = unittest.TextTestRunner(
        verbosity=0,
        resultclass=VerboseTestResult,
        stream=open(os.devnull, 'w'),  # Suppress default output
        buffer=True
    )
    
    result = runner.run(suite)
    
    # Print final summary
    print("\n" + "=" * 80)
    print("FINAL TEST SUMMARY")
    print("=" * 80)
    print(f"Tests run: {result.testsRun}")
    print(f"Successes: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    
    if result.failures:
        print(f"\nFAILURES:")
        for test, traceback in result.failures:
            print(f"  - {test}")
    
    if result.errors:
        print(f"\nERRORS:")
        for test, traceback in result.errors:
            print(f"  - {test}")
    
    # Add comprehensive card type summary
    try:
        test_instance = TestJsonCardImport()
        test_instance.setUpClass()
        
        print("\n" + "=" * 80)
        print("COMPREHENSIVE CARD TYPE SUMMARY")
        print("=" * 80)
        
        total_cards = 0
        for obj_type, objects in test_instance.all_objects.items():
            count = len(objects)
            total_cards += count
            print(f"{obj_type.upper()}: {count}")
        
        print(f"\nTOTAL CARDS IMPORTED: {total_cards}")
        print("=" * 80)
        
    except Exception as e:
        print(f"\n⚠️ Could not generate card type summary: {e}")
    
    if result.wasSuccessful():
        print(f"\n🎉 ALL TESTS PASSED! JSON card import system is working perfectly!")
        return True
    else:
        print(f"\n💥 Some tests failed. Please review the issues above.")
        return False

if __name__ == '__main__':
    run_comprehensive_test() 
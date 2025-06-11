import random
from typing import Optional, List, Any
from utils import get_card_database

class HumanAgent:
    """Human-controlled agent for Pokemon TCG Pocket battles via terminal input"""
    
    def __init__(self, player):
        self.player = player

    def get_action(self, actions, match, context=None):
        """Choose an action from the available actions."""
        print(f"🐛 DEBUG: HumanAgent.get_action called with actions: {actions}, context: {context}")
        if not actions:
            return None
        
        self._display_game_state(match)
        
        # Handle specific contexts
        if context == "initial_bench_choice":
            print("\n🎯 Initial Setup - Bench Placement")
            print("Do you want to place another basic Pokemon on your bench?")
            print(f"  1. Place on bench (current bench: {len(self.player.bench_pokemons)}/{match.MAX_BENCH_SIZE})")
            print(f"  2. Keep in hand")
            
            while True:
                try:
                    choice = input("\nChoose option (1-2): ").strip()
                    if choice == "1":
                        return "place_on_bench"
                    elif choice == "2":
                        return "keep_in_hand"
                    else:
                        print("❌ Please enter 1 or 2")
                except KeyboardInterrupt:
                    print("\n👋 Game interrupted by user")
                    exit(0)
        
        elif context == "choose_attack":
            print("\n🎯 Choose Attack")
            attacks = actions  # In this context, actions contains the available attacks
            for i, attack in enumerate(attacks, 1):
                cost_str = ""
                if hasattr(attack, 'energy_cost') and attack.energy_cost:
                    costs = [f"{count}{energy[0].upper()}" for energy, count in attack.energy_cost.items()]
                    cost_str = f"[{'/'.join(costs)}] "
                
                damage_str = f"{attack.damage}" if hasattr(attack, 'damage') and attack.damage else "?"
                effect_str = f" - {attack.effect}" if hasattr(attack, 'effect') and attack.effect else ""
                
                print(f"  {i}. {attack.name} {cost_str}{damage_str} damage{effect_str}")
            
            while True:
                try:
                    choice = input(f"\nChoose attack (1-{len(attacks)}): ").strip()
                    choice_num = int(choice)
                    if 1 <= choice_num <= len(attacks):
                        selected = attacks[choice_num - 1]
                        print(f"✅ You chose: {selected.name}")
                        return selected
                    else:
                        print(f"❌ Please enter a number between 1 and {len(attacks)}")
                except ValueError:
                    print("❌ Please enter a valid number")
                except KeyboardInterrupt:
                    print("\n👋 Game interrupted by user")
                    exit(0)
        
        elif context == "precise_action":
            print("\n🎯 Choose your action:")
            
            # Separate retreat and end turn actions for ordering
            attack_actions = []
            ability_actions = []
            retreat_actions = []
            end_turn_actions = []
            other_actions = []
            
            for action in actions:
                if action.startswith("use_attack_"):
                    attack_actions.append(action)
                elif action == "use_ability":
                    ability_actions.append(action)
                elif action == "retreat":
                    retreat_actions.append(action)
                elif action == "end_turn":
                    end_turn_actions.append(action)
                else:
                    other_actions.append(action)
            
            # Reorder actions: attacks, abilities, other, retreat, end_turn
            ordered_actions = attack_actions + ability_actions + other_actions + retreat_actions + end_turn_actions
            
            for i, action in enumerate(ordered_actions, 1):
                description = self._get_action_description(action, match)
                print(f"  {i}. {description}")
            
            while True:
                try:
                    choice = input(f"\nChoose action (1-{len(ordered_actions)}): ").strip()
                    choice_num = int(choice)
                    if 1 <= choice_num <= len(ordered_actions):
                        selected = ordered_actions[choice_num - 1]
                        description = self._get_action_description(selected, match)
                        print(f"✅ You chose: {description}")
                        return selected
                    else:
                        print(f"❌ Please enter a number between 1 and {len(ordered_actions)}")
                except ValueError:
                    print("❌ Please enter a valid number")
                except KeyboardInterrupt:
                    print("\n👋 Game interrupted by user")
                    exit(0)
        
        # Standard action selection
        print(f"\n🎯 Choose your action:")
        action_descriptions = {
            "play_card": "🃏 Play a card from your hand",
            "attack": "⚔️ Attack with your active Pokemon",
            "retreat": "🏃 Switch your active Pokemon",
            "pass": "⏭️ End your turn",
            "evolve": "📈 Evolve a Pokemon",
            "pokemon_action": "🎭 Use a Pokemon ability"
        }
        
        for i, action in enumerate(actions, 1):
            description = action_descriptions.get(action, action)
            print(f"  {i}. {description}")
        
        # Get user choice
        while True:
            try:
                choice = input(f"\nChoose action (1-{len(actions)}): ").strip()
                choice_num = int(choice)
                if 1 <= choice_num <= len(actions):
                    selected = actions[choice_num - 1]
                    action_name = action_descriptions.get(selected, selected)
                    print(f"✅ You chose: {action_name}")
                    
                    return selected
                else:
                    print(f"❌ Please enter a number between 1 and {len(actions)}")
            except ValueError:
                print("❌ Please enter a valid number")
            except KeyboardInterrupt:
                print("\n👋 Game interrupted by user")
                exit(0)

    def get_chosen_card(self, options, match, context=None):
        """Choose a card or Pokémon from the given options."""
        print(f"🐛 DEBUG: HumanAgent.get_chosen_card called with {len(options)} options, context: {context}")
        if not options:
            return None
        
        self._display_game_state(match)
        
        # Context-specific displays
        if context == "choose_active":
            print("\n🎯 Choose Your Starting Active Pokémon:")
            self._display_pokemon_options(options, context)
        elif context == "choose_bench":
            print("\n🎯 Choose Pokémon for Your Bench:")
            self._display_pokemon_options(options, context)
        elif context == "choose_new_active":
            print("\n🎯 Choose New Active Pokémon:")
            self._display_pokemon_options(options, context)
        elif context == "choose_pokemon_to_attach_energy":
            print("\n🎯 Choose Pokémon to Attach Energy:")
            self._display_pokemon_options(options, context)
        elif context and "choose_pokemon_to_heal" in context:
            print(f"\n🎯 Choose Pokémon to Heal with {context.split('_')[-1]}:")
            self._display_pokemon_options(options, context)
        elif context == "draw_prize":
            print(f"\n🏆 Choose Prize Card to Draw:")
            self._display_card_options(options, context, match)
        elif context == "play_card":
            print(f"\n🃏 Choose Card to Play from Hand:")
            self._display_card_options(options, context, match)
        elif context == "choose_retreat_target":
            print("\n🏃 Choose Pokémon to Switch to:")
            self._display_pokemon_options(options, context)
        elif "choose_pokemon" in context:
            print("\n🎯 Choose Pokémon:")
            self._display_pokemon_options(options, context)
        elif context == "choose_evolution":
            print("\n🔄 Choose Evolution Card:")
            for i, (evolution, targets) in enumerate(options, 1):
                target_names = [p.name for p in targets]
                print(f"  {i}. {evolution.name} (can evolve: {', '.join(target_names)})")
        elif context == "choose_target_for_evolution":
            print("\n🔄 Choose which Pokémon to evolve:")
            self._display_pokemon_options(options, context)
        elif context == "choose_evolution_target":
            print("\n🔄 Choose which Pokémon to evolve:")
            self._display_pokemon_options(options, context)
        else:
            # Generic display
            for i, option in enumerate(options, 1):
                print(f"  {i}. {self._get_option_name(option)}")
        
        # Get user input
        while True:
            try:
                choice = input(f"\nChoose option (1-{len(options)}): ").strip()
                choice_num = int(choice)
                if 1 <= choice_num <= len(options):
                    selected = options[choice_num - 1]
                    print(f"✅ You chose: {self._get_option_name(selected)}")
                    return selected
                else:
                    print(f"❌ Please enter a number between 1 and {len(options)}")
            except ValueError:
                print("❌ Please enter a valid number")
            except KeyboardInterrupt:
                print("\n👋 Game interrupted by user")
                exit(0)

    def _display_game_state(self, match):
        """Display the current game state in a clear format."""
        
        print(f"\n📊 Game State - Turn {match.turn}")
        print("=" * 60)
        
        opponent = match.player1 if match.current_player == match.player2 else match.player2
        
        # Show opponent's Pokemon (top)
        print(f"\n🔴 {opponent.name}'s Pokemon:")
        print("-" * 40)
        
        # Opponent's active Pokemon
        if opponent.active_pokemon:
            active = opponent.active_pokemon
            energy_str = self._format_energy_display(active.equipped_energies)
            attacks_str = self._format_attacks_display(active.attacks)
            print(f"  🥊 Active: {active.name} ({active.current_hp}/{active.max_hp} HP) {energy_str}")
            if attacks_str:
                print(f"       Attacks: {attacks_str}")
        
        # Opponent's bench
        if opponent.bench_pokemons:
            print(f"  🪑 Bench: {len(opponent.bench_pokemons)} Pokemon")
            for i, pokemon in enumerate(opponent.bench_pokemons, 1):
                energy_str = self._format_energy_display(pokemon.equipped_energies)
                attacks_str = self._format_attacks_display(pokemon.attacks)
                print(f"    {i}. {pokemon.name} ({pokemon.current_hp}/{pokemon.max_hp} HP) {energy_str}")
                if attacks_str:
                    print(f"       Attacks: {attacks_str}")
        else:
            print(f"  🪑 Bench: Empty")
        
        print("\n" + "-" * 40)
        
        # Show current player's Pokemon (bottom)
        print(f"\n🔵 {match.current_player.name}'s Pokemon:")
        print("-" * 40)
        
        # Current player's active Pokemon
        if match.current_player.active_pokemon:
            active = match.current_player.active_pokemon
            energy_str = self._format_energy_display(active.equipped_energies)
            attacks_str = self._format_attacks_display(active.attacks)
            print(f"  🥊 Active: {active.name} ({active.current_hp}/{active.max_hp} HP) {energy_str}")
            if attacks_str:
                print(f"       Attacks: {attacks_str}")
        
        # Current player's bench
        if match.current_player.bench_pokemons:
            print(f"  🪑 Bench: {len(match.current_player.bench_pokemons)} Pokemon")
            for i, pokemon in enumerate(match.current_player.bench_pokemons, 1):
                energy_str = self._format_energy_display(pokemon.equipped_energies)
                attacks_str = self._format_attacks_display(pokemon.attacks)
                print(f"    {i}. {pokemon.name} ({pokemon.current_hp}/{pokemon.max_hp} HP) {energy_str}")
                if attacks_str:
                    print(f"       Attacks: {attacks_str}")
        else:
            print(f"  🪑 Bench: Empty")
        
        print("\n" + "=" * 60)
        
        # Determine which player is the human player (self.player) and which is the opponent
        human_player = self.player
        opponent_player = match.player1 if human_player == match.player2 else match.player2
        
        # Show opponent info
        print(f"\n🔴 {opponent_player.name}'s Status:")
        print(f"  🃏 Hand: {len(opponent_player.cards_in_hand)} cards (hidden)")
        print(f"  📚 Deck: {len(opponent_player.remaining_cards)} cards remaining")
        
        # Show human player's hand (always show YOUR hand, not current player's hand)
        if human_player.cards_in_hand:
            print(f"\n🔵 {human_player.name}'s Hand ({len(human_player.cards_in_hand)} cards):")
            for i, card in enumerate(human_player.cards_in_hand, 1):
                card_details = self._format_card_details(card)
                print(f"  {i}. {card_details}")
        else:
            print(f"\n🔵 {human_player.name}'s Hand: Empty")
        
        # Show human player's deck info
        print(f"  📚 Your Deck: {len(human_player.remaining_cards)} cards remaining")
        
        print("\n" + "=" * 60)

    def _display_pokemon_options(self, options, context):
        """Display Pokémon options with detailed information."""
        for i, pokemon in enumerate(options, 1):
            # Get location information
            location = ""
            if hasattr(self, 'player') and self.player:
                if self.player.active_pokemon == pokemon:
                    location = " (Active)"
                elif pokemon in self.player.bench_pokemons:
                    bench_pos = self.player.bench_pokemons.index(pokemon) + 1
                    location = f" (Bench #{bench_pos})"
            
            # Format energy information
            energy_info = ""
            if pokemon.equipped_energies:
                energies = [f"{count}x{energy}" for energy, count in pokemon.equipped_energies.items() if count > 0]
                energy_info = f" ⚡ {', '.join(energies)}"
            
            # Format attack information
            attacks_info = ""
            if hasattr(pokemon, 'attacks') and pokemon.attacks:
                attacks_info = f" - {self._format_attacks_display(pokemon.attacks)}"
            
            hp_info = f"({pokemon.current_hp}/{pokemon.max_hp} HP)"
            print(f"  {i}. {pokemon.name}{location} {hp_info}{energy_info}{attacks_info}")

    def _display_card_options(self, options, context, match):
        """Display card options with enhanced information"""
        for i, card in enumerate(options, 1):
            card_info = self._get_detailed_card_info(card, match)
            print(f"  {i}. {card_info}")

    def _display_energy_options(self, options, context):
        """Display energy type options"""
        for i, energy_type in enumerate(options, 1):
            print(f"  {i}. {energy_type.title()} Energy")

    def _get_action_description(self, action, match):
        """Get a human-readable description of an action"""
        descriptions = {
            "attach_energy": "⚡ Attach Energy to Pokemon",
            "play_card": "🃏 Play Card from Hand",
            "pokemon_action": "⚔️ Pokemon Action (Attack/Ability/Retreat)",
            "evolve": "🔄 Evolve Pokemon",
            "end_turn": "⏭️ End Turn",
            "retreat": "🏃 Retreat Active Pokemon",
            "use_ability": "✨ Use Pokemon Ability",
            "cancel": "↩️ Back to Main Menu"
        }
        
        if action.startswith("use_attack_"):
            attack_id = action.split("_")[2]
            # Try to get attack name from database
            db = get_card_database()
            if db and 'attacks' in db:
                full_attack_id = f"attack_{attack_id}" if not attack_id.startswith("attack_") else attack_id
                if full_attack_id in db['attacks']:
                    attack = db['attacks'][full_attack_id]
                    damage = getattr(attack, 'damage', '?')
                    # Show energy cost
                    cost_str = ""
                    if hasattr(attack, 'energy_cost') and attack.energy_cost:
                        costs = []
                        for energy, count in attack.energy_cost.items():
                            if count > 0:
                                energy_abbrev = energy[0].upper()
                                costs.append(f"{count}{energy_abbrev}")
                        if costs:
                            cost_str = f"[{'/'.join(costs)}] "
                    return f"⚔️ Attack: {attack.name} {cost_str}({damage} damage)"
            return f"⚔️ Attack (ID: {attack_id})"
        
        return descriptions.get(action, action)

    def _get_option_name(self, option):
        """Get a human-readable name for an option"""
        if hasattr(option, 'name'):
            return option.name
        elif isinstance(option, str):
            return option
        elif isinstance(option, tuple) and len(option) == 2:
            # For evolution options (evolution_card, target_list)
            return f"Evolve into {option[0].name}"
        else:
            return str(option)

    def _get_detailed_card_info(self, card, match):
        """Get detailed information about a card"""
        if not hasattr(card, 'card_type'):
            return str(card)
            
        if card.card_type == 'pokemon':
            stage = getattr(card, 'stage', 'unknown')
            hp = getattr(card, 'max_hp', '?')
            pokemon_type = getattr(card, 'pokemon_type', 'unknown')
            info = f"{card.name} ({stage}, {hp} HP, {pokemon_type})"
            
            if hasattr(card, 'evolves_from') and card.evolves_from:
                info += f" [Evolves from {card.evolves_from}]"
                
            return info
            
        elif card.card_type in ['trainer', 'item']:
            # Add effect description if available
            effect = getattr(card, 'effect_description', '')
            if effect:
                return f"{card.name} ({card.card_type}) - {effect}"
            else:
                return f"{card.name} ({card.card_type})"
                
        return f"{card.name} ({card.card_type})"

    def _format_energy_zone(self, energy_zone):
        """Format energy zone information for display"""
        if not energy_zone:
            return ""
        
        # Count energy types
        energy_counts = {}
        for energy in energy_zone:
            energy_counts[energy] = energy_counts.get(energy, 0) + 1
        
        # Format as string
        if energy_counts:
            energy_strs = [f"{count}x{energy}" for energy, count in energy_counts.items()]
            return f"[⚡ {', '.join(energy_strs)}]"
        
        return ""

    def _get_pokemon_choice(self, options, context):
        """Get a valid pokemon choice from the user"""
        while True:
            try:
                choice = input(f"\nChoose a {context}: ").strip()
                choice_num = int(choice)
                if 1 <= choice_num <= len(options):
                    selected = options[choice_num - 1]
                    print(f"✅ You chose: {self._get_option_name(selected)}")
                    return selected
                else:
                    print(f"❌ Please enter a number between 1 and {len(options)}")
            except ValueError:
                print("❌ Please enter a valid number")
            except KeyboardInterrupt:
                print("\n👋 Game interrupted by user")
                exit(0)

    def _format_energy_display(self, equipped_energies):
        """Format energy display for Pokemon."""
        if not equipped_energies:
            return ""
        energies = [f"{count}x{energy}" for energy, count in equipped_energies.items() if count > 0]
        return f"⚡ {', '.join(energies)}" if energies else ""
    
    def _format_attacks_display(self, attacks):
        """Format attacks display for Pokemon."""
        if not attacks:
            return ""
        attack_strings = []
        for attack in attacks:
            cost_str = ""
            if hasattr(attack, 'energy_cost') and attack.energy_cost:
                # Only show energy types with non-zero costs
                costs = []
                for energy, count in attack.energy_cost.items():
                    if count > 0:
                        # Use first letter of energy type, capitalized
                        energy_abbrev = energy[0].upper()
                        costs.append(f"{count}{energy_abbrev}")
                if costs:
                    cost_str = f"[{'/'.join(costs)}] "
            damage_str = f"{attack.damage}" if hasattr(attack, 'damage') and attack.damage else "?"
            attack_strings.append(f"{attack.name} {cost_str}{damage_str}")
        return " | ".join(attack_strings)
    
    def _format_card_details(self, card):
        """Format detailed card information for hand display."""
        card_type = getattr(card, 'card_type', 'unknown')
        if card_type == 'pokemon':
            hp = getattr(card, 'max_hp', '?')
            stage = getattr(card, 'stage', 'unknown')
            attacks_str = self._format_attacks_display(getattr(card, 'attacks', []))
            base_info = f"{card.name} ({stage}, {hp} HP)"
            if attacks_str:
                return f"{base_info} - Attacks: {attacks_str}"
            return base_info
        elif card_type == 'energy':
            energy_type = getattr(card, 'energy_type', 'unknown')
            return f"{card.name} ({energy_type} energy)"
        else:
            return f"{card.name} ({card_type})" 
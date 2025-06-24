from .card import Card
from .tool import Tool
from .attack import Attack
from .ability import Ability
from .energy import Energy


class Pokemon(Card):

    class PokemonType:
        EX = "ex"
        BEAST = "beast"
        ALOLAN = "alolan"
    
    def __init__(self, id: str, name: str, element: Energy.Type, type: Card.Type, subtype: Card.Subtype, health: int, set: str, pack: str, rarity: str, attacks: list[Attack], retreat_cost: int, weakness: Energy.Type, evolves_from: str, image_url: str = None, ability: Ability = None):
        # Call the parent Card constructor
        super().__init__(id, name, type, subtype, set, pack, rarity, image_url, ability)

        self.element: Energy.Type = element
        self.health: int = health # This is the original max health of the pokemon
        self.attacks: list[Attack] = attacks
        self.retreat_cost: int = retreat_cost
        self.weakness: Energy.Type = weakness
        self.evolves_from = evolves_from

        self.pokemon_types = set()
        self.pokemon_types.add(Pokemon.PokemonType.EX) if name.endswith(' ex') else None


        # STILL NEED TO FIGURE OUT THESE VALUES
        # Evolution tracking
        self.evolves_from_ids = []
        self.evolves_to_ids = []

        # Game variables
        self.poketool: Tool = None
        self.can_retreat = True
        self.damage_nerf = 0
        self.damage_taken = 0
        self.effect_status = []
        self.equipped_energies = {'grass': 0, 'fire': 0, 'water': 0, 'lightning': 0, 'psychic': 0, 'fighting': 0, 'darkness': 0, 'metal': 0, 'fairy': 0, 'normal': 0}
        self.placed_or_evolved_this_turn = 1
        self.used_ability_this_turn = False
    
    def current_health(self) -> int:
        return self.health - self.damage_taken
    
    def to_display_string(self) -> str:
        """Generate a detailed string representation of the Pokemon for display."""
        lines = []
        
        # Header with name and element
        health_str = f"{self.current_health()}/{self.health}" if self.damage_taken > 0 else str(self.health)
        lines.append(f"{self.name} [{self.element.upper()}] HP: {health_str}")
        
        # Ability if present
        if self.ability:
            lines.append(f"Ability: {self.ability.name} - {self.ability.effect}")
        
        # Attacks
        if self.attacks:
            lines.append("Attacks:")
            for attack in self.attacks:
                energy_cost = []
                for energy_type, amount in attack.cost.items():
                    if amount > 0:
                        energy_cost.append(f"{amount}x{energy_type}")
                cost_str = ", ".join(energy_cost) if energy_cost else "No cost"
                lines.append(f"  - {attack.name} ({cost_str}) - {attack.damage} damage")
        
        # Weakness
        if self.weakness:
            lines.append(f"Weakness: {self.weakness}")
        
        # Retreat cost
        if self.retreat_cost > 0:
            lines.append(f"Retreat Cost: {self.retreat_cost}")
        
        return "\n".join(lines)
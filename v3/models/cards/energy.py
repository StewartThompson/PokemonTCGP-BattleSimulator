class Energy:
    class Type:
        FIRE = 'fire'
        WATER = 'water'
        ROCK = 'rock'
        GRASS = 'grass'
        NORMAL = 'normal'
        ELECTRIC = 'electric'
        PSYCHIC = 'psychic'
        DARK = 'dark'
        METAL = 'metal'

    def __init__(self, cost: dict[Type, int] = None):
        self.cost: dict[Energy.Type, int] = cost if cost else {
            Energy.Type.FIRE: 0,
            Energy.Type.WATER: 0,
            Energy.Type.ROCK: 0,
            Energy.Type.GRASS: 0,
            Energy.Type.NORMAL: 0,
            Energy.Type.ELECTRIC: 0,
            Energy.Type.PSYCHIC: 0,
            Energy.Type.DARK: 0,
            Energy.Type.METAL: 0
        }

    @classmethod
    def from_string_list(cls, energy_list: list[str]) -> 'Energy':
        """Create an Energy object from a list of energy type strings"""
        cost = {
            Energy.Type.FIRE: 0,
            Energy.Type.WATER: 0,
            Energy.Type.ROCK: 0,
            Energy.Type.GRASS: 0,
            Energy.Type.NORMAL: 0,
            Energy.Type.ELECTRIC: 0,
            Energy.Type.PSYCHIC: 0,
            Energy.Type.DARK: 0,
            Energy.Type.METAL: 0
        }
        
        for energy_str in energy_list:
            try:
                energy_type = Energy.Type[energy_str.upper()]
                cost[energy_type] += 1
            except KeyError:
                raise ValueError(f"Unknown energy type: {energy_str}")
        
        return cls(cost)

    @classmethod
    def from_string(cls, energy_str: str) -> 'Energy':
        """Create an Energy object from a single energy type string"""
        return cls.from_string_list([energy_str])

    def can_afford(self, required_energy: 'Energy') -> bool:
        """Check if this energy can afford the required energy cost"""
        for energy_type, required_amount in required_energy.cost.items():
            if self.cost[energy_type] < required_amount:
                return False
        return True

    def get_total_cost(self) -> int:
        """Get the total number of energy required"""
        return sum(self.cost.values())

    def is_empty(self) -> bool:
        """Check if no energy is required"""
        return self.get_total_cost() == 0

    def __str__(self) -> str:
        """String representation of energy cost"""
        parts = []
        for energy_type, amount in self.cost.items():
            if amount > 0:
                parts.append(f"{amount} {energy_type}")
        return ", ".join(parts) if parts else "No energy required"

    def __repr__(self) -> str:
        return f"Energy({self.cost})"

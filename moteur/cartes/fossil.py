class Fossil:
    def __init__(self, fossil_id, name, hp=50, special_values=None):
        self.card_type = "fossil"
        self.fossil_id = fossil_id
        self.name = name
        self.hp = hp  # Default 50 HP for fossils
        self.max_hp = hp
        self.current_hp = hp
        self.special_values = special_values
        
        # Evolution attributes (fossils can evolve into Pokemon)
        self.evolutions_name = None
        self.pre_evolution_name = None
        
        # Fossil-specific properties
        self.can_retreat = False  # Fossils cannot retreat
        self.can_attack = False   # Fossils cannot attack
        self.is_basic_pokemon = False  # Fossils don't count as basic Pokemon
        self.pokemon_type = "colorless"  # Default type for fossils
        self.weakness = None
        self.retreat_cost = 0
        self.attack_ids = []  # No attacks
        self.ability_id = None  # No abilities
        self.equipped_energies = {'fire': 0, 'water': 0, 'rock': 0, 'grass': 0, 'normal': 0, 'electric': 0, 'psychic': 0, 'dark': 0, 'metal': 0, 'dragon': 0, 'fairy': 0}
        self.effect_status = []

    def __str__(self):
        return f"{self.name} (Fossil) - {self.current_hp}/{self.max_hp} HP - Cannot retreat or attack"

    def __repr__(self):
        return str(self)

    def reset(self):
        self.current_hp = self.max_hp
        for energy_type in self.equipped_energies:
            self.equipped_energies[energy_type] = 0
        self.effect_status = [] 
class Attack:
    def __init__(self, id_attaque, name, description, damage, energy_cost=None, effect_type=None, special_values=None):
        self.id_attaque = id_attaque
        self.name = name
        self.description = description
        self.damage = damage
        self.energy_cost = energy_cost if energy_cost else {'fire': 0, 'water': 0, 'rock': 0, 'grass': 0, 'normal': 0, 'electric': 0, 'psychic': 0, 'dark': 0, 'metal': 0, 'dragon': 0, 'fairy': 0}
        self.effect_type = effect_type
        self.special_values = special_values

    def __str__(self):
        return f"{self.name} ({self.damage} damage) ({self.energy_cost})"

    def __repr__(self):
        return str(self)
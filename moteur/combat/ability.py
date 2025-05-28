class Ability:
    def __init__(self, ability_id, name, description, effect_type, special_values, amount_of_times):
        self.ability_id = ability_id
        self.name = name
        self.description = description
        self.effect_type = effect_type
        self.special_values = special_values
        self.amount_of_times = amount_of_times

    def __str__(self):
        return f"{self.name} ({self.description})"

    def __repr__(self):
        return str(self)
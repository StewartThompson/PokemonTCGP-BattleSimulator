class Trainer:
    def __init__(self, trainer_id, name, effect, special_values=None):
        self.card_type = "trainer"
        self.trainer_id = trainer_id
        self.name = name
        self.effect = effect
        self.special_values = special_values

    def __str__(self):
        return f"{self.name} ({self.effect})"

    def __repr__(self):
        return str(self)

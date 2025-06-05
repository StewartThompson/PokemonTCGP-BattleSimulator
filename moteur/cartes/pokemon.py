class Pokemon:
    def __init__(self, card_id, name, stage, attack_ids, ability_id, max_hp, pre_evolution_name, evolutions_name, pokemon_type, weakness, retreat_cost, current_hp=None, tool_id=None, equipped_energies=None, effect_status=None):
        self.card_type = "pokemon"
        self.card_id = card_id
        self.name = name
        self.stage = stage
        self.attack_ids = attack_ids
        self.ability_id = ability_id
        self.max_hp = max_hp
        self.current_hp = current_hp if current_hp else max_hp
        self.pre_evolution_name = pre_evolution_name
        self.evolutions_name = evolutions_name
        self.retreat_cost = retreat_cost
        self.pokemon_type = pokemon_type
        self.weakness = weakness
        self.tool_id = tool_id
        self.equipped_energies = equipped_energies if equipped_energies else {'fire': 0, 'water': 0, 'rock': 0, 'grass': 0, 'electric': 0, 'psychic': 0, 'dark': 0, 'metal': 0, 'dragon': 0, 'fairy': 0}
        self.effect_status = effect_status if effect_status else []
        self.turn_since_placement = 1
        self.used_ability_this_turn = False
        self.hiding = False
        self.damage_nerf = 0


    def __str__(self):
        return f"{self.name} ({self.stage}) ({self.ability_id})- {self.current_hp}/{self.max_hp} HP - Energies {self.equipped_energies} - Status: {self.effect_status} - Retreat Cost: {self.retreat_cost} - Type: {self.pokemon_type} - Weakness: {self.weakness}"

    def __repr__(self):
        return str(self)

    def reset(self):
        self.current_hp = self.max_hp
        self.tool_id = None
        for energy_type in self.equipped_energies:
            self.equipped_energies[energy_type] = 0
        self.effect_status = []
        self.turn_since_placement = 1
        self.used_ability_this_turn = False
        self.damage_nerf = 0
        self.hiding = False

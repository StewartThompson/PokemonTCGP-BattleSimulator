class Pokemon:
    def __init__(self, card_id, name, stage, attack_ids, ability_id, max_hp, pre_evolution_name, evolutions_name, pokemon_type, weakness, retreat_cost, pack_number=None, current_hp=None, attached_tool=None, equipped_energies=None, effect_status=None):
        self.card_type = "pokemon"
        self.card_id = card_id
        self.name = name
        self.stage = stage
        self.attack_ids = attack_ids
        self.ability_id = ability_id
        self.max_hp = max_hp
        self.damage_taken = 0  # Damage counters - starts at 0
        # Keep current_hp for backwards compatibility, but calculate it from damage
        self.current_hp = max_hp  # This will be calculated as max_hp - damage_taken
        self.pre_evolution_name = pre_evolution_name
        self.evolutions_name = evolutions_name
        self.retreat_cost = retreat_cost
        self.pokemon_type = pokemon_type
        self.weakness = weakness
        self.pack_number = pack_number
        self.attached_tool = attached_tool  # Tool object or None
        self.equipped_energies = equipped_energies if equipped_energies else {'fire': 0, 'water': 0, 'rock': 0, 'grass': 0, 'normal': 0, 'electric': 0, 'psychic': 0, 'dark': 0, 'metal': 0, 'dragon': 0, 'fairy': 0}
        self.effect_status = effect_status if effect_status else []
        self.turn_since_placement = 1
        self.used_ability_this_turn = False
        self.hiding = False
        self.damage_nerf = 0
        self.can_retreat = True
        self.ability_used = False

    @property
    def current_hp(self):
        """Calculate current HP as max HP minus damage taken."""
        return max(0, self.max_hp - self.damage_taken)
    
    @current_hp.setter 
    def current_hp(self, value):
        """Set current HP by calculating damage taken."""
        # For backwards compatibility, allow setting current_hp
        # This calculates damage_taken based on the difference from max_hp
        self.damage_taken = max(0, self.max_hp - value)

    @property
    def attacks(self):
        """Get attack objects from attack IDs."""
        from utils import get_card_database
        db = get_card_database()
        if not db or 'attacks' not in db:
            return []
        
        attack_objects = []
        for attack_id in self.attack_ids:
            if attack_id in db['attacks']:
                attack_objects.append(db['attacks'][attack_id])
        return attack_objects

    def __str__(self):
        pack_info = f" [{self.pack_number}]" if self.pack_number else ""
        damage_info = f" (Damage: {self.damage_taken})" if self.damage_taken > 0 else ""
        return f"{self.name}{pack_info} ({self.stage}) ({self.ability_id})- {self.current_hp}/{self.max_hp} HP{damage_info} - Energies {self.equipped_energies} - Status: {self.effect_status} - Retreat Cost: {self.retreat_cost} - Type: {self.pokemon_type} - Weakness: {self.weakness}"

    def __repr__(self):
        return str(self)

    def reset(self):
        self.damage_taken = 0  # Reset damage counters
        self.attached_tool = None
        for energy_type in self.equipped_energies:
            self.equipped_energies[energy_type] = 0
        self.effect_status = []
        self.turn_since_placement = 1
        self.used_ability_this_turn = False
        self.damage_nerf = 0
        self.hiding = False
        self.can_retreat = True
        self.ability_used = False

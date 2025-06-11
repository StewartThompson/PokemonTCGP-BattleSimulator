from typing import List
from moteur.cartes.pokemon import Pokemon

def player_extensions(cls):
    """Extensions for the Player class."""

    def all_pokemons(self) -> List[Pokemon]:
        """Returns all Pokémon in play (active and bench)."""
        return [p for p in ([self.active_pokemon] + self.bench_pokemons) if p]

    def has_pokemons(self) -> bool:
        """Checks if the player has any Pokémon in play."""
        return self.active_pokemon is not None or len(self.bench_pokemons) > 0

    def swap_active(self, new_active: Pokemon) -> None:
        """Swaps the active Pokémon with one from the bench."""
        if new_active in self.bench_pokemons:
            self.bench_pokemons.remove(new_active)
            if self.active_pokemon:
                self.bench_pokemons.append(self.active_pokemon)
            self.active_pokemon = new_active

    def reset_effects(self) -> None:
        """Resets temporary effects on all Pokémon."""
        for pokemon in self.all_pokemons():
            pokemon.hiding = False

    # Attach the extension methods to the class
    cls.all_pokemons = all_pokemons
    cls.has_pokemons = has_pokemons
    cls.swap_active = swap_active
    cls.reset_effects = reset_effects
    
    return cls 
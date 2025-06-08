import time
import pygame as pg
from pokemon import Pokemon


class Team:
    def __init__(self, data, display_size=pg.Vector2(480, 360)):
        self.pokemon = list()
        for pkData in data:
            pokemon = Pokemon(**pkData)
            self.pokemon.append(pokemon)

        # self.battle_display = TeamDisplay(display_size, self)
        self.display_running = False

        self.active_index = 0

    def __len__(self):
        return len(self.pokemon)

    def __iter__(self):
        for pokemon in self.pokemon:
            yield pokemon

    def get_active_pokemon(self):
        return self.pokemon[self.active_index]

    def get_index(self, pokemon):
        return self.pokemon.index(pokemon) if pokemon in self.pokemon else None

    def get_pk_up(self, start_index):
        idx = (start_index - 1) % len(self.pokemon)
        return self.pokemon[idx], idx

    def get_pk_down(self, start_index):
        idx = (start_index + 1) % len(self.pokemon)
        return self.pokemon[idx], idx

    def swap_pokemon(self, pk_1, pk_2):
        idx_1, idx_2 = self.get_index(pk_1), self.get_index(pk_2)
        if idx_1 is not None and idx_2 is not None:
            self.pokemon[idx_1], self.pokemon[idx_2] = pk_2, pk_1


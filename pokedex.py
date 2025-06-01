import pandas as pd
import pygame as pg

from pokemon import pokedex
from displays.pokedex.pokedex_display import PokedexDisplayMain


class Pokedex:
    def __init__(self, game):
        self.game = game
        self.controller = game.controller

        self.data: pd.Dataframe = pokedex
        if "appearances" not in self.data.columns:
            self.data["appearances"] = 0

        self.main_display = None
        self.touch_display = None

        self.load_surfaces()

    def update_display(self, flip=True):
        self.game.topSurf.blit(self.main_display.get_surface(), (0, 0))

        # self.game.bottomSurf.blit(self.poketech.getSurface(), (0, 0))
        if flip:
            pg.display.flip()

    def loop(self):
        self.update_display()

        action = None

        while not action:
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    self.game.save()
                    self.game.running = False
                    return None

                elif event.type == pg.KEYDOWN:
                    if event.key == self.controller.b:
                        return None
                    elif event.key == self.controller.up:
                        if self.main_display.pokemon_idx != 1:
                            self.main_display.pokemon_idx -= 1
                            self.main_display.update_image()
                            self.update_display()

                    if event.key == self.controller.down:
                        if self.main_display.pokemon_idx != 151:
                            self.main_display.pokemon_idx += 1
                            self.main_display.update_image()
                            self.update_display()

    def clear_surfaces(self):
        self.main_display = None
        self.touch_display = None

    def load_surfaces(self):
        self.main_display = PokedexDisplayMain(self.game.displaySize, self.game.graphics_scale, pokedex=self)
        self.touch_display = None
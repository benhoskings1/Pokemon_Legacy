import pandas as pd
import pygame as pg

from pokemon import pokedex
from displays.pokedex.pokedex_display import PokedexDisplay, PokedexDisplayStates


class Pokedex:
    def __init__(self, game):
        self.game = game
        self.controller = game.controller

        self.national_dex = pd.read_csv("game_data/Pokedex/NationalDex/NationalDex.tsv", delimiter='\t', index_col=0)

        self.data: pd.Dataframe = pokedex
        if "appearances" not in self.data.columns:
            self.data["appearances"] = 0
        if "caught" not in self.data.columns:
            self.data["caught"] = False

        self.main_display = None
        self.touch_display = None

        self.load_surfaces()

    def update_display(self, flip=True):
        self.game.topSurf.blit(self.main_display.active_display.get_surface(), (0, 0))

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
                    if event.key == self.controller.a and self.main_display.display_state == PokedexDisplayStates.home:
                        self.main_display.display_state = PokedexDisplayStates.info
                        self.main_display.update()
                        self.update_display()

                    elif event.key == self.controller.b:
                        if self.main_display.display_state == PokedexDisplayStates.home:
                            return None
                        else:
                            self.main_display.display_state = PokedexDisplayStates.home
                            self.main_display.update()
                            self.update_display()

                    elif event.key == self.controller.up:
                        if self.main_display.pokemon_idx != 1:
                            self.main_display.pokemon_idx -= 1
                            self.main_display.update()
                            self.update_display()

                    if event.key == self.controller.down:
                        if self.main_display.pokemon_idx != 151:
                            self.main_display.pokemon_idx += 1
                            self.main_display.update()
                            self.update_display()
                            print("down")

    def clear_surfaces(self):
        self.main_display = None
        self.touch_display = None

    def load_surfaces(self):
        self.main_display = PokedexDisplay(self.game.displaySize, self.game.graphics_scale, pokedex=self)
        self.touch_display = None
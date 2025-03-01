import time
import pygame as pg
from Displays.team_display_battle import TeamDisplay, PartyAction
from pokemon import Pokemon


class Team:
    def __init__(self, data, display_size=pg.Vector2(480, 360)):
        self.pokemon = []
        for pkData in data:
            pokemon = Pokemon(**pkData)
            self.pokemon.append(pokemon)

        self.battle_display = TeamDisplay(display_size, self)
        self.display_running = False

    def display_loop(self, surface, controller,):
        self.display_running = True

        t1 = time.monotonic()
        while self.display_running:
            keys = pg.key.get_pressed()

            action = self.battle_display.update(keys, controller, self.pokemon)

            if action != PartyAction.nothing:
                if action == PartyAction.home:
                    self.display_running = False
                else:
                    return action

            surface.blit(self.battle_display.getSurface(), (0, 0))
            pg.display.flip()

            for event in pg.event.get():
                if event.type == pg.QUIT:
                    self.display_running = False
                    print("Quit")

            while time.monotonic() - t1 < 0.1:
                pass

            t1 = time.monotonic()


import pygame as pg
from game import Game


if __name__ == "__main__":
    pg.init()
    pg.event.pump()

    game = Game(1.5, new=True, overwrite=True)
    game.loop()

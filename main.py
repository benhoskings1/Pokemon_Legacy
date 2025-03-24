import pygame as pg
from game import Game


if __name__ == "__main__":
    pg.init()
    pg.event.pump()

    game = Game(1.5, fromPickle=False, overwrite=True)
    game.loop()

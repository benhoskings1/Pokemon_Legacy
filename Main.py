import pygame as pg

from Game import Game

pg.init()
pg.event.pump()

game = Game(1.5, fromPickle=True, overwrite=True)
game.loop()

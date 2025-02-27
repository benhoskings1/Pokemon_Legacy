from math import ceil

import pygame as pg

from screen import Screen, BlitLocation


class EvolveDisplay:
    def __init__(self, size):
        self.upperScreen = Screen(size)
        self.lowerScreen = Screen(size)

        self.upperScreen.loadImage("Images/Evolve/Upper Evolve 1.png", fill=True, base=True)
        self.lowerScreen.loadImage("Images/Evolve/Lower Evolve 1.png", fill=True, base=True)

        self.upperScreen.refresh()
        self.lowerScreen.refresh()

        self.text = ""

    def getUpperSurface(self):
        return self.upperScreen.surface

    def getLowerSurface(self):
        return self.lowerScreen.surface

    def cropScreen(self, height):

        upperRect = pg.Rect(0, 0, 512, height)
        lowerRect = pg.Rect(0, 265 - height, 512, height)

        pg.draw.rect(self.upperScreen.surface, pg.Color(0, 0, 0), upperRect)
        pg.draw.rect(self.upperScreen.surface, pg.Color(0, 0, 0), lowerRect)

    def update(self, image):
        self.upperScreen.refresh()
        self.upperScreen.addText2(self.text, pg.Vector2(25, 290), lines=ceil(len(self.text) / 28))

        self.upperScreen.addImage(image, pg.Vector2(256, 132), location=BlitLocation.centre)

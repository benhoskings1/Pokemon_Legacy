from math import ceil

import pygame as pg

from screen import Screen, BlitLocation


class LoadDisplay:
    def __init__(self, size):
        self.topScreen = Screen(size)
        self.bottomScreen = Screen(size, colour=pg.Color(255, 255, 255))

        self.topScreen.loadImage("Images/Load Displays/Upper.png", fill=True, base=True)
        self.topScreen.loadImage("Images/Load Displays/Title Image.png", pos=pg.Vector2(256, 156), size=(380, 120),
                                 base=True, location=BlitLocation.centre)

        self.topScreen.refresh()
        self.bottomScreen.refresh()

    def updateAnimationLocation(self, directory):
        self.bottomScreen.refresh()
        self.bottomScreen.addText2("Loading Animations", pos=(256, 50), location=BlitLocation.centre)
        self.bottomScreen.addText2("From Directory", pos=(256, 100), location=BlitLocation.centre)
        self.bottomScreen.addText2(directory, pos=(256, 150), lines=ceil(len(directory) / 28),
                                   location=BlitLocation.centre)

    def loadTeam(self, name):
        self.bottomScreen.refresh()
        self.bottomScreen.addText2("Loading Team Animations", pos=(256, 50), location=BlitLocation.centre)
        self.bottomScreen.addText2(name.title(), pos=(256, 100), location=BlitLocation.centre)

    def loadFoe(self, name):
        self.bottomScreen.refresh()
        self.bottomScreen.addText2("Loading Foe Animations", pos=(256, 50), location=BlitLocation.centre)
        self.bottomScreen.addText2(name.title(), pos=(256, 100), location=BlitLocation.centre)

    def finish(self):
        self.bottomScreen.refresh()
        self.bottomScreen.addText2("Finished Setup", pos=(256, 50), location=BlitLocation.centre)

    def getScreens(self):
        return self.topScreen.surface, self.bottomScreen.surface

from enum import Enum

import pygame as pg

from general.utils import Colours
from screen import Screen, BlitLocation, FontOption


class PartyAction(Enum):
    nothing = 5
    home = 4
    pk1 = 0
    pk2 = 1
    pk3 = 2
    pk4 = 3


class PartyDisplay:
    def __init__(self, size, team):

        self.screen = Screen(size)

        self.screens = [Screen(size) for _ in range(len(team) + 1)]

        for screen in self.screens:
            screen.loadImage("Images/Battle/Party displays/Party Base.png", fill=True, base=True)

        container = pg.image.load("Images/Battle/Party displays/Pokemon Container.png")
        selectedContainer = pg.image.load("Images/Battle/Party displays/Selected Container.png")
        primarySelected = pg.image.load("Images/Base Selected 0.png")

        size = pg.Vector2(container.get_size())
        size = pg.Vector2(size.x * 2, size.y * 1.9)
        self.container = pg.transform.scale(container, size)

        size = pg.Vector2(selectedContainer.get_size())
        size = pg.Vector2(size.x * 2, size.y * 1.9)
        self.selectedContainer = pg.transform.scale(selectedContainer, size)

        size = pg.Vector2(primarySelected.get_size())
        size = pg.Vector2(size.x * 2, size.y * 1.9)

        self.primarySelected = pg.transform.scale(primarySelected, size)

        self.screenIdx = 0
        self.prevIdx = self.screenIdx

        self.updateScreens(team)

    def getSurface(self):
        return self.screens[self.screenIdx].surface

    def updateScreens(self, team):

        for screen in self.screens:
            screen.refresh()

        pkOffset = pg.Vector2(-95, -28)
        levelOffset = pg.Vector2(-80, 22)
        textOffset = pg.Vector2(15, 22)
        nameOffset = pg.Vector2(-30, -20)
        pkPositions = [pg.Vector2(128, 45), pg.Vector2(384, 60),
                       pg.Vector2(128, 135), pg.Vector2(384, 150),
                       pg.Vector2(128, 224), pg.Vector2(384, 239)]

        for screenIdx, screen in enumerate(self.screens):
            for [idx, pk] in enumerate(team):
                if idx != 0:
                    if idx != screenIdx:
                        screen.addImage(self.container, pkPositions[idx], location=BlitLocation.centre)
                    else:
                        screen.addImage(self.selectedContainer, pkPositions[idx], location=BlitLocation.centre)
                else:
                    if idx == screenIdx:
                        screen.addImage(self.primarySelected, pkPositions[idx], location=BlitLocation.centre)
                if pk.smallImage is not None:
                    screen.addImage(pk.smallImage, pkPositions[idx] + pkOffset)

                screen.addText2(str(pk.name), pkPositions[idx] + nameOffset, colour=Colours.white.value,
                                shadowColour=Colours.darkGrey.value)
                # add level
                screen.addText2(str(pk.level), pkPositions[idx] + levelOffset, fontOption=FontOption.level)

                screen.addText2(str.format("{0}/{1}", pk.health, pk.stats.health), pkPositions[idx] + textOffset,
                                fontOption=FontOption.level, colour=Colours.white)

            if screenIdx == len(self.screens) - 1:
                rect = pg.Rect(400, 300, 112, 50)
                pg.draw.rect(screen.surface, Colours.red.value, rect, width=5, border_radius=15)

    def update(self, keys, controller):
        action = PartyAction.nothing

        if keys[controller.down]:
            if self.screenIdx < len(self.screens) - 2:
                self.prevIdx = self.screenIdx
                self.screenIdx += 2
            elif self.screenIdx == len(self.screens) - 2:
                self.prevIdx = self.screenIdx
                self.screenIdx += 1

        elif keys[controller.up]:
            if self.screenIdx == len(self.screens) - 1:
                self.screenIdx = self.prevIdx
            elif self.screenIdx >= 2:
                self.screenIdx -= 2

        elif keys[controller.left]:
            self.prevIdx = self.screenIdx
            if self.screenIdx > 0:
                self.screenIdx -= 1
            else:
                self.screenIdx = len(self.screens) - 1

        elif keys[controller.right]:
            self.prevIdx = self.screenIdx
            if self.screenIdx < len(self.screens) - 1:
                self.screenIdx += 1
            else:
                self.screenIdx = 0

        elif keys[controller.a]:
            if self.screenIdx == len(self.screens) - 1:
                action = PartyAction.home
                self.screenIdx = 0
            else:
                action = PartyAction(self.screenIdx)

        elif keys[controller.b]:
            action = PartyAction.home

        return action

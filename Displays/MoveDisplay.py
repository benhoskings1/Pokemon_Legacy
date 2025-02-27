from enum import Enum

import pygame as pg

from General.Selector import Selector3
from screen import Screen, BlitLocation, FontOption


class FightAction(Enum):
    nothing = 5
    home = 4
    move1 = 0
    move2 = 1
    move3 = 2
    move4 = 3


class MoveDisplay:
    def __init__(self, size, moves, scale=15/8):

        self.screen = Screen((256, 192))

        selectorImage = pg.image.load("Images/Medium Selector.png")
        cancelImage = pg.image.load("Images/Battle/Fight/Cancel Selector.png")
        size = pg.Vector2(int(124 * scale), int(55 * scale))
        selectorImage = pg.transform.scale(selectorImage, size)

        self.movePositions = [pg.Vector2(2, 24), pg.Vector2(130, 24), pg.Vector2(2, 82), pg.Vector2(130, 82)]

        positions = [(int(2 * scale), int(24 * scale)), (int(130 * scale), int(24 * scale)),
                     (int(2 * scale), int(80 * scale)), (int(130 * scale), int(80 * scale)),
                     (int(9 * scale), int(147 * scale))]

        self.containers = {}
        moveTypes = ["Normal", "Fire", "Water", "Electric", "Grass", "Ice", "Fighting", "Poison",
                     "Ground", "Flying", "Psychic", "Bug", "Rock", "Ghost", "Dragon", "Dark", "Steel"]

        for moveType in moveTypes:
            self.containers[moveType] = pg.image.load(
                str.format("Images/Battle/Fight/Move Containers/{} Container.png", moveType))

        sizes = [size, size, size, size, pg.Vector2((int(240 * scale), int(45 * scale)))]

        self.selector = Selector3(shape=[pg.Vector2(2, 2), pg.Vector2(1, 1)],
                                  blitPositions=positions, sizes=sizes,
                                  imageType=[0, 0, 0, 0, 1],
                                  images=[selectorImage, cancelImage])

        # create home screen base
        self.screen.loadImage("Images/Battle/Fight/Fight Base.png", fill=True, base=True)

        moveNameOffset = pg.Vector2((int(62 * scale), int(13 * scale)))
        PPOffset = pg.Vector2((int(56 * scale), int(31 * scale)))

        for idx, move in enumerate(moves):
            self.screen.addImage(self.containers[move.type], self.movePositions[idx], base=True)

        self.screen.scaleSurface(scale, base=True)

        for idx, move in enumerate(moves):
            self.screen.addText2(move.name, (self.movePositions[idx] * scale) + moveNameOffset, base=True,
                                 location=BlitLocation.midTop)
            self.screen.addText2("PP", (self.movePositions[idx] * scale) + PPOffset,
                                 colour=pg.Color(63, 48, 41), shadowColour=pg.Color(153, 158, 136), base=True,
                                 location=BlitLocation.midTop)

        self.screen.refresh()

    def getSurface(self):
        [image, pos, _] = self.selector.getValues()
        surface = self.screen.getSurface(image, pos)
        return surface

    def updateScreen(self, moves, scale=15/8):
        self.screen.refresh()
        for [idx, move] in enumerate(moves):
            self.screen.addText2(str.format("{0}/{1}", move.PP, move.maxPP),
                                 (self.movePositions[idx] * scale) + pg.Vector2((int(108 * scale), int(34 * scale))),
                                 fontOption=FontOption.level, location=BlitLocation.topRight)

    def update(self, controller, keys=None):
        action = FightAction.nothing

        if keys:
            if keys[controller.up]:
                self.selector.moveUp()

            elif keys[controller.down]:
                self.selector.moveDown()

            elif keys[controller.left]:
                self.selector.moveLeft()

            elif keys[controller.right]:
                self.selector.moveRight()

            elif keys[controller.a]:
                [_, _, idx] = self.selector.getValues()

                if idx == len(self.selector.blitPositions) - 1:
                    action = FightAction.home
                    self.selector.reset()
                else:
                    action = FightAction(idx)

            elif keys[controller.b]:
                action = FightAction.home

        return action

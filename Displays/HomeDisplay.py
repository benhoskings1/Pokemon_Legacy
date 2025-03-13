from enum import Enum
from math import ceil

import pygame as pg

from general.Controller import Controller
from general.Selector import Selector3
from screen import Screen


class HomeAction(Enum):
    nothing = 5
    fight = 0
    bag = 1
    run = 2
    team = 3


class HomeDisplay:
    def __init__(self, size):

        self.screen = Screen(size)

        smallSelector = pg.image.load("Images/Small Selector.png")
        largeSelector = pg.image.load("Images/Large Selector.png")

        positions = [(int(20 * 15 / 8), int(33 * 15 / 8)), (int(1 * 15 / 8), int(136 * 15 / 8)),
                     (int(89 * 15 / 8), int(145 * 15 / 8)), (int(176 * 15 / 8), int(136 * 15 / 8))]

        sizes = [(ceil(216 * 15 / 8), ceil(88 * 15 / 8)), (ceil(79 * 15 / 8), ceil(46 * 15 / 8)),
                 (ceil(79 * 15 / 8), ceil(46 * 15 / 8)), (ceil(79 * 15 / 8), ceil(46 * 15 / 8))]

        self.selector = Selector3(shape=[pg.Vector2(1, 1), pg.Vector2(3, 1)],
                                  blitPositions=positions, sizes=sizes,
                                  images=[largeSelector, smallSelector],
                                  imageType=[0, 1, 1, 1])

        # create home screen base
        self.screen.loadImage("Images/Battle/Home Base.png", fill=True, base=True)

        self.screen.refresh()

    def getSurface(self):
        [image, pos, _] = self.selector.getValues()
        surface = self.screen.getSurface(image, pos)
        return surface

    def update(self, keys, controller: Controller):
        action = HomeAction.nothing

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
            action = HomeAction(idx)

        return action

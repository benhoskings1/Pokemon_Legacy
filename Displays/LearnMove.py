from enum import Enum
from math import ceil

import pygame as pg

from General.Colours import Colours
from General.Move import Move, getMove
from General.Selector import Selector3
from pokemon import Pokemon
from screen import Screen, BlitLocation


class LearnState(Enum):
    screen1 = 0
    screen2 = 1
    screen3 = 2
    screen4 = 3


class LearnAction(Enum):
    nothing = 5
    move1 = 0
    move2 = 1
    move3 = 2
    move4 = 3
    giveUp = 4


class LearnMoveDisplay:
    def __init__(self, size):
        screen1 = Screen(pg.Vector2(256, 192))
        screen2 = Screen(pg.Vector2(256, 192), colour=Colours.white.value)
        screen3 = Screen(pg.Vector2(256, 192))
        screen4 = Screen(pg.Vector2(256, 192))

        self.displayMove = getMove("Tackle")

        self.state = LearnState.screen1
        self.prevState = self.state

        selectorImage = pg.image.load("Images/Medium Selector.png")
        cancelImage = pg.image.load("Images/Battle/Bag/Cancel Selector.png")

        positions = [(int(128 * 15 / 8), int(66 * 15 / 8)), (int(128 * 15 / 8), int(138 * 15 / 8))]
        sizes = [(ceil(247 * 15 / 8), ceil(63 * 15 / 8)), (ceil(247 * 15 / 8), ceil(63 * 15 / 8))]

        # self.selector1 = Selector2(selectorImage, positions=screen1Positions, optionCount=2)
        self.selector1 = Selector3(shape=[pg.Vector2(1, 1), pg.Vector2(1, 1)],
                                   blitPositions=positions, sizes=sizes, imageType=[0, 0],
                                   images=[selectorImage])

        self.selector4 = Selector3(shape=[pg.Vector2(1, 1), pg.Vector2(1, 1)],
                                   blitPositions=positions, sizes=sizes, imageType=[0, 0],
                                   images=[selectorImage])

        positions = [(int(1 * 15 / 8), int(47 * 15 / 8)), (int(129 * 15 / 8), int(47 * 15 / 8)),
                     (int(1 * 15 / 8), int(97 * 15 / 8)), (int(129 * 15 / 8), int(97 * 15 / 8)),
                     (int(65 * 15 / 8), int(145 * 15 / 8)), (int(217 * 15 / 8), int(152 * 15 / 8))]
        sizes = [(ceil(126 * 15 / 8), ceil(47 * 15 / 8)), (ceil(126 * 15 / 8), ceil(47 * 15 / 8)),
                 (ceil(126 * 15 / 8), ceil(47 * 15 / 8)), (ceil(126 * 15 / 8), ceil(47 * 15 / 8)),
                 (ceil(126 * 15 / 8), ceil(47 * 15 / 8)), (ceil(38 * 15 / 8), ceil(39 * 15 / 8))]

        self.selector2 = \
            Selector3(shape=[pg.Vector2(2, 2), pg.Vector2(2, 1)],
                      blitPositions=positions, sizes=sizes,
                      imageType=[0, 0, 0, 0, 0, 1], images=[selectorImage, cancelImage])

        positions = [(int(1 * 15 / 8), int(152 * 15 / 8)), (int(217 * 15 / 8), int(152 * 15 / 8))]
        sizes = [(ceil(206 * 15 / 8), ceil(39 * 15 / 8)), (ceil(38 * 15 / 8), ceil(39 * 15 / 8))]

        self.selector3 = Selector3(shape=[pg.Vector2(2, 1)],
                                   blitPositions=positions, sizes=sizes, imageType=[0, 1],
                                   images=[selectorImage, cancelImage])

        self.selectors = [self.selector1, self.selector2, self.selector3, self.selector4]

        screen1.loadImage("Images/Battle/Learn Move/Screen 1/Screen.png", fill=True, base=True)
        screen1.scaleSurface(15 / 8, base=True)
        screen1.addText2("Forget a move!", (int(128 * 15 / 8), int(70 * 15 / 8)),
                         location=BlitLocation.centre, base=True, colour=Colours.white.value)

        screen1.addText2("Keep old moves!", (int(128 * 15 / 8), int(142 * 15 / 8)),
                         location=BlitLocation.centre, base=True, colour=Colours.white.value)

        screen1.refresh()

        screen2.loadImage("Images/Battle/Learn Move/Screen 2/Base.png", base=True)
        screen3.loadImage("Images/Battle/Learn Move/Screen 3/Base.png", base=True)

        screen4.loadImage("Images/Battle/Learn Move/Screen 1/Screen.png", fill=True, base=True)

        self.screens = [screen1, screen2, screen3, screen4]

        self.text = ""

        self.screenIdx = 0
        self.moveIdx = 0

    def updateScreens(self, pk: Pokemon, newMove: Move):
        screen2 = self.screens[1]
        screen2.refresh()
        screen2.scaleSurface(15 / 8)

        screen2.addText2(pk.name, pg.Vector2(80, 24))

        if pk.smallImage:
            screen2.addImage(pk.smallImage, pg.Vector2(48, 25),
                             location=BlitLocation.centre)

        positions = [(int(64 * 15 / 8), int(70 * 15 / 8)), (int(192 * 15 / 8), int(70 * 15 / 8)),
                     (int(64 * 15 / 8), int(122 * 15 / 8)), (int(192 * 15 / 8), int(122 * 15 / 8)),
                     (int(128 * 15 / 8), int(170 * 15 / 8))]

        allMoves = pk.moves.copy()
        allMoves.append(newMove)
        for idx, move in enumerate(allMoves):
            screen2.addText2(move.name, positions[idx] + pg.Vector2(0, int(-8 * 15 / 8)),
                             location=BlitLocation.centre, colour=Colours.white.value,
                             shadowColour=Colours.shadow.value)

            screen2.addText2(str.format("{}/{}", move.PP, move.maxPP), positions[idx] +
                             pg.Vector2(int(22 * 15 / 8), int(10 * 15 / 8)),
                             location=BlitLocation.centre, colour=Colours.white.value,
                             shadowColour=Colours.darkGrey.value)

            screen2.loadImage(str.format("Images/Type Labels/{} Label.png", move.type),
                              positions[idx] + pg.Vector2(int(-36 * 15 / 8), int(10 * 15 / 8)),
                              location=BlitLocation.centre, scale=pg.Vector2(2, 1.7))

        screen3 = self.screens[2]
        move = allMoves[self.moveIdx]
        screen3.refresh()
        screen3.loadImage(str.format("Images/Battle/Party Displays/Move Display/{}.png", move.category.title()),
                          (9, 81))
        screen3.loadImage(str.format("Images/Type Labels/{} Label.png", move.type.title()), (110, 41))

        screen3.scaleSurface(15 / 8)
        screen3.addImage(pk.smallImage, (int(20 * 15 / 8), int(10 * 15 / 8)), location=BlitLocation.centre)
        screen3.addText2(pk.name, (int(50 * 15 / 8), int(12 * 15 / 8)), colour=Colours.white.value)

        screen3.addText2(move.name, (int(22 * 15 / 8), int(43 * 15 / 8)), colour=Colours.white.value)
        screen3.addText2("CATEGORY", (int(47 * 15 / 8), int(67 * 15 / 8)), colour=Colours.white.value,
                         location=BlitLocation.midTop)
        screen3.addText2("POWER", (int(9 * 15 / 8), int(107 * 15 / 8)), colour=Colours.white.value)
        screen3.addText2("ACCURACY", (int(9 * 15 / 8), int(131 * 15 / 8)), colour=Colours.white.value)
        screen3.addText2("PP", (int(154 * 15 / 8), int(43 * 15 / 8)), colour=Colours.white.value)
        screen3.addText2(move.category, (int(72 * 15 / 8), int(84 * 15 / 8)), location=BlitLocation.midTop)
        screen3.addText2(str.format("{}/{}", move.PP, move.maxPP), (int(184 * 15 / 8), int(43 * 15 / 8)),
                         colour=Colours.white.value)

        if move.power:
            screen3.addText2(str(move.power), (int(104 * 15 / 8), int(107 * 15 / 8)), location=BlitLocation.topRight)
        else:
            screen3.addText2("---", (int(104 * 15 / 8), int(107 * 15 / 8)), location=BlitLocation.topRight)

        if move.power:
            screen3.addText2(str(move.accuracy), (int(104 * 15 / 8), int(131 * 15 / 8)), location=BlitLocation.topRight)
        else:
            screen3.addText2("---", (int(104 * 15 / 8), int(131 * 15 / 8)), location=BlitLocation.topRight)

        if move.description:
            screen3.addText2(move.description, (int(130 * 15 / 8), int(67 * 15 / 8)),
                             lines=ceil(len(move.description) / 14))

        if self.moveIdx == 4:
            screen3.addText2("CANCEL", (int(104 * 15 / 8), int(172 * 15 / 8)), location=BlitLocation.centre,
                             colour=Colours.white.value, shadowColour=Colours.white.value)
        else:
            screen3.addText2("FORGET", (int(104 * 15 / 8), int(172 * 15 / 8)), location=BlitLocation.centre,
                             colour=Colours.white.value, shadowColour=Colours.white.value)

        screen4 = self.screens[3]
        screen4.refresh()
        screen4.scaleSurface(15 / 8)
        screen4.addText2(str.format("Give up on {}!", newMove.name), pg.Vector2(256, 128),
                         location=BlitLocation.centre, colour=Colours.white.value,
                         shadowColour=Colours.shadow.value)
        screen4.addText2(str.format("Don't give up on {}!", newMove.name), pg.Vector2(256, 262),
                         location=BlitLocation.centre, colour=Colours.white.value,
                         shadowColour=Colours.shadow.value)

        self.screens[1:] = [screen2, screen3, screen4]

    def getSurface(self):
        selector = self.selectors[self.state.value]
        screen = self.screens[self.state.value]
        [image, pos, _] = selector.getValues()
        if self.state == LearnState.screen1 or self.state == LearnState.screen4:
            surface = screen.getSurface(image, pos, location=BlitLocation.centre)
        else:
            surface = screen.getSurface(image, pos)
        return surface

    def update(self, keys, controller, pk, move):
        action = LearnAction.nothing

        selector = self.selectors[self.state.value]

        if keys[controller.up]:
            selector.moveUp()

        elif keys[controller.down]:
            selector.moveDown()

        elif keys[controller.left]:
            selector.moveLeft()

        elif keys[controller.right]:
            selector.moveRight()

        elif keys[controller.a]:

            [_, _, idx] = selector.getValues()

            self.prevState = self.state

            if self.state == LearnState.screen1:
                if idx == 0:
                    self.state = LearnState.screen2
                else:
                    self.state = LearnState.screen4

                selector.reset()

            elif self.state == LearnState.screen2:
                if idx == selector.options - 1:
                    self.state = LearnState.screen4
                else:
                    self.moveIdx = idx
                    self.state = LearnState.screen3

                self.updateScreens(pk, move)

            elif self.state == LearnState.screen3:
                [_, _, idx2] = self.selector2.getValues()

                if idx == selector.options - 1:
                    self.state = LearnState.screen2

                elif idx2 == self.selector2.options - 2:
                    self.state = LearnState.screen4
                else:
                    action = LearnAction(idx2)

                selector.reset()

            elif self.state == LearnState.screen4:
                if idx == 0:
                    action = LearnAction.giveUp
                else:
                    self.state = LearnState.screen1
                selector.reset()

        elif keys[controller.b]:
            if self.state != LearnState.screen1:
                if self.state == self.prevState:
                    self.state = LearnState(self.state.value - 1)
                else:
                    self.state = self.prevState
                self.screenIdx = self.state.value

        if self.state == LearnState.screen1:
            text = "Make it forget another move?"
        elif self.state == LearnState.screen2 or \
                self.state == LearnState.screen3:
            text = "Which move should be forgotten?"
        else:
            text = "Should this pokemon give up on leaning this new move"

        return action, text

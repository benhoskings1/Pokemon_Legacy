import time
from enum import Enum
from math import ceil

import pandas as pd
import pygame as pg

import general.Move
from pokemon import Pokemon
from general.Colours import Colours
from general.Selector import Selector3
from screen import Screen, BlitLocation, FontOption

levelUpValues = pd.read_csv("game_data/Level Up.tsv", delimiter='\t')


class PartyAction(Enum):
    nothing = 7
    home = 6
    pk1 = 0
    pk2 = 1
    pk3 = 2
    pk4 = 3
    pk5 = 4
    pk6 = 5


class PartyState(Enum):
    screen1 = 0
    screen2 = 1


class TeamDisplay:
    def __init__(self, size, team):
        self.screen = Screen(pg.Vector2(256, 192))
        self.screen.loadImage("Images/Battle/Party displays/Screen 1/Base.png", base=True)

        selectorImage = pg.image.load("Images/Medium Selector.png")
        cancelImage = pg.image.load("Images/Battle/Bag/Cancel Selector.png")

        self.positions = [pg.Vector2(2, 4), pg.Vector2(242, 19), pg.Vector2(2, 94),
                          pg.Vector2(242, 109), pg.Vector2(2, 184), pg.Vector2(242, 199),
                          (407, 285)]
        sizes = [(236, 86), (236, 86), (236, 86), (236, 86),
                 (236, 86), (236, 86), (71, 73)]

        self.selector = Selector3(shape=[pg.Vector2(2, 3), pg.Vector2(1, 1)],
                                  blitPositions=self.positions, sizes=sizes,
                                  imageType=[0, 0, 0, 0, 0, 0, 1],
                                  images=[selectorImage, cancelImage])

        positions2 = [(int(9 * 15 / 8), int(8 * 15 / 8)), (int(1 * 15 / 8), int(152 * 15 / 8)),
                      (int(105 * 15 / 8), int(152 * 15 / 8)), (int(217 * 15 / 8), int(152 * 15 / 8))]

        sizes2 = [(ceil(238 * 15 / 8), ceil(135 * 15 / 8)), (ceil(102 * 15 / 8), ceil(39 * 15 / 8)),
                  (ceil(102 * 15 / 8), ceil(39 * 15 / 8)), (ceil(38 * 15 / 8), ceil(39 * 15 / 8))]

        selector2 = Selector3(shape=[pg.Vector2(1, 1), pg.Vector2(3, 1)], blitPositions=positions2,
                              sizes=sizes2, imageType=[0, 0, 0, 1], images=[selectorImage, cancelImage])

        screen2 = Screen(pg.Vector2(256, 192))
        screen2.loadImage("Images/Battle/Party displays/Screen 2/Base.png", base=True)
        screen2.refresh()
        screen2.scaleSurface(15 / 8, base=True)
        screen2.addText2("SHIFT", (int(128 * 15 / 8), int(110 * 15 / 8)), location=BlitLocation.centre, base=True,
                         colour=Colours.white.value, shadowColour=Colours.white.value)
        screen2.addText2("SUMMARY", (int(25 * 15 / 8), int(168 * 15 / 8)), base=True,
                         colour=Colours.white.value, shadowColour=Colours.white.value)
        screen2.addText2("CHECK MOVES", (int(118 * 15 / 8), int(168 * 15 / 8)), base=True,
                         colour=Colours.white.value, shadowColour=Colours.white.value)
        screen2.refresh()

        summaryScreen = Screen(pg.Vector2(256, 192))
        summaryScreen.loadImage("Images/Battle/Party displays/Summary/Base.png", base=True)
        summaryScreen.refresh()
        summaryScreen.scaleSurface(15 / 8, base=True)
        summaryScreen.addText2("CHECK MOVES", (int(148 * 15 / 8), int(172 * 15 / 8)), location=BlitLocation.centre,
                               base=True, colour=Colours.white.value, shadowColour=Colours.white.value)
        summaryScreen.refresh()

        summaryPositions = [(int(1 * 15 / 8), int(152 * 15 / 8)), (int(41 * 15 / 8), int(152 * 15 / 8)),
                            (int(97 * 15 / 8), int(152 * 15 / 8)), (int(217 * 15 / 8), int(152 * 15 / 8))]
        summarySizes = [(ceil(38 * 15 / 8), ceil(39 * 15 / 8)), (ceil(38 * 15 / 8), ceil(39 * 15 / 8)),
                        (ceil(102 * 15 / 8), ceil(39 * 15 / 8)), (ceil(38 * 15 / 8), ceil(39 * 15 / 8))]

        summarySelector = Selector3(shape=[pg.Vector2(4, 1)], blitPositions=summaryPositions,
                                    sizes=summarySizes, imageType=[1, 1, 0, 1], images=[selectorImage, cancelImage])

        checkScreen = Screen(pg.Vector2(256, 192))
        checkScreen.loadImage("Images/Battle/Party displays/Check Moves/Base.png", base=True)
        checkScreen.refresh()

        checkPositions = [(int(1 * 15 / 8), int(48 * 15 / 8)), (int(130 * 15 / 8), int(48 * 15 / 8)),
                          (int(1 * 15 / 8), int(97 * 15 / 8)), (int(130 * 15 / 8), int(97 * 15 / 8)),
                          (int(1 * 15 / 8), int(152 * 15 / 8)), (int(41 * 15 / 8), int(152 * 15 / 8)),
                          (int(97 * 15 / 8), int(152 * 15 / 8)), (int(217 * 15 / 8), int(152 * 15 / 8))]

        checkSizes = [(ceil(126 * 15 / 8), ceil(47 * 15 / 8)), (ceil(126 * 15 / 8), ceil(47 * 15 / 8)),
                      (ceil(126 * 15 / 8), ceil(47 * 15 / 8)), (ceil(126 * 15 / 8), ceil(47 * 15 / 8)),
                      (ceil(38 * 15 / 8), ceil(39 * 15 / 8)), (ceil(38 * 15 / 8), ceil(39 * 15 / 8)),
                      (ceil(102 * 15 / 8), ceil(39 * 15 / 8)), (ceil(38 * 15 / 8), ceil(39 * 15 / 8))]

        checkSelector = Selector3(shape=[pg.Vector2(2, 2), pg.Vector2(4, 1)], blitPositions=checkPositions,
                                  sizes=checkSizes, imageType=[0, 0, 0, 0, 1, 1, 0, 1],
                                  images=[selectorImage, cancelImage])

        moveScreen = Screen((256, 192))
        moveScreen.loadImage("Images/Battle/Party displays/Move Display/Base.png", base=True)
        moveScreen.refresh()
        movePositions = [(int(88 * 15 / 8), int(153 * 15 / 8)), (int(128 * 15 / 8), int(153 * 15 / 8)),
                         (int(217 * 15 / 8), int(152 * 15 / 8)), (int(88 * 15 / 8), int(168 * 15 / 8)),
                         (int(128 * 15 / 8), int(168 * 15 / 8)), (int(217 * 15 / 8), int(152 * 15 / 8))]
        moveSizes = [(ceil(40 * 15 / 8), ceil(16 * 15 / 8)), (ceil(40 * 15 / 8), ceil(16 * 15 / 8)),
                     (ceil(38 * 15 / 8), ceil(39 * 15 / 8)), (ceil(40 * 15 / 8), ceil(16 * 15 / 8)),
                     (ceil(40 * 15 / 8), ceil(16 * 15 / 8)), (ceil(38 * 15 / 8), ceil(39 * 15 / 8))]
        moveSelector = Selector3(shape=[pg.Vector2(3, 1), pg.Vector2(3, 1)], blitPositions=movePositions,
                                 sizes=moveSizes, imageType=[0, 0, 1, 0, 0, 1],
                                 images=[selectorImage, cancelImage])

        self.screens = [self.screen, screen2, summaryScreen, checkScreen, moveScreen]
        self.selectors = [self.selector, selector2, summarySelector, checkSelector, moveSelector]

        self.screenIdx = 0
        self.teamSize = len(team.pokemon)
        self.pokemonIdx = 0
        self.moveIdx = 0

        self.updateScreen(team.pokemon)

    def getSurface(self):
        selector = self.selectors[self.screenIdx]
        screen = self.screens[self.screenIdx]
        [image, pos, _] = selector.getValues()
        surface = screen.getSurface(image, pos)
        return surface

    def updateScreen(self, team):

        screen1 = self.screens[0]
        screen1.refresh()
        activeContainer = pg.image.load("Images/Battle/Party displays/Screen 1/Active Container.png")
        teamContainer = pg.image.load("Images/Battle/Party displays/Screen 1/Team Container.png")
        emptyContainer = pg.image.load("Images/Battle/Party displays/Screen 1/Empty Container.png")
        positions = [pg.Vector2(1, 2), pg.Vector2(129, 10),
                     pg.Vector2(1, 50), pg.Vector2(129, 58),
                     pg.Vector2(1, 98), pg.Vector2(129, 106)]

        for idx in range(6):
            position = positions[idx]
            if idx < len(team):
                if idx == 0:
                    screen1.addImage(activeContainer, position)
                else:
                    screen1.addImage(teamContainer, position)
            else:
                screen1.addImage(emptyContainer, position)

        screen1.scaleSurface(15 / 8)

        pkOffset = pg.Vector2(34, 20)
        nameOffset = pg.Vector2(70, 20)
        levelOffset = pg.Vector2(25, 60)
        hpOffset = pg.Vector2(int(64 * 15 / 8), int(26 * 15 / 8))

        for idx, pk in enumerate(team):
            pk: Pokemon
            position = positions[idx] * 15 / 8
            screen1.addImage(pk.smallImage, position + pkOffset,
                             location=BlitLocation.centre)

            screen1.addText2(pk.name.upper(), position + nameOffset,
                             colour=Colours.white.value)

            screen1.addText2(str.format("Lv {}", pk.level), position + levelOffset,
                             fontOption=FontOption.level)

            hpRatio = pk.health / pk.stats.health
            hpRect = pg.Rect(hpOffset, ((47 * 15 / 8) * hpRatio, 4))
            hpRect.topleft += position

            if pk.health > 0:
                if pk.health >= pk.stats.health * 0.5:
                    colour = "High"
                elif pk.health >= pk.stats.health * 0.25:
                    colour = "Medium"
                else:
                    colour = "Low"
            else:
                hpRect = pg.Rect(0, 0, 0, 0)
                colour = "Low"

            imPath = str.format("Images/Battle/Party displays/Screen 1/Health {}.png", colour)
            screen1.loadImage(imPath, pos=hpRect.topleft, size=hpRect.size)

        screen2 = self.screens[1]
        pk: Pokemon = team[self.pokemonIdx]
        screen2.refresh()
        # screen2.scaleSurface(15 / 8)
        screen2.addImage(pk.smallImage, (int(128 * 15 / 8), int(70 * 15 / 8)),
                         location=BlitLocation.centre)
        screen2.addText2(pk.name, (int(148 * 15 / 8), int(45 * 15 / 8)),
                         location=BlitLocation.topRight, colour=Colours.white.value)

        if pk.gender == "Male":
            symbol = pg.image.load("Images/Gender/Male.png")
        else:
            symbol = pg.image.load("Images/Gender/Female.png")

        symbol = pg.transform.scale(symbol, pg.Vector2(symbol.get_size()) * 1.8)

        screen2.addImage(symbol, (int(154 * 15 / 8), int(45 * 15 / 8)))

        # summary screen

        screen3 = self.screens[2]
        screen3.refresh()

        screen3.addImage(pk.smallImage, (int(20 * 15 / 8), int(10 * 15 / 8)), location=BlitLocation.centre)
        screen3.addText2(pk.name, (int(50 * 15 / 8), int(12 * 15 / 8)), colour=Colours.white.value)
        screen3.addText2(str.format("Lv. {}", pk.level), (int(8 * 15 / 8), int(35 * 15 / 8)),
                         colour=Colours.white.value)
        screen3.addText2("NEXT LV", (int(8 * 15 / 8), int(51 * 15 / 8)),
                         colour=Colours.white.value)
        XP = int(levelUpValues.loc[pk.level, pk.growthRate])
        nextLvExp = XP - pk.exp
        screen3.addText2(str(nextLvExp), (int(107 * 15 / 8), int(51 * 15 / 8)))
        screen3.addText2(pk.ability, (int(8 * 15 / 8), int(75 * 15 / 8)), colour=Colours.white.value)

        screen3.addText2("HP", (int(168 * 15 / 8), int(35 * 15 / 8)), colour=Colours.white.value)
        screen3.addText2("Attack", (int(168 * 15 / 8), int(59 * 15 / 8)), colour=Colours.white.value)
        screen3.addText2("Defence", (int(168 * 15 / 8), int(75 * 15 / 8)), colour=Colours.white.value)
        screen3.addText2("SP. Atk", (int(168 * 15 / 8), int(91 * 15 / 8)), colour=Colours.white.value)
        screen3.addText2("SP. Def", (int(168 * 15 / 8), int(107 * 15 / 8)), colour=Colours.white.value)
        screen3.addText2("Speed", (int(168 * 15 / 8), int(123 * 15 / 8)), colour=Colours.white.value)

        screen3.addText2(str.format("{}/{}", pk.health, pk.stats.health), (int(248 * 15 / 8), int(35 * 15 / 8)),
                         location=BlitLocation.topRight)
        screen3.addText2(str(pk.stats.attack), (int(248 * 15 / 8), int(59 * 15 / 8)), location=BlitLocation.topRight)
        screen3.addText2(str(pk.stats.defence), (int(248 * 15 / 8), int(75 * 15 / 8)), location=BlitLocation.topRight)
        screen3.addText2(str(pk.stats.spAttack), (int(248 * 15 / 8), int(91 * 15 / 8)), location=BlitLocation.topRight)
        screen3.addText2(str(pk.stats.spDefence), (int(248 * 15 / 8), int(107 * 15 / 8)),
                         location=BlitLocation.topRight)
        screen3.addText2(str(pk.stats.speed), (int(248 * 15 / 8), int(123 * 15 / 8)), location=BlitLocation.topRight)

        if pk.item:
            pass
        else:
            screen3.addText2("No item held", (int(32 * 15 / 8), int(130 * 15 / 8)), colour=Colours.white.value)

        screen4 = self.screens[3]
        screen4.refresh()
        # screen4.scaleSurface(15 / 8)
        move = pg.image.load("Images/Battle/Party displays/Check Moves/Move Container.png")
        emptyContainer = pg.image.load("Images/Battle/Party displays/Check Moves/Empty Container.png")
        movePositions = [pg.Vector2(1, 48), pg.Vector2(130, 48), pg.Vector2(1, 97), pg.Vector2(130, 97)]
        for idx in range(4):
            position = movePositions[idx]
            if idx < len(pk.moves):
                screen4.addImage(move, position)
            else:
                screen4.addImage(emptyContainer, position + pg.Vector2(0, 2))

        for idx, move in enumerate(pk.moves):
            screen4.loadImage(str.format("Images/Type Labels/{} Label.png", move.type.title()),
                              movePositions[idx] + pg.Vector2(7, 26))

        screen4.scaleSurface(15 / 8)

        screen4.addImage(pk.smallImage, (int(20 * 15 / 8), int(10 * 15 / 8)), location=BlitLocation.centre)
        screen4.addText2(pk.name, (int(50 * 15 / 8), int(12 * 15 / 8)), colour=Colours.white.value)

        screen4.addText2("SUMMARY", (int(148 * 15 / 8), int(172 * 15 / 8)), location=BlitLocation.centre,
                         colour=Colours.white.value, shadowColour=Colours.white.value)

        for idx, move in enumerate(pk.moves):
            position = movePositions[idx] * (15 / 8)
            move: general.Move.Move2

            screen4.addText2(move.name.upper(), position + pg.Vector2(int(63 * 15 / 8), int(17 * 15 / 8)),
                             location=BlitLocation.centre, colour=Colours.white.value)
            screen4.addText2("PP", position + pg.Vector2(int(48 * 15 / 8), int(28 * 15 / 8)),
                             colour=Colours.white.value, shadowColour=Colours.darkGrey.value)
            screen4.addText2(str.format("{}/{}", move.PP, move.maxPP),
                             position + pg.Vector2(int(105 * 15 / 8), int(28 * 15 / 8)),
                             location=BlitLocation.topRight, colour=Colours.white.value,
                             shadowColour=Colours.darkGrey.value)

        screen5 = self.screens[4]
        screen5.refresh()
        move = pk.moves[self.moveIdx]
        movePositions = [(88, 153), (128, 153), (88, 168), (128, 168)]
        selectedContainer = pg.image.load("Images/Battle/Party displays/Move Display/Selected Container.png")
        otherContainer = pg.image.load("Images/Battle/Party displays/Move Display/Container.png")
        for idx in range(4):
            if idx == self.moveIdx:
                screen5.addImage(selectedContainer, movePositions[idx])
            else:
                screen5.addImage(otherContainer, movePositions[idx])

        screen5.loadImage(str.format("Images/Battle/Party displays/Move Display/{}.png", move.category.title()),
                          (9, 81))
        screen5.loadImage(str.format("Images/Type Labels/{} Label.png", move.type.title()), (110, 41))

        screen5.scaleSurface(15 / 8)

        screen5.addImage(pk.smallImage, (int(20 * 15 / 8), int(10 * 15 / 8)), location=BlitLocation.centre)
        screen5.addText2(pk.name, (int(50 * 15 / 8), int(12 * 15 / 8)), colour=Colours.white.value)

        screen5.addText2(move.name, (int(22 * 15 / 8), int(43 * 15 / 8)), colour=Colours.white.value)
        screen5.addText2("CATEGORY", (int(47 * 15 / 8), int(67 * 15 / 8)), colour=Colours.white.value,
                         location=BlitLocation.midTop)
        screen5.addText2("POWER", (int(9 * 15 / 8), int(107 * 15 / 8)), colour=Colours.white.value)
        screen5.addText2("ACCURACY", (int(9 * 15 / 8), int(131 * 15 / 8)), colour=Colours.white.value)
        screen5.addText2("PP", (int(154 * 15 / 8), int(43 * 15 / 8)), colour=Colours.white.value)
        screen5.addText2(move.category, (int(72 * 15 / 8), int(84 * 15 / 8)), location=BlitLocation.midTop)
        screen5.addText2(str.format("{}/{}", move.PP, move.maxPP), (int(184 * 15 / 8), int(43 * 15 / 8)),
                         colour=Colours.white.value)

        if move.power:
            screen5.addText2(str(move.power), (int(104 * 15 / 8), int(107 * 15 / 8)), location=BlitLocation.topRight)
        else:
            screen5.addText2("---", (int(104 * 15 / 8), int(107 * 15 / 8)), location=BlitLocation.topRight)

        if move.power:
            screen5.addText2(str(move.accuracy), (int(104 * 15 / 8), int(131 * 15 / 8)), location=BlitLocation.topRight)
        else:
            screen5.addText2("---", (int(104 * 15 / 8), int(131 * 15 / 8)), location=BlitLocation.topRight)

        if move.description:
            screen5.addText2(move.description, (int(130 * 15 / 8), int(67 * 15 / 8)), lines=5)

    def update(self, keys, controller, team):
        action = PartyAction.nothing

        selector = self.selectors[self.screenIdx]

        if keys[controller.down]:
            selector.moveDown()

        elif keys[controller.up]:
            selector.moveUp()

        elif keys[controller.left]:
            selector.moveLeft()

        elif keys[controller.right]:
            selector.moveRight()

        elif keys[controller.a]:
            [_, _, idx] = selector.getValues()
            if idx == selector.options - 1 or (self.screenIdx == 4 and idx == 2):
                if self.screenIdx == 0:
                    action = PartyAction.home
                else:
                    if self.screenIdx == 3:
                        self.screenIdx -= 1

                    self.screenIdx -= 1
            else:
                if self.screenIdx == 0:
                    if idx < self.teamSize:
                        self.screenIdx = 1
                        self.pokemonIdx = idx
                elif self.screenIdx == 1:
                    if idx == 0:
                        # swap pokemon
                        action = PartyAction(self.pokemonIdx)
                    if idx == 1:
                        self.screenIdx = 2
                    elif idx == 2:
                        self.screenIdx = 3

                    self.moveIdx = 0

                elif self.screenIdx == 2:
                    if idx == 0:
                        self.pokemonIdx = (self.pokemonIdx + 1) % len(team)
                        self.updateScreen(team)
                    elif idx == 1:
                        self.pokemonIdx = (self.pokemonIdx - 1) % len(team)

                    elif idx == 2:
                        self.screenIdx = ((self.screenIdx - 1) % 2) + 2
                        selector.reset()

                elif self.screenIdx == 3:
                    if idx < len(team[self.pokemonIdx].moves):
                        self.screenIdx = 4
                        self.moveIdx = idx
                    elif idx == 4:
                        self.pokemonIdx = (self.pokemonIdx + 1) % len(team)
                        self.updateScreen(team)
                    elif idx == 5:
                        self.pokemonIdx = (self.pokemonIdx - 1) % len(team)

                    elif idx == 6:
                        self.screenIdx = ((self.screenIdx - 1) % 2) + 2
                        selector.reset()

                elif self.screenIdx == 4:
                    if idx < len(team[self.pokemonIdx].moves):
                        self.moveIdx = idx

            self.updateScreen(team)

        elif keys[controller.b]:
            if self.screenIdx == 0:
                action = PartyAction.home
            else:
                self.screenIdx -= 1

        return action

    def set_default_view(self):
        self.screenIdx, self.pokemonIdx, self.moveIdx = 0, 0, 0

        for selector in self.selectors:
            selector.level = 0
            selector.position = pg.Vector2(0, 0)
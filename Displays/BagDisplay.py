from enum import Enum
from math import ceil, floor

import pygame as pg

from bag import Bag
from General.Colours import Colours
from General.Selector import Selector3
from screen import Screen, BlitLocation


class BagState(Enum):
    home = 0
    restore = 1
    pokeball = 2
    status = 3
    item = 4


class BagAction(Enum):
    nothing = 0
    home = 1
    item = 2


class BagDisplay:
    def __init__(self, bag: Bag, size=pg.Vector2(256, 192)):

        self.state = BagState.home

        self.homeScreen = [Screen(size)]

        HPRestoreItems = {}
        StatusItems = {}
        for item in bag.medicine:
            if item.battleType == "HP/PP":
                HPRestoreItems[item] = bag.medicine[item]
            elif item.battleType == "Status":
                StatusItems[item] = bag.medicine[item]

        if len(HPRestoreItems) > 0:
            self.restoreScreens = [Screen(size) for _ in range(ceil(len(HPRestoreItems) / 6))]
        else:
            self.restoreScreens = [Screen(size)]
        self.restoreIdx = 0

        if len(bag.pokeballs) > 0:
            self.pokeballScreens = [Screen(size) for _ in range(ceil(len(bag.pokeballs) / 6))]
        else:
            self.pokeballScreens = [Screen(size)]
        self.pokeballIdx = 0

        if len(StatusItems) > 0:
            self.statusScreens = [Screen(size) for _ in range(ceil(len(StatusItems) / 6))]
        else:
            self.statusScreens = [Screen(size)]
        self.statusIdx = 0

        if len(bag.items) > 0:
            self.itemScreens = [Screen(size) for _ in range(ceil(len(bag.items) / 6))]
        else:
            self.itemScreens = [Screen(size)]
        self.itemIdx = 0

        self.screenIndices = [self.restoreIdx, self.pokeballIdx, self.statusIdx, self.itemIdx]

        self.screens = [self.homeScreen, self.restoreScreens, self.pokeballScreens,
                        self.statusScreens, self.itemScreens]

        selectorImage = pg.image.load("Images/Medium Selector.png")
        cancelImage = pg.image.load("Images/Battle/Bag/Cancel Selector.png")

        self.positions = [(int(1 * 15 / 8), int(8 * 15 / 8)), (int(129 * 15 / 8), int(8 * 15 / 8)),
                          (int(1 * 15 / 8), int(56 * 15 / 8)), (int(129 * 15 / 8), int(56 * 15 / 8)),
                          (int(1 * 15 / 8), int(104 * 15 / 8)), (int(129 * 15 / 8), int(104 * 15 / 8)),
                          (int(1 * 15 / 8), int(152 * 15 / 8)), (int(41 * 15 / 8), int(152 * 15 / 8)),
                          (int(217 * 15 / 8), int(152 * 15 / 8))]

        sizes = [(ceil(126 * 15 / 8), ceil(47 * 15 / 8)), (ceil(126 * 15 / 8), ceil(47 * 15 / 8)),
                 (ceil(126 * 15 / 8), ceil(47 * 15 / 8)), (ceil(126 * 15 / 8), ceil(47 * 15 / 8)),
                 (ceil(126 * 15 / 8), ceil(47 * 15 / 8)), (ceil(126 * 15 / 8), ceil(47 * 15 / 8)),
                 (ceil(38 * 15 / 8), ceil(39 * 15 / 8)), (ceil(38 * 15 / 8), ceil(39 * 15 / 8)),
                 (ceil(38 * 15 / 8), ceil(39 * 15 / 8))]

        homePositions = [(int(1 * 15 / 8), int(8 * 15 / 8)), (int(129 * 15 / 8), int(8 * 15 / 8)),
                         (int(1 * 15 / 8), int(80 * 15 / 8)), (int(129 * 15 / 8), int(80 * 15 / 8)),
                         (int(1 * 15 / 8), int(152 * 15 / 8)), (int(217 * 15 / 8), int(152 * 15 / 8))]

        homeSizes = [(int(126 * 15 / 8), int(71 * 15 / 8)), (int(126 * 15 / 8), int(71 * 15 / 8)),
                     (int(126 * 15 / 8), int(71 * 15 / 8)), (int(126 * 15 / 8), int(71 * 15 / 8)),
                     (int(206 * 15 / 8), int(39 * 15 / 8)), (int(39 * 15 / 8), int(38 * 15 / 8))]

        self.homeSelector = \
            Selector3(shape=[pg.Vector2(2, 2), pg.Vector2(2, 1)],
                      blitPositions=homePositions, sizes=homeSizes,
                      imageType=[0, 0, 0, 0, 1, 2],
                      images=[selectorImage, selectorImage, cancelImage])

        self.restoreSelector = Selector3(shape=[pg.Vector2(2, 3), pg.Vector2(3, 1)],
                                         blitPositions=self.positions, sizes=sizes,
                                         imageType=[0, 0, 0, 0, 0, 0, 1, 1, 1],
                                         images=[selectorImage, cancelImage])

        self.pokeballSelector = Selector3(shape=[pg.Vector2(2, 3), pg.Vector2(3, 1)],
                                          blitPositions=self.positions, sizes=sizes,
                                          imageType=[0, 0, 0, 0, 0, 0, 1, 1, 1],
                                          images=[selectorImage, cancelImage])

        self.statusSelector = Selector3(shape=[pg.Vector2(2, 3), pg.Vector2(3, 1)],
                                        blitPositions=self.positions, sizes=sizes,
                                        imageType=[0, 0, 0, 0, 0, 0, 1, 1, 1],
                                        images=[selectorImage, cancelImage])

        self.itemSelector = Selector3(shape=[pg.Vector2(2, 3), pg.Vector2(3, 1)],
                                      blitPositions=self.positions, sizes=sizes,
                                      imageType=[0, 0, 0, 0, 0, 0, 1, 1, 1],
                                      images=[selectorImage, cancelImage])

        self.selectors = [self.homeSelector, self.restoreSelector, self.pokeballSelector,
                          self.statusSelector, self.itemSelector]

        # create home screen base
        for [idx, screens] in enumerate(self.screens):
            if idx == 0:
                screen = screens[0]
                screen: Screen
                screen.loadImage("Images/Battle/Bag/Home/Base.png", base=True)
                screen.scaleSurface(15 / 8)

            else:
                for screen in screens:
                    screen.loadImage(
                        "Images/Battle/Bag/Item Displays/Base.png", base=True)
                    screen.scaleSurface(15 / 8)

        for screen in self.restoreScreens:
            screen.addText2("HP/PP Restore", (int(126 * 15 / 8), int(170 * 15 / 8)), lines=3,
                            location=BlitLocation.centre,
                            colour=Colours.white.value, shadowColour=Colours.lightGrey.value, base=True)
        for screen in self.pokeballScreens:
            screen.addText2("Pokeballs", pg.Vector2(256, 324), location=BlitLocation.centre,
                            colour=Colours.white.value, shadowColour=Colours.lightGrey.value, base=True)
        for screen in self.statusScreens:
            screen.addText2("Status Healers", pg.Vector2(256, 324), lines=3, location=BlitLocation.centre,
                            colour=Colours.white.value, shadowColour=Colours.lightGrey.value, base=True)
        for screen in self.itemScreens:
            screen.addText2("Battle Items", pg.Vector2(256, 324), lines=3, location=BlitLocation.centre,
                            colour=Colours.white.value, shadowColour=Colours.lightGrey.value, base=True)

        self.updateScreens(bag)

    def loadItem(self, item, num, count, screen):
        imageOffset = pg.Vector2(int(36 * 15 / 8), int(34 * 15 / 8))
        nameOffset = pg.Vector2(int(63 * 15 / 8), int(11 * 15 / 8))
        amountOffset = pg.Vector2(int(65 * 15 / 8), int(28 * 15 / 8))
        screen.addImage(item.image, self.positions[count % 6] + imageOffset,
                        scale=pg.Vector2(1.8, 1.8), location=BlitLocation.centre)
        screen.addText2(item.name, self.positions[count % 6] + nameOffset,
                        location=BlitLocation.midTop, colour=Colours.white.value)
        screen.addText2(str.format("x{}", num), self.positions[count % 6] + amountOffset,
                        colour=Colours.white.value)

    def loadItemContainer(self, count, screen, type="Empty"):
        positions = [(1, 8), (129, 8), (1, 56), (129, 56), (1, 104), (129, 104)]
        if type == "Empty":
            offset = pg.Vector2(0, 2)
        else:
            offset = pg.Vector2(0, 0)
        screen.loadImage(str.format("Images/Battle/Bag/Item Displays/{} Container.png", type),
                         pos=pg.Vector2(positions[count % 6]) + offset)

    def updateScreens(self, bag):
        for screens in self.screens:
            for screen in screens:
                screen.refresh()

        homeScreen = self.screens[0][0]
        homeScreen.loadImage("Images/Battle/Bag/Home/Empty Container.png", (1, 154))
        homeScreen.scaleSurface(15 / 8)
        homeScreen.addText2("HP/PP Restore", (int(66 * 15 / 8), int(42 * 15 / 8)), location=BlitLocation.midTop,
                            lines=3, colour=Colours.white.value)
        homeScreen.addText2("POKE BALLS", (int(193 * 15 / 8), int(42 * 15 / 8)), location=BlitLocation.midTop,
                            lines=3, colour=Colours.white.value)
        homeScreen.addText2("STATUS HEALERS", (int(66 * 15 / 8), int(114 * 15 / 8)),
                            location=BlitLocation.midTop,
                            lines=3, colour=Colours.white.value)
        self.screens[0][0].addText2("BATTLE ITEMS", (int(193 * 15 / 8), int(114 * 15 / 8)),
                                    location=BlitLocation.midTop,
                                    lines=3, colour=Colours.white.value)

        HPRestoreItems = {}
        StatusItems = {}
        for item in bag.medicine:
            if item.battleType == "HP/PP":
                HPRestoreItems[item] = bag.medicine[item]
            elif item.battleType == "Status":
                StatusItems[item] = bag.medicine[item]

        for idx in range(len(self.restoreScreens) * 6):
            if idx < len(HPRestoreItems):
                screenIdx = floor(idx / 6)
                self.loadItemContainer(idx, self.restoreScreens[screenIdx], "Restore")
            else:
                screenIdx = floor(idx / 6)
                self.loadItemContainer(idx, self.restoreScreens[screenIdx])

        for idx in range(len(self.pokeballScreens) * 6):
            if idx < len(bag.pokeballs):
                screenIdx = floor(idx / 6)
                self.loadItemContainer(idx, self.pokeballScreens[screenIdx], "Pokeball")
            else:
                screenIdx = floor(idx / 6)
                self.loadItemContainer(idx, self.pokeballScreens[screenIdx])

        for idx in range(len(self.statusScreens) * 6):
            if idx < len(StatusItems):
                screenIdx = floor(idx / 6)
                self.loadItemContainer(idx, self.statusScreens[screenIdx], "Status")
            else:
                screenIdx = floor(idx / 6)
                self.loadItemContainer(idx, self.statusScreens[screenIdx])

        for idx, screens in enumerate(self.screens):
            if idx != 0:
                for screen in screens:
                    if len(screens) > 1:
                        screen.loadImage("Images/Battle/Bag/Item Displays/Up.png", (1, 152))
                        screen.loadImage("Images/Battle/Bag/Item Displays/Down.png", (41, 152))
                    else:
                        screen.loadImage("Images/Battle/Bag/Item Displays/Empty Up.png", (1, 152))
                        screen.loadImage("Images/Battle/Bag/Item Displays/Empty Down.png", (41, 152))
                    screen.scaleSurface(15 / 8)

            if idx == 1:
                for screen in screens:
                    screen.addText2("HP/PP Restore", (int(126 * 15 / 8), int(172 * 15 / 8)), lines=3,
                                    location=BlitLocation.centre, colour=Colours.white.value,
                                    shadowColour=Colours.lightGrey.value)
            elif idx == 2:
                for screen in screens:
                    screen.addText2("Pokeballs", (int(126 * 15 / 8), int(172 * 15 / 8)), lines=3,
                                    location=BlitLocation.centre, colour=Colours.white.value,
                                    shadowColour=Colours.lightGrey.value)
            elif idx == 3:
                for screen in screens:
                    screen.addText2("Status Healers", (int(126 * 15 / 8), int(172 * 15 / 8)), lines=3,
                                    location=BlitLocation.centre, colour=Colours.white.value,
                                    shadowColour=Colours.lightGrey.value)
            elif idx == 4:
                for screen in screens:
                    screen.addText2("Battle Items", (int(126 * 15 / 8), int(172 * 15 / 8)), lines=3,
                                    location=BlitLocation.centre, colour=Colours.white.value,
                                    shadowColour=Colours.lightGrey.value)

        for idx, item in enumerate(HPRestoreItems):
            screenIdx = floor(idx / 6)
            self.loadItem(item, HPRestoreItems[item], idx, self.restoreScreens[screenIdx])

        for idx, item in enumerate(bag.pokeballs):
            screenIdx = floor(idx / 6)
            self.loadItem(item, bag.pokeballs[item], idx, self.pokeballScreens[screenIdx])

        for idx, item in enumerate(StatusItems):
            screenIdx = floor(idx / 6)
            self.loadItem(item, StatusItems[item], idx, self.statusScreens[screenIdx])

    def getSurface(self):
        selector = self.selectors[self.state.value]
        [image, pos, _] = selector.getValues()
        surface = self.getScreen().getSurface(image, pos)
        return surface

    def getScreen(self):
        if self.state == BagState.home:
            return self.homeScreen[0]
        else:
            return self.screens[self.state.value][self.screenIndices[self.state.value - 1]]

    def update(self, keys, controller):
        action = BagAction.nothing
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
            # 6 up 7 down
            if idx == len(selector.blitPositions) - 1:
                if self.state == BagState.home:
                    action = BagAction.home
                self.state = BagState.home
                selector.reset()

            elif idx == 6:
                if self.screenIndices[self.state.value - 1] > 0:
                    self.screenIndices[self.state.value - 1] -= 1
            elif idx == 7:
                if self.screenIndices[self.state.value - 1] < len(self.screens[self.state.value]) - 1:
                    self.screenIndices[self.state.value - 1] += 1

            elif self.state == BagState.home:
                if idx == 4:
                    print("Last used item")
                elif BagState(idx + 1) == BagState.pokeball:
                    self.state = BagState.pokeball
                elif BagState(idx + 1) == BagState.restore:
                    self.state = BagState.restore
                elif BagState(idx + 1) == BagState.status:
                    self.state = BagState.status
                elif BagState(idx + 1) == BagState.item:
                    self.state = BagState.item

            elif self.state != BagState.home:
                action = BagAction.item

        elif keys[controller.b]:
            if self.state == BagState.home:
                action = BagAction.home
            else:
                self.state = BagState.home

        return action

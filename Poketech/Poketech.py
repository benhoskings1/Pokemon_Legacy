import datetime
from enum import Enum

import pygame as pg

from font.Font import ClockFont
from screen import Screen, BlitLocation

largeClockFont = ClockFont(1.85)
smallClockFont = ClockFont(0.8)


class State(Enum):
    clock = 0
    pedometer = 1


class Poketech:
    def __init__(self, time, size=pg.Vector2(256, 192)):
        self.state = State.clock

        self.time = time

        self.baseDisplay = Screen(size)
        self.baseDisplay.loadImage("Poketech/Images/Poketech Base.png", fill=True, base=True)
        self.clockDisplay = Screen(pg.Vector2(192, 160))
        self.clockDisplay.loadImage("Poketech/Images/Clock Base.png", fill=True, base=True)
        self.pedometerDisplay = Screen(pg.Vector2(192, 160))
        self.pedometerDisplay.loadImage("Poketech/Images/Pedometer Base.png", fill=True, base=True)

        self.pedometerSteps = 0
        self.pedometerReset = pg.Rect((int(66 * 15 / 8), int(81 * 15 / 8)), (int(66 * 15 / 8), int(58 * 15 / 8)))
        self.pedometerReset.topleft += pg.Vector2(int(16 * 15 / 8), int(16 * 15 / 8))

        self.updateClock(self.time)
        self.updatePedometer()
        self.baseDisplay.refresh()

        self.buttonRect = pg.Rect((434, 159), (66, 169))

    def updateClock(self, time):
        self.time = time
        self.clockDisplay.refresh()
        self.clockDisplay.scaleSurface(15 / 8)
        surf = largeClockFont.renderText(self.time.strftime("%H:%M"))
        self.clockDisplay.addImage(surf, pos=(int(4 * 15 / 8), int(36 * 15 / 8)))

    def updatePedometer(self):
        self.pedometerDisplay.refresh()
        self.pedometerDisplay.scaleSurface(15 / 8)
        surf = smallClockFont.renderText(str(self.pedometerSteps))
        self.pedometerDisplay.addImage(surf, pos=(int(96 * 15 / 8), int(48 * 15 / 8)), location=BlitLocation.centre)

    def getSurface(self):
        self.baseDisplay.refresh()
        self.baseDisplay.scaleSurface(15 / 8)
        if self.state == State.clock:
            if self.time.minute != datetime.datetime.now().minute:
                self.updateClock(datetime.datetime.now())
            self.baseDisplay.addImage(self.clockDisplay.surface, pos=(int(16 * 15 / 8), int(16 * 15 / 8)))

        elif self.state == State.pedometer:
            self.baseDisplay.addImage(self.pedometerDisplay.surface, pos=(int(16 * 15 / 8), int(16 * 15 / 8)))

        return self.baseDisplay.surface

    def interact(self, mousePos):
        if self.buttonRect.collidepoint(pg.Vector2(mousePos) - pg.Vector2(0, 354)):
            if self.state.value < len(State) - 1:
                self.state = State(self.state.value + 1)
            else:
                self.state = State(0)

        elif self.state == State.pedometer:
            if self.pedometerReset.collidepoint(pg.Vector2(mousePos) - pg.Vector2(0, 354)):
                self.pedometerSteps = 0
                self.updatePedometer()

    def clearSurfaces(self):
        self.baseDisplay = None
        self.pedometerDisplay = None
        self.clockDisplay = None

    def loadSurfaces(self, time):
        self.baseDisplay = Screen(pg.Vector2(256, 192))
        self.baseDisplay.loadImage("Poketech/Images/Poketech Base.png", base=True)
        self.clockDisplay = Screen(pg.Vector2(192, 160))
        self.clockDisplay.loadImage("Poketech/Images/Clock Base.png", base=True)
        self.pedometerDisplay = Screen(pg.Vector2(192, 160))
        self.pedometerDisplay.loadImage("Poketech/Images/Pedometer Base.png", base=True)

        self.updateClock(time)
        self.updatePedometer()
        self.baseDisplay.refresh()



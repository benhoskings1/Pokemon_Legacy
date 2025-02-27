from math import ceil

import pygame as pg

from General.Colours import Colours
from General.Environment import Environment
from pokemon import Pokemon
from screen import Screen, BlitLocation, FontOption


class BattleDisplay:
    def __init__(self, size, time, environment: Environment):

        self.screen = Screen(size, colour=Colours.black.value)
        self.screen2 = Screen((256, 192), colour=Colours.black.value)
        self.screen2.loadImage(str.format("Images/Battle/Backgrounds/{} {}.png", time.value, environment.value),
                               base=True)

        basePath = str.format("Images/Battle/Backgrounds/{0} {1}", time.value, environment.value)

        self.screen2.loadImage("Images/Battle/Top Screen/Text box.png", pg.Vector2(3, 146), base=True)

        self.text = ""

        self.screen.refresh()
        self.screen2.refresh()

    def getSurface(self):
        return self.screen2.surface

    def updateScreen(self, fPk: Pokemon, wPk: Pokemon, lines=None, opacity=None, friendly=False):

        self.screen2.refresh()

        if opacity:
            offset = 120 * (1 - (opacity / 255))
        else:
            offset = 0

        # add pokemon names, level, hp,
        if wPk.visible:
            self.screen2.loadImage("Images/Battle/Top Screen/Opponent HP.png",
                                   pg.Vector2(0 - offset * (not friendly), 21))

            wildRatio = (wPk.health / wPk.stats.health)
            # 50
            if wPk.health > 0:
                wRect = pg.Rect(50, 41, 48 * wildRatio, 4)
                if wPk.health >= wPk.stats.health * 0.5:
                    wColour = "High"
                elif wPk.health >= wPk.stats.health * 0.25:
                    wColour = "Medium"
                else:
                    wColour = "Low"
            else:
                wRect = pg.Rect(0, 0, 0, 0)
                wColour = "Low"

            # Draw the health bar on the screen
            self.screen2.loadImage(str.format("Images/Battle/Other/Health {}.png", wColour),
                                   wRect.topleft, size=wRect.size)

        if fPk.visible:
            self.screen2.loadImage("Images/Battle/Top Screen/Friendly HP.png", pg.Vector2(256 + offset * friendly, 97),
                                   location=BlitLocation.topRight)
            fRatio = (fPk.health / fPk.stats.health)
            if fPk.health > 0:
                fRect = pg.Rect(198, 117, 48 * fRatio, 4)
                if fPk.health >= fPk.stats.health * 0.5:
                    fColour = "High"
                elif fPk.health >= fPk.stats.health * 0.25:
                    fColour = "Medium"
                else:
                    fColour = "Low"
            else:
                fRect = pg.Rect(0, 0, 0, 0)
                fColour = "Low"

            # Draw the health bar on the screen
            self.screen2.loadImage(str.format("Images/Battle/Other/Health {}.png", fColour),
                                   fRect.topleft, size=fRect.size)

        self.screen2.scaleSurface(15 / 8)

        # Display options for the wild Pokémon
        if wPk.visible:
            # add the name of the Pokémon

            self.screen2.addText2(wPk.name, pg.Vector2(int((4 - offset * (not friendly)) * 15 / 8), int(27 * 15 / 8)))

            # add the level of the Pokémon
            wildLevel = str.format("Lv{}", wPk.level)
            self.screen2.addText2(wildLevel, pg.Vector2(int((90 - offset * (not friendly)) * 15 / 8), int(29 * 15 / 8)),
                                  location=BlitLocation.topRight, fontOption=FontOption.level)

            # if the Pokémon has any status conditions, add display them
            if wPk.status:
                self.screen2.loadImage(str.format("Images/Status Labels/{}.png", wPk.status.name),
                                       pg.Vector2(int((10 - offset * (not friendly)) * 15 / 8), int(62 * 15 / 8)),
                                       scale=pg.Vector2(2, 2))

            # finally add the image of the Pokémon
            if opacity and not friendly:
                wPk.image.set_alpha(opacity)

            self.screen2.addImage(wPk.displayImage, pg.Vector2(int(192 * 15 / 8), int(90 * 15 / 8)),
                                  location=BlitLocation.midBottom)

        # Display options for the friendly Pokémon
        if fPk.visible:
            # add the name of the Pokémon
            self.screen2.addText2(fPk.name, pg.Vector2(int((152 - offset * friendly) * 15 / 8), int(103 * 15 / 8)))

            # add the level of the Pokémon
            friendlyLevel = str.format("Lv{}", fPk.level)
            self.screen2.addText2(friendlyLevel, pg.Vector2(int((221 - offset * friendly) * 15 / 8), int(105 * 15 / 8)),
                                  fontOption=FontOption.level)

            # if the Pokémon has any status conditions, add display them
            if fPk.status:
                self.screen2.loadImage(str.format("Images/Status Labels/{}.png", fPk.status.name),
                                       pg.Vector2(int((152 - offset * friendly) * 15 / 8), int(103 * 15 / 8)))

            # add the text showing the Pokémon's health
            if fPk.health > 0:
                health = fPk.health
            else:
                health = 0

            self.screen2.addText2(str.format("{0}/{1}", round(health), fPk.stats.health),
                                  pg.Vector2(int((246 - offset * friendly) * 15 / 8), int(125 * 15 / 8)),
                                  location=BlitLocation.topRight,
                                  fontOption=FontOption.level)

            # finally add the image of the Pokémon
            if opacity and friendly:
                fPk.image.set_alpha(opacity)
            self.screen2.addImage(fPk.displayImage,
                                  pg.Vector2(int((66 - offset * friendly) * 15 / 8), int(144 * 15 / 8)),
                                  location=BlitLocation.midBottom)

        if self.text:
            if lines:
                self.screen2.addText2(self.text, pg.Vector2(int(16 * 15 / 8), int(156 * 15 / 8)), lines=lines)
            else:
                self.screen2.addText2(self.text, pg.Vector2(int(16 * 15 / 8), int(156 * 15 / 8)),
                                      lines=ceil(len(self.text) / 28))

    def clearSurfaces(self):
        self.screen.clearSurfaces()
        self.screen2.clearSurfaces()

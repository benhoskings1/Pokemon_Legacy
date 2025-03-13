import os
from enum import Enum
from math import floor

import numpy as np
import pygame as pg

letterSurfaces = {}


class Baseline(Enum):
    centre = 0
    lower = 1


def colourChange(surface, baseColours, shadowColours=None):

    pixels = pg.surfarray.pixels3d(surface)

    for layer in range(3):
        array = np.array(pixels[:, :, layer])
        for row in range(pixels.shape[0]):
            for col in range(pixels.shape[1]):
                value = array[row, col]
                if value == baseColours[0][layer]:
                    pixels[row, col, layer] = baseColours[1][layer]

                if shadowColours:
                    if value == shadowColours[0][layer]:
                        pixels[row, col, layer] = shadowColours[1][layer]

    newImage = pg.surfarray.make_surface(pixels)
    newImage.set_colorkey(pg.Color(0, 0, 0))
    return newImage


class Font:
    def __init__(self, scale):
        self.scale = scale

        self.space = 1 * scale

        self.letters = {}
        self.sizes = {}

        names = sorted(os.listdir("font/Letter Images"))

        for name in names:
            letter = name[0]
            if "Upper" in name:
                letter = str.upper(letter)
            elif "slash" in name:
                letter = "/"

            if name.endswith(".png"):
                image = pg.image.load(str.format("font/Letter Images/{}", name))
                newImage = pg.transform.scale(image, pg.Vector2(image.get_size()) * scale)
                self.sizes[letter] = newImage.get_size()
                self.letters[letter] = newImage

        self.baselines = {"0": Baseline.centre, "1": Baseline.centre,
                          "2": Baseline.centre, "3": Baseline.centre,
                          "4": Baseline.centre, "5": Baseline.centre,
                          "6": Baseline.centre, "7": Baseline.centre,
                          "8": Baseline.centre, "9": Baseline.centre,
                          "a": Baseline.centre, "A": Baseline.centre,
                          "b": Baseline.centre, "B": Baseline.centre,
                          "c": Baseline.centre, "C": Baseline.centre,
                          "d": Baseline.centre, "D": Baseline.centre,
                          "e": Baseline.centre, "E": Baseline.centre,
                          "f": Baseline.centre, "F": Baseline.centre,
                          "g": Baseline.lower, "G": Baseline.centre,
                          "h": Baseline.centre, "H": Baseline.centre,
                          "i": Baseline.centre, "I": Baseline.centre,
                          "j": Baseline.lower, "J": Baseline.centre,
                          "k": Baseline.centre, "K": Baseline.centre,
                          "l": Baseline.centre, "L": Baseline.centre,
                          "m": Baseline.centre, "M": Baseline.centre,
                          "n": Baseline.centre, "N": Baseline.centre,
                          "o": Baseline.centre, "O": Baseline.centre,
                          "p": Baseline.lower, "P": Baseline.centre,
                          "q": Baseline.lower, "Q": Baseline.centre,
                          "r": Baseline.centre, "R": Baseline.centre,
                          "s": Baseline.centre, "S": Baseline.centre,
                          "t": Baseline.centre, "T": Baseline.centre,
                          "u": Baseline.centre, "U": Baseline.centre,
                          "v": Baseline.centre, "V": Baseline.centre,
                          "w": Baseline.centre, "W": Baseline.centre,
                          "x": Baseline.centre, "X": Baseline.centre,
                          "y": Baseline.lower, "Y": Baseline.centre,
                          "z": Baseline.centre, "Z": Baseline.centre,
                          "?": Baseline.centre, "!": Baseline.centre,
                          "/": Baseline.centre, "-": Baseline.centre,
                          ".": Baseline.centre, "'": Baseline.centre,
                          "(": Baseline.centre, ")": Baseline.centre,
                          "+": Baseline.centre}

        self.size = 10

    def renderText(self, text: str, lineCount=1, colour=None, shadowColour=None):
        words = text.split(" ")
        lines = []
        totalLetters = len("".join(words))
        letters = 0

        for idx, word in enumerate(words):
            lines.append(floor(letters / (totalLetters / lineCount)))
            letters += len(word)

        surfaces = []

        for line in range(lineCount):
            lineWords = []
            for idx, word in enumerate(words):
                if lines[idx] == line:
                    lineWords.append(word)

            lineText = " ".join(lineWords)

            width = 0
            height = 0
            lowerBase = False
            for letter in lineText:
                if letter == " ":
                    width += 3 * self.space
                else:

                    width += self.sizes[letter][0]
                    if self.sizes[letter][1] > height and self.baselines[letter] != Baseline.lower:
                        height = self.sizes[letter][1]

                    if self.baselines[letter] == Baseline.lower:
                        lowerBase = True

            if lowerBase:
                height += 2 * self.scale

            width += self.space * (len(lineText) - 1)

            if width < 0:
                width = 0

            surf = pg.Surface((width, height), pg.SRCALPHA)
            surfSize = pg.Vector2(surf.get_size())

            offset = 0
            for letter in lineText:
                if letter == " ":
                    offset += 3 * self.space
                else:
                    if self.baselines[letter] == Baseline.centre:
                        surf.blit(self.letters[letter], (offset, surfSize.y - self.sizes[letter][1] - 2 * self.scale * lowerBase))
                        offset += self.sizes[letter][0] + self.space
                    else:
                        surf.blit(self.letters[letter], (offset, surfSize.y - self.sizes[letter][1]))
                        offset += self.sizes[letter][0] + self.space

            surfaces.append(surf)

        totalSize = pg.Vector2(0, 0)
        for surface in surfaces:
            size = pg.Vector2(surface.get_size())
            if size.x > totalSize.x:
                totalSize.x = size.x

            totalSize.y += size.y + (lineCount - 1) * self.scale

        textSurf = pg.Surface(totalSize, pg.SRCALPHA)

        heightOffset = 0
        for surface in surfaces:
            textSurf.blit(surface, (0, heightOffset))
            heightOffset += surface.get_size()[1] + 2 * self.scale

        if colour:
            textColours = [pg.Color(16, 24, 32), colour]
            if shadowColour:
                shadowColours = [pg.Color(168, 184, 184), shadowColour]
                textSurf = colourChange(textSurf, textColours, shadowColours=shadowColours)
            else:
                textSurf = colourChange(textSurf, textColours)

        return textSurf


class LevelFont:
    def __init__(self, scale):
        self.scale = scale

        self.space = 0

        self.letters = {}
        self.sizes = {}

        names = sorted(os.listdir("font/Level"))

        for name in names:

            letter = name[0]
            if "slash" in name:
                letter = "/"

            image = pg.image.load(str.format("font/Level/{}", name))
            newImage = pg.transform.scale(image, pg.Vector2(image.get_size()) * scale)
            self.sizes[letter] = newImage.get_size()
            self.letters[letter] = newImage

    def renderText(self, text: str, lineCount, colour=None, shadowColour=None):

        width = 0

        for letter in text:
            if letter == " ":
                width += 3 * self.space
            else:

                width += self.sizes[letter][0]

        height = self.sizes["0"][1]
        width += self.space * (len(text) - 1)

        if width < 0:
            width = 0

        surf = pg.Surface((width, height), pg.SRCALPHA)
        surfSize = pg.Vector2(surf.get_size())

        offset = 0
        for letter in text:
            if letter == " ":
                offset += 3 * self.space
            else:
                surf.blit(self.letters[letter], (offset, surfSize.y - self.sizes[letter][1]))
                offset += self.sizes[letter][0] + self.space

        if colour:
            textColours = [pg.Color(16, 24, 32), colour]
            if shadowColour:
                shadowColours = [pg.Color(168, 184, 184), shadowColour]
                textSurf = colourChange(surf, textColours, shadowColours=shadowColours)
            else:
                textSurf = colourChange(surf, textColours)

        return surf


class ClockFont:
    def __init__(self, scale):
        self.scale = scale

        self.space = 1 * scale

        self.letters = {}
        self.sizes = {}

        names = sorted(os.listdir("font/Clock"))

        for name in names:
            letter = name[0]

            if "Colon" in name:
                letter = ":"

            if name.endswith(".png"):
                image = pg.image.load(str.format("font/Clock/{}", name))
                newImage = pg.transform.scale(image, pg.Vector2(image.get_size()) * scale)
                self.sizes[letter] = newImage.get_size()
                self.letters[letter] = newImage

    def renderText(self, text: str):
        size = pg.Vector2(0, 0)
        size.y = self.sizes["0"][1]
        for letter in text:
            size.x += self.sizes[letter][0]

        textSurf = pg.Surface(size, pg.SRCALPHA)

        offset = pg.Vector2(0, 0)
        for letter in text:
            textSurf.blit(self.letters[letter], pg.Vector2(0, 0) + offset)
            offset.x += self.sizes[letter][0]

        return textSurf

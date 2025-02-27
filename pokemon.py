import datetime
import pickle
from enum import Enum
from math import floor
from random import randint, choice, random

import cv2
import pandas as pd
import pygame as pg

from General.Animations import Animations, createAnimation
from General.Move import getMove
from Image_Processing.ImageEditor import ImageEditor

with open("Game Data/Pokedex/LocalDex/LocalDex.pickle", 'rb') as file:
    pokedex: pd.DataFrame = pickle.load(file)
    print("Successfully loaded from pickle")

oldPokedex = pd.read_csv("Game Data/Pokedex/Local Dex.tsv", delimiter='\t', index_col=1)
attributes = pd.read_csv("Game Data/Pokedex/AttributeDex.tsv", delimiter='\t', index_col=1)
effectiveness = pd.read_csv("Game Data/Effectiveness.csv", index_col=0)
levelUpValues = pd.read_csv("Game Data/Level Up.tsv", delimiter='\t')
natures = pd.read_csv("Game Data/Natures.tsv", delimiter='\t', index_col=0)

capWildMoves = True


stageMultipliers = {-6: 2 / 8, -5: 2 / 7, -4: 2 / 6, -3: 2 / 5, -2: 2 / 4, -1: 2 / 3,
                    0: 1, 1: 3 / 2, 2: 4 / 2, 3: 5 / 2, 4: 6 / 2, 5: 7 / 2, 6: 8 / 2}
otherMultipliers = {-6: 33 / 100, -5: 36 / 100, -4: 43 / 100, -3: 50 / 100, -2: 60 / 100, -1: 75 / 100,
                    1: 133 / 100, 2: 166 / 100, 3: 200 / 100, 4: 250 / 100, 5: 266 / 100, 6: 300 / 100}
critChance = {0: 1 / 16, 1: 1 / 8, 2: 1 / 4, 3: 1 / 3, 4: 1 / 2}

allSprites = cv2.imread("Sprites/Pokemon/Gen_IV_Sprites.png", cv2.IMREAD_UNCHANGED)
smallSprites = cv2.imread("Sprites/Pokemon/Gen_IV_Small_Sprites.png", cv2.IMREAD_UNCHANGED)
editor = ImageEditor()


def getImages(ID, shiny=False):
    gridWidth = 5
    perRow = 32
    pos = pg.Vector2((ID - 1) % (perRow / 2), floor((ID - 1) / (perRow / 2)))

    topleft = pg.Vector2(pos.x * (80 + gridWidth) * 2 + gridWidth, pos.y * (80 + gridWidth) * 2 + gridWidth)
    frontRect = pg.Rect(topleft, (80, 80))
    backRect = frontRect.copy()
    backRect.topleft += pg.Vector2(80 + gridWidth, 0)
    frontShinyRect = frontRect.copy()
    frontShinyRect.topleft += pg.Vector2(0, 80 + gridWidth)
    backShinyRect = frontRect.copy()
    backShinyRect.topleft += pg.Vector2(85, 80 + gridWidth)

    perRow = 16
    pos = pg.Vector2((ID - 1) % perRow, floor((ID - 1) / perRow))
    topLeftSmall = pg.Vector2(pos.x * (32 + gridWidth) + gridWidth, pos.y * (32 + gridWidth) + gridWidth)
    smallRect = pg.Rect(topLeftSmall, (32, 32))

    if not shiny:
        frontData = allSprites[frontRect.top:frontRect.bottom, frontRect.left:frontRect.right, :]
        backData = allSprites[backRect.top:backRect.bottom, backRect.left:backRect.right, :]
    else:
        frontData = allSprites[frontShinyRect.top:frontShinyRect.bottom,
                               frontShinyRect.left:frontShinyRect.right, :]
        backData = allSprites[backShinyRect.top:backShinyRect.bottom,
                              backShinyRect.left:backShinyRect.right, :]

    smallData = smallSprites[smallRect.top:smallRect.bottom,
                             smallRect.left:smallRect.right, :]

    editor.loadData(frontData)
    editor.cropImage(overwrite=True)
    editor.scaleImage((2, 2), overwrite=True)
    frontImage = editor.createSurface()

    editor.loadData(backData)
    editor.cropImage(overwrite=True)
    editor.scaleImage((2, 2), overwrite=True)
    backImage = editor.createSurface()

    editor.loadData(smallData)
    smallScale = 3
    editor.scaleImage((smallScale, smallScale), overwrite=True)
    smallImage = editor.createSurface()

    return frontImage, backImage, smallImage


class StatusEffect(Enum):
    Burned = "Burned"
    Frozen = "Frozen"
    Paralysed = "Paralysed"
    Poisoned = "Poisoned"
    Sleeping = "Sleeping"
    Confusion = "Confusion"


class Stats:
    def __init__(self, health=0, attack=0, defence=0, spAttack=0, spDefence=0, speed=0, exp=0):
        self.health = health
        self.attack = attack
        self.defence = defence
        self.spAttack = spAttack
        self.spDefence = spDefence
        self.speed = speed
        self.exp = exp

    def display(self):
        print(self.health, self.attack, self.defence, self.spAttack, self.spDefence, self.speed)


class StatStages:
    def __init__(self, attack=0, defence=0, spAttack=0, spDefence=0, speed=0, accuracy=0, evasion=0):
        self.attack = attack
        self.defence = defence
        self.spAttack = spAttack
        self.spDefence = spDefence
        self.speed = speed
        self.accuracy = accuracy
        self.evasion = evasion

    def display(self):
        print(self.attack, self.defence, self.spAttack, self.spDefence, self.speed)


class Pokemon:
    def __init__(self, Name, Level=None, XP=None, Move_Names=None, Move_PPs=None, Health=None, Status=None,
                 EVs=None, IVs=None, Gender=None, Nature=None, Ability=None, KO=False, Stat_Stages=None,
                 Friendly=False, Shiny=None, Visible=True, Catch_Location=None, Catch_Level=None,
                 Catch_Date=None):

        data = pokedex.loc[Name]
        oldData = oldPokedex.loc[Name]

        self.name = Name
        self.ID = data.Local_Num
        self.growthRate = data.Growth_Rate
        self.catchRate = data.Catch_Rate
        self.EVYield = data.EV_Yield
        self.moveData = data.Learnset

        if type(data.Type) == str:
            self.type1 = data.Type
            self.type2 = None
        else:
            # will be in as a tuple
            self.type1 = data.Type[0]
            self.type2 = data.Type[1]

        if XP is None:
            XP = int(levelUpValues.loc[Level - 1, self.growthRate])
        if Level is None:
            Level = randint(1, 10)

        self.level, self.exp = Level, XP

        self.evolveLevel = oldData.Evolve_Level

        if Move_Names is None:
            Move_Names = []
            possibleMoves = []
            for name, level in self.moveData:
                if capWildMoves:
                    if level <= self.level:
                        possibleMoves.append(name)

                else:
                    possibleMoves.append(name)

                if len(possibleMoves) < 4:
                    moveCount = len(possibleMoves)
                else:
                    moveCount = 4

                for _ in range(moveCount):
                    move = choice(possibleMoves)
                    Move_Names.append(move)
                    possibleMoves.remove(move)

        self.moveNames = Move_Names
        self.moves = []

        for moveName in Move_Names:
            move = getMove(moveName)
            self.moves.append(move)

        if EVs is None:
            EVs = [0 for _ in range(6)]
        if IVs is None:
            IVs = [randint(0, 31) for _ in range(6)]
            if sum(IVs) >= 140:
                print("strong pokemon")

        self.EVs, self.IVs = EVs, IVs
        self.stats = Stats(exp=data.Base_Exp)
        self.updateStats()

        if Health:
            self.health = Health
        else:
            self.health = self.stats.health

        self.friendly = Friendly

        if Gender:
            self.gender = Gender
        else:
            genders = data.Gender
            num = random() * 100
            if num < genders[0]:
                self.gender = "Male"
            else:
                self.gender = "Female"

        if Ability:
            self.ability = Ability
        else:
            abilities = data.Abilities[:len(data.Abilities)]
            self.ability = choice(abilities)

        if Nature:
            self.nature = Nature
        else:
            self.nature = natures.loc[randint(0, 24)].Name

        if Shiny:
            self.shiny = Shiny
        else:
            num = randint(0, 4095)
            if num == 0:
                self.shiny = True
            else:
                self.shiny = False

        front, back, small = getImages(self.ID, self.shiny)

        if Friendly:
            self.image = back
        else:
            self.image = front

        self.smallImage = small

        self.animation = None

        self.displayImage = self.image

        if Move_PPs:
            for idx, move in enumerate(self.moves):
                if Move_PPs[idx]:
                    move.PP = Move_PPs[idx]
                else:
                    move.PP = move.maxPP

        # in battle stats
        self.visible = Visible

        if Stat_Stages:
            self.statStages = StatStages(**Stat_Stages)
        else:
            self.statStages = StatStages()

        if Status:
            self.status = StatusEffect(Status)
        else:
            self.status = None

        self.KO = KO

        self.item = None

        self.catchLocation = Catch_Location
        self.catchLevel = Catch_Level
        if Catch_Date:
            year, month, day = Catch_Date.split("-")
            self.catchDate = datetime.date(int(year), int(month), int(day))
        else:
            self.catchDate = None

        # loading for the first time from the start team
        if self.friendly and (not Catch_Date and not Catch_Location and not Catch_Level):
            self.catchLocation = None
            self.catchLevel = self.level
            self.catchDate = datetime.datetime.now()

    def loadAnimation(self):
        animations = createAnimation(self.name)

        if self.shiny:
            self.animation = animations.frontShiny
        else:
            self.animation = animations.front

    def getMoveDamage(self, move, target, ignoreModifiers=False):

        if move.category == "Physical":
            if move.power:
                if ignoreModifiers:
                    if target.statStages.defence >= 0:
                        #  ignore the targets positive stat stages
                        effectiveDefence = target.stats.defence
                    else:
                        effectiveDefence = target.stats.defence * stageMultipliers[target.statStages.defence]

                    if self.statStages.attack <= 0:
                        #  ignore the attackers negative stat stages
                        effectiveAttack = self.stats.attack
                    else:
                        effectiveAttack = self.stats.attack * stageMultipliers[self.statStages.attack]
                else:
                    effectiveDefence = target.stats.defence * stageMultipliers[target.statStages.defence]
                    effectiveAttack = self.stats.attack * stageMultipliers[self.statStages.attack]

                damage = floor(((2 * self.level / 5) + 2) * move.power *
                               effectiveAttack / effectiveDefence) / 50

            else:
                damage = 0

        elif move.category == "Special":
            if move.power:
                if ignoreModifiers:
                    if target.statStages.spDefence >= 0:
                        #  ignore the targets positive stat stages
                        effectiveDefence = target.stats.spDefence
                    else:
                        effectiveDefence = target.stats.spDefence * stageMultipliers[target.stats.spDefence]

                    if self.statStages.spAttack <= 0:
                        #  ignore the attackers negative stat stages
                        effectiveAttack = self.stats.spAttack
                    else:
                        effectiveAttack = self.stats.spAttack * stageMultipliers[self.statStages.spAttack]
                else:
                    effectiveDefence = target.stats.spDefence * stageMultipliers[target.statStages.spDefence]
                    effectiveAttack = self.stats.spAttack * stageMultipliers[self.statStages.spAttack]

                damage = floor(floor(floor(2 * self.level / 5) + 2) * move.power *
                               floor(effectiveAttack / effectiveDefence)) / 50
            else:
                damage = 0

        else:
            damage = 0

        return damage

    def useMove(self, move, target):
        critStage = 0

        if move.effect:
            inflictCondition, modify, hits, heal = move.effect.getEffect()

        else:
            inflictCondition = None
            modify = None
            hits = 1
            heal = 0

        num = randint(0, 99) / 100
        if num < critChance[critStage]:
            crit = True
            critical = 2
        else:
            crit = False
            critical = 1

        baseDamage = self.getMoveDamage(move, target, crit)

        if self.status == StatusEffect.Burned and move.type == "Physical":
            burn = 0.5
        else:
            burn = 1

        screen, targets, weather, FF = 1, 1, 1, 1

        damage = baseDamage * burn * screen * targets * weather * FF + 2

        item, first = 1, 1

        rand = randint(85, 100) / 100

        if move.type == self.type1 or move.type == self.type2:
            STAB = 1.5
        else:
            STAB = 1

        type1 = effectiveness.loc[str.upper(move.type), target.type1]

        if target.type2:
            type2 = effectiveness.loc[str.upper(move.type), target.type2]
        else:
            type2 = 1

        SRF, EB, TL, Berry = 1, 1, 1, 1

        damage = damage * critical * item * first * rand * STAB * type1 * type2 * SRF * EB * TL * Berry

        move.PP -= 1

        damage = floor(damage)

        if move.category == "Status":
            damage = 0

        # the move will consist of the following properties:
        # -> damage     -> effective
        return damage, type1 * type2, inflictCondition, heal, modify, hits, crit

    def updateEVs(self, name):
        data = pokedex.loc[name]
        EVYield = data.EV_Yield
        for [idx, value] in enumerate(EVYield):
            self.EVs[idx] += value

    def getMoves(self):
        moveNames = "["
        for move in self.moves:
            moveNames += str.format("{}, ", move.name)

        moveNames = moveNames[0:len(moveNames) - 2] + "]"

        return moveNames

    def getFaintXP(self):
        a, e, f, L, Lp, p, s, t, v = 1, 1, 1, 1, 1, 1, 1, 1, 1

        b = self.stats.exp
        L = self.level

        exp = (a * t * b * e * L * p * f * v) / (7 * s)
        return exp

    def updateStats(self):
        data = pokedex.loc[self.name]
        stats = data.Stats

        baseHP, baseAttack, baseDefence = stats[0], stats[1], stats[2]
        baseSpAttack, baseSpDefence, baseSpeed = stats[3], stats[4], stats[5]

        maxHealth = \
            floor((2 * baseHP + self.EVs[0] + floor(self.EVs[0] / 4)) * self.level / 100 + self.level + 10)
        attack = \
            floor(floor((2 * baseAttack + self.EVs[1] + floor(self.EVs[1] / 4)) * self.level / 100 + 5) * 1)
        defence = \
            floor(floor((2 * baseDefence + self.EVs[2] + floor(self.EVs[2] / 4)) * self.level / 100 + 5) * 1)
        spAttack = \
            floor(floor((2 * baseSpAttack + self.EVs[3] + floor(self.EVs[3] / 4)) * self.level / 100 + 5) * 1)
        spDefence = \
            floor(floor((2 * baseSpDefence + self.EVs[4] + floor(self.EVs[4] / 4)) * self.level / 100 + 5) * 1)
        speed = \
            floor(floor((2 * baseSpeed + self.EVs[5] + floor(self.EVs[5] / 4)) * self.level / 100 + 5) * 1)

        self.stats = Stats(maxHealth, attack, defence, spAttack, spDefence, speed, self.stats.exp)

    def checkLevelUp(self):
        level = 99
        levelUp = False
        moves = []
        for idx in range(99, 0, -1):
            if self.exp < levelUpValues.loc[idx, self.growthRate]:
                level = idx

        if self.level != level:
            levelUp = True

        for levelVal in range(self.level + 1, level + 1):
            for name, learnLevel in self.moveData:
                if levelVal == learnLevel:
                    move = getMove(name)
                    moves.append(move)

        if not moves:
            moves = None

        return [levelUp, level - self.level, moves]

    def switchImage(self, direction="back"):
        front, back, small = getImages(self.ID, self.shiny)

        if direction == "back":
            self.image = back
        else:
            self.image = front

    def addMove(self, moveName, pos=None):
        move = getMove(moveName)
        if not pos:
            self.moves.append(move)
        else:
            self.moves[pos] = move

    def getEvolution(self):
        return oldPokedex[oldPokedex["ID"] == self.ID + 1].index[0]

    def clearImages(self):
        self.image = None
        self.animation = None
        self.displayImage = None
        self.smallImage = None

    def loadImages(self, animations: Animations):
        front, back, small = getImages(self.ID, self.shiny)
        if self.friendly:
            self.image = back
        else:
            self.image = front

        self.smallImage = small
        self.animation = animations.front
        self.displayImage = self.image

    def resetStatStages(self):
        self.statStages = StatStages()

    def restore(self):
        self.health = self.stats.health
        self.status = None

        for move in self.moves:
            move.PP = move.maxPP

    def getJSONData(self):
        movePPs = [move.PP for move in self.moves]
        if self.status:
            status = self.status.value
        else:
            status = None

        if self.friendly:
            self.visible = True

        data = {"Name": self.name, "Level": self.level, "XP": self.exp,
                "Move_Names": self.moveNames, "Move_PPs": movePPs, "Health": self.health,
                "Status": status, "EVs": self.EVs, "IVs": self.IVs,
                "Gender": self.gender, "Nature": self.nature, "Ability": self.ability,
                "KO": self.KO, "Stat_Stages": self.statStages.__dict__,
                "Friendly": self.friendly, "Shiny": self.shiny, "Visible": self.visible,
                "Catch_Date": self.catchDate.strftime("%Y-%m-%d"),
                "Catch_Location": self.catchLocation,
                "Catch_Level": self.catchLevel}

        return data

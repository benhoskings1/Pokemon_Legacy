import random
from enum import Enum

import pandas as pd

movesData = pd.read_csv("game_data/Moves.tsv", delimiter='\t', index_col=0)


class EffectType(Enum):
    stat = "Stat"
    heal = "Heal"
    condition = "Condition"
    multiple = "Multiple"


def getMove(name):
    moveData = movesData.loc[name]

    if not pd.isna(moveData.Effect):
        effect = moveData.Effect[1: len(moveData.Effect) - 1].split(", ")
        moveEffect = MoveEffect(effect)
        move = Move2(name, moveData.Type, moveData.Cat, moveData.Power,
                     moveData.Acc, moveData.PP, moveData.Description, moveEffect)
    else:
        move = Move2(name, moveData.Type, moveData.Cat, moveData.Power,
                     moveData.Acc, moveData.PP, moveData.Description)

    return move


class Move2:
    def __init__(self, name, moveType, category, power, accuracy, PP, description, effect=None):
        self.name = name
        self.type = moveType.title()
        self.category = category
        self.maxPP = int(PP)
        self.PP = int(PP)

        if power != "-":
            self.power = int(power)
        else:
            self.power = None

        if accuracy != "-":
            self.accuracy = int(accuracy)
        else:
            self.accuracy = None

        if pd.isna(description):
            self.description = None
        else:
            self.description = description

        self.effect = effect

    def __str__(self):
        return f"{self.name}: {self.type} {self.category} {self.power} {self.accuracy}"

    def __repr__(self):
        return f"Move({self.name},{self.type},{self.category},{self.power},{self.accuracy})"


class MoveEffect:
    def __init__(self, effect):
        self.effect = effect

        if effect[0] == "Condition":
            self.condition = True
        else:
            self.condition = False

        if effect[0] == "Stat":
            self.modify = True
        else:
            self.modify = False

        if effect[0] == "Multiple":
            self.multipleHits = True
        else:
            self.multipleHits = False

        if effect[0] == "Heal":
            self.heal = True
        else:
            self.heal = False

        self.duration = 1

    def getEffect(self):
        if self.condition:
            num = random.randint(0, 99)
            if num < int(self.effect[2]) - 1:
                inflictCondition = self.effect[1]
            else:
                inflictCondition = None
        else:
            inflictCondition = None

        if self.modify:
            num = random.randint(0, 99)
            if num < int(self.effect[1]) - 1:
                modify = [int(self.effect[2]), self.effect[3], self.effect[4], self.effect[5]]
            else:
                modify = None
        else:
            modify = None

        if self.multipleHits:
            hits = random.randint(int(self.effect[1]), int(self.effect[2]))
        else:
            hits = 1

        if self.heal:
            heal = int(self.effect[1])
        else:
            heal = 0

        return inflictCondition, modify, hits, heal

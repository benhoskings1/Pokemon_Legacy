from enum import Enum


class BattleActionType(Enum):
    attack = "attack",
    catch = "catch",
    heal = "heal",
    switch = "switch"

    
from enum import Enum


class BattleActionType(Enum):
    attack = "attack",
    catch = "catch",
    heal = "heal",
    switch = "switch"


class BattleAction:
    def __init__(self, action_type: BattleActionType,):
        self.action_type = action_type

        self.animation = None


    
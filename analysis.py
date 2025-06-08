import datetime
import enum
import os

import numpy as np
import pygame as pg

from pokemon import Pokemon
from team import Team

root = "."

pyLines = {}
jsonSizes = {}
lines = 0
for path, subdirs, files in os.walk(root):
    for filename in files:
        if not path.startswith("./venv"):
            if filename.endswith(".py"):
                with open(os.path.join(path, filename)) as f:
                    count = sum(1 for _ in f)
                    lines += count
                pyLines[os.path.join(path, filename)] = count

            elif filename.endswith(".json"):
                size = os.stat(os.path.join(path, filename)).st_size
                jsonSizes[os.path.join(path, filename)] = size


def is_builtin_class_instance(obj):
    return obj.__class__.__module__ == 'builtins'


def isBaseObj(obj):
    base = False
    if is_builtin_class_instance(obj) and type(obj) != dict:
        base = True

    elif type(obj) in [pg.Vector2, pg.surface.Surface, pg.Rect, pg.Color, np.ndarray]:
        # print("Pygame variable")
        base = True

    elif type(obj) == datetime.datetime:
        base = True

    elif type(obj) == Pokemon or type(obj) == Team:
        # print("Pokemon", base)
        pass

    try:
        if enum.Enum in obj.__mro__:
            # print("Enum variable")
            base = True

    except AttributeError:
        pass

    return base


def isLowestTier(obj):
    idx = 0
    try:
        for idx, var in enumerate([getattr(obj, var) for var in vars(obj).keys()]):
            if not isBaseObj(var):
                return False, var, list(vars(obj).keys())[idx], idx

        return True, None, None, None

    except TypeError:
        print("Something went wrong, probably the use of a dictionary")
        return True, None, None, idx


class ObjInfo:
    def __init__(self, obj, name):
        self.name = name
        self.obj = obj
        try:
            self.varNames = list(vars(obj).keys())
            self.variables = [getattr(obj, var) for var in self.varNames]
            self.baseVariables = []
            self.lowest = False

        except TypeError:
            self.varNames = ""
            self.variables = obj
            self.baseVariables = [obj]
            self.lowest = True

    def checkLowest(self):
        if not self.lowest:
            self.lowest, *other = isLowestTier(self.obj)

        return self.lowest


def getLowestObj(obj, name):
    attributes = {}
    lowest = False
    tier = 0
    names = [name]
    objects = [obj]
    while not lowest:
        lowest, var, name, idx = isLowestTier(obj)
        if not lowest:
            tier += 1
            names.append(name)
            obj = var
            objects.append(obj)

    for name in list(vars(objects[len(objects) - tier - 1]).keys()):
        variables = {}
        var = getattr(objects[len(objects) - tier - 1], name)
        if not isBaseObj(var):
            for varName in list(vars(var).keys()):
                attributes[name] = {}
                variables1 = {}
                variable = getattr(var, varName)
                if type(variable) == dict:
                    for key, value in variable.items():
                        variables1[key] = str(type(value).__name__)
                else:
                    variables1 = str(type(variable).__name__)

                variables[varName] = variables1

            attributes[name] = variables
        else:
            attributes[name] = str(type(var).__name__)

    return attributes, names, obj, tier


def tierObject(obj, name):
    baseObj = obj
    tiers = {0: [(name, obj, None)]}
    tier = 0

    while not checkLowestTier(tiers[tier]):
        for idx, (name, obj, pointer) in enumerate(tiers[tier]):
            if not isBaseObj(obj):
                print(name)
                if type(obj) == dict:
                    obj: dict
                    var = {}
                    if tier + 1 not in tiers.keys():
                        for key, value in obj.items():
                            tiers[tier + 1] = [(key, value, idx)]
                    else:
                        for key, value in obj.items():
                            tiers[tier + 1] .append((key, value, idx))

                else:
                    for name in list(vars(obj).keys()):
                        var = getattr(obj, name)
                        if tier + 1 not in tiers.keys():
                            tiers[tier + 1] = [(name, var, idx)]
                        else:
                            tiers[tier + 1].append((name, var, idx))
        tier += 1

    return tiers


def jsonTier(obj, name):
    jsonObject = {}
    tiers = tierObject(obj, name)
    convertToJson2(tiers)
    for (idx, tier) in tiers.items():
        jsonObject[idx] = convertToJson(tier)

    return jsonObject


def checkLowestTier(tier):
    lowest = True
    for (name, obj, pointer) in tier:
        if not isBaseObj(obj):
            lowest = False

    return lowest


def convertToJson(tier):
    tierString = []
    for (name, obj, pointer) in tier:
        tierString.append((name, str(type(obj).__name__), pointer))

    return tierString


def convertToJson2(tiers):
    tierIndices = list(tiers.keys())
    tierIndices.sort(reverse=True)
    print(tierIndices)
    allObjects = []
    for tierIdx in tierIndices:
        tier = tiers[tierIdx]
        tierObjects = {}
        for (name, obj, pointer) in tier:
            if tierIdx != 0:
                pointerName = tiers[tierIdx - 1][pointer][0]
                if pointer not in tierObjects.keys():
                    tierObjects[pointer] = {name: type(obj)}
                else:
                    tierObjects[pointer][name] = type(pointerName)

        allObjects.append(tierObjects)

    jsonObject = {}
    print(allObjects)


# game = Game(1.5, from_pickle=True)
# data = jsonTier(game.player, "player")
#
# with open("Analysis.json", "w") as write_file:
#     json.dump(data, write_file, indent=4)
print(pyLines)
print(lines)


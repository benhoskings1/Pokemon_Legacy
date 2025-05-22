from enum import Enum
from PIL import Image

import pickle
import pandas as pd
import numpy as np
import pygame as pg

from Image_Processing.ImageEditor import ImageEditor

editor = ImageEditor()


with open("game_data/Pokedex/LocalDex/LocalDex.pickle", 'rb') as file:
    pokedex: pd.DataFrame = pickle.load(file)
    print("Successfully loaded from pickle")


def create_display_bar(val: float, max_val: float, bar_type: str) -> pg.Surface:
    """
    This function creates the display bar used for health and exp displays within the game screen.

    :param val: current value of health/exp
    :param max_val: maximum value of health/exp
    :param bar_type: health or exp
    :return: pygame surface that is coloured and truncated relative to the maximum value
    """
    ratio = val / max_val

    if bar_type == "HP":
        if ratio > 0.5:
            colour = "high"
        elif ratio > 0.25:
            colour = "medium"
        else:
            colour = "low"
        bar_surf = pg.image.load(f"assets/battle/main_display/health_bar/health_{colour}.png")
    else:
        bar_surf = pg.image.load("assets/battle/touch_display/pokemon/exp_bar.png")

    bar_size = pg.Vector2(bar_surf.get_size())

    return pg.transform.scale(bar_surf, pg.Vector2(bar_size.x * ratio, bar_size.y))


def load_gif(gif_path: str, bit_mask=None, opacity=255, scale=1) -> list[pg.Surface]:
    """
    This function loads a gif and returns a list of pygame surfaces.
    :param gif_path: path of the gif file
    :return: animation representing the frames of the gif
    """
    frames = []
    gif_image = Image.open(gif_path)
    for frame in range(gif_image.n_frames):
        gif_image.seek(frame)
        img = gif_image.copy()
        if scale != 1:
            img = img.resize((int(img.size[0] * scale), int(img.size[1] * scale)))

        image_data = np.asarray(img.convert("RGBA")).copy()
        if bit_mask is not None:
            image_data = image_data[:bit_mask.shape[0], :bit_mask.shape[1]]
            image_data[:, :, 3] = bit_mask

        editor.loadData(image_data)
        surf = editor.createSurface(bgr=False)
        if opacity != 255:
            surf.set_alpha(opacity)

        frames.append(surf)

    return frames


class Colours(Enum):
    clear = pg.SRCALPHA
    white = pg.Color(255, 255, 255)
    black = pg.Color(1, 1, 1)
    darkGrey = pg.Color(60, 60, 60)
    lightGrey = pg.Color(200, 200, 200)
    green = pg.Color(100, 255, 100)
    red = pg.Color(255, 100, 100)
    shadow = pg.Color(180, 180, 180)

# def load_pokemon_json(name):
#     data = pokedex.loc[name]
#
#     pokemon_data = {
#         "id": data.Local_Num, "name": data.name, "growth_rate": data.Growth_Rate,
#         "catch_rate": data.Catch_Rate, "ev_yield": data.EV_Yield, "learnset": data.Learnset
#     }
#
#     if isinstance(data.Type, tuple):
#         pokemon_data["type_1"] = data.Type[0]
#         pokemon_data["type_2"] = data.Type[1]
#     else:
#         pokemon_data["type_1"] = data.Type
#         pokemon_data["type_2"] = None
#
#
#     if XP is None:
#         XP = int(levelUpValues.loc[Level - 1, self.growthRate])
#     # if Level is None:
#     #     Level = randint(1, 10)
#     #
#     # self.level, self.exp = Level, XP
#     #
#     # self.evolveLevel = oldData.Evolve_Level
#     #
#     # if Move_Names is None:
#     #     Move_Names = []
#     #     possibleMoves = []
#     #     for name, level in self.moveData:
#     #         if capWildMoves:
#     #             if level <= self.level:
#     #                 possibleMoves.append(name)
#     #
#     #         else:
#     #             possibleMoves.append(name)
#     #
#     #         if len(possibleMoves) < 4:
#     #             moveCount = len(possibleMoves)
#     #         else:
#     #             moveCount = 4
#     #
#     #         for _ in range(moveCount):
#     #             move = choice(possibleMoves)
#     #             Move_Names.append(move)
#     #             possibleMoves.remove(move)
#     #
#     # self.moveNames = Move_Names
#     # self.moves = []
#     #
#     # for moveName in Move_Names:
#     #     move = getMove(moveName)
#     #     self.moves.append(move)
#     #
#     # if EVs is None:
#     #     EVs = [0 for _ in range(6)]
#     # if IVs is None:
#     #     IVs = [randint(0, 31) for _ in range(6)]
#     #     if sum(IVs) >= 140:
#     #         print("strong pokemon")
#     #
#     # self.EVs, self.IVs = EVs, IVs
#     # self.stats = Stats(exp=data.Base_Exp)
#     # self.updateStats()
#     #
#     # if Health:
#     #     self.health = Health
#     # else:
#     #     self.health = self.stats.health
#     #
#     # self.friendly = Friendly
#     #
#     # if Gender:
#     #     self.gender = Gender
#     # else:
#     #     genders = data.Gender
#     #     num = random() * 100
#     #     if num < genders[0]:
#     #         self.gender = "Male"
#     #     else:
#     #         self.gender = "Female"
#     #
#     # if Ability:
#     #     self.ability = Ability
#     # else:
#     #     abilities.tsv = data.Abilities[:len(data.Abilities)]
#     #     self.ability = choice(abilities.tsv)
#     #
#     # if Nature:
#     #     self.nature = Nature
#     # else:
#     #     self.nature = natures.loc[randint(0, 24)].Name
#     #
#     # if Shiny:
#     #     self.shiny = Shiny
#     # else:
#     #     num = randint(0, 4095)
#     #     if num == 0:
#     #         self.shiny = True
#     #     else:
#     #         self.shiny = False
#     #
#     # front, back, small = getImages(self.ID, self.shiny)
#     #
#     # if Friendly:
#     #     self.image = back
#     # else:
#     #     self.image = front
#     #
#     # self.smallImage = small
#     #
#     # self.animation = None
#     #
#     # self.displayImage = self.image
#     #
#     # if Move_PPs:
#     #     for idx, move in enumerate(self.moves):
#     #         if Move_PPs[idx]:
#     #             move.PP = Move_PPs[idx]
#     #         else:
#     #             move.PP = move.maxPP
#     #
#     # if Stat_Stages:
#     #     self.statStages = StatStages(**Stat_Stages)
#     # else:
#     #     self.statStages = StatStages()
#     #
#     # if Status:
#     #     self.status = StatusEffect(Status)
#     # else:
#     #     self.status = None
#     #
#     # self.KO = KO
#     #
#     # self.item = None
#     #
#     # self.catchLocation = Catch_Location
#     # self.catchLevel = Catch_Level
#     # if Catch_Date:
#     #     year, month, day = Catch_Date.split("-")
#     #     self.catchDate = datetime.date(int(year), int(month), int(day))
#     # else:
#     #     self.catchDate = None
#     #
#     # # loading for the first time from the start team
#     # if self.friendly and (not Catch_Date and not Catch_Location and not Catch_Level):
#     #     self.catchLocation = None
#     #     self.catchLevel = self.level
#     #     self.catchDate = datetime.datetime.now()
import pickle
import pandas as pd


with open("game_data/Pokedex/LocalDex/LocalDex.pickle", 'rb') as file:
    pokedex: pd.DataFrame = pickle.load(file)
    print("Successfully loaded from pickle")


def load_pokemon_json(name):
    data = pokedex.loc[name]

    pokemon_data = {
        "id": data.Local_Num, "name": data.name, "growth_rate": data.Growth_Rate,
        "catch_rate": data.Catch_Rate, "ev_yield": data.EV_Yield, "learnset": data.Learnset
    }

    if isinstance(data.Type, tuple):
        pokemon_data["type_1"] = data.Type[0]
        pokemon_data["type_2"] = data.Type[1]
    else:
        pokemon_data["type_1"] = data.Type
        pokemon_data["type_2"] = None


    if XP is None:
        XP = int(levelUpValues.loc[Level - 1, self.growthRate])
    # if Level is None:
    #     Level = randint(1, 10)
    #
    # self.level, self.exp = Level, XP
    #
    # self.evolveLevel = oldData.Evolve_Level
    #
    # if Move_Names is None:
    #     Move_Names = []
    #     possibleMoves = []
    #     for name, level in self.moveData:
    #         if capWildMoves:
    #             if level <= self.level:
    #                 possibleMoves.append(name)
    #
    #         else:
    #             possibleMoves.append(name)
    #
    #         if len(possibleMoves) < 4:
    #             moveCount = len(possibleMoves)
    #         else:
    #             moveCount = 4
    #
    #         for _ in range(moveCount):
    #             move = choice(possibleMoves)
    #             Move_Names.append(move)
    #             possibleMoves.remove(move)
    #
    # self.moveNames = Move_Names
    # self.moves = []
    #
    # for moveName in Move_Names:
    #     move = getMove(moveName)
    #     self.moves.append(move)
    #
    # if EVs is None:
    #     EVs = [0 for _ in range(6)]
    # if IVs is None:
    #     IVs = [randint(0, 31) for _ in range(6)]
    #     if sum(IVs) >= 140:
    #         print("strong pokemon")
    #
    # self.EVs, self.IVs = EVs, IVs
    # self.stats = Stats(exp=data.Base_Exp)
    # self.updateStats()
    #
    # if Health:
    #     self.health = Health
    # else:
    #     self.health = self.stats.health
    #
    # self.friendly = Friendly
    #
    # if Gender:
    #     self.gender = Gender
    # else:
    #     genders = data.Gender
    #     num = random() * 100
    #     if num < genders[0]:
    #         self.gender = "Male"
    #     else:
    #         self.gender = "Female"
    #
    # if Ability:
    #     self.ability = Ability
    # else:
    #     abilities.tsv = data.Abilities[:len(data.Abilities)]
    #     self.ability = choice(abilities.tsv)
    #
    # if Nature:
    #     self.nature = Nature
    # else:
    #     self.nature = natures.loc[randint(0, 24)].Name
    #
    # if Shiny:
    #     self.shiny = Shiny
    # else:
    #     num = randint(0, 4095)
    #     if num == 0:
    #         self.shiny = True
    #     else:
    #         self.shiny = False
    #
    # front, back, small = getImages(self.ID, self.shiny)
    #
    # if Friendly:
    #     self.image = back
    # else:
    #     self.image = front
    #
    # self.smallImage = small
    #
    # self.animation = None
    #
    # self.displayImage = self.image
    #
    # if Move_PPs:
    #     for idx, move in enumerate(self.moves):
    #         if Move_PPs[idx]:
    #             move.PP = Move_PPs[idx]
    #         else:
    #             move.PP = move.maxPP
    #
    # if Stat_Stages:
    #     self.statStages = StatStages(**Stat_Stages)
    # else:
    #     self.statStages = StatStages()
    #
    # if Status:
    #     self.status = StatusEffect(Status)
    # else:
    #     self.status = None
    #
    # self.KO = KO
    #
    # self.item = None
    #
    # self.catchLocation = Catch_Location
    # self.catchLevel = Catch_Level
    # if Catch_Date:
    #     year, month, day = Catch_Date.split("-")
    #     self.catchDate = datetime.date(int(year), int(month), int(day))
    # else:
    #     self.catchDate = None
    #
    # # loading for the first time from the start team
    # if self.friendly and (not Catch_Date and not Catch_Location and not Catch_Level):
    #     self.catchLocation = None
    #     self.catchLevel = self.level
    #     self.catchDate = datetime.datetime.now()
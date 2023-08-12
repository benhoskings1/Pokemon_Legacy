import pandas as pd
import pygame as pg

prices = pd.read_csv("Game Data/Item Prices.tsv", delimiter="\t", index_col=0)
pokeballs = pd.read_csv("Game Data/Items/Pokeballs.tsv", delimiter="\t", index_col=0)
medicine = pd.read_csv("Game Data/Items/Medicine.tsv", delimiter="\t", index_col=0)


class Item:
    def __init__(self, name, type, description=""):
        data = prices.loc[name]
        self.name = name
        self.type = type
        self.image = pg.image.load(str.format("Sprites/Items/{}/{}.png", self.type, name))

        if pd.isna(data.Buy_Price):
            self.buyPrice = None
        else:
            self.buyPrice = data.Buy_Price

        if pd.isna(data.Sell_Price):
            self.sellPrice = None
        else:
            self.sellPrice = data.Sell_Price

        self.description = description

    def display(self):
        print(vars(self))


class Pokeball(Item):
    def __init__(self, name):
        data = pokeballs.loc[name]
        if pd.isna(data.Description):
            super().__init__(name, type="Pokeball")
        else:
            super().__init__(name, type="Pokeball", description=data.Description)

        self.modifier = data.Rate_Modifier

        if pd.isna(data.Conditions):
            self.conditions = None
        else:
            self.conditions = data.Conditions


class MedicineItem(Item):
    def __init__(self, name):
        data = medicine.loc[name]
        if pd.isna(data.Description):
            super().__init__(name, type="Medicine")
        else:
            super().__init__(name, type="Medicine", description=data.Description)

        if pd.isna(data.Heal_Amount):
            self.heal = False
        else:
            self.heal = data.Heal_Amount

        if pd.isna(data.Status):
            self.status = None
        else:
            self.status = data.Status

        if pd.isna(data.Battle_Type):
            self.battleType = None
        else:
            self.battleType = data.Battle_Type

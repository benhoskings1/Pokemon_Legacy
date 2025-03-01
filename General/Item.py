import pandas as pd
import pygame as pg

item_data = pd.read_csv("game_data/items.tsv", delimiter="\t", index_col=0)
pokeballs = pd.read_csv("game_data/Items/pokeballs.tsv", delimiter="\t", index_col=0)
medicine = pd.read_csv("game_data/Items/medicine.tsv", delimiter="\t", index_col=0)

item_data = item_data.merge(medicine, on="item_id", how="left").merge(pokeballs, on="item_id", how="left")


class Item:
    def __init__(self, data, type, description=""):
        self.name = data["name"]
        self.type = type
        self.image = pg.image.load(str.format("Sprites/Items/{}/{}.png", self.type, data["name"]))

        if pd.isna(data.buy_price):
            self.buyPrice = None
        else:
            self.buyPrice = data.buy_price

        if pd.isna(data.sell_price):
            self.sellPrice = None
        else:
            self.sellPrice = data.sell_price

        self.description = description

    def display(self):
        print(vars(self))


class Pokeball(Item):
    def __init__(self, name):
        data = item_data.loc[item_data["name"] == name].iloc[0]
        if pd.isna(data.description):
            super().__init__(data, type="Pokeball")
        else:
            super().__init__(data, type="Pokeball", description=data.description)

        self.modifier = data.Rate_Modifier

        if pd.isna(data.Conditions):
            self.conditions = None
        else:
            self.conditions = data.Conditions


class MedicineItem(Item):
    def __init__(self, name):
        data = item_data.loc[item_data["name"] == name].iloc[0]
        if pd.isna(data.description):
            super().__init__(data, type="Medicine")
        else:
            super().__init__(data, type="Medicine", description=data.description)

        if pd.isna(data.heal_amount):
            self.heal = False
        else:
            self.heal = data.heal_amount

        if pd.isna(data.status):
            self.status = None
        else:
            self.status = data.status

        if pd.isna(data.battle_type):
            self.battle_type = None
        else:
            self.battle_type = data.battle_type

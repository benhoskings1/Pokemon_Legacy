import pandas as pd

from General.Item import Item, Pokeball, MedicineItem

pokeballs = pd.read_csv("Game Data/Items/Pokeballs.tsv", delimiter="\t", index_col=0)


class Bag:
    def __init__(self, Items, Medicine, Pokeballs, TMs, Berries, Battle_Items, Key_Items):

        self.items = {}
        for name in Items:
            item = Item(name=name, type="Item")
            self.items[item] = Items[name]

        self.medicine = {}
        for name in Medicine:
            item = MedicineItem(name=name)
            self.medicine[item] = Medicine[name]

        self.pokeballs = {}
        for name in Pokeballs:
            item = Pokeball(name=name)
            self.pokeballs[item] = Pokeballs[name]

        self.TMs = {}
        self.berries = {}
        self.battleItems = {}
        self.keyItems = {}

    def clearSurfaces(self):
        for (item, count) in self.medicine:
            item.clearSurfaces()

        for (item, count) in self.pokeballs:
            item.clearSurfaces()

    def loadSurfaces(self):
        for (item, count) in self.medicine:
            item.loadSurfaces()

        for (item, count) in self.pokeballs:
            item.loadSurfaces()

    def getJSONData(self):
        itemData = {}
        for item in self.items:
            itemData[item.name] = self.items[item]

        pokeballData = {}
        for pokeball in self.pokeballs:
            pokeballData[pokeball.name] = self.pokeballs[pokeball]

        medicineData = {}
        for medicine in self.medicine:
            medicineData[medicine.name] = self.medicine[medicine]

        TMData = {}
        berryData = {}
        battleItemData = {}
        keyItemData = {}

        data = {"Items": itemData, "Pokeballs": pokeballData,
                "Medicine": medicineData, "TMs": TMData,
                "Berries": berryData, "Battle_Items": battleItemData,
                "Key_Items": keyItemData}

        return data

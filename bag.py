import os
import json
import time

import pandas as pd
import pygame as pg

from general.Item import Item, Pokeball, MedicineItem

# Used for visualisation
from general.Controller import Controller
from displays.bag_display import BagDisplay, BagAction, BagState
from battle import Battle

pokeballs = pd.read_csv("game_data/Items/pokeballs.tsv", delimiter="\t", index_col=0)


class Bag:
    def __init__(self, Items, Medicine, Pokeballs, TMs, Berries,
                 Battle_Items, Key_Items, display_size=pg.Vector2(480, 360)):

        self.items = {}
        for name in Items:
            item = Item(name=name, type="Item")
            self.items[item] = Items[name]

        self.medicine = {}
        for name in Medicine:
            item = MedicineItem(name=name)
            self.medicine[item] = Medicine[name]

        self.hp_restore_items = {item: self.medicine[item] for item in self.medicine if item.battle_type == "HP/PP"}
        self.status_restore_items = {item: self.medicine[item] for item in self.medicine if item.battle_type == "Status"}

        self.pokeballs = {}
        for name in Pokeballs:
            item = Pokeball(name=name)
            self.pokeballs[item] = Pokeballs[name]

        self.TMs = {}
        self.berries = {}
        self.battleItems = {}
        self.keyItems = {}

        self.display = BagDisplay(self, size=display_size)

        self.running = False

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

    def get_json_data(self):
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

    def select_item(self, battle: Battle = None):
        screen = self.display.screenIndices[self.display.state.value - 1]
        [_, _, pos] = self.display.selectors[self.display.state.value].getValues()

        idx = pos + screen * 6

        if self.display.state in (BagState.restore, BagState.status):
            if self.display.state == BagState.restore:
                items = self.hp_restore_items
            else:
                items = self.status_restore_items

            # ensure that the selected box has an associated item
            if idx > len(items):
                return None

            item, count = list(items.items())[idx]
            if item.heal and battle.friendly.health != battle.friendly.stats.health:
                self.medicine[item] -= 1
                if self.medicine[item] == 0:
                    self.medicine.pop(item)
                return item

            elif item.heal:
                battle.displayMessage("It won't have any effect", 1500)
                battle.battleDisplay.text = str.format("What will {} do?", battle.friendly.name)
                print("no effect - current health is full")
                return None

            if item.status and battle.friendly.status:
                if item.status == battle.friendly.status.value:
                    # self.useItem(item)
                    self.medicine[item] -= 1
                    if self.medicine[item] == 0:
                        self.medicine.pop(item)
                else:
                    battle.displayMessage("It won't have any effect", 1500)
                    battle.battleDisplay.text = str.format("What will {} do?", battle.friendly.name)
                    return None

            elif item.status:
                battle.displayMessage("It won't have any effect", 1500)
                battle.battleDisplay.text = str.format("What will {} do?", battle.friendly.name)
                return None

            battle.battleDisplay.text = str.format("What will {} do?", battle.friendly.name)
            return None

        elif self.display.state == BagState.pokeball:
            if idx >= len(self.pokeballs):
                return None

            item, count = list(self.pokeballs.items())[idx]
            self.pokeballs[item] -= 1
            if self.pokeballs[item] == 0:
                self.pokeballs.pop(item)

            return item

    def loop(self, surface, controller, battle=None):
        self.running = True

        t1 = time.monotonic()
        while self.running:
            keys = pg.key.get_pressed()

            action = self.display.update(keys, controller)

            if action != BagAction.nothing:
                print(action)
                if action == BagAction.home:
                    self.running = False
                    return BagAction.home, None
                elif action == BagAction.item:
                    item = self.select_item(battle)
                    if item:
                        print(item.name)
                        self.running = False
                        return BagAction.item, item

            surface.blit(self.display.getSurface(), (0, 0))
            pg.display.flip()

            for event in pg.event.get():
                if event.type == pg.QUIT:
                    self.running = False
                    print("Quit")

            while time.monotonic() - t1 < 0.1:
                pass

            t1 = time.monotonic()


if __name__ == "__main__":
    # pygame setup
    pg.init()
    window = pg.display.set_mode(pg.Vector2(240, 180) * 2)

    # test data set up
    cont = Controller()

    with open("test_data/bag/test_bag.json", "r") as read_file:
        bag_data = json.load(read_file)

    demo_bag = Bag(**bag_data, display_size=window.get_size())
    demo_bag.loop(window, cont)









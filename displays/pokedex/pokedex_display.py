from enum import Enum

import pygame
import pygame as pg

from displays.display_container import DisplayContainer
from screen_V2 import Screen
from sprite_screen import SpriteScreen

from pokemon import getImages, oldPokedex


NAME_CONTAINER_POSITIONS = [
    (117, 20), (113, 32), (111, 48), (106, 72), (111, 96), (113, 112), (117, 128),
]


class PokedexDisplayStates(Enum):
    home = 0
    select = 1


class NameContainer(DisplayContainer):
    def __init__(self, pk_id, pk_name: str, pos, offset, scale=1):
        img_path = "assets/containers/menu/pokedex/name_container.png"
        DisplayContainer.__init__(self, img_path, "name_container", pos, scale)

        self.add_text_2(pk_name.upper(), text_box=pg.Rect(pg.Vector2(49, 4)*scale, (200, 100)))
        self.add_text_2(f"{pk_id:03}", text_box=pg.Rect(pg.Vector2(22, 4) * scale, (200, 100)))

        self.image = self.get_surface()

        self.offset = offset


class PokedexDisplayMain(SpriteScreen):
    def __init__(self, size, scale, pokedex):
        SpriteScreen.__init__(self, size)
        self.load_image("assets/menu/pokedex/pokedex_background_upper.png", scale=scale, base=True)
        self.scale = scale

        self.pokedex = pokedex

        self.pokemon_idx = 1

        self.update_image()

    def update_image(self):
        front_image, _, _ = getImages(self.pokemon_idx, crop=False)

        self.kill_sprites()

        self.refresh()

        name = oldPokedex.loc[oldPokedex["ID"] == self.pokemon_idx].index.values[0]
        if self.pokedex.data.loc[name, "appearances"] > 0:
            self.add_image(front_image, pg.Vector2(16, 40)*self.scale)
        else:
            # self.add_image(front_image, pg.Vector2(16, 40)*self.scale)
            ...

        for i in sorted(range(max([-(self.pokemon_idx-1), -3]), min([4, -(self.pokemon_idx - 152)])), key=lambda x: abs(x), reverse=True):
            name = oldPokedex.loc[oldPokedex["ID"] == self.pokemon_idx+i].index.values[0]
            if self.pokedex.data.loc[name, "appearances"] < 1:
                name = "----"

            container = NameContainer(self.pokemon_idx+i, name, NAME_CONTAINER_POSITIONS[3+i], scale=self.scale, offset=i)

            self.sprites.add(container)



import os
import sys
import time

from pygame import Surface

import pokemon
from screen_V2 import Colours, FontOption, Screen, BlitLocation
from sprite_screen import SpriteScreen, PokeballCatchAnimation
from pokemon import Pokemon, PokemonSpriteSmall
import pygame as pg
from enum import Enum

from general.utils import create_display_bar
from general.Item import Pokeball, MedicineItem, BattleItemType
from general.Move import Move2
# from bag import BagV2


class DisplayContainer(pg.sprite.Sprite, SpriteScreen):
    """
    Main game object button. Inherits from Sprite and SpriteScreen, enabling the full set of screen methods to
    act on the sprite image.
    """
    def __init__(self, image_path, sprite_id, pos=(0, 0), scale=None):
        """
        Provide the image path for the base asset to create the sprite from

        :param image_path:
        :param sprite_id:
        :param pos:
        :param scale:
        """
        pg.sprite.Sprite.__init__(self)

        self.sprite_type = "container"
        self.image = pg.image.load(image_path)
        if scale:
            self.image = pg.transform.scale(self.image, pg.Vector2(self.image.get_size()) * scale)
            pos = pg.Vector2(pos) * scale

        self.rect = self.image.get_rect()
        self.rect.topleft = pos
        self.id = sprite_id
        self.scale = scale

        SpriteScreen.__init__(self, self.image.get_size())
        self.load_image(image_path, base=True, scale=pg.Vector2(scale, scale))

    def click_return(self):
        return self.sprite_type, self.id

    def is_clicked(self, pos):
        if self.rect.collidepoint(pos):
            return True
        else:
            return False

import pygame as pg
from screen_V2 import Screen, Colours


class AttackAnimation(pg.sprite.Sprite):
    def __init__(self, colour=Colours.white):
        super().__init__()

        self.image = pg.Surface((100, 100))
        pg.draw.circle(self.image, colour.value, pg.Vector2(self.image.get_size()) / 2, 50)

        self.rect = self.image.get_rect()
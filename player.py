import os
from enum import Enum

import pygame as pg

from general.Direction import Direction
from Sprites.SpriteSet import SpriteSet2


class Movement(Enum):
    walking = 0
    running = 1


class Player(pg.sprite.Sprite):
    def __init__(self, sprite_path: os.PathLike | str, position=pg.Vector2(0, 0)):
        # ======== INITIALISATION =======
        pg.sprite.Sprite.__init__(self)
        self.sprite_type = "player"
        self.id = "benji"

        self.spriteIdx = 3
        self.facingDirection = Direction.down
        self.leg = True

        self.sprite_sets: dict | None = None
        self.sprites: list[pg.Surface] | None = None
        self.image: pg.Surface | None = None
        self.movement = Movement.walking
        self.loadSurfaces(sprite_path)
        self.position = position
        self.blit_rect = self.image.get_rect()
        self.rect = pg.Rect((0, 0), (32, 32))

        self.steps = 0

    def update(self):
        self.sprites = self.sprite_sets[self.movement].sprites
        self.image = self.sprites[self.spriteIdx]

    def clearSurfaces(self):
        self.sprites = None
        self.image = None

    def loadSurfaces(self, sprite_path: str | os.PathLike):
        self.sprite_sets = {
            Movement.walking: SpriteSet2(
                os.path.join(sprite_path, "Walking Sprites.png"), 12, pg.Vector2(34, 50), pg.Vector2(0, 0)
            ),
            Movement.running: SpriteSet2(
                os.path.join(sprite_path, "Running Sprites.png"), 12, pg.Vector2(40, 50), pg.Vector2(0, 0)
            )
        }

        self.update()

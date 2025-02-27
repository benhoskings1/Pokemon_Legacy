import os
from enum import Enum

import pygame as pg

from General.Direction import Direction
from Sprites.SpriteSet import SpriteSet2


class Movement(Enum):
    walking = 0
    running = 1


class Player(pg.sprite.Sprite):
    def __init__(self, spritePath: os.PathLike, position=pg.Vector2(0, 0)):
        pg.sprite.Sprite.__init__(self)
        self.spriteIdx = 3
        self.facingDirection = Direction.down
        self.leg = True

        self.walkingSpriteSet = SpriteSet2(os.path.join(spritePath, "Walking Sprites.png"),
                                           12, pg.Vector2(34, 50), pg.Vector2(0, 0))

        self.runningSpriteSet = SpriteSet2(os.path.join(spritePath, "Running Sprites.png"),
                                           12, pg.Vector2(40, 50), pg.Vector2(0, 0))

        self.movement = Movement.walking
        self.sprites = self.walkingSpriteSet.sprites

        self.image = self.sprites[self.spriteIdx]
        self.position = position
        self.rect = self.image.get_rect()

        self.steps = 0

    def update(self):
        if self.movement == Movement.walking:
            self.sprites = self.walkingSpriteSet.sprites
            self.image = self.sprites[self.spriteIdx]
            self.rect = self.image.get_rect()

        elif self.movement == Movement.running:
            self.sprites = self.walkingSpriteSet.sprites
            self.image = self.sprites[self.spriteIdx]
            self.rect = self.image.get_rect()

    def getOffset(self, surfSize, gameMap):
        centre = pg.Vector2(surfSize) / 2
        playerOffset = pg.Vector2(- self.position.x * gameMap.data.tilewidth,
                                  - self.position.y * gameMap.data.tileheight) * gameMap.scale
        playerOffset += pg.Vector2(0, self.rect.h - gameMap.data.tileheight * gameMap.scale)
        return centre / 2 + playerOffset

    def clearSurfaces(self):
        self.sprites = None
        self.image = None
        self.walkingSpriteSet = None
        self.runningSpriteSet = None

    def loadSurfaces(self, spritePath: os.PathLike):

        self.walkingSpriteSet = SpriteSet2(os.path.join(spritePath, "Walking Sprites.png"),
                                           12, pg.Vector2(34, 50), pg.Vector2(0, 0))

        self.runningSpriteSet = SpriteSet2(os.path.join(spritePath, "Running Sprites.png"),
                                           12, pg.Vector2(40, 50), pg.Vector2(0, 0))

        self.update()

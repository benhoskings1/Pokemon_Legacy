import pygame as pg
import pytmx

from Map_Files.Map_Objects.Tall_Grass import TallGrass, Obstacle
from Screen import Screen

clear = pg.SRCALPHA


class TiledMap:
    def __init__(self, filePath, scale=1):
        self.data = pytmx.load_pygame(filePath, pixelalpha=True)
        size = (self.data.tilewidth * self.data.width, self.data.tileheight * self.data.height)

        self.screen = Screen(size)

        self.scale = scale
        self.grassObjects = []
        self.obstacles = pg.sprite.Group()

        self.xLimits = pg.Vector2(8, self.data.width - 8)
        self.yLimits = pg.Vector2(7, self.data.height - 6)

        for layer in self.data.layers:
            if isinstance(layer, pytmx.TiledTileLayer):
                for x, y, gid, in layer:
                    tileImage = self.data.get_tile_image_by_gid(gid)
                    if tileImage:
                        (width, height) = tileImage.get_size()
                        pos = (x * self.data.tilewidth, (y + 1) * self.data.tileheight - height)
                        self.screen.addImage(tileImage, pos, base=True)

        self.screen.baseSurface = pg.transform.scale(self.screen.baseSurface, self.screen.size * scale)
        self.screen.refresh()

        for obj in self.data.objects:
            rect = pg.Rect(obj.x, obj.y, obj.width, obj.height)
            if obj.name == "Grass":
                grass = TallGrass(rect, self.scale, obj.Location)
                self.grassObjects.append(grass)
            elif obj.name == "Obstacle":
                obstacle = Obstacle(rect, self.scale)
                self.obstacles.add(obstacle)

    def getSurface(self, size, playerPos):
        position = playerPos * self.data.tilewidth * self.scale

        rect = pg.Rect(position, size)
        rect.topleft -= pg.Vector2(size) / 2
        rect.topleft += (pg.Vector2(self.data.tilewidth) * self.scale) / 2
        subSurf = self.screen.surface.subsurface(rect)

        return subSurf

    def render(self, surface, offset):
        surface.blit(self.screen.surface, offset)

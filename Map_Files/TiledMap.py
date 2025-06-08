import pygame as pg
import pytmx
from pytmx import TiledMap
from pytmx.util_pygame import pygame_image_loader

from Map_Files.Map_Objects.Tall_Grass import TallGrass, Obstacle
from screen import Screen
from sprite_screen import SpriteScreen

from player import Player

clear = pg.SRCALPHA


class TiledMapLegacy:
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


class TiledMap2(TiledMap, SpriteScreen):
    def __init__(self, file_path, size, player, scale=1):
        """
        This map dynamically renders the players immediate surroundings, rather than the entire map.

        :param file_path:
        :param size:
        :param scale:
        """

        SpriteScreen.__init__(self, size)
        args = []
        kwargs = {"pixelalpha": True, "image_loader": pygame_image_loader}
        TiledMap.__init__(self, file_path, *args, **kwargs)

        self.scale = scale
        self.grassObjects = []
        self.obstacles = pg.sprite.Group()

        self.x_limits = (8, self.data.width - 8)
        self.y
        _limits = (7, self.data.height - 6)

        for obj in self.data.objects:
            rect = pg.Rect(obj.x, obj.y, obj.width, obj.height)
            if obj.name == "Grass":
                grass = TallGrass(rect, self.scale, obj.Location)
                self.grassObjects.append(grass)
            elif obj.name == "Obstacle":
                obstacle = Obstacle(rect, self.scale)
                self.obstacles.add(obstacle)

        self.player = player
        self.sprites.add(player)

    def render(self, player_pos):

        self.refresh()

        for layer in self.layers:
            if isinstance(layer, pytmx.TiledTileLayer):
                for x, y, gid in layer:
                    if self.x_limits[0] <= x <= self.x_limits[1] and self.y_limits[0] <= y <= self.y_limits[1]:
                        tileImage = self.get_tile_image_by_gid(gid)
                        if tileImage:
                            (width, height) = tileImage.get_size()
                            pos = (x * self.tilewidth, (y + 1) * self.tileheight - height)
                            self.add_image(tileImage, pos)


if __name__ == '__main__':
    pg.init()
    native_size = pg.Vector2(256, 382)
    graphics_scale = 2
    displaySize = native_size * graphics_scale
    pg.display.set_mode(displaySize)

    # load all attributes which utilise any pygame surfaces!
    pg.display.set_caption('Map Files')
    pg.event.pump()

    player = Player("Sprites/Player Sprites", position=pg.Vector2(10, 9))

    sinnoh_map = TiledMap2('Map_Files/Sinnoh Map.tmx', displaySize, player=player)

    # print(sinnoh_map.data.)
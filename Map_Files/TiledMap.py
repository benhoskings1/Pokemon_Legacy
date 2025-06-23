import pygame as pg
import pytmx
from pytmx import TiledMap
from pytmx.util_pygame import pygame_image_loader

from general.utils import Colours
from Map_Files.Map_Objects.Tall_Grass import TallGrass, Obstacle
from sprite_screen import SpriteScreen

from player import Player


class TiledMap2(TiledMap, SpriteScreen):
    def __init__(self, file_path, size, player, scale=1):
        """
        This map dynamically renders the players immediate surroundings, rather than the entire map.

        :param file_path:
        :param size:
        :param scale:
        """
        args = []
        kwargs = {"pixelalpha": True, "image_loader": pygame_image_loader}
        TiledMap.__init__(self, file_path, *args, **kwargs)

        size = pg.Vector2(size[0], size[1]) + 4 * pg.Vector2(self.tilewidth, self.tileheight)
        SpriteScreen.__init__(self, size)

        self.scale = scale
        self.grassObjects = pg.sprite.Group()
        self.obstacles = pg.sprite.Group()

        self.x_limits = (8, self.width - 8)
        self.y_limits = (7, self.height - 6)

        for obj in self.objects:
            rect = pg.Rect(obj.x, obj.y, obj.width, obj.height)
            if obj.name == "Grass":
                grass = TallGrass(rect, self.scale, obj.Location)
                self.grassObjects.add(grass)
            elif obj.name == "Obstacle":
                obstacle = Obstacle(rect, self.scale)
                self.obstacles.add(obstacle)

        self.player = player
        self.render(self.player.position)

    def render(self, player_pos: pg.Vector2, grid_lines=False):

        self.refresh()

        for layer in self.layers:
            count = 0
            if isinstance(layer, pytmx.TiledTileLayer):
                for x, y, gid in layer:
                    if player_pos.x - 10 <= x <= player_pos.x + 10 and player_pos.y - 8 <= y+1 <= player_pos.y + 8:
                        tileImage = self.get_tile_image_by_gid(gid)
                        if tileImage:
                            (width, height) = tileImage.get_size()
                            pos = pg.Vector2(self.tilewidth * (count % 21), self.tileheight * (count // 21) - height) + pg.Vector2(-16, 0)
                            self.add_image(tileImage, pos)
                            if grid_lines:
                                pg.draw.rect(self.surface, Colours.red.value, pg.Rect(pos, tileImage.get_size()), width=2)
                        count += 1
        if grid_lines:
            pg.draw.line(self.surface, Colours.green.value, self.surface.get_rect().midtop,
                         self.surface.get_rect().midbottom, width=5)

    def detect_collision(self) -> list[pg.sprite.Sprite]:
        """
        Detects collisions between the player and the grass objects.

        :return: bool if the player is standing in the tall grass.
        """
        return pg.sprite.spritecollide(self.player, self.grassObjects, dokill=False)


if __name__ == '__main__':
    pg.init()
    native_size = pg.Vector2(256, 192)
    graphics_scale = 2
    displaySize = native_size * graphics_scale
    window = pg.display.set_mode(displaySize)

    # load all attributes which utilise any pygame surfaces!
    pg.display.set_caption('Map Files')
    pg.event.pump()

    player = Player("Sprites/Player Sprites", position=pg.Vector2(14, 13))

    sinnoh_map = TiledMap2('Map_Files/Sinnoh Map.tmx', displaySize, player=player)
    sinnoh_map.render(player.position)
    while True:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
            elif event.type == pg.KEYDOWN:
                ...

        window.blit(sinnoh_map.get_surface(), (32, 32))
        pg.display.flip()


    # print(sinnoh_map.data.)
from enum import Enum
import pygame as pg

from sprite_screen import SpriteScreen
from Map_Files.TiledMap import TiledMap

from displays.menu.menu_display_popup import MenuDisplayPopup


class GameDisplayStates(Enum):
    pokedex = 0
    team = 1
    bag = 2
    player = 3
    save = 4
    options = 5
    exit = 6


class GameDisplay(SpriteScreen):
    def __init__(self, size, player, scale: int | float = 1):
        # ==== INIT ====
        SpriteScreen.__init__(self, size)

        self.player = player
        self.map = TiledMap("Map_Files/Sinnoh Map.tmx", scale=scale)

        self.player.rect.topleft = (
                pg.Vector2(self.surface.get_rect().center) -
                pg.Vector2(
                    self.player.image.get_rect().centerx,
                    self.map.data.tilewidth * self.map.scale / 2 + 16
                )
        )

        self.sprites.add(self.player)

    def get_surface(self, show_sprites=True):
        if self.power_off:
            return self.power_off_surface

        if show_sprites:
            self.sprites.draw(self)

        self.add_image(self.map.getSurface(self.size, self.player.position), (0, 0))

        display_surf = self.base_surface.copy()
        display_surf.blit(self.surface, (0, 0))
        display_surf.blit(self.sprite_surface, (0, 0))

        return display_surf

    def menu_loop(self, game):
        """
        Loop to return an action based on the menu selection
        :return:
        """
        action = None
        popup = MenuDisplayPopup(scale=game.graphics_scale)
        self.sprites.add(popup)
        game.updateDisplay()

        while not action:
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    game.running = False
                elif event.type == pg.KEYDOWN:
                    if event.key == game.controller.y:
                        popup.kill()
                        return None
                    elif event.key == game.controller.a:
                        return GameDisplayStates(popup.selector.position_idx)

                    else:
                        popup.process_input(event.key, controller=game.controller)
                        # game.menu_active = not game.menu_active
                        game.updateDisplay()

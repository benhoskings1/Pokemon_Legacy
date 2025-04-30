import pygame as pg
from math import floor
from screen_V2 import Screen, Colours


class PokeballCatchAnimation(pg.sprite.Sprite):
    def __init__(self, sprite_id):
        pg.sprite.Sprite.__init__(self)

        self.id = sprite_id
        self.frames = 100
        self.frame_weights = [1, 1, 1, 1, 1, 1, 1, 1, 1, 3, 1,
                              1, 1, 1, 1, 3, 1, 1.5, 1, 2, 2, 2]

        ims = [
            pg.image.load(
                f"action_animations/catch_animations/pokeball/frame_{image_idx}.png"
            ) for image_idx in range(22)
        ]

        self.images = [
            pg.transform.scale2x(im) for im in ims
        ]

        self.image_idx = 0
        self.image = self.images[0]
        self.frame_idx = 0
        self.rect = self.image.get_rect()

        self.sprite_type = "pokeball"

    def update(self, frame_idx):
        self.image = self.images[self.image_idx]

        if self.image_idx <= 7:
            x = frame_idx * 13
            y = 200 + 0.003 * x * (x - 500)
        elif 7 < self.image_idx <= 14:
            x, y = int(192 * 15 / 8), int(50 * 15 / 8)
        else:
            x, y = int(192 * 15 / 8), int(80 * 15 / 8)

        self.rect.topleft = (x, y)


class GameObjects(pg.sprite.Group):
    def __init__(self, sprites):
        super().__init__(self, sprites)

    def draw(self, screen: Screen, bgsurf=None, special_flags: int = 0):
        for obj in self.sprites():
            if obj.sprite_type == "pokemon":
                if obj.visible:
                    screen.add_surf(obj.image, pos=obj.rect.topleft, sprite=True)
            elif (obj.sprite_type == "animation" or
                    obj.sprite_type == "pokeball"):
                screen.add_surf(obj.image, pos=obj.rect.topleft, sprite=True)
            else:
                screen.add_surf(obj.image, pos=obj.rect.topleft, sprite=True)


class SpriteScreen(Screen):
    def __init__(self, size, colour=None):
        super().__init__(size, colour=colour)

        self.sprites = GameObjects([])
        self.show_sprites = True

    def click_test(self, pos):
        if self.sprites:
            for sprite in self.sprites:
                if sprite.is_clicked(pos):
                    return sprite.click_return()

        return None

    def kill_sprites(self):
        self.sprites.empty()

    def get_surface(self, show_sprites=True):
        if self.power_off:
            return self.power_off_surface

        if show_sprites:
            self.sprites.draw(self)

        display_surf = self.base_surface.copy()
        display_surf.blit(self.surface, (0, 0))
        display_surf.blit(self.sprite_surface, (0, 0))

        return display_surf

    def get_object(self, object_id):
        for game_object in self.sprites:
            if game_object.id == object_id:
                return game_object

from math import floor, ceil

from general.Environment import Environment
from screen_V2 import Screen, BlitLocation, Colours, FontOption
from sprite_screen import SpriteScreen, GameObjects, PokeballCatchAnimation
from pokemon import Pokemon
import pygame as pg


class BattleDisplayTouch(SpriteScreen):
    def __init__(self, window, size):
        """
        This is the main battle display. The native screen size is 256x192 px
        :param window: The pygame surface to blit the display onto
        :param size: the size of the display
        :param time: the time of day, used to configure the battle background option
        :param environment:
        """
        super().__init__(size, colour=Colours.black)

        self.layer_names = ["background", "stats", "animations", "text"]

        self.screens = {
            name: SpriteScreen(size) for name in self.layer_names
        }

        self.window = window

        self.image_scale = pg.Vector2(15 / 8, 15 / 8)

        self.sprites = GameObjects([])

        self.text: str = None

        # configure base surfaces for each screen level
        self.screens["background"].load_image(
            "assets/battle/touch_display/home/background.png",
            base=True, scale=self.image_scale
        )

        self.bounce_friendly_stat = False
        self.friendly_stat_bounce_val = 0

    def add_text(self, text, pos, lines=1, location=BlitLocation.topLeft, base=False, colour=None, surface_idx=0):

        words = text.split()
        # print(words)

        for word in words:
            # self.screens["text"].add
            ...

    def update_display_text(self, text):
        self.screens["text"].refresh()
        self.screens["text"].addText(text, pg.Vector2(int(16 * 15 / 8), int(156 * 15 / 8)))

    def add_pokemon_sprites(self, pokemon):
        for pk in pokemon:
            self.sprites.add(pk)

        self.friendly = pokemon[0]
        self.foe = pokemon[1]

        #
        self.screens["stats"].get_object("friendly").initialise_info(
            name=self.friendly.name, sex=self.friendly.gender, level=self.friendly.level
        )

        self.screens["stats"].get_object("foe").initialise_info(
            name=self.foe.name, sex=self.foe.gender, level=self.foe.level
        )

    def render_pokemon_details(self, opacity=None, friendly=False, lines=None):
        self.refresh()

        if opacity:
            offset = 120 * (1 - (opacity / 255))
        else:
            offset = 0

        # Display options for the wild Pokémon
        if self.foe.visible:
            # print(self.foe.health, self.foe.health / self.foe.stats.health)
            # add the name of the Pokémon
            self.screens["stats"].get_object("foe").update_stats(
                current_health=self.foe.health, max_health=self.foe.stats.health
            )

            # if the Pokémon has any status conditions, add display them
            if self.foe.status:
                self.load_image(str.format("Images/Status Labels/{}.png", self.foe.status.name),
                                pg.Vector2(int((10 - offset * (not friendly)) * 15 / 8), int(62 * 15 / 8)),
                                scale=pg.Vector2(2, 2))

            # finally add the image of the Pokémon
            if opacity and not friendly:
                self.foe.image.set_alpha(opacity)

        # Display options for the friendly Pokémon
        if self.friendly.visible:
            # draw the health onto the screen
            self.screens["stats"].get_object("friendly").update_stats(
                current_health=self.friendly.health, max_health=self.friendly.stats.health
            )

    def intro_animations(self, window: pg.Surface, duration):
        self.render_pokemon_details()
        if self.foe.animation:
            frames = len(self.foe.animation)
            for frame in self.foe.animation:
                self.foe.image = frame
                window.blit(self.get_surface(), (0, 0))
                pg.display.flip()
                pg.time.delay(int(0.75 * duration / frames))
                self.refresh()

            self.foe.displayImage = self.foe.image
            pg.time.delay(int(0.25 * duration))
        else:
            pg.time.delay(duration)

        window.blit(self.get_surface(), (0, 0))
        pg.display.flip()

    def catch_animation(self, duration, checks):
        frames = 100
        timePerFrame = duration / frames
        images = 22

        # the proportion of frames for each of the 21 images!
        frameWeight = [1, 1, 1, 1, 1, 1, 1, 1, 1, 3, 1,
                       1, 1, 1, 1, 3, 1, 1.5, 1, 2, 2, 2]

        imageFrames = []
        for [idx, weight] in enumerate(frameWeight):
            if idx == 0:
                imageFrames.append(frames * (weight / sum(frameWeight)))
            else:
                imageFrames.append(imageFrames[idx - 1] + (frames * (weight / sum(frameWeight))))

        for idx, frameCount in enumerate(imageFrames):
            imageFrames[idx] = floor(frameCount)

        throwFrames = imageFrames[15]
        shakeFrames = imageFrames[19]

        animation = PokeballCatchAnimation()
        self.sprites.add(animation)

        for frame in range(throwFrames):
            animation.image_idx = images
            for idx in range(images - 1, -1, -1):
                if frame <= imageFrames[idx]:
                    animation.image_idx = idx

            animation.update(frame)

            if animation.image_idx == 10:
                self.foe.image.set_alpha(0)

            self.refresh()
            # self.render_pokemon_details()
            self.window.blit(self.get_surface(), (0, 0))
            pg.display.flip()
            pg.time.delay(int(timePerFrame))

        for check in range(checks):
            for frame in range(throwFrames, shakeFrames):
                animation.image_idx = images
                for idx in range(images - 1, -1, -1):
                    if frame <= imageFrames[idx]:
                        animation.image_idx = idx

                animation.update(frame)

                self.refresh()
                # self.render_pokemon_details()
                self.window.blit(self.get_surface(), (0, 0))
                pg.display.flip()
                pg.time.delay(int(timePerFrame))
            pg.time.delay(500)

        if checks != 3:
            # break free!
            pass
        else:
            for frame in range(shakeFrames, frames):
                animation.image_idx = images
                for idx in range(images - 1, -1, -1):
                    if frame <= imageFrames[idx]:
                        animation.image_idx = idx

                animation.update(frame)

                self.refresh()
                # self.render_pokemon_details()
                self.window.blit(self.get_surface(), (0, 0))
                pg.display.flip()
                pg.time.delay(int(timePerFrame))

        self.sprites.remove(animation)

    def refresh(self, text=True):
        self.surface = pg.Surface(self.size, pg.SRCALPHA)
        self.screens["stats"].refresh()
        if text:
            self.screens["text"].refresh()

        self.sprite_surface = pg.Surface(self.size, pg.SRCALPHA)

    def get_surface(self, show_sprites=True):
        if self.power_off:
            return self.power_off_surface

        if show_sprites:
            self.sprites.draw(self)

        display_surf = self.base_surface.copy()
        display_surf.blit(self.surface, (0, 0))

        for name in self.layer_names:
            display_surf.blit(self.screens[name].get_surface(show_sprites=True), (0, 0))

        display_surf.blit(self.sprite_surface, (0, 0))

        if self.bounce_friendly_stat:
            self.screens["stats"].refresh()
            self.friendly_stat_bounce_val = (self.friendly_stat_bounce_val + 1) % 7

            stat_container: pg.sprite.Sprite = self.screens["stats"].get_object("friendly")
            stat_container.rect.top += self.friendly_stat_bounce_val - 3

        return display_surf

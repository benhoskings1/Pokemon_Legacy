import os
from math import floor, ceil

from PIL.ImageChops import hard_light

from general.Environment import Environment
from screen_V2 import Screen, BlitLocation, Colours, FontOption
from battle_action import BattleAction, BattleAttack, BattleActionType
from sprite_screen import SpriteScreen, GameObjects, PokeballCatchAnimation
from pokemon import Pokemon
import pygame as pg

from font.font import Font, LevelFont


class StatContainer(pg.sprite.Sprite):
    def __init__(self, sprite_id, friendly=True):
        pg.sprite.Sprite.__init__(self)

        # convention across game to be able to retrieve sprites
        self.id = sprite_id
        self.friendly = friendly

        self.base_image = pg.image.load(
            f"assets/battle/main_display/stat_container_{'friendly' if friendly else 'foe'}.png"
        )
        self.image = self.base_image
        self.image = pg.transform.scale(self.image, pg.Vector2(self.image.get_size()) * 15 / 8)
        self.rect = self.image.get_rect()

        self.sprite_type = "stat_container"

        if friendly:
            self.rect.topright = pg.Vector2(256, 97) * 15 / 8
        else:
            self.rect.topleft = pg.Vector2(0, 21) * 15 / 8

    def initialise_info(self, name, sex, level, base_health=None):
        print("initialising info")
        font, level_font = Font(scale=2), LevelFont(scale=2)
        name_text = font.render_text(name, lineCount=1)
        if self.friendly:
            self.image.blit(name_text, pg.Vector2(16, 5) * 15/8)
            self.image.blit(level_font.render_text(f"Lv{level}", lineCount=1), pg.Vector2(90, 8) * 15/8)
        else:
            self.image.blit(name_text, pg.Vector2(5, 5) * 15 / 8)
            self.image.blit(level_font.render_text(f"Lv{level}", lineCount=1), pg.Vector2(70, 8) * 15 / 8)

        self.base_image = self.image

    def update_stats(self, current_health, max_health):
        health_ratio = current_health / max_health

        self.image = self.base_image.copy()

        if self.friendly:
            bar_rect = pg.Rect(pg.Vector2(117, 39), pg.Vector2(48 * health_ratio * 15 / 8, 4))
        else:
            bar_rect = pg.Rect(pg.Vector2(94, 39), pg.Vector2(48 * health_ratio * 15 / 8, 4))

        if health_ratio > 0.5:
            colour = "high"
        elif health_ratio > 0.25:
            colour = "medium"
        else:
            colour = "low"

        health_bar = pg.image.load(f"assets/battle/main_display/health_bar/health_{colour}.png")
        health_bar = pg.transform.scale(health_bar, bar_rect.size)
        self.image.blit(health_bar, bar_rect.topleft)

        if self.friendly:
            level_font = LevelFont(scale=2)
            health_text = level_font.render_text(f"{floor(current_health)}/{max_health}", lineCount=1)
            heath_text_rect = pg.Rect(pg.Vector2(115, 36) * 15 / 8, health_text.get_size())
            heath_text_rect.topleft -= pg.Vector2(health_text.get_size())
            self.image.blit(health_text, heath_text_rect.topleft)


class BattleDisplay(SpriteScreen):
    def __init__(self, window, size, time, environment: Environment):
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

        self.friendly: Pokemon = None
        self.foe: Pokemon = None

        self.text: str = None

        # configure base surfaces for each screen level
        self.screens["background"].load_image(
            f"assets/battle/main_display/backgrounds/{environment.value}_{time.value}.png",
            base=True, scale=self.image_scale
        )

        self.text_rect = self.screens["text"].load_image(
            "assets/battle/main_display/text_box_main.png", pg.Vector2(size.x / 2, size.y - 5),
            base=True, scale=self.image_scale, location=BlitLocation.midBottom
        )

        self.screens["stats"].sprites.add([
            StatContainer(sprite_id="friendly", friendly=True),
            StatContainer(sprite_id="foe", friendly=False)
        ])

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


if __name__ == "__main__":
    import time

    pg.init()
    window = pg.display.set_mode(pg.Vector2(240, 180) * 2)

    bd = BattleDisplay(size=window.get_size())

    window.blit(bd.get_surface(), (0, 0))

    pg.event.pump()

    while True:
        time.sleep(1)

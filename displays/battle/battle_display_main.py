import os
import time
from math import floor, ceil

from PIL import Image
import pygame as pg
import numpy as np
from Image_Processing.ImageEditor import ImageEditor

from general.Environment import Environment
from screen_V2 import Screen, BlitLocation, Colours
from sprite_screen import SpriteScreen, GameObjects, PokeballCatchAnimation
from pokemon import Pokemon


from font.font import Font, LevelFont


editor = ImageEditor()
STAT_NAMES = ["Max. HP", "Attack", "Defence", "Sp. Atk", "Sp. Def", "Speed"]


class StatContainer(pg.sprite.Sprite):
    def __init__(self, sprite_id, friendly=True, scale=2):
        pg.sprite.Sprite.__init__(self)

        # convention across game to be able to retrieve sprites
        self.id = sprite_id
        self.friendly = friendly
        self.scale = scale

        self.base_image = pg.image.load(
            f"assets/battle/main_display/stat_container_{'friendly' if friendly else 'foe'}.png"
        )
        self.image = self.base_image
        self.image = pg.transform.scale(self.image, pg.Vector2(self.image.get_size()) * 2)
        self.rect = self.image.get_rect()

        self.sprite_type = "stat_container"

        if friendly:
            self.rect.topright = pg.Vector2(256, 97) * scale
        else:
            self.rect.topleft = pg.Vector2(0, 21) * scale

        self.pos_update = time.monotonic()
        self.pos_offset = 0

    def initialise_info(self, name, sex, level, base_health=None):
        font, level_font = Font(scale=2), LevelFont(scale=2)
        name_text = font.render_text(name, lineCount=1)
        if self.friendly:
            self.image.blit(name_text, pg.Vector2(16, 5) * self.scale)
            self.image.blit(level_font.render_text(f"Lv{level}", lineCount=1), pg.Vector2(90, 8) * self.scale)
        else:
            self.image.blit(name_text, pg.Vector2(5, 5) * self.scale)
            self.image.blit(level_font.render_text(f"Lv{level}", lineCount=1), pg.Vector2(70, 8) * self.scale)

        self.base_image = self.image

    def update_stats(self, current_health, max_health, current_xp=0, max_xp=0):
        health_ratio = current_health / max_health

        self.image = self.base_image.copy()

        if self.friendly:
            bar_rect = pg.Rect(pg.Vector2(62, 20) * self.scale, pg.Vector2(48 * health_ratio * self.scale, 4 * self.scale))

            xp_ratio = current_xp / max_xp
            xp_rect = pg.Rect(pg.Vector2(30, 38) * self.scale, pg.Vector2(88 * xp_ratio * self.scale, 2 * self.scale))
        else:
            bar_rect = pg.Rect(pg.Vector2(50, 20) * self.scale, pg.Vector2(48 * health_ratio * self.scale, 4 * self.scale))
            xp_rect = None

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
            xp_bar = pg.Surface(xp_rect.size, pg.SRCALPHA)
            xp_bar.fill(pg.Color(63, 180, 190, 200))

            self.image.blit(xp_bar, xp_rect.topleft)

            level_font = LevelFont(scale=2)
            health_text = level_font.render_text(f"{floor(current_health)}/{max_health}", lineCount=1)
            heath_text_rect = pg.Rect(pg.Vector2(115, 36) * self.scale, health_text.get_size())
            heath_text_rect.topleft -= pg.Vector2(health_text.get_size())
            self.image.blit(health_text, heath_text_rect.topleft)

    def update_pos(self):
        now = time.monotonic()
        if now - self.pos_update > 0.1:
            self.pos_update = now
            self.pos_offset = (self.pos_offset + 1) % 7
            self.rect.top += self.pos_offset - 3


class TextBox(pg.sprite.Sprite, Screen):
    def __init__(self, sprite_id, scale):
        pg.sprite.Sprite.__init__(self)
        self.sprite_type = "text_box"
        self.id = sprite_id

        imageAnimation = Image.open("assets/battle/main_display/text_box.gif")
        self.frames = []
        self.frame_count = imageAnimation.n_frames
        for frame in range(self.frame_count):
            imageAnimation.seek(frame)
            imageData = np.asarray(imageAnimation.convert("RGBA"))
            editor.loadData(imageData)
            surf = editor.createSurface(bgr=False)
            surf = pg.transform.scale(surf, pg.Vector2(surf.get_size())*scale)
            self.frames.append(surf)

        self.image = self.frames[0]
        Screen.__init__(self, size=self.frames[0].get_size())

        self.rect = self.image.get_rect()
        self.rect.topleft = pg.Vector2(0, 144) * scale

        self.frame_idx = 0
        self.frame_update = time.monotonic()

    def update_image(self):
        now = time.monotonic()
        if now - self.frame_update > 0.8:
            self.frame_update = now
            self.frame_idx = (self.frame_idx + 1) % self.frame_count

        self.image = self.frames[self.frame_idx].copy()
        self.image.blit(self.get_surface(), (0, 0))

    # def set_image(self):
    #     # self.image.blit(self.get_surface(), (0, 0))


class LevelUpBox(pg.sprite.Sprite, Screen):
    def __init__(self, sprite_id, scale, new_stats, old_stats=None):
        pg.sprite.Sprite.__init__(self)
        self.sprite_type = "text_box"
        self.id = sprite_id

        img = pg.image.load("assets/battle/main_display/level_up.png")
        img = pg.transform.scale(img, pg.Vector2(img.get_size())*scale)

        Screen.__init__(self, size=img.get_size())
        self.add_image(img, (0, 0), base=True)
        self.rect = img.get_rect()
        self.rect.topleft = pg.Vector2(130, 50) * scale

        values = (new_stats - old_stats).get_values() if old_stats else new_stats.get_values()

        for idx, h in enumerate([(9 + idx * 16) * scale for idx in range(6)]):
            self.addText(f"{STAT_NAMES[idx]}", pos=(6 * scale, h))
            if old_stats:
                self.addText(f"+ {values[idx]}", pos=(96 * scale, h))
            else:
                self.addText(f"{values[idx]}", pos=(100 * scale, h))

        self.image = self.get_surface()


class BattleDisplayMain(SpriteScreen):
    def __init__(self, window, size, time, environment: Environment, scale=2):
        """
        This is the main battle display. The native screen size is 256x192 px
        :param window: The pygame surface to blit the display onto
        :param size: the size of the display
        :param time: the time of day, used to configure the battle background option
        :param environment:
        """
        super().__init__(size, colour=Colours.black)
        self.scale = scale

        self.layer_names = ["background", "stats", "animations", "text"]

        self.screens = {
            name: SpriteScreen(size) for name in self.layer_names
        }

        self.text_box = TextBox(sprite_id="text_box", scale=2)

        self.window = window

        # self.image_scale = pg.Vector2(15 / 8, 15 / 8)

        self.sprites = GameObjects([])

        self.friendly: Pokemon = None
        self.foe: Pokemon = None

        self.text: str = None

        # configure base surfaces for each screen level
        self.screens["background"].load_image(
            f"assets/battle/main_display/backgrounds/{environment.value}_{time.value}.png",
            base=True, scale=pg.Vector2(self.scale, self.scale)
        )

        self.screens["text"].sprites.add(self.text_box)

        self.screens["stats"].sprites.add([
            StatContainer(sprite_id="friendly", friendly=True, scale=self.scale),
            StatContainer(sprite_id="foe", friendly=False, scale=self.scale)
        ])

        self.bounce_friendly_stat = False
        self.friendly_stat_bounce_val = 0

    def add_text(self, text, pos, lines=1, location=BlitLocation.topLeft, base=False, colour=None):
        self.text_box.addText(text, pos, lines, location, base, colour)

        words = text.split()
        # print(words)

        for word in words:
            # self.screens["text"].add
            ...

    def update_display_text(self, text):
        self.text_box.refresh()
        self.text_box.addText(text, pg.Vector2(16, 11) * self.scale)

    def add_pokemon_sprites(self, pokemon):
        for pk in pokemon:
            self.screens["stats"].sprites.add(pk)

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
                current_health=self.friendly.health, max_health=self.friendly.stats.health,
                current_xp=self.friendly.exp - self.friendly.level_exp, max_xp=self.friendly.level_up_exp - self.friendly.level_exp,
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

        animation = PokeballCatchAnimation(sprite_id="pokeball")
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
        self.screens["text"].refresh()
        self.text_box.update_image()

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
            self.screens["stats"].get_object("friendly").update_pos()

        return display_surf


if __name__ == "__main__":
    import time

    pg.init()
    window = pg.display.set_mode(pg.Vector2(240, 180) * 2)

    bd = BattleDisplayMain(size=window.get_size())

    window.blit(bd.get_surface(), (0, 0))

    pg.event.pump()

    while True:
        time.sleep(1)

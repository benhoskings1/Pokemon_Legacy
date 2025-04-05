import os
from math import floor, ceil

from general.Environment import Environment
from screen_V2 import Screen, BlitLocation, Colours, FontOption
from battle_action import BattleAction, BattleAttack, BattleActionType
from sprite_screen import SpriteScreen, GameObjects, PokeballCatchAnimation
from pokemon import Pokemon
import pygame as pg

from font.Font import Font, LevelFont


class BattleDisplayV2(SpriteScreen):
    def __init__(self, window, size, time, environment: Environment):
        super().__init__(size, colour=Colours.black)

        self.window = window
        self.info_surface = pg.Surface(size, pg.SRCALPHA)

        self.image_scale = pg.Vector2(15 / 8, 15 / 8)

        self.load_image(f"Images/Battle/Backgrounds/{environment.value} {time.value}.png",
                        base=True, scale=self.image_scale)
        self.text_rect = self.load_image("Images/Battle/Top Screen/Text box.png", pg.Vector2(size.x / 2, size.y - 5),
                                         base=True, scale=self.image_scale,
                                         location=BlitLocation.midBottom)

        self.sprites = GameObjects([])

        self.friendly: Pokemon = None
        self.foe: Pokemon = None

        self.text: str = None

    def add_pokemon_sprites(self, pokemon):
        for pk in pokemon:
            self.sprites.add(pk)

        self.friendly = pokemon[0]
        self.foe = pokemon[1]

    def render_pokemon_details(self, opacity=None, friendly=False, lines=None):
        self.refresh()

        if opacity:
            offset = 120 * (1 - (opacity / 255))
        else:
            offset = 0

        # add pokemon names, level, hp,
        if self.foe.visible:
            detail_rect_foe = self.load_image("Images/Battle/Top Screen/Opponent HP.png",
                                              pg.Vector2(0 - offset * (not friendly), 21))

            wildRatio = (self.foe.health / self.foe.stats.health)
            # 50
            if self.foe.health > 0:
                wRect = pg.Rect(50, 41, 48 * wildRatio, 4)
                if self.foe.health >= self.foe.stats.health * 0.5:
                    wColour = "High"
                elif self.foe.health >= self.foe.stats.health * 0.25:
                    wColour = "Medium"
                else:
                    wColour = "Low"
            else:
                wRect = pg.Rect(0, 0, 0, 0)
                wColour = "Low"

            # Draw the health bar on the screen
            self.load_image(str.format("Images/Battle/Other/Health {}.png", wColour),
                            wRect.topleft, size=wRect.size)

        if self.friendly.visible:
            self.load_image("Images/Battle/Top Screen/Friendly HP.png", pg.Vector2(256 + offset * friendly, 97),
                            location=BlitLocation.topRight)
            fRatio = (self.friendly.health / self.friendly.stats.health)
            if self.friendly.health > 0:
                fRect = pg.Rect(198, 117, 48 * fRatio, 4)
                if self.friendly.health >= self.friendly.stats.health * 0.5:
                    fColour = "High"
                elif self.friendly.health >= self.friendly.stats.health * 0.25:
                    fColour = "Medium"
                else:
                    fColour = "Low"
            else:
                fRect = pg.Rect(0, 0, 0, 0)
                fColour = "Low"

            # Draw the health bar on the screen
            self.load_image(str.format("Images/Battle/Other/Health {}.png", fColour),
                            fRect.topleft, size=fRect.size)

        self.scale_surface(self.image_scale.x)

        # Display options for the wild Pokémon
        if self.foe.visible:
            # add the name of the Pokémon
            # print(detail_rect_foe, detail_rect_foe.size.scale_by(self.image_scale.x, self.image_scale.y))
            self.addText(self.foe.name, pos=pg.Vector2(int((4 - offset * (not friendly)) * 15 / 8), int(27 * 15 / 8)),
                         surface=self.info_surface,)

            # add the level of the Pokémon
            wildLevel = str.format("Lv{}", self.foe.level)
            self.addText(wildLevel, pg.Vector2(int((70 - offset * (not friendly)) * self.image_scale.x),
                                               int(29 * self.image_scale.x)), fontOption=FontOption.main.level,
                         surface=self.info_surface,)

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
            # # add the name of the Pokémon
            self.addText(self.friendly.name,
                         pg.Vector2(int((152 - offset * friendly) * 15 / 8), int(103 * 15 / 8)),
                         surface=self.info_surface,)

            # add the level of the Pokémon
            friendlyLevel = str.format("Lv{}", self.friendly.level)
            self.addText(friendlyLevel, pg.Vector2(int((221 - offset * friendly) * 15 / 8), int(105 * 15 / 8)),
                         fontOption=FontOption.level,
                         surface=self.info_surface,)

            # if the Pokémon has any status conditions, add display them
            if self.friendly.status:
                ...
                # self.loadImage(str.format("Images/Status Labels/{}.png", self.friendly.status.name),
                #                        pg.Vector2(int((152 - offset * friendly) * 15 / 8), int(103 * 15 / 8)))

            # add the text showing the Pokémon's health
            if self.friendly.health > 0:
                health = self.friendly.health
            else:
                health = 0

            self.addText(str.format("{0}/{1}", round(health), self.friendly.stats.health),
                         pg.Vector2(int((246 - offset * friendly) * 15 / 8), int(125 * 15 / 8)),
                         location=BlitLocation.topRight,
                         fontOption=FontOption.level,
                         surface=self.info_surface,)

        if self.text:
            if lines:
                self.addText(self.text, pg.Vector2(int(16 * 15 / 8), int(156 * 15 / 8)), lines=lines,
                             surface=self.info_surface,)
            else:
                self.addText(self.text, pg.Vector2(int(16 * 15 / 8), int(156 * 15 / 8)),
                             lines=ceil(len(self.text) / 28),
                             surface=self.info_surface,)

        # pg.draw.rect(self.surface, Colours.red.value, self.friendly.rect, width=2)
        # pg.draw.rect(self.surface, Colours.red.value, self.foe.rect, width=2)

    def intro_animations(self, window: pg.Surface, duration):
        if self.foe.animation:
            frames = len(self.foe.animation)
            for frame in self.foe.animation:
                self.foe.image = frame
                self.render_pokemon_details()
                window.blit(self.get_surface(), (0, 0))
                pg.display.flip()
                pg.time.delay(int(0.75 * duration / frames))
                self.refresh()

            self.foe.displayImage = self.foe.image
            pg.time.delay(int(0.25 * duration))
        else:

            pg.time.delay(duration)

        self.render_pokemon_details()
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
            self.render_pokemon_details()
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
                self.render_pokemon_details()
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
                self.render_pokemon_details()
                self.window.blit(self.get_surface(), (0, 0))
                pg.display.flip()
                pg.time.delay(int(timePerFrame))

        self.sprites.remove(animation)

    def refresh(self):
        self.surface = pg.Surface(self.size, pg.SRCALPHA)
        self.info_surface = pg.Surface(self.size, pg.SRCALPHA)
        self.sprite_surface = pg.Surface(self.size, pg.SRCALPHA)

    def get_surface(self, show_sprites=True):
        if self.power_off:
            return self.power_off_surface

        if show_sprites:
            self.sprites.draw(self)

        display_surf = self.base_surface.copy()
        display_surf.blit(self.surface, (0, 0))
        display_surf.blit(self.info_surface, (0, 0))
        display_surf.blit(self.sprite_surface, (0, 0))

        return display_surf


if __name__ == "__main__":
    import time

    pg.init()
    window = pg.display.set_mode(pg.Vector2(240, 180) * 2)

    bd = BattleDisplayV2(size=window.get_size())

    window.blit(bd.get_surface(), (0, 0))

    pg.event.pump()

    while True:
        time.sleep(1)

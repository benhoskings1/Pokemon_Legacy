import os
import re

import pygame as pg

from sprite_screen import SpriteScreen

ANIMATION_PATH = "assets/battle/move_animations"
FRAME_REGEX = r".*.png"


def get_image_frame(file_name):
    """ Extracts the number of the frame string using regex """
    match = re.search(r".*_(\d+).png", file_name)
    if match:
        return int(match.group(1))
    else:
        return None


class BattleAnimation:
    def __init__(self, move, target, size=None, opacity=255):
        self.sprite_screen = SpriteScreen(size=(256, 198))

        frame_files = sorted(os.listdir(os.path.join(ANIMATION_PATH, move, target)), key=get_image_frame)
        self.frames = [pg.image.load(os.path.join(ANIMATION_PATH, move, target, frame))
                       for frame in frame_files if re.match(FRAME_REGEX, frame)]

        if size:
            self.frames = [pg.transform.scale(frame, size) for frame in self.frames]
            if opacity != 255:
                for frame in self.frames:
                    frame.set_alpha(opacity)

        self.frame_pause = 15

    def get_frame(self, idx):
        return self.frames[idx]


if __name__ == "__main__":
    display = pg.display.set_mode((592, 384))
    background = pg.Surface(display.get_size())
    background.fill((255, 255, 255))

    animation = BattleAnimation(move="growl", friendly=False, size=display.get_size())

    pg.event.pump()

    while True:
        for frame in animation.frames:
            display.blit(background, (0, 0))
            display.blit(frame, (0, 0))
            pg.display.flip()
            pg.time.wait(15)

        display.blit(background, (0, 0))
        pg.display.flip()
        pg.time.wait(1500)


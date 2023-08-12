import pygame as pg


class Controller:
    def __init__(self, a=pg.K_d, b=pg.K_s, x=pg.K_w, y=pg.K_a,
                 up=pg.K_UP, down=pg.K_DOWN, left=pg.K_LEFT, right=pg.K_RIGHT):
        self.a = a
        self.b = b
        self.x = x
        self.y = y
        self.up = up
        self.down = down
        self.left = left
        self.right = right

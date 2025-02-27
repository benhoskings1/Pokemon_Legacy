import pygame as pg

from pokemon import Stats
from screen import Screen


class LevelUpDisplay:
    def __init__(self, size):
        self.screen = Screen(size)

        self.screen.loadImage("Images/Battle/Other/Stat Change.png", base=True)

        self.screen.addText2("Max. HP", pos=pg.Vector2(16, 16), base=True)
        self.screen.addText2("Attack", pos=pg.Vector2(16, 44), base=True)
        self.screen.addText2("Defence", pos=pg.Vector2(16, 72), base=True)
        self.screen.addText2("Sp. Atk", pos=pg.Vector2(16, 100), base=True)
        self.screen.addText2("Sp. Def", pos=pg.Vector2(16, 128), base=True)
        self.screen.addText2("Speed", pos=pg.Vector2(16, 156), base=True)
        self.screen.refresh()

    def getSurface(self):
        return self.screen.surface

    def update(self, newStats: Stats, oldStats: Stats = None):

        self.screen.refresh()
        if oldStats:
            self.screen.addText2(str.format("+ {}", newStats.health - oldStats.health),
                                 pos=pg.Vector2(self.screen.size.x - 56, 16))
            self.screen.addText2(str.format("+ {}", newStats.attack - oldStats.attack),
                                 pos=pg.Vector2(self.screen.size.x - 56, 44))
            self.screen.addText2(str.format("+ {}", newStats.defence - oldStats.defence),
                                 pos=pg.Vector2(self.screen.size.x - 56, 72))
            self.screen.addText2(str.format("+ {}", newStats.spAttack - oldStats.spAttack),
                                 pos=pg.Vector2(self.screen.size.x - 56, 100))
            self.screen.addText2(str.format("+ {}", newStats.spDefence - oldStats.spDefence),
                                 pos=pg.Vector2(self.screen.size.x - 56, 128))
            self.screen.addText2(str.format("+ {}", newStats.speed - oldStats.speed),
                                 pos=pg.Vector2(self.screen.size.x - 56, 156))
        else:
            self.screen.addText2(str(newStats.health), pos=pg.Vector2(self.screen.size.x - 56, 16))
            self.screen.addText2(str(newStats.attack), pos=pg.Vector2(self.screen.size.x - 56, 44))
            self.screen.addText2(str(newStats.defence), pos=pg.Vector2(self.screen.size.x - 56, 72))
            self.screen.addText2(str(newStats.spAttack), pos=pg.Vector2(self.screen.size.x - 56, 100))
            self.screen.addText2(str(newStats.spDefence), pos=pg.Vector2(self.screen.size.x - 56, 128))
            self.screen.addText2(str(newStats.speed), pos=pg.Vector2(self.screen.size.x - 56, 156))

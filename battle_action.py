from enum import Enum
import pygame as pg
from pokemon import Pokemon


class BattleActionType(Enum):
    attack = "attack",
    catch = "catch",
    heal = "heal",
    switch = "switch"


class BattleAction:
    def __init__(self, battle_action_type: BattleActionType, ):
        self.action_type = battle_action_type


class BattleAttack(pg.sprite.Sprite, BattleAction, ):
    def __init__(self, attacker: Pokemon):
        super().__init__()

        self.action_type = BattleActionType.attack

        self.image_size = pg.Vector2(60, 60)
        self.image = pg.Surface((60, 60), pg.SRCALPHA)
        pg.draw.circle(self.image, (255, 0, 0), (30, 30), 30)

        self.sprite_type = "animation"
        self.friendly_action = attacker.friendly

        self.frame_count = 10
        self.frame_idx = 0

        if self.friendly_action:
            print(attacker.rect.right)
            self.start_pos = attacker.rect.midright - pg.Vector2(0, self.image_size.y / 2)
        else:
            # print(attacker.rect.)
            self.start_pos = attacker.rect.midleft - pg.Vector2(self.image_size.x, self.image_size.y / 2)

        self.rect = pg.Rect(self.start_pos, self.image.get_size())

    def render_animation(self):
        frames = 10

    def update(self):
        if self.friendly_action:
            position = self.start_pos + pg.Vector2(14, -7) * self.frame_idx
        else:
            position = self.start_pos + pg.Vector2(-14, 7) * self.frame_idx

        self.rect = pg.Rect(position, self.image.get_size())

        return self.image


if __name__ == '__main__':
    attack = BattleAttack()

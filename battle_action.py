import os.path
from enum import Enum
import pygame as pg

from pokemon import Pokemon
from battle_animation import BattleAnimation


class BattleActionType(Enum):
    attack = "attack",
    catch = "catch",
    heal = "heal",
    switch = "switch"


class BattleAction:
    def __init__(self, battle_action_type: BattleActionType, ):
        self.action_type = battle_action_type


class BattleAttack(pg.sprite.Sprite, BattleAction, ):
    def __init__(self, target: Pokemon, move, animation_size=pg.Vector2(256, 192)):
        pg.sprite.Sprite.__init__(self)
        BattleAction.__init__(self, BattleActionType.attack)

        self.action_type = BattleActionType.attack

        self.image_size = pg.Vector2(60, 60)
        self.image = pg.Surface((60, 60), pg.SRCALPHA)
        # pg.draw.circle(self.image, (255, 0, 0), (30, 30), 30)

        self.sprite_type = "animation"
        self.friendly_action = target.friendly

        if os.path.isdir(f"assets/battle/move_animations/{move.name}"):
            self.animation = BattleAnimation(move=move.name.lower(), size=animation_size, friendly=self.friendly_action)
            self.frame_count = len(self.animation.frames)
            self.frame_idx = 0
        else:
            self.animation = None
            self.frame_count, self.frame_idx = 0, 0

    def get_animation_frame(self, idx):
        return self.animation.get_frame(idx)


if __name__ == '__main__':
    attack = BattleAttack()

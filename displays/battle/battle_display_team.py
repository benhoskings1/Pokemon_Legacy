import os
import sys
import time

from pygame import Surface

import pokemon
from screen_V2 import Colours, FontOption, Screen, BlitLocation
from sprite_screen import SpriteScreen, PokeballCatchAnimation
from pokemon import Pokemon, PokemonSpriteSmall
import pygame as pg
from enum import Enum

from displays.battle.battle_display_touch import DisplayContainer
from general.utils import create_display_bar
from general.Item import Pokeball, MedicineItem, BattleItemType
from general.Move import Move2


TEAM_CONTAINER_POSITIONS = [(1, 1), (129, 9), (1, 49), (129, 56), (1, 96), (129, 104)]


# =========== SETUP =============
class TeamDisplayStates(Enum):
    home = 0
    select = 1
    summary = 2
    moves = 3
    move_summary = 4




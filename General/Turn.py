from enum import Enum

from Pokemon import Pokemon


class Action(Enum):
    fight = 1
    bag = 2
    run = 3
    pokemon = 4
    learnMove = 5
    evolve = 6


class Turn:
    def __init__(self, pokemon: Pokemon):
        self.pokemon = pokemon
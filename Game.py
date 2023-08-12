import json
import os
import pickle
import random
from datetime import datetime

import pandas as pd
import pygame as pg

from Bag import Bag
from Battle import Battle, State
from Displays.LoadDisplay import LoadDisplay
from General.Animations import createAnimation
from General.Colours import Colours
from General.Controller import Controller
from General.Direction import Direction
from General.Time import Time
from Map_Files.TiledMap import TiledMap
from Player import Player, Movement
from Pokemon import Pokemon
from Poketech.Poketech import Poketech
from Team import Team

pokedex = pd.read_csv("Game Data/Pokedex/Local Dex.tsv", delimiter='\t', index_col=1)


class Game:
    def __init__(self, scale, optimize=False, new=False, fromPickle=False, overwrite=False):

        self.overwrite: str = overwrite

        if new:
            self.dataPath = "Game Data/Save States/Start"
        else:
            self.dataPath = "Game Data/Save States/Current Game"

        self.running = True

        self.time = datetime.now()
        self.timeOfDay = self.getTimeOfDay()
        self.controller = Controller()

        self.displaySize = pg.Vector2(480, 720)

        # load all attributes which utilise any pygame surfaces!

        self.window = pg.display.set_mode(self.displaySize)
        self.topSurf = self.window.subsurface(((0, 0), (self.displaySize.x, self.displaySize.y / 2)))
        self.bottomSurf = self.window.subsurface(((0, self.displaySize.y / 2),
                                                  (self.displaySize.x, self.displaySize.y / 2)))
        self.bottomSurf.fill(Colours.white.value)
        self.loadDisplay = LoadDisplay(self.topSurf.get_size())
        self.map = TiledMap("Map_Files/Sinnoh Map.tmx", scale=scale)

        self.animations = {}

        with open(os.path.join(self.dataPath, "Team.json"), "r") as read_file:
            # Convert JSON file to Python Types
            teamData = json.load(read_file)

        self.team = Team(teamData)

        for pk in self.team.pokemon:
            if not (pk.name in self.animations.keys()):
                self.loadDisplay.loadTeam(pk.name)
                top, bottom = self.loadDisplay.getScreens()
                self.topSurf.blit(top, (0, 0))
                self.bottomSurf.blit(bottom, (0, 0))
                pg.display.flip()
                print("Creating ", pk.name)
                self.animations[pk.name] = createAnimation(pk.name)
                animations = self.animations[pk.name]
                pk.loadImages(animations)
            else:
                pk.loadImages(self.animations[pk.name])

        self.team.pokemon = self.team.pokemon

        with open(os.path.join(self.dataPath, "Bag.json"), "r") as read_file:
            # Convert JSON file to Python Types
            bagData = json.load(read_file)

        self.bag = Bag(**bagData)

        spriteDirectory = "Sprites/Pokemon Sprites/Gen IV 2"

        if fromPickle and not os.path.exists(os.path.join(self.dataPath, "Game.pickle")):
            print("No pickle data not present / corrupted")

        if fromPickle and os.path.exists(os.path.join(self.dataPath, "Game.pickle")):
            gameFile = open(os.path.join(self.dataPath, "game.pickle"), 'rb')
            gameData = pickle.load(gameFile, encoding='bytes')

            # update player with the Surfaces
            self.player = gameData.player
            self.player.loadSurfaces("Sprites/Player Sprites")
            self.player.walkingSpriteSet.scaleSprites(1.4)
            self.player.runningSpriteSet.scaleSprites(1.4)
            self.player.update()

            # update poketech with the Surfaces
            self.poketech = gameData.poketech
            self.poketech.loadSurfaces(self.time)

            # update each of the Pokémon with their surfaces

            if gameData.battle:
                self.battle = Battle(self, pickleData=gameData.battle)
            else:
                self.battle = None

            self.appearances = gameData.appearances

        else:
            # create new player instance
            self.player = Player("Sprites/Player Sprites", position=pg.Vector2(10, 9))
            self.player.walkingSpriteSet.scaleSprites(1.4)
            self.player.runningSpriteSet.scaleSprites(1.4)
            self.player.update()

            self.poketech = Poketech(self.time)

            self.battle = None

            self.appearances = {}

        if optimize:
            totalSeen = 0
            for key in self.appearances:
                totalSeen += int(self.appearances[key])

            if totalSeen != 0:
                for idx, name in enumerate(pokedex.index):
                    if name in self.appearances.keys():
                        appearanceRatio = self.appearances[name] / totalSeen
                        if appearanceRatio >= 0.4:
                            print(name, appearanceRatio)
                            directory = os.path.join(spriteDirectory, name)
                            self.loadDisplay.updateAnimationLocation(directory)
                            top, bottom = self.loadDisplay.getScreens()
                            self.topSurf.blit(top, (0, 0))
                            self.bottomSurf.blit(bottom, (0, 0))
                            pg.display.flip()
                            pkAnimations = createAnimation(name)
                            self.animations[name] = pkAnimations

        # happens after all attributes initialised
        self.loadDisplay.finish()
        top, bottom = self.loadDisplay.getScreens()
        self.topSurf.blit(top, (0, 0))
        self.bottomSurf.blit(bottom, (0, 0))
        pg.display.flip()
        pg.time.delay(750)

        self.fadeToBlack(500)

    def createPokemon(self, name, friendly=False, level=None, exp=None, moveNames=None, EVs=None, IVs=None, shiny=None,
                      appearance=True, location=None):

        if appearance and name not in self.appearances:
            self.appearances[name] = 1
        elif appearance:
            self.appearances[name] += 1

        if not (name in self.animations.keys()):
            print("Creating ", name)
            self.animations[name] = createAnimation(name)

        animations = self.animations[name]

        pokemon = Pokemon(name, Level=level, XP=exp, Move_Names=moveNames, EVs=EVs, IVs=IVs,
                          Friendly=friendly, Shiny=shiny)

        pokemon.animation = animations.front

        return pokemon

    def fadeToBlack(self, duration):
        blackSurf = pg.Surface(self.topSurf.get_size())
        blackSurf.fill(Colours.black.value)
        blackSurf.set_alpha(0)
        count = 100
        for t in range(0, count):
            blackSurf.set_alpha(t / count * 255)
            pg.time.delay(int(duration / count))
            self.topSurf.blit(blackSurf, (0, 0))
            self.bottomSurf.blit(blackSurf, (0, 0))
            pg.display.flip()

    def fadeFromBlack(self, duration, battle=False):
        blackSurf = pg.Surface(self.topSurf.get_size())
        blackSurf.fill(Colours.black.value)
        blackSurf.set_alpha(255)
        count = 100
        for t in range(0, count):
            blackSurf.set_alpha((count - t) / count * 255)
            pg.time.delay(int(duration / count))
            if not battle:
                self.updateDisplay(flip=False)
            else:
                if self.battle.state == State.home:
                    self.battle.updateScreen(cover=True, flip=False)
                else:
                    self.battle.updateScreen(flip=False)

            self.topSurf.blit(blackSurf, (0, 0))
            self.bottomSurf.blit(blackSurf, (0, 0))
            pg.display.flip()

    def getTimeOfDay(self):
        if 6 < self.time.hour <= 16:
            return Time.day
        elif 16 < self.time.hour <= 20:
            return Time.evening
        else:
            return Time.night

    def updateDisplay(self, flip=True):
        self.topSurf.blit(self.map.getSurface(self.topSurf.get_size(), self.player.position), (0, 0))
        self.topSurf.blit(self.player.image, pg.Vector2(self.topSurf.get_rect().center) -
                          pg.Vector2(self.player.image.get_rect().centerx,
                                     self.map.data.tilewidth * self.map.scale / 2 + 16))

        # pg.draw.line(self.topSurf, Colours.black.value, self.topSurf.get_rect().midtop,
        #              self.topSurf.get_rect().midbottom, 5)
        # pg.draw.line(self.topSurf, Colours.black.value, self.topSurf.get_rect().midleft,
        #              self.topSurf.get_rect().midright, 5)

        self.bottomSurf.blit(self.poketech.getSurface(), (0, 0))
        if flip:
            pg.display.flip()

    def movePlayer(self, direction, detectGrass=True):
        if self.player.movement == Movement.walking:
            self.player.sprites = self.player.walkingSpriteSet.sprites

        elif self.player.movement == Movement.running:
            self.player.sprites = self.player.runningSpriteSet.sprites

        self.player.image = self.player.sprites[self.player.spriteIdx]

        moved = False

        if self.player.leg:
            self.player.image = self.player.sprites[self.player.spriteIdx + 1]
        else:
            self.player.image = self.player.sprites[self.player.spriteIdx + 2]

        if self.player.facingDirection == direction:
            if not self.checkCollision(direction):
                moved = True
                # shift the map
                if self.player.movement == Movement.walking:
                    self.moveAnimation(direction, 200)
                elif self.player.movement == Movement.running:
                    self.moveAnimation(direction, 125)

        self.player.image = self.player.sprites[self.player.spriteIdx]

        self.updateDisplay()
        if moved:
            if detectGrass:
                self.detectGrassCollision()
            self.player.steps += 1
            self.poketech.pedometerSteps += 1
            self.poketech.updatePedometer()

        self.player.facingDirection = direction
        self.player.leg = not self.player.leg

        if not moved:
            # add an optional delay here
            pass

        return moved

    def checkCollision(self, direction):
        playerPos = self.player.position + direction.value

        for obstacle in self.map.obstacles.sprites():
            if obstacle.rect.collidepoint(playerPos * self.map.data.tilewidth * self.map.scale):
                return True

        return False

    def moveAnimation(self, direction, duration):
        frames = 20

        if self.player.leg:
            self.player.image = self.player.sprites[self.player.spriteIdx + 1]
        else:
            self.player.image = self.player.sprites[self.player.spriteIdx + 2]

        for frame in range(frames):
            self.player.position += direction.value / frames
            self.updateDisplay()
            pg.time.delay(int(duration / frames))

        self.player.image = self.player.sprites[self.player.spriteIdx]
        self.player.position = pg.Vector2(round(self.player.position.x), round(self.player.position.y))

    def detectGrassCollision(self, battle=False):
        for grass in self.map.grassObjects:
            coordinate = self.player.position * self.map.data.tilewidth * self.map.scale
            if grass.rect.collidepoint(coordinate):
                if coordinate.x != grass.rect.right:
                    if battle:
                        location = grass.route
                        pg.time.delay(100)
                        self.battleIntro(250)
                        self.startBattle(route=location)
                    else:
                        num = random.randint(0, 255)
                        if num < grass.encounterNum:
                            location = grass.route
                            pg.time.delay(100)
                            self.battleIntro(250)
                            self.startBattle(route=location)

    def startBattle(self, route="Route 201", name=None, level=None):
        battle = Battle(self, routeName=route, wildName=name, wildLevel=level)
        self.battle = battle
        battle.loop2()
        self.battle = None

    def battleIntro(self, time):
        blackSurf = pg.Surface(self.topSurf.get_size())
        blackSurf.fill(Colours.darkGrey.value)
        for count in range(2):
            self.topSurf.blit(blackSurf, (0, 0))
            pg.display.flip()
            pg.time.delay(time)
            self.updateDisplay()

    def addPokemon(self, pk):
        self.team.pokemon.append(pk)

    def loop(self):
        if self.battle:
            self.battle.updateScreen(flip=False)
            self.fadeFromBlack(500, battle=True)
            self.battle.loop2()
            self.battle = None
            self.updateDisplay()
        else:
            self.updateDisplay(flip=False)
            self.fadeFromBlack(500)

        while self.running:
            pg.time.delay(25)  # set the debounce-time for keys
            keys = pg.key.get_pressed()
            mouse = pg.mouse.get_pressed()
            if keys[self.controller.up]:
                self.player.spriteIdx = 0
                self.movePlayer(Direction.up)
            elif keys[self.controller.down]:
                self.player.spriteIdx = 3
                self.movePlayer(Direction.down)
            elif keys[self.controller.left]:
                self.player.spriteIdx = 6
                self.movePlayer(Direction.left)
            elif keys[self.controller.right]:
                self.player.spriteIdx = 9
                self.movePlayer(Direction.right)

            elif keys[pg.K_h]:
                print("Restoring all pokemon in team")
                for pk in self.team.pokemon:
                    pk.restore()

                pg.time.delay(100)

            if keys[self.controller.b]:
                self.player.movement = Movement.running

            else:
                if self.player.movement != Movement.walking:
                    self.player.movement = Movement.walking
                    self.player.update()
                    self.updateDisplay()

            if any(mouse):
                self.poketech.interact(pg.mouse.get_pos())
                self.updateDisplay()
                pg.time.delay(100)

            if self.time.minute != datetime.now().minute:
                self.updateDisplay()

            for event in pg.event.get():
                if event.type == pg.QUIT:
                    self.running = False

        if self.overwrite:
            self.save()

    def demo(self):
        pg.event.pump()
        self.player.position = pg.Vector2(10, 9)

        self.player.spriteIdx = 9
        for step in range(10):
            self.movePlayer(Direction.right)
            pg.time.delay(25)

        self.player.movement = Movement.running
        self.player.update()

        for step in range(6):
            self.movePlayer(Direction.right)
            pg.time.delay(25)

        for idx in [3, 6, 0, 9, 3]:
            self.player.spriteIdx = idx
            self.player.update()
            self.updateDisplay()
            pg.time.delay(750)

        self.player.movement = Movement.walking
        self.player.update()

        for step in range(4):
            self.player.spriteIdx = 3
            self.movePlayer(Direction.down, detectGrass=False)

        pg.time.delay(500)
        self.movePlayer(Direction.down, detectGrass=False)
        self.detectGrassCollision(battle=True)

        while True:
            pg.time.delay(1000)
            pg.event.pump()

    def save(self):
        if not os.path.exists("Game Data/Save States/Save Test"):
            os.mkdir("Game Data/Save States/Save Test")
        try:
            teamData = []
            for pokemon in self.team.pokemon:
                teamData.append(pokemon.getJSONData())

            with open("Game Data/Save States/Save Test/Team.json", "w") as write_file:
                json.dump(teamData, write_file, indent=4)

            bagData = self.bag.getJSONData()

            with open("Game Data/Save States/Save Test/Bag.json", "w") as write_file:
                json.dump(bagData, write_file, indent=4)

            # need to set all pygame surfaces to none
            self.animations = None
            self.loadDisplay = None
            self.map = None

            # the player image is a pygame surface
            self.player.clearSurfaces()

            self.poketech.clearSurfaces()

            self.bag = None

            self.team = None

            self.window = None
            self.topSurf = None
            self.bottomSurf = None

            if self.battle:
                self.battle.clearSurfaces()

            with open("Game Data/Save States/Save Test/Game.pickle", 'wb') as f:
                pickle.dump(self, f)
                print("Successfully pickled")

            # can
            for root, dirs, files in os.walk("Game Data/Save States/Current Game", topdown=False):
                for name in files:
                    os.remove(os.path.join(root, name))
                for name in dirs:
                    os.rmdir(os.path.join(root, name))

            os.rename("Game Data/Save States/Save Test", "Game Data/Save States/Current Game")

        except TypeError:
            print("Pickle Failed")
            print("The data was not overwritten")
            for root, dirs, files in os.walk("Game Data/Save States/Save Test", topdown=False):
                for name in files:
                    os.remove(os.path.join(root, name))
                for name in dirs:
                    os.rmdir(os.path.join(root, name))

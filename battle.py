import datetime
import math
from enum import Enum
from math import floor
from random import randint

import pygame as pg

from battle_action import BattleAction, BattleActionType, BattleAttack
from Displays.bag_display import BagAction
from Displays.battle_display import BattleDisplayV2
from Displays.BattleDisplay import BattleDisplay
from Displays.EvolveDisplay import EvolveDisplay
from Displays.HomeDisplay import HomeDisplay, HomeAction
from Displays.LearnMove import LearnMoveDisplay, LearnAction
from Displays.LevelUpDisplay import LevelUpDisplay
from Displays.MoveDisplay import MoveDisplay, FightAction
from Displays.team_display_battle import PartyAction
from general.Animations import createAnimation
from general.Colours import Colours
from general.Condition import StatusCondition
from general.Environment import Environment
from general.Image import Image
from general.Item import Item, Pokeball, MedicineItem
from general.Route import Route
from general.Status_Conditions.Burn import Burn
from general.Status_Conditions.Poison import Poison
from pokemon import Pokemon
from team import Team


class State(Enum):
    home = 0
    fight = 1
    bag = 2
    run = 3
    pokemon = 4
    learnMove = 5
    evolve = 6


class Battle:
    def __init__(self, game, environment=Environment.grassland, routeName="Route 201", wildName=None, wildLevel=None,
                 pickleData=None):
        self.game = game
        self.running = True
        self.catchLocation = routeName
        self.pokemon_team: Team = game.team

        # set up the displays

        self.friendly: Pokemon = self.pokemon_team.get_active_pokemon()
        friendlyMoves = self.friendly.moves

        self.screenSize = pg.Vector2(game.topSurf.get_size())

        if pickleData:
            self.foe = pickleData.foe
            # load foe images and animation
            if not (self.foe.name in self.game.animations.keys()):
                self.game.loadDisplay.loadFoe(self.foe.name)
                top, bottom = self.game.loadDisplay.getScreens()
                self.game.topSurf.blit(top, (0, 0))
                self.game.bottomSurf.blit(bottom, (0, 0))
                pg.display.flip()
                print("Creating ", self.foe.name)
                self.game.animations[self.foe.name] = createAnimation(self.foe.name)

            animations = self.game.animations[self.foe.name]
            self.foe.loadImages(animations)

            self.environment = pickleData.environment
            self.timeOfDay = pickleData.timeOfDay

            self.battleDisplay = BattleDisplay(self.screenSize, self.environment, self.timeOfDay)
            self.battleDisplay.text = pickleData.battleDisplay.text

            self.state = pickleData.state

            self.movesToLearn = pickleData.movesToLearn

        else:

            # wild pokemon
            if not wildName:
                route = Route(routeName)
                pkName, pkLevel = route.encounter(game.time)

                self.foe: Pokemon = self.game.createPokemon(pkName, level=pkLevel)
            else:
                if wildLevel:
                    self.foe: Pokemon = self.game.createPokemon(wildName, level=wildLevel)
                else:
                    self.foe: Pokemon = self.game.createPokemon(wildName, level=10)

            self.environment = environment
            self.timeOfDay = self.game.getTimeOfDay()

            self.battleDisplay = BattleDisplay(self.screenSize, self.environment, self.timeOfDay)
            self.battleDisplay.text = str.format("A wild {} appeared!", self.foe.name)

            self.state = State.home

            self.movesToLearn = None

        self.activePokemon = [self.friendly, self.foe]

        self.battle_display = BattleDisplayV2(self.game.topSurf ,self.screenSize, self.timeOfDay, self.environment)
        self.battle_display.add_pokemon_sprites(self.activePokemon)

        # Top screen
        self.homeDisplay = HomeDisplay(self.screenSize)  # Home screen
        self.moveDisplay = MoveDisplay(self.screenSize, friendlyMoves)  # Move screen

        self.learnMoveDisplay = LearnMoveDisplay(self.screenSize)  # Learn Move Screens
        self.levelUpDisplay = LevelUpDisplay((254, 196))

        self.evolveDisplay = EvolveDisplay(self.screenSize)  # Evolve Screens

        self.moveDisplay.updateScreen(self.friendly.moves)
        self.moveDisplay.update(self.game.controller)
        self.battleDisplay.updateScreen(self.friendly, self.foe)

        lowerScreenBase = pg.image.load("Images/Battle/Other/Lower Base.png")
        self.lowerScreenBase = pg.transform.scale(lowerScreenBase, game.bottomSurf.get_size())

        self.displayFriendly = True
        self.displayWild = True

        if not pickleData:
            pg.event.pump()
            print("starting animation")
            self.battle_display.intro_animations(self.game.topSurf, 2000)

    def updateUpperScreen(self, opacity=None, friendly=False):
        if self.state != State.evolve:
            self.battle_display.render_pokemon_details()
            self.game.topSurf.blit(self.battle_display.get_surface(show_sprites=True), (0, 0))
        else:
            self.game.topSurf.blit(self.evolveDisplay.getUpperSurface(), (0, 0))

    def updateLowerScreen(self, cover=False):
        if cover:
            self.game.bottomSurf.blit(self.lowerScreenBase, (0, 0))
        elif self.state == State.home:
            # self.updateHomeScreen()
            self.game.bottomSurf.blit(self.homeDisplay.getSurface(), (0, 0))
        elif self.state == State.fight:
            self.game.bottomSurf.blit(self.moveDisplay.getSurface(), (0, 0))
        elif self.state == State.learnMove:
            self.game.bottomSurf.blit(self.learnMoveDisplay.getSurface(), (0, 0))
        elif self.state == State.evolve:
            self.game.bottomSurf.blit(self.evolveDisplay.getLowerSurface(), (0, 0))

    def updateScreen(self, cover=False, flip=True):
        self.updateUpperScreen()
        self.updateLowerScreen(cover)
        if flip:
            pg.display.flip()

    def fightLogic(self, keys):
        action = self.moveDisplay.update(self.game.controller, keys=keys)
        self.updateScreen()
        if action == FightAction.home:
            self.state = State.home
        elif action != FightAction.nothing:
            return action

        return None

    def homeLogic(self, keys):
        action = self.homeDisplay.update(keys, self.game.controller)
        if action != HomeAction.nothing:
            self.state = State(action.value + 1)
        self.updateScreen()

    def learnLogic(self, move):
        if len(self.friendly.moves) == 4:
            self.state = State.learnMove
            self.displayMessage(str.format("{} wants to learn the move {}", self.friendly.name,
                                           move.name), 1500)
            self.displayMessage(str.format("But {} can't learn more than 4 moves.", self.friendly.name), 1500)
            self.displayMessage("Make it forget another move?", 1500)

            self.learnMoveDisplay = LearnMoveDisplay(self.screenSize)
            self.learnMoveDisplay.updateScreens(self.friendly, move)

            action = None
            while not action:
                pg.time.delay(100)  # set the debounce-time for keys
                keys = pg.key.get_pressed()
                action = self.learnMove(self.learnMoveDisplay, keys, move)
                self.quitCheck()
        else:
            self.displayMessage(str.format("{} learnt {}", self.friendly.name, move.name), 1000)
            self.friendly.moves.append(move)
            self.friendly.moveNames.append(move.name)

    def displayMessage(self, text, duration=None):
        self.battle_display.text = text
        self.battleDisplay.text = text
        self.updateUpperScreen()
        self.game.bottomSurf.blit(self.lowerScreenBase, (0, 0))
        pg.display.flip()
        if duration:
            pg.time.delay(duration)

    def displayMessageEvolve(self, text, image, time):
        self.evolveDisplay.text = text
        self.evolveDisplay.update(image)
        self.updateScreen()
        pg.time.delay(time)

    def learnMove(self, display, keys, move):
        action, text = display.update(keys, self.game.controller, self.friendly, move)
        self.battleDisplay.text = text
        self.updateScreen()
        if action == LearnAction.giveUp:
            self.displayMessage(str.format("{} did not learn {}", self.friendly.name, move.name), 1000)

            self.running = False

            return True

        elif action != LearnAction.nothing:

            self.displayMessage("1 2 and... ... Poof!", 1000)

            self.displayMessage(str.format("{} forgot how to use {}", self.friendly.name,
                                           self.friendly.moves[action.value].name), 1000)

            self.displayMessage("And...", 800)

            self.displayMessage(str.format("Learned {}", move.name), 1000)

            self.friendly.moves[action.value] = move

            return True

        return False

    def attack(self, attacker: Pokemon, target: Pokemon, move):

        displayTime, graphicsTime, attackTime, effectTime = 500, 500, 1000, 1000

        frames = 100
        attackTimePerFrame = attackTime / frames

        [damage, effective, inflictCondition, heal, modify, hits, crit] = attacker.useMove(move, target)

        if target.health < damage:
            damage = target.health + 1

        self.game.bottomSurf.blit(self.lowerScreenBase, (0, 0))

        hitCount = 0
        for hit in range(hits):
            if target.health > 0:
                hitCount += 1
                if hit == 0:
                    self.displayMessage(f"{attacker.name} used {move.name}!", displayTime)
                else:
                    self.displayMessage(None, displayTime)

                # Do attack graphics
                battle_attack = BattleAttack(attacker=attacker)
                self.battle_display.sprites.add(battle_attack)

                for frame in range(battle_attack.frame_count):
                    battle_attack.frame_idx = frame
                    battle_attack.update()
                    self.game.topSurf.blit(self.battle_display.get_surface(show_sprites=True), (0, 0))
                    pg.display.flip()
                    pg.time.delay(80)
                    self.battle_display.refresh()

                self.battle_display.sprites.remove(battle_attack)

                # Health reduction
                self.reduceHealth(target, damage, frames, attackTimePerFrame)

        if heal:
            health = floor(damage * (heal / 100))
            if health == 0:
                health = 1

            attacker.health += health
            if attacker.health > attacker.stats.health:
                attacker.health = attacker.stats.health

            self.displayMessage(str.format("{} had its energy drained", target.name), 1000)

        if target.health > 0:
            if inflictCondition:
                for condition in StatusCondition:
                    if condition.value.name == inflictCondition:
                        self.displayMessage(str.format("The wild {} was {}nd", target.name, inflictCondition), 1000)
                        target.status = condition.value

        if damage != 0:
            if crit:
                self.displayMessage("A critical hit!", effectTime)

            if hits != 1:
                self.displayMessage(str.format("Hit {} times(s)", hitCount), effectTime)

            if effective != 1:
                if effective > 1:
                    self.displayMessage("It's super effective", effectTime)
                else:
                    self.displayMessage("It's not very effective...", effectTime)

        if target.health > 0:
            if modify:
                limit = False
                if modify[3] == "Raise":
                    change = modify[0]
                    descriptor = "rose"
                    if abs(change) > 1:
                        descriptor = "sharply rose"
                else:
                    change = -modify[0]
                    descriptor = "fell"
                    if abs(change) > 1:
                        descriptor = "harshly fell"

                if modify[2] == "Self":
                    modified = attacker
                else:
                    modified = target

                if modify[1] == "Attack":
                    modified.statStages.attack += change
                    if modified.statStages.attack < -6:
                        modified.statStages.attack = -6
                        limit = True
                    elif modified.statStages.attack > 6:
                        modified.statStages.attack = 6
                        limit = True

                elif modify[1] == "Defence":
                    modified.statStages.defence += change
                    if modified.statStages.defence < -6:
                        modified.statStages.defence = -6
                        limit = True
                    elif modified.statStages.defence > 6:
                        modified.statStages.defence = 6
                        limit = True

                elif modify[1] == "Sp Attack":
                    modified.statStages.spAttack += change
                    if modified.statStages.spAttack < -6:
                        modified.statStages.spAttack = -6
                        limit = True
                    elif modified.statStages.spAttack > 6:
                        modified.statStages.spAttack = 6
                        limit = True
                elif modify[1] == "Sp Defence":
                    modified.statStages.spDefence += change
                    if modified.statStages.spDefence < -6:
                        modified.statStages.spDefence = -6
                        limit = True
                    elif modified.statStages.spDefence > 6:
                        modified.statStages.spDefence = 6
                        limit = True
                elif modify[1] == "Speed":
                    modified.statStages.speed += change
                    if modified.statStages.speed < -6:
                        modified.statStages.speed = -6
                        limit = True
                    elif modified.statStages.speed > 6:
                        modified.statStages.speed = 6
                        limit = True

                if modified.friendly:
                    start = ""
                else:
                    start = "The wild "

                if limit:
                    if change > 0:
                        descriptor = "won't go any higher"
                    else:
                        descriptor = "won't go any lower"

                self.displayMessage(str.format("{}{}'s {} {}", start, modified.name, modify[1], descriptor), 2000)

        target.health = round(target.health)
        self.battleDisplay.text = str.format("What will {} do?", self.friendly.name)

    def fadeOut(self, duration):
        blackSurf = pg.Surface(self.screenSize)
        blackSurf.fill(Colours.black.value)
        blackSurf.set_alpha(0)
        count = 100
        for t in range(0, count):
            blackSurf.set_alpha(t / count * 255)
            pg.time.delay(int(duration / count))
            self.game.topSurf.blit(blackSurf, (0, 0))
            self.game.bottomSurf.blit(blackSurf, (0, 0))
            pg.display.flip()

    def wildKO(self):
        self.friendly.updateEVs(self.foe.name)
        self.battleDisplay.text = str.format("The wild {} fainted", self.foe.name)
        self.updateUpperScreen()
        pg.display.flip()
        self.KOAnimation(1500)
        self.gainExp(1500)
        [levelUp, levels, moves] = self.friendly.checkLevelUp()
        if levelUp:
            self.levelUpFriendly(levels)

        if self.friendly.level > self.friendly.evolveLevel:
            self.state = State.evolve
            # evolvedPk = Pokemon(name, friendly=True, level=level, exp=exp, moveNames=moves, EVs=EVs, IVs=IVs)
            evolutionName = self.friendly.getEvolution()
            evolution = Pokemon(evolutionName, Friendly=True,
                                Level=self.friendly.level, XP=self.friendly.exp,
                                Move_Names=self.friendly.moveNames, EVs=self.friendly.EVs,
                                IVs=self.friendly.IVs)

            evolution.switchImage("front")
            self.evolveAnimation(evolution)

        if moves and levelUp:
            self.movesToLearn = moves
            print(self.movesToLearn)
            for move in self.movesToLearn:
                self.learnLogic(move)
                self.movesToLearn: list
                self.movesToLearn.pop(self.movesToLearn.index(move))

    def friendlyKO(self):
        self.battleDisplay.text = str.format("{} fainted!", self.friendly.name)
        self.updateUpperScreen()
        pg.display.flip()
        self.KOAnimation(1500, friendly=True)

    def catchWild(self):
        self.catchAnimation(8000)
        self.updateUpperScreen()
        pg.display.flip()
        pg.time.delay(1000)
        self.foe.switchImage()
        self.game.addPokemon(self.foe)
        self.displayWild = False
        self.running = False

    def levelUpFriendly(self, levels, duration=1000):
        for level in range(levels):
            self.friendly.level += 1

            prevStats = self.friendly.stats
            self.battleDisplay.text = str.format("{0} grew to Lv. {1}!", self.friendly.name, self.friendly.level)

            self.friendly.updateStats()
            newStats = self.friendly.stats
            self.friendly.health += newStats.health - prevStats.health

            self.battleDisplay.updateScreen(self.friendly, self.foe, lines=2)
            self.levelUpDisplay.update(newStats, oldStats=prevStats)
            self.battleDisplay.screen2.surface.blit(self.levelUpDisplay.getSurface(), pg.Vector2(226, 90))
            self.game.topSurf.blit(self.battleDisplay.getSurface(), (0, 0))
            pg.display.flip()
            pg.time.delay(duration)

            self.battleDisplay.updateScreen(self.friendly, self.foe, lines=2)
            self.levelUpDisplay.update(newStats)
            self.battleDisplay.screen2.surface.blit(self.levelUpDisplay.getSurface(), pg.Vector2(226, 90))
            self.game.topSurf.blit(self.battleDisplay.getSurface(), (0, 0))
            pg.display.flip()
            pg.time.delay(duration)

    def gainExp(self, duration):
        xpGain = round(self.foe.getFaintXP())
        self.friendly.exp += xpGain
        self.battleDisplay.text = str.format("{0} gained {1} Exp. Points", self.friendly.name, xpGain)
        self.updateUpperScreen()
        pg.display.flip()
        pg.time.delay(duration)

    def evolveAnimation(self, evolution):

        self.friendly.switchImage(direction="front")

        self.displayMessageEvolve("What?", self.friendly.image, 1000)

        self.displayMessageEvolve(str.format("{} is evolving", str.upper(self.friendly.name)),
                                  self.friendly.image, 1000)

        finalHeight = 40
        increment = 1
        height = 0
        duration = 1500

        while height < finalHeight:
            height += increment
            self.evolveDisplay.cropScreen(height)
            self.updateScreen()
            pg.time.delay(int(duration / (finalHeight / increment)))

        image = Image(self.friendly.image)
        evoImage = Image(evolution.image)
        # shrink image

        self.scaleAnimation(500, 1, 0.05, 0.5, image, height)

        self.scaleAnimation(500, 0.5, 0.05, 1, evoImage, height, white=True)
        count = 0
        for i in range(3):
            self.scaleAnimation(300 * (1 - (count / 12)), 1, 0.05, 0.5, image, height, white=True)
            count += 1
            self.scaleAnimation(300 * (1 - (count / 12)), 0.5, 0.05, 1, evoImage, height, white=True)
            count += 1
            self.scaleAnimation(300 * (1 - (count / 12)), 1, 0.05, 0.5, image, height, white=True)
            count += 1
            self.scaleAnimation(300 * (1 - (count / 12)), 0.5, 0.05, 1, evoImage, height, white=True)
            count += 1

        self.evolveDisplay.update(evoImage.baseSurface)
        self.updateScreen()

        pg.time.delay(300)
        self.evolveDisplay.text = str.format("Congratulations! Your {} evolved into {}", self.friendly.name,
                                             evolution.name)
        self.evolveDisplay.update(evoImage.baseSurface)
        self.updateScreen()
        pg.time.delay(1000)

        idx = self.pokemon_team.active_index
        self.game.team.pokemon[idx] = evolution

        evolution.switchImage("back")

        self.friendly = evolution

    def scaleAnimation(self, duration, startScale, increment, finalScale, image, cropHeight, white=False):
        if startScale < finalScale:
            while startScale < finalScale:
                startScale += increment
                image.scale(pg.Vector2(startScale, startScale))
                if white:
                    image.replaceWithWhite()

                self.evolveDisplay.update(image.surface)
                self.evolveDisplay.cropScreen(cropHeight)
                self.updateScreen()
                pg.time.delay(int(duration / ((finalScale - 0.5) / increment)))
        else:
            while startScale > finalScale:
                startScale -= increment
                image.scale(pg.Vector2(startScale, startScale))
                if white:
                    image.replaceWithWhite()

                self.evolveDisplay.update(image.surface)
                self.evolveDisplay.cropScreen(cropHeight)
                self.updateScreen()
                pg.time.delay(int(duration / ((1 - finalScale) / increment)))

    ##

    def quitCheck(self):
        for event in pg.event.get():
            if event.type == pg.QUIT:
                if self.game.overwrite:
                    self.game.save()
                quit()

    def use_item(self, item, targetFriendly=True):
        # Ensure that the pokeball targets the friendly Pokémon
        if item.type == "Pokeball":
            targetFriendly = False

        self.displayMessage(str.format("Used the {}", item.name), 1000)

        if targetFriendly:
            target = self.friendly
        else:
            target = self.foe

        if type(item) == Pokeball:
            item: Pokeball
            if target.status:
                if target.status.name == "Sleeping" or target.status.name == "Frozen":
                    statusModifier = 2
                elif target.status.name == "Paralysed" or target.status.name == "Poisoned" or \
                        target.status.name == "Burned":
                    statusModifier = 1.5
                else:
                    statusModifier = 1
            else:
                statusModifier = 1

            a = ((3 * target.stats.health - 2 * target.health) * target.catchRate * item.modifier * statusModifier) \
                / (3 * target.stats.health)

            b = floor(1048560 / floor(math.sqrt(floor(math.sqrt(floor(16711680 / a))))))

            fail = False
            check = 0
            for check in range(4):
                num = randint(0, 65535)
                if num >= b:
                    fail = True

                if fail:
                    break

            self.battle_display.catch_animation(3000, check)

            if not fail:
                self.displayMessage(str.format("The wild {} was caught!", target.name), 2000)
                target.catchDate = datetime.datetime.now()
                target.catchLocation = self.catchLocation
                target.catchLevel = target.level
                target.health = 0
                target.friendly = True
                target.visible = False
                target.switchImage()
                self.game.addPokemon(target)
                self.running = False
                return True
            else:
                target.image.set_alpha(255)

        elif type(item) == MedicineItem:
            item: MedicineItem
            if item.heal:
                if target.health + item.heal > target.stats.health:
                    healAmount = target.stats.health - target.health
                else:
                    healAmount = item.heal

                self.displayMessage(str.format("{}'s health was restored by {} Points", target.name, int(healAmount)))

                self.reduceHealth(target, -healAmount, 100, 10)

            if item.status:
                target.status = None
                if item.status == "Burned":
                    self.displayMessage(str.format("{} was cured of its burn", target.name), 1500)
                elif item.status == "Poisoned":
                    self.displayMessage(str.format("{} was cured of its poison", target.name), 1500)
                elif item.status == "Sleeping":
                    self.displayMessage(str.format("{} woke up", target.name), 1500)

            self.battleDisplay.text = str.format("What will {} do?", self.friendly.name)

        return False

    def checkKOs(self):
        for pokemon in self.activePokemon:
            if pokemon.health <= 0 and pokemon.friendly:
                print("KO")
                self.friendlyKO()
                self.running = False
                return True
            elif pokemon.health <= 0:
                self.wildKO()
                self.running = False
                return True

        return False

    def KOAnimation(self, duration, friendly=False):
        count = 100
        for frame in range(0, count):
            opacity = (1 - frame / count) * 255
            self.updateUpperScreen(opacity=opacity, friendly=friendly)
            pg.display.flip()
            pg.time.delay(int(duration / count))

        self.foe.visible = False

    def reduceHealth(self, target, damage, frames, delay):
        for frame in range(frames):
            target.health -= damage / frames
            self.updateUpperScreen()
            pg.display.flip()
            pg.time.delay(int(delay))

        target.health = round(target.health)

    def select_action(self):
        action = None
        while not action:
            pg.time.delay(100)  # set the debounce-time for keys
            keys = pg.key.get_pressed()
            if self.state == State.home:
                self.homeLogic(keys)

            elif self.state == State.fight:
                action = self.fightLogic(keys)

            elif self.state == State.bag:
                action, item = self.game.bag.loop(self.game.bottomSurf, self.game.controller, battle=self)
                if action == BagAction.item:
                    self.use_item(item, targetFriendly=True)
                else:
                    action = None

                self.game.bag.display.set_default_view()
                self.state = State.home

            elif self.state == State.pokemon:
                action = self.game.team.display_loop(self.game.bottomSurf, self.game.controller)
                if action != PartyAction.home:
                    self.tag_in_teammate(action)

                self.game.team.battle_display.set_default_view()
                self.state = State.home

            elif self.state == State.run:
                if self.friendly.stats.speed > self.foe.stats.speed:
                    action = True
                    self.displayMessage("Successfully fled the battle", 1500)
                    self.running = False
                else:
                    attempts = 1
                    escapeNum = ((self.friendly.stats.speed * 128 / self.foe.stats.speed) + 30 * attempts) % 256
                    num = randint(0, 255)
                    if num < escapeNum:
                        action = True
                        self.displayMessage("Successfully fled the battle", 1500)
                        self.running = False
                    else:
                        self.displayMessage("Couldn't Escape!", 1500)
                        action = FightAction.nothing

            elif self.state == State.learnMove:
                for move in self.movesToLearn:
                    self.learnLogic(move)
                    self.movesToLearn.pop(self.movesToLearn.index(move))

                action = True
                self.running = False

            self.quitCheck()

            # self.updateScreen()

        return action

    def takeTurn(self, pokemon, action):
        if type(action) == FightAction:
            move = pokemon.moves[action.value]
            if pokemon.friendly:
                self.attack(attacker=pokemon, target=self.foe, move=move)
            else:
                self.attack(attacker=pokemon, target=self.friendly, move=move)

    def tag_in_teammate(self, teammate: PartyAction):
        pkIndex = self.activePokemon.index(self.friendly)
        self.activePokemon[pkIndex] = self.pokemon_team.pokemon[teammate.value]
        self.friendly = self.activePokemon[pkIndex]
        self.moveDisplay = MoveDisplay(self.screenSize, self.friendly.moves)

    def loop2(self):
        while self.running:
            # get speed of wild Pokémon
            self.battle_display.text = f"What will {self.friendly.name} do?"
            friendlyAction = self.select_action()

            moveIdx = randint(0, len(self.foe.moves) - 1)
            foeAction = FightAction(moveIdx)

            speeds = []
            for pokemon in self.activePokemon:
                speed = pokemon.stats.speed
                speeds.append(speed)

            speeds.sort(reverse=True)

            order = []

            for speed in speeds:
                for pokemon in self.activePokemon:
                    if pokemon.stats.speed == speed:
                        order.append(pokemon)

            if type(friendlyAction) == bool:
                end = friendlyAction
            else:
                end = False

            for pokemon in order:
                if not end:
                    if pokemon.health > 0:
                        if pokemon.friendly:
                            self.takeTurn(pokemon, friendlyAction)
                        else:
                            self.takeTurn(pokemon, foeAction)
                    # check if both Pokémon are still alive

                    if self.checkKOs():
                        end = True

            for pokemon in order:
                if pokemon.health > 0 and not end:
                    if pokemon.status:
                        if type(pokemon.status) == Burn:
                            self.battleDisplay.text = str.format("{} is hurt by its burn", pokemon.name)
                            self.reduceHealth(pokemon, pokemon.status.damage * pokemon.stats.health, 100, 10)
                        elif type(pokemon.status) == Poison:
                            pokemon.health -= pokemon.status.damage * pokemon.stats.health
                            self.displayMessage(str.format("{} is hurt by its poison", pokemon.name), 1000)

            self.moveDisplay.updateScreen(self.friendly.moves)

            if not end:
                self.checkKOs()

            self.state = State.home

        # anything here happens after all the Pokémon have fainted
        for pk in self.pokemon_team.pokemon:
            pk.resetStatStages()

        self.game.bottomSurf.blit(self.lowerScreenBase, (0, 0))
        pg.display.flip()
        self.fadeOut(1000)

    def clearSurfaces(self):

        for pk in self.pokemon_team.pokemon:
            pk.clearImages()

        for pk in self.activePokemon:
            pk.clearImages()

        self.battleDisplay.clearSurfaces()
        self.homeDisplay = None
        self.moveDisplay = None
        self.learnMoveDisplay = None
        self.levelUpDisplay = None
        self.evolveDisplay = None
        self.lowerScreenBase = None


if __name__ == '__main__':
    from game import Game
    from bag import Bag
    import json

    pg.init()

    with open("test_data/bag/test_bag.json", "r") as read_file:
        bag_data = json.load(read_file)

    demo_game = Game(scale=1, fromPickle=False, overwrite=False)

    demo_game.bag = Bag(**bag_data)

    battle = Battle(demo_game, routeName="Route 201", wildName="Abra", wildLevel=20)

    battle.loop2()

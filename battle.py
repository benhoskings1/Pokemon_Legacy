import datetime
import math
from enum import Enum
from math import floor
from random import randint

import pygame as pg

from battle_action import BattleAction, BattleActionType, BattleAttack, BattleTagIn
from displays.battle.battle_display_main import BattleDisplayMain, LevelUpBox
from displays.battle.battle_display_touch import *
from displays.battle.learn_move_display import LearnMoveDisplay

# from displays.EvolveDisplay import EvolveDisplay
# from displays.LearnMove import LearnMoveDisplay, LearnAction
from displays.team_display_battle import PartyAction
from general.utils import *
from general.Animations import createAnimation
from general.Condition import StatusCondition
from general.Environment import Environment
from general.Image import Image
from general.Item import Item, Pokeball, MedicineItem, medicine
from general.Move import Move2
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
    def __init__(self, game, environment=Environment.grassland, route_name="Route 201",
                 wild_name=None, wildLevel=None, pickleData=None):
        self.game = game
        self.running = True
        self.catchLocation = route_name
        self.pokemon_team: Team = game.team

        # set up the displays
        self.friendly: Pokemon = self.pokemon_team.get_active_pokemon()

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

            # self.battleDisplay = BattleDisplay(self.screenSize, self.environment, self.timeOfDay)
            # self.battleDisplay.text = pickleData.battleDisplay.text

            self.state = pickleData.state

            self.movesToLearn = pickleData.movesToLearn

        else:

            # wild pokemon
            if not wild_name:
                route = Route(route_name)
                pkName, pkLevel = route.encounter(game.time)

                self.foe: Pokemon = self.game.createPokemon(pkName, level=pkLevel)
            else:
                if wildLevel:
                    self.foe: Pokemon = self.game.createPokemon(wild_name, level=wildLevel)
                else:
                    self.foe: Pokemon = self.game.createPokemon(wild_name, level=10)

            self.environment = environment
            self.timeOfDay = self.game.getTimeOfDay()

            # self.battleDisplay = BattleDisplay(self.screenSize, self.environment, self.timeOfDay)
            # self.battleDisplay.text = str.format("A wild {} appeared!", self.foe.name)

            self.state = State.home

            self.movesToLearn = None

        self.active_pokemon = [self.friendly, self.foe]
        self.active_pokemon_2 = {
            "friendly": [self.friendly],
            "foe": [self.foe],
        }

        self.battle_display = BattleDisplayMain(self.game.topSurf, self.screenSize, self.timeOfDay, self.environment)
        self.battle_display.add_pokemon_sprites(self.active_pokemon)

        self.touch_displays = {
            TouchDisplayStates.home: BattleDisplayTouch(self.game.bottomSurf, self.screenSize, self.game.graphics_scale),
            TouchDisplayStates.fight: BattleDisplayFight(self.game.bottomSurf, self.screenSize, self.game.graphics_scale),
            TouchDisplayStates.bag: BattleDisplayBag(self.game.bottomSurf, self.screenSize, self.game.bag, self.game.graphics_scale),
            TouchDisplayStates.team: BattleDisplayTeam(self.screenSize, self.pokemon_team, self.game.graphics_scale),
        }

        self.touch_displays[TouchDisplayStates.fight].load_move_sprites(self.friendly.moves)

        self.active_touch_display = self.touch_displays[TouchDisplayStates.home]
        self.evolveDisplay = None

        lowerScreenBase = pg.image.load("Images/Battle/Other/Lower Base.png")
        self.lowerScreenBase = pg.transform.scale(lowerScreenBase, game.bottomSurf.get_size())

        self.displayFriendly = True
        self.displayWild = True

        self.update_screen(cover=True)

        if not pickleData:
            pg.event.pump()
            self.battle_display.intro_animations(self.game.topSurf, 2000)
            self.battle_display.bounce_friendly_stat = True

    # ======== GRAPHICS HANDLERS =========
    def update_upper_screen(self):
        if self.state != State.evolve:
            self.game.topSurf.blit(self.battle_display.get_surface(show_sprites=True), (0, 0))
        else:
            self.game.topSurf.blit(self.evolveDisplay.getUpperSurface(), (0, 0))

    def update_lower_screen(self, cover=False):
        if cover:
            self.game.bottomSurf.blit(self.lowerScreenBase, (0, 0))
        else:
            self.game.bottomSurf.blit(self.active_touch_display.get_surface(show_sprites=True), (0, 0))

    def update_screen(self, cover=False, flip=True):
        self.update_upper_screen()
        self.update_lower_screen(cover)
        if flip:
            pg.display.flip()

    def learn_move(self, move):
        pokemon = self.active_pokemon[0]
        if len(self.active_pokemon[0].moves) < 4:
            self.battle_display.refresh()
            self.update_upper_screen()
            self.displayMessage(f"{pokemon.name} learned {move.name.title()}!", duration=2000)
            self.active_pokemon[0].moves.append(move)
        else:
            learn_display = LearnMoveDisplay(self.screenSize, self.active_pokemon[0], move, scale=2)
            forget_move = learn_display.select_action(battle=self)

            if forget_move:
                print(forget_move)
                self.displayMessage("1 2 and... ... Poof!", duration=2000)
                self.displayMessage(f"{pokemon.name} forgot how to use {forget_move.name}.", duration=2000)
                self.displayMessage("And...", duration=2000)
                self.displayMessage(f"{pokemon.name} learned {move.name}!", duration=2000)

                # replace the pokemon's move
                self.active_pokemon[0].moves[pokemon.moves.index(forget_move)] = move

    def wait(self, duration):
        """ Wait for the given time in milliseconds"""
        start = time.monotonic()

        duration = duration / 1000
        while time.monotonic() - start < duration:
            self.update_screen(cover=True)

    # ======== BATTLE FUNCTIONS ==========
    def attack(self, attacker: Pokemon, target: Pokemon, move):

        displayTime, graphicsTime, attackTime, effectTime = 1000, 500, 1000, 1000

        frames = 100
        attackTimePerFrame = attackTime / frames

        [damage, effective, inflictCondition, heal, modify, hits, crit] = attacker.useMove(move, target)

        damage = min([target.health, damage])

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
                battle_attack = BattleAttack(target=target, move=move, animation_size=self.battle_display.size)
                # self.battle_display.sprites.add(battle_attack)
                self.battle_display.bounce_friendly_stat = False

                if battle_attack.animation:
                    for frame in range(battle_attack.frame_count):
                        battle_attack.frame_idx = frame
                        battle_attack.update()
                        if battle_attack.animation.frames:
                            self.battle_display.screens["animations"].surface = battle_attack.get_animation_frame(frame)
                        self.game.topSurf.blit(self.battle_display.get_surface(show_sprites=True), (0, 0))
                        pg.display.flip()
                        pg.time.delay(15)
                        self.battle_display.refresh(text=False)

                    self.battle_display.screens["animations"].refresh()

                # Health reduction
                self.reduce_health(target, damage, frames, attackTimePerFrame)
                self.battle_display.bounce_friendly_stat = True

        if heal:
            health = floor(damage * (heal / 100))
            health = max([health, 1])

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

                start = "" if modified.friendly else "The wild "

                if limit:
                    descriptor = f"won't go any {'higher' if change > 0 else 'lower'}"

                self.displayMessage(str.format("{}{}'s {} {}", start, modified.name, modify[1], descriptor), 2000)
                # self.displayMessage(, 10)
                direction = "raise" if change > 0 else "lower"
                self.battle_display.render_pokemon_animation(self.game.topSurf, target, f"stat_{direction}", duration=2000)

        target.health = round(target.health)

        self.touch_displays[TouchDisplayStates.team].update_stats()

    def displayMessage(self, text, duration=1000):
        self.battle_display.update_display_text(text)
        self.update_upper_screen()
        self.game.bottomSurf.blit(self.lowerScreenBase, (0, 0))
        pg.display.flip()

        for char_idx in range(1, len(text)+1):
            self.battle_display.update_display_text(text, max_chars=char_idx)
            self.update_upper_screen()
            self.game.bottomSurf.blit(self.lowerScreenBase, (0, 0))
            pg.display.flip()
            self.wait(round(duration * 0.7 / len(text)))

        self.wait(duration * 0.3)

    def displayMessageEvolve(self, text, image, time):
        self.evolveDisplay.text = text
        self.evolveDisplay.update(image)
        self.update_screen()
        pg.time.delay(time)

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

    def wild_ko(self):
        self.friendly.updateEVs(self.foe.name)
        self.update_upper_screen()
        pg.display.flip()
        self.ko_animation(1500, self.foe)

        frames, duration = 100, 1500
        exp_gain = round(self.foe.getFaintXP() * 1000)
        self.displayMessage(f"{self.friendly.name} gained {exp_gain} Exp.", duration=2000)
        for frame in range(frames):
            self.friendly.exp += exp_gain / frames
            self.battle_display.render_pokemon_details()
            pg.display.flip()
            pg.time.delay(int(duration / frames))
            if self.friendly.exp >= self.friendly.level_up_exp:
                self.level_up_friendly(1000)
                new_moves = self.friendly.get_new_moves()
                if new_moves:
                    for move in new_moves:
                        self.learn_move(move)

        self.friendly.exp = round(self.friendly.exp)

    def friendlyKO(self):
        # self.battleDisplay.text = str.format("{} fainted!", self.friendly.name)
        self.update_upper_screen()
        pg.display.flip()
        self.ko_animation(1500, self.friendly)

    def level_up_friendly(self, duration=1000):

        prevStats = self.friendly.stats
        self.friendly.level_up()
        newStats = self.friendly.stats
        self.friendly.health += newStats.health - prevStats.health

        self.displayMessage(f"{self.friendly.name} grew to Lv. {self.friendly.level}!", duration=duration)
        # stat_container = self.battle_display.screens["stats"].get_object("friendly_stats")

        for old_stats in [prevStats, None]:
            level_up_box = LevelUpBox("level_up", self.game.graphics_scale, new_stats=newStats, old_stats=old_stats)
            self.battle_display.sprites.add(level_up_box)
            self.update_upper_screen()
            pg.display.flip()
            pg.time.delay(duration)
            level_up_box.kill()

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
            self.update_screen()
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
        self.update_screen()

        pg.time.delay(300)
        self.evolveDisplay.text = str.format("Congratulations! Your {} evolved into {}", self.friendly.name,
                                             evolution.name)
        self.evolveDisplay.update(evoImage.baseSurface)
        self.update_screen()
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
                self.update_screen()
                pg.time.delay(int(duration / ((finalScale - 0.5) / increment)))
        else:
            while startScale > finalScale:
                startScale -= increment
                image.scale(pg.Vector2(startScale, startScale))
                if white:
                    image.replaceWithWhite()

                self.evolveDisplay.update(image.surface)
                self.evolveDisplay.cropScreen(cropHeight)
                self.update_screen()
                pg.time.delay(int(duration / ((1 - finalScale) / increment)))

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

        target = self.friendly if targetFriendly else self.foe

        if isinstance(item, Pokeball):
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

        elif isinstance(item, MedicineItem):
            item: MedicineItem
            print(item.heal)
            if item.heal:
                if target.health + item.heal > target.stats.health:
                    healAmount = target.stats.health - target.health
                else:
                    healAmount = item.heal

                self.displayMessage(str.format("{}'s health was restored by {} Points", target.name, int(healAmount)))

                self.reduce_health(target, -healAmount, 100, 10)

            if item.status:
                target.status = None
                if item.status == "Burned":
                    self.displayMessage(str.format("{} was cured of its burn", target.name), 1500)
                elif item.status == "Poisoned":
                    self.displayMessage(str.format("{} was cured of its poison", target.name), 1500)
                elif item.status == "Sleeping":
                    self.displayMessage(str.format("{} woke up", target.name), 1500)

        count = self.game.bag.data[item.item_type][item] -1
        self.game.bag.data[item.item_type][item] = count

        if self.game.bag.data[item.item_type][item] == 0:
            self.game.bag.data[item.item_type].pop(item)

        self.active_touch_display.update_container(item, count)

        # self.touch_displays[TouchDisplayStates.bag].sub_displays[BAG_DISPLAY_ITEM_TYPE_MAP[item.item_type]]

        return False

    def checkKOs(self):
        for pokemon in self.active_pokemon:
            if pokemon.health <= 0 and pokemon.friendly:
                print("KO")
                self.friendlyKO()
                self.running = False
                return True
            elif pokemon.health <= 0:
                self.wild_ko()
                self.running = False
                return True

        return False

    def ko_animation(self, duration, pokemon):
        container_type = "friendly" if pokemon.friendly else "foe"
        move_direction = 1 if pokemon.friendly else -1

        stat_container = self.battle_display.screens["stats"].get_object(f"{container_type}_stats")
        container_size = stat_container.image.get_size()[0]

        initial_position = stat_container.rect.topleft

        count = 100
        for frame in range(0, count):
            opacity = (1 - frame / count) * 255
            pokemon.image.set_alpha(opacity)

            stat_container.rect.topleft = initial_position + pg.Vector2(move_direction * frame * (container_size / count), 0)

            self.update_upper_screen()
            pg.display.flip()
            pg.time.delay(int(duration / count))

        self.foe.visible = False
        stat_container.kill()

    def reduce_health(self, target, damage, frames, delay):
        for frame in range(frames):
            target.health = max(0, target.health - damage / frames)
            self.battle_display.render_pokemon_details()
            self.update_upper_screen()
            pg.display.flip()
            pg.time.delay(int(delay))

        target.health = round(target.health)

    def select_action(self):
        def process_input(res):
            if res[0] == "container" and res[1] in self.touch_displays.keys():
                self.state = res[1]
                self.active_touch_display = self.touch_displays[res[1]]
                self.update_screen()

            elif res[0] == "container" and self.state == TouchDisplayStates.bag:
                self.active_touch_display = self.touch_displays[TouchDisplayStates.bag].sub_displays[res[1]]
                self.update_screen()

            elif res[0] == "container" and res[1] == "run":
                if self.friendly.stats.speed > self.foe.stats.speed:
                    self.displayMessage("Successfully fled the battle", 1500)
                    self.running = False
                    return True
                else:
                    self.displayMessage("Couldn't Escape!", 1500)
                    self.battle_display.update_display_text(f"What will {self.friendly.name} do?")
                    return None

            elif res[0] == "container" and res[1] == TeamDisplayStates.select:
                self.active_touch_display = self.touch_displays[TouchDisplayStates.team].sub_displays[TeamDisplayStates.select]
                display_pk_idx = self.touch_displays[TouchDisplayStates.team].select_idx
                pk_select = self.pokemon_team.pokemon[display_pk_idx]
                self.active_touch_display.load_pk_details(pk_select)

            elif res[0] == "container" and (res[1] == TeamDisplayStates.summary or res[1] == TeamDisplayStates.moves):
                self.active_touch_display = self.touch_displays[TouchDisplayStates.team].sub_displays[res[1]]
                display_pk_idx = self.touch_displays[TouchDisplayStates.team].select_idx
                pk_select = self.pokemon_team.pokemon[display_pk_idx]
                self.active_touch_display.refresh()
                self.active_touch_display.load_pk_details(pk_select)

            elif res[0] == "container" and (res[1] == "up" or res[1] == "down"):
                pk_idx = self.touch_displays[TouchDisplayStates.team].select_idx
                if res[1] == "up":
                    pk, self.touch_displays[TouchDisplayStates.team].select_idx = self.pokemon_team.get_pk_up(pk_idx)

                else:
                    pk, self.touch_displays[TouchDisplayStates.team].select_idx = self.pokemon_team.get_pk_down(pk_idx)

                self.active_touch_display.refresh()
                self.active_touch_display.load_pk_details(pk)
                self.update_screen()

            elif (res[0] == "move_container" or res[0] == "move_summary_select") and isinstance(res[1], Move2):
                self.active_touch_display = self.touch_displays[TouchDisplayStates.team].sub_displays[TeamDisplayStates.move_summary]
                pk_idx = self.touch_displays[TouchDisplayStates.team].select_idx
                self.active_touch_display.load_pk_details(self.pokemon_team.pokemon[pk_idx])
                self.active_touch_display.load_move_details(res[1])

            elif res[0] == "move":
                return res[1]  # returns the selected move

            elif res[0] == "item_container":
                item, count = res[1]
                select_display = BattleDisplayItemSelect(self.screenSize, item=item, count=count,
                                                         parent=self.active_touch_display.parent_display_type,
                                                         scale=2)
                self.active_touch_display = select_display
                self.update_screen()

            elif res[0] == "item":
                item = res[1]
                if isinstance(item, MedicineItem):
                    # only these items have the heal attribute
                    if (item.heal and self.friendly.health == self.friendly.stats.health) or \
                            (item.status != self.friendly.status):
                        # print(item.status, self.friendly.status)
                        self.displayMessage("It will have no effect...", 1500)
                        self.battle_display.update_display_text(f"What will {self.friendly.name} do?")
                        self.update_screen()
                    else:
                        parent_display_type = self.active_touch_display.parent_display_type
                        self.active_touch_display = self.touch_displays[TouchDisplayStates.bag].sub_displays[
                            parent_display_type]
                        return item
                else:
                    return item

            elif res[0] == "pokemon_container" and res[1] is not None:
                pokemon = res[1]
                self.active_touch_display.select_idx = self.pokemon_team.get_index(pokemon)
                self.active_touch_display.set_sub_displays()
                self.active_touch_display = self.active_touch_display.sub_displays[TeamDisplayStates.select]
                self.update_screen()

            elif res[0] == "pokemon_select":
                pokemon = res[1]
                print(f"{pokemon} now in battle")
                return pokemon

        action = None
        while not action:
            for event in pg.event.get():
                if event.type == pg.MOUSEBUTTONDOWN:
                    pos = pg.mouse.get_pos()
                    pos = pg.Vector2(pos) - pg.Vector2(0, self.battle_display.size.y)
                    clicked = self.active_touch_display.click_test(pos)

                    if clicked:
                        action = process_input(clicked)
                        if action:
                            return action

                elif event.type == pg.KEYDOWN:
                    # send event key to display selector
                    ...

                elif event.type == pg.QUIT:
                    if self.game.overwrite:
                        self.game.save()
                    quit()

            self.update_screen()

        return action

    def take_turn(self, pokemon, action):
        if isinstance(action, Move2):
            if pokemon.friendly:
                self.attack(attacker=pokemon, target=self.foe, move=action)
                self.touch_displays[TouchDisplayStates.fight].update_container(action)
            else:
                self.attack(attacker=pokemon, target=self.friendly, move=action)

        elif isinstance(action, Item):
            self.use_item(action, targetFriendly=True)

        elif isinstance(action, Pokemon):
            self.tag_in_teammate(action)

    def tag_in_teammate(self, teammate: Pokemon):
        self.displayMessage(f"{self.active_pokemon[0].name} switch out", duration=1000)
        # self.battle_display.update_display_text()
        tag_in = BattleTagIn(animation_size=self.screenSize)
        self.battle_display.bounce_friendly_stat = False
        self.friendly.visible = False

        if tag_in.animation:
            for frame in range(tag_in.frame_count):
                tag_in.frame_idx = frame
                tag_in.update()
                if tag_in.animation.frames:
                    self.battle_display.screens["animations"].surface = tag_in.get_animation_frame(frame)
                self.game.topSurf.blit(self.battle_display.get_surface(show_sprites=True), (0, 0))
                pg.display.flip()
                pg.time.delay(15)
                self.battle_display.refresh(text=False)

            self.battle_display.screens["animations"].refresh()

        pkIndex = self.active_pokemon.index(self.friendly)
        self.active_pokemon[pkIndex] = teammate

        self.friendly = teammate
        self.battle_display.switch_active_pokemon(teammate)
        self.touch_displays[TouchDisplayStates.fight].load_move_sprites(self.friendly.moves)
        self.touch_displays[TouchDisplayStates.fight].refresh()
        self.friendly.visible = True

        self.update_upper_screen()

    def loop(self):
        while self.running:
            # get speed of wild Pokémon
            self.battle_display.update_display_text(f"What will {self.friendly.name} do?")
            # self.battle_display.text = f"What will {self.friendly.name} do?"
            friendlyAction = self.select_action()

            moveIdx = randint(0, len(self.foe.moves) - 1)
            foeAction = self.foe.moves[moveIdx]

            speeds = []
            for pokemon in self.active_pokemon:
                speed = pokemon.stats.speed
                speeds.append(speed)

            speeds.sort(reverse=True)

            order = []

            for speed in speeds:
                for pokemon in self.active_pokemon:
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
                            self.take_turn(pokemon, friendlyAction)
                        else:
                            self.take_turn(pokemon, foeAction)
                    # check if both Pokémon are still alive

                    if self.checkKOs():
                        end = True

            for pokemon in order:
                if pokemon.health > 0 and not end:
                    if pokemon.status:
                        if type(pokemon.status) == Burn:
                            # self.battleDisplay.text = str.format("{} is hurt by its burn", pokemon.name)
                            self.reduce_health(pokemon, pokemon.status.damage * pokemon.stats.health, 100, 10)
                        elif type(pokemon.status) == Poison:
                            pokemon.health -= pokemon.status.damage * pokemon.stats.health
                            self.displayMessage(str.format("{} is hurt by its poison", pokemon.name), 1000)

            if not end:
                self.checkKOs()

            self.state = State.home

            self.active_touch_display = self.touch_displays[TouchDisplayStates.home]
            self.update_screen()

        # anything here happens after all the Pokémon have fainted
        for pk in self.pokemon_team.pokemon:
            pk.resetStatStages()

        self.game.bottomSurf.blit(self.lowerScreenBase, (0, 0))
        pg.display.flip()
        self.fadeOut(1000)

    def clearSurfaces(self):

        for pk in self.pokemon_team.pokemon:
            pk.clearImages()

        for pk in self.active_pokemon:
            pk.clearImages()

        # self.battleDisplay.clearSurfaces()
        self.battle_display = None
        self.evolveDisplay = None
        self.lowerScreenBase = None
        self.touch_displays = None
        self.active_touch_display = None


if __name__ == '__main__':
    from game import Game
    from bag import Bag, BagV2
    import json

    pg.init()
    pg.event.pump()

    with open("test_data/bag/test_bag.json", "r") as read_file:
        bag_data = json.load(read_file)

    demo_game = Game(scale=1, fromPickle=False, overwrite=False, optimize=False)
    print("game loaded")

    demo_game.bag = BagV2(bag_data)

    battle = Battle(demo_game, route_name="Route 201", wild_name="Abra", wildLevel=1, pickleData=None)

    battle.loop()

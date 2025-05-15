import os
import sys
import time

import pokemon
from screen_V2 import Colours, FontOption, Screen, BlitLocation
from sprite_screen import SpriteScreen, PokeballCatchAnimation
from pokemon import Pokemon, PokemonSpriteSmall
import pygame as pg
from enum import Enum

from general.Item import Pokeball, MedicineItem, BattleItemType
# from bag import BagV2


MOVE_CONTAINER_POSITIONS = [(2, 25), (130, 25), (2, 85), (130, 85)]
ITEM_CONTAINER_POSITIONS = [(1, 6), (130, 6), (2, 85), (130, 85)]
TEAM_CONTAINER_POSITIONS = [(1, 1), (129, 9), (1, 49), (129, 56), (1, 96), (129, 104)]

class TouchDisplayStates(Enum):
    home = 0
    fight = 1
    team = 2
    bag = 3


class BagDisplayStates(Enum):
    home = 0
    restore = 1
    pokeball = 2
    healers = 3
    battle_items = 4
    select = 5


class TeamDisplayStates(Enum):
    home = 0
    select = 1
    summary = 2
    moves = 3


BAG_DISPLAY_ITEM_TYPE_MAP = {
    BagDisplayStates.restore: BattleItemType.restore,
    BagDisplayStates.pokeball: BattleItemType.pokeball,
    BagDisplayStates.healers: BattleItemType.healer,
    BagDisplayStates.battle_items: BattleItemType.battle_item
}

# ======== CONTAINERS ==============
class DisplayContainer(pg.sprite.Sprite, SpriteScreen):
    def __init__(self, image_path, sprite_id, pos=(0, 0), scale=None):
        pg.sprite.Sprite.__init__(self)

        self.sprite_type = "container"
        self.image = pg.image.load(image_path)
        if scale:
            self.image = pg.transform.scale(self.image, pg.Vector2(self.image.get_size()) * scale)
            pos = pg.Vector2(pos) * scale

        self.rect = self.image.get_rect()
        self.rect.topleft = pos
        self.id = sprite_id
        self.scale = scale

        SpriteScreen.__init__(self, self.image.get_size())
        self.load_image(image_path, base=True, scale=pg.Vector2(scale, scale))

    def click_return(self):
        return self.sprite_type, self.id

    def is_clicked(self, pos):
        if self.rect.collidepoint(pos):
            return True
        else:
            return False


class MoveContainer(DisplayContainer):
    def __init__(self, move, pos=(0, 0), scale=None):

        img_path = f"Images/Battle/Fight/Move Containers/{move.type} Container.png"
        DisplayContainer.__init__(self, img_path, move, pos, scale)

        self.sprite_type = "move"

        self.addText(move.name, pg.Vector2((int(62 * scale), int(13 * scale))), base=True, location=BlitLocation.midTop)

        self.addText("PP", pg.Vector2((int(56 * scale), int(31 * scale))),
                             colour=pg.Color(63, 48, 41), shadowColour=pg.Color(153, 158, 136), base=True,
                             location=BlitLocation.midTop)

        self.image = self.get_surface()

        self.scale = scale

    def update_info(self, move):
        self.refresh()
        self.addText(f"{move.PP}/{move.maxPP}", pg.Vector2((int(108 * self.scale), int(34 * self.scale))),
                             fontOption=FontOption.level, location=BlitLocation.topRight)

        self.image = self.get_surface()


class ItemContainer(DisplayContainer):
    def __init__(self, item, count, parent_display_type, pos=pg.Vector2(0, 0), scale=None):
        container= "pokeball"
        if isinstance(item, Pokeball):
            container = "pokeball"
        elif isinstance(item, MedicineItem):
            container = item.battle_item_type.value  # edit this

        DisplayContainer.__init__(self, f"assets/containers/item_{container}.png", item, pos=pos, scale=scale)
        self.sprite_type = "item_container"
        self.parent_display_type = parent_display_type

        self.item = item
        self.count = count
        self.addText(item.name, pg.Vector2(67.5, 11) * scale, colour=Colours.white.value, shadowColour=Colours.lightGrey.value, base=True, location=BlitLocation.midTop)
        self.addText(f"x{count}", pos=pg.Vector2(62, 31) * scale, colour=Colours.white.value, shadowColour=Colours.lightGrey.value,)
        self.add_image(item.image, pos=pg.Vector2(39, 33) * scale, location=BlitLocation.centre, base=True, scale=pg.Vector2(scale, scale))
        self.image = self.get_surface()

    def update_info(self, count):
        self.refresh()
        self.addText(f"x{count}", pos=pg.Vector2(62, 31) * self.scale, colour=Colours.white.value,
                     shadowColour=Colours.lightGrey.value, )
        self.image = self.get_surface()

    def click_return(self):
        return self.sprite_type, (self.item, self.count)


class PokemonContainerTeam(DisplayContainer):
    def __init__(self, pokemon, primary=False, pos=pg.Vector2(0, 0), scale=None):
        self.primary = primary
        if pokemon is not None:
            container_type = "primary" if primary else "secondary"
        else:
            container_type = "empty"

        DisplayContainer.__init__(self, f"assets/containers/team_{container_type}.png", pokemon, pos=pos, scale=scale)

        self.pokemon = pokemon
        self.sprite_type = "pokemon_container"
        self.small_sprite = None
        if pokemon:
            self.small_sprite = PokemonSpriteSmall(pokemon.small_animation)
            self.small_sprite.rect.center = pg.Vector2(13, 19) * self.scale
            self.addText(pokemon.name, pg.Vector2(31, 9) * self.scale, base=True, colour=Colours.white.value, shadowColour=Colours.lightGrey.value,)
            self.addText(f"{pokemon.health}/{pokemon.stats.health}", pg.Vector2(72, 32) * self.scale,
                         colour=Colours.white.value,shadowColour=Colours.white.value, fontOption=FontOption.level)
            self.addText(f"Lv{pokemon.level}", pg.Vector2(12, 32) * self.scale,
                         colour=Colours.white.value, shadowColour=Colours.white.value, fontOption=FontOption.level, base=True,)

            self.sprites.add(self.small_sprite)

        self.image = self.get_surface()
        self.img_update = time.monotonic()
        self.image_idx = 0

    def update_stats(self):
        self.refresh()
        health_ratio = self.pokemon.health / self.pokemon.stats.health

        bar_rect = pg.Rect(pg.Vector2(63, 24), pg.Vector2(48 * health_ratio, 4))

        if health_ratio > 0.5:
            colour = "high"
        elif health_ratio > 0.25:
            colour = "medium"
        else:
            colour = "low"

        health_bar = pg.image.load(f"assets/battle/main_display/health_bar/health_{colour}.png")
        health_bar = pg.transform.scale(health_bar, bar_rect.size)
        bar_pos = pg.Vector2(63, 23) if self.primary else pg.Vector2(63, 24)
        self.add_image(health_bar, pos=bar_pos * self.scale, scale=pg.Vector2(self.scale, self.scale))
        self.addText(f"{self.pokemon.health}/{self.pokemon.stats.health}", pg.Vector2(72, 32) * self.scale,
                     colour=Colours.white.value, shadowColour=Colours.white.value, fontOption=FontOption.level)

    def toggle_mini(self):
        now = time.monotonic()
        if now - self.img_update > 0.15:
            self.refresh(sprite_only=True)
            self.small_sprite.toggle_image()
            self.image = self.get_surface()
            self.img_update = time.monotonic()


class PokemonContainerSingle(DisplayContainer):
    def __init__(self, pokemon, pos=pg.Vector2(0, 0), scale=None):
        self.scale = scale
        self.pokemon = pokemon
        self.small_sprite = PokemonSpriteSmall(pokemon.small_animation)
        self.small_sprite.rect.center = pg.Vector2(119, 69) * self.scale
        DisplayContainer.__init__(self, "assets/containers/pokemon_container_1.png", pokemon, pos=pos, scale=self.scale)
        self.sprite_type = "pokemon_select"

        self.addText(pokemon.name, pos=pg.Vector2(119, 35) * self.scale, location=BlitLocation.midTop, colour=Colours.white.value, base=True,)
        self.addText("SHIFT", pos=pg.Vector2(119, 97) * self.scale, location=BlitLocation.midTop, colour=Colours.white.value, base=True, )

        self.sprites.add(self.small_sprite)
        # self.add_image(self.small_sprite.im, pos=pg.Vector2(119, 69) * self.scale, location=BlitLocation.centre)
        self.image = self.get_surface()
        self.img_update = time.monotonic()
        self.image_idx = 0

    def toggle_mini(self):
        now = time.monotonic()
        if now - self.img_update > 0.15:
            self.refresh(sprite_only=True)
            self.small_sprite.toggle_image()
            self.image = self.get_surface()
            self.img_update = time.monotonic()

# ======== DISPLAYS ==============
class BattleDisplayTouch(SpriteScreen):
    def __init__(self, window, window_size, scale):
        """
        This is the main battle display. The native screen size is 256x192 px
        :param window: The pygame surface to blit the display onto
        :param size: the size of the display
        :param time: the time of day, used to configure the battle background option
        :param environment:
        """
        super().__init__(window_size, colour=Colours.black)

        self.display_type = TouchDisplayStates.home

        self.window = window

        self.scale = scale

        self.load_image("assets/battle/touch_display/home/background.png", base=True, scale=pg.Vector2(self.scale, self.scale))

        fight_container = DisplayContainer("assets/containers/battle_fight.png", TouchDisplayStates.fight, pos=(20, 35), scale=self.scale)
        bag_container = DisplayContainer("assets/containers/battle_bag.png", TouchDisplayStates.bag, pos=(1, 145), scale=self.scale)
        run_container = DisplayContainer("assets/containers/battle_run.png", "run", pos=(89, 153), scale=self.scale)
        team_container = DisplayContainer("assets/containers/battle_team.png", TouchDisplayStates.team, pos=(177, 145), scale=self.scale)

        self.sprites.add([fight_container, bag_container, run_container, team_container])


class BattleDisplayFight(SpriteScreen):
    def __init__(self, window, size, scale):
        """
        This is the main battle display. The native screen size is 256x192 px
        :param window: The pygame surface to blit the display onto
        :param size: the size of the display
        :param time: the time of day, used to configure the battle background option
        :param environment:
        """
        super().__init__(size, colour=Colours.black)
        self.display_type = TouchDisplayStates.fight

        self.window = window

        self.scale = scale

        self.load_image("assets/battle/touch_display/fight/background.png", base=True,
                        scale=pg.Vector2(self.scale, self.scale))

        self.cancel_container = DisplayContainer("assets/containers/fight_cancel.png", TouchDisplayStates.home, pos=(9, 153),
                                            scale=self.scale)

        self.sprites.add([self.cancel_container])

    def load_move_sprites(self, moves):
        self.sprites.empty()

        containers = [
            MoveContainer(move, pos=MOVE_CONTAINER_POSITIONS[idx], scale=self.scale)
            for idx, move in enumerate(moves)
        ]

        for idx, container in enumerate(containers):
            container.update_info(moves[idx])

        self.sprites.add(containers + [self.cancel_container])

    def update_container(self, move):
        self.get_object(move).update_info(move)


class BattleDisplayBag(SpriteScreen):
    def __init__(self, window, size, bag, scale):
        """
        This is the main battle display. The native screen size is 256x192 px
        :param window: The pygame surface to blit the display onto
        :param size: the size of the display
        :param time: the time of day, used to configure the battle background option
        :param environment:
        """
        super().__init__(size, colour=Colours.black)
        self.display_type = TouchDisplayStates.bag

        self.window = window

        self.scale = scale

        self.bag = bag

        self.load_image("assets/battle/touch_display/bag/background_home.png", base=True, scale=pg.Vector2(self.scale, self.scale))

        return_container = DisplayContainer("assets/containers/bag_return.png", TouchDisplayStates.home, pos=(217, 152), scale=self.scale)
        restore_container = DisplayContainer("assets/containers/bag_restore.png", BagDisplayStates.restore, pos=(1, 8), scale=self.scale)
        pokeball_container = DisplayContainer("assets/containers/bag_pokeball.png", BagDisplayStates.pokeball, pos=(129, 8), scale=self.scale)
        healer_container = DisplayContainer("assets/containers/bag_healers.png", BagDisplayStates.healers, pos=(1, 80), scale=self.scale)
        item_container = DisplayContainer("assets/containers/bag_items.png", BagDisplayStates.battle_items, pos=(129, 80), scale=self.scale)

        self.sprites.add([return_container, restore_container, pokeball_container, healer_container, item_container])

        self.sub_displays = {
            state: BattleDisplayBagItem(
                size, state, self.bag.get_items(battle_item_type=BAG_DISPLAY_ITEM_TYPE_MAP[state]), scale
            ) for state in BagDisplayStates if state not in (BagDisplayStates.home, BagDisplayStates.select)
        }


class BattleDisplayBagItem(SpriteScreen):
    def __init__(self, size, display_type, items, scale):
        super().__init__(size, colour=Colours.black)

        self.parent_display_type = display_type
        self.scale = scale

        self.load_image("assets/battle/touch_display/bag/background_item.png", base=True, scale=pg.Vector2(self.scale, self.scale))
        return_container = DisplayContainer("assets/containers/bag_return.png", TouchDisplayStates.bag, pos=(217, 152), scale=self.scale)

        self.sprites.add([return_container])

        item_containers = [ItemContainer(item, count, self.parent_display_type, pos=ITEM_CONTAINER_POSITIONS[idx], scale=scale) for idx, (item, count) in enumerate(items.items())]
        self.sprites.add(item_containers)

    def update_container(self, item, count):
        if count == 0:
            self.get_object(item).kill()
            self.refresh()
        else:
            self.get_object(item).update_info(count)


class BattleDisplayItemSelect(SpriteScreen):
    def __init__(self, size, item, count, parent, scale):
        super().__init__(size, colour=Colours.black)
        self.display_type = TouchDisplayStates.bag
        self.scale = scale
        self.parent_display_type = parent

        item_type = item.battle_item_type.value
        if not os.path.exists(f"assets/battle/touch_display/bag/background_{item.battle_item_type.value}.png"):
            item_type = "pokeball"

        self.load_image(f"assets/battle/touch_display/bag/background_{item_type}.png", base=True,
                        scale=pg.Vector2(self.scale, self.scale))

        self.add_image(item.image, pos=pg.Vector2(36, 40) * self.scale, scale=pg.Vector2(self.scale, self.scale), location=BlitLocation.centre)
        self.addText(item.name, pos=pg.Vector2(56, 35) * self.scale, colour=Colours.white.value, shadowColour=Colours.darkGrey.value)
        self.addText(f"x{count}", pos=pg.Vector2(160, 35) * self.scale, colour=Colours.white.value, shadowColour=Colours.darkGrey.value)
        if item.description:
            self.addText(item.description.replace("é", "e"), pos=pg.Vector2(20, 75) * self.scale, lines=3,
                               colour=Colours.white.value, shadowColour=Colours.darkGrey.value)

        return_container = DisplayContainer("assets/containers/bag_return.png", self.parent_display_type, pos=(217, 152),
                                            scale=self.scale)

        select_container = DisplayContainer("assets/containers/item_select_pokeball.png", item, pos=(1, 152), scale=self.scale)
        select_container.sprite_type = "item"
        select_container.addText("USE", pos=pg.Vector2(92, 17) * self.scale, colour=Colours.white.value, shadowColour=Colours.darkGrey.value)
        select_container.image = select_container.get_surface()

        self.sprites.add([return_container, select_container])


class BattleDisplayTeam(SpriteScreen):
    def __init__(self, size, team, scale):
        super().__init__(size, colour=Colours.black)
        self.scale = scale
        self.display_type = TouchDisplayStates.team

        self.team = team

        self.load_image("assets/battle/touch_display/pokemon/background.png", base=True,
                        scale=pg.Vector2(self.scale, self.scale))

        self.load_image("assets/battle/touch_display/pokemon/choose_bubble.png", pos=pg.Vector2(3, 162) * self.scale,
                        scale=pg.Vector2(self.scale, self.scale), base=True)

        return_container = DisplayContainer("assets/containers/bag_return.png", TouchDisplayStates.home, pos=(217, 152),
                                            scale=self.scale)

        self.pk_containers = pg.sprite.Group()
        for idx in range(6):
            if idx == 0:
                self.pk_containers.add(PokemonContainerTeam(self.team.pokemon[0], primary=True, pos=pg.Vector2(TEAM_CONTAINER_POSITIONS[0]), scale=self.scale))
            elif idx < len(self.team.pokemon):
                self.pk_containers.add(PokemonContainerTeam(self.team.pokemon[idx], pos=pg.Vector2(TEAM_CONTAINER_POSITIONS[idx]), scale=self.scale))
            else:
                self.pk_containers.add(PokemonContainerTeam(None, pos=pg.Vector2(TEAM_CONTAINER_POSITIONS[idx]), scale=self.scale))

        self.sprites.add(return_container)
        self.sprites.add(self.pk_containers)

        for cont in [cont for cont in self.pk_containers if cont.pokemon]:
            cont.update_stats()

        self.img_update = time.monotonic()

        self.select_idx = 0

        self.sub_displays = None
        self.set_sub_displays()

        self.active_display = self

    def set_sub_displays(self):
        self.sub_displays = {
            TeamDisplayStates.select: PokemonSelector(self.size, self.team.pokemon[self.select_idx], self.scale),
            TeamDisplayStates.summary: PokemonSummary(self.size, self.team.pokemon[self.select_idx], self.scale),
        }

    def select_action(self):
        action = None
        while not action:
            for event in pg.event.get():
                if event.type == pg.MOUSEBUTTONDOWN:
                    pos = pg.mouse.get_pos()
                    pos = pg.Vector2(pos) - pg.Vector2(0, self.size.y)
                    clicked = self.active_display.click_test(pos)

                    if clicked:
                        print(clicked)
                        if action:
                            return action

    def update_stats(self):
        print("refresh")
        self.refresh()
        for cont in [cont for cont in self.pk_containers if cont.pokemon]:
            cont.update_stats()

    def get_surface(self, show_sprites=True):
        self.refresh()

        if show_sprites:
            self.sprites.draw(self)

        display_surf = self.base_surface.copy()
        display_surf.blit(self.surface, (0, 0))
        display_surf.blit(self.sprite_surface, (0, 0))

        for cont in [cont for cont in self.pk_containers if cont.pokemon]:
            cont.toggle_mini()

        return display_surf


class PokemonSelector(SpriteScreen):
    def __init__(self, size, pokemon, scale):
        super().__init__(size, colour=Colours.black)
        self.display_type = TouchDisplayStates.team
        self.scale = scale

        self.load_image("assets/battle/touch_display/pokemon/background_select.png", base=True,
                        scale=pg.Vector2(self.scale, self.scale))

        self.select_container = PokemonContainerSingle(pokemon, pos=(9, 8), scale=self.scale)

        return_container = DisplayContainer("assets/containers/bag_return.png", TouchDisplayStates.team, pos=(217, 152),
                                            scale=self.scale)
        summary_container = DisplayContainer("assets/containers/pokemon_container_2.png", TeamDisplayStates.summary, pos=(1, 152), scale=self.scale)
        summary_container.addText("SUMMARY", pos=pg.Vector2(51, 16) * self.scale, lines=1, location=BlitLocation.midTop,
                                  colour=Colours.white.value, shadowColour=Colours.lightGrey.value)
        summary_container.image = summary_container.get_surface()

        check_container = DisplayContainer("assets/containers/pokemon_container_2.png", TeamDisplayStates.moves, pos=(105, 152),
                                             scale=self.scale)
        check_container.addText("CHECK MOVES", pos=pg.Vector2(51, 16) * self.scale, lines=1, location=BlitLocation.midTop,
                                  colour=Colours.white.value, shadowColour=Colours.lightGrey.value)
        check_container.image = check_container.get_surface()

        self.sprites.add([summary_container, return_container, check_container, self.select_container])

    def get_surface(self, show_sprites=True):
        self.refresh()

        if show_sprites:
            self.sprites.draw(self)

        display_surf = self.base_surface.copy()
        display_surf.blit(self.surface, (0, 0))
        display_surf.blit(self.sprite_surface, (0, 0))

        self.select_container.toggle_mini()

        return display_surf

    def load_pk_details(self, pokemon):
        print(f"loading {pokemon}")
        self.sprites.remove(self.select_container)
        self.select_container = PokemonContainerSingle(pokemon, pos=(9, 8), scale=self.scale)
        self.sprites.add(self.select_container)


class PokemonSummary(SpriteScreen):
    def __init__(self, size, pokemon, scale):
        self.scale = scale
        SpriteScreen.__init__(self, size, colour=Colours.black)
        self.load_image("assets/battle/touch_display/pokemon/background_summary.png", base=True,
                        scale=pg.Vector2(self.scale, self.scale))

        up_arrow = DisplayContainer("assets/containers/team_up_arrow.png", "up", pos=pg.Vector2(1, 152), scale=self.scale)
        down_arrow = DisplayContainer("assets/containers/team_down_arrow.png", "down", pos=pg.Vector2(41, 152),
                                    scale=self.scale)
        return_container = DisplayContainer("assets/containers/bag_return.png", TeamDisplayStates.select, pos=(217, 152),
                                            scale=self.scale)

        summary_container = DisplayContainer("assets/containers/pokemon_container_2.png", TeamDisplayStates.moves, pos=(97, 152),
                                             scale=self.scale)
        summary_container.addText("Check Moves", pos=pg.Vector2(51, 16) * self.scale, lines=1, location=BlitLocation.midTop,
                                  colour=Colours.white.value, shadowColour=Colours.lightGrey.value)
        summary_container.image = summary_container.get_surface()

        self.sprites.add([return_container, up_arrow, down_arrow, summary_container])

        self.addText("Lv.", pos=pg.Vector2(8, 35) * self.scale, base=True,
                     colour=Colours.white.value, shadowColour=Colours.darkGrey.value)
        self.addText("NEXT LV", pos=pg.Vector2(8, 51) * self.scale, base=True,
                     colour=Colours.white.value, shadowColour=Colours.darkGrey.value)

        self.addText("HP", pos=pg.Vector2(168, 35) * self.scale, base=True,
                     colour=Colours.white.value, shadowColour=Colours.darkGrey.value)
        self.addText("ATTACK", pos=pg.Vector2(168, 59) * self.scale, base=True,
                     colour=Colours.white.value, shadowColour=Colours.darkGrey.value)
        self.addText("DEFENCE", pos=pg.Vector2(168, 75) * self.scale, base=True,
                     colour=Colours.white.value, shadowColour=Colours.darkGrey.value)
        self.addText("SP. ATK", pos=pg.Vector2(168, 91) * self.scale, base=True,
                     colour=Colours.white.value, shadowColour=Colours.darkGrey.value)
        self.addText("SP. DEF", pos=pg.Vector2(168, 107) * self.scale, base=True,
                     colour=Colours.white.value, shadowColour=Colours.darkGrey.value)
        self.addText("SPEED", pos=pg.Vector2(168, 123) * self.scale, base=True,
                     colour=Colours.white.value, shadowColour=Colours.black.value)

        self.small_sprite = None
        self.load_pk_details(pokemon)
        self.img_update = time.monotonic()

    def load_pk_details(self, pokemon):
        # add small sprite to the top
        small = self.get_object("small")
        if small:
            small.kill()

        self.small_sprite = PokemonSpriteSmall(pokemon.small_animation, pos=pg.Vector2(23, 16) * self.scale)
        self.sprites.add(self.small_sprite)

        # ======== PK Details =============
        self.addText(pokemon.name, pos=pg.Vector2(40, 11) * self.scale,
                     colour=Colours.white.value, shadowColour=Colours.black.value)

        self.load_image(f"Images/Type Labels/{pokemon.type1} Label.png", pos=pg.Vector2(114, 9) * self.scale, scale=pg.Vector2(self.scale))
        if pokemon.type2 is not None:
            self.load_image(f"Images/Type Labels/{pokemon.type2} Label.png", pos=pg.Vector2(148, 9) * self.scale,
                            scale=pg.Vector2(self.scale))

        self.addText(f"{pokemon.level}", pos=pg.Vector2(40, 35) * self.scale,
                     colour=Colours.white.value, shadowColour=Colours.black.value)
        self.addText(f"{pokemon.level_up_exp - pokemon.exp}", pos=pg.Vector2(152, 51) * self.scale, location=BlitLocation.topRight,
                     colour=Colours.darkGrey.value, shadowColour=Colours.midGrey.value)

        self.addText(pokemon.ability, pos=pg.Vector2(9, 75) * self.scale,
                     colour=Colours.white.value, shadowColour=Colours.black.value)

        if pokemon.item is not None:
            ...
        else:
            self.addText("No item held", pos=pg.Vector2(32, 130) * self.scale,
                         colour=Colours.white.value, shadowColour=Colours.black.value)

        # ======== Battle Stats =============
        self.addText(f"{pokemon.health}/{pokemon.stats.health}", pos=pg.Vector2(205, 35) * self.scale,
                     colour=Colours.darkGrey.value, shadowColour=Colours.midGrey.value)

        self.addText(f"{pokemon.stats.attack}", pos=pg.Vector2(247, 59) * self.scale, location=BlitLocation.topRight,
                     colour=Colours.darkGrey.value, shadowColour=Colours.midGrey.value)
        self.addText(f"{pokemon.stats.defence}", pos=pg.Vector2(247, 75) * self.scale, location=BlitLocation.topRight,
                     colour=Colours.darkGrey.value, shadowColour=Colours.midGrey.value)
        self.addText(f"{pokemon.stats.spAttack}", pos=pg.Vector2(247, 91) * self.scale, location=BlitLocation.topRight,
                     colour=Colours.darkGrey.value, shadowColour=Colours.midGrey.value)
        self.addText(f"{pokemon.stats.spDefence}", pos=pg.Vector2(247, 107) * self.scale, location=BlitLocation.topRight,
                     colour=Colours.darkGrey.value, shadowColour=Colours.midGrey.value)
        self.addText(f"{pokemon.stats.speed}", pos=pg.Vector2(247, 123) * self.scale, location=BlitLocation.topRight,
                     colour=Colours.darkGrey.value, shadowColour=Colours.midGrey.value)

        # health bar
        health_ratio = pokemon.health / pokemon.stats.health

        bar_rect = pg.Rect(pg.Vector2(63, 24), pg.Vector2(48 * health_ratio, 4))

        if health_ratio > 0.5:
            colour = "high"
        elif health_ratio > 0.25:
            colour = "medium"
        else:
            colour = "low"

        health_bar = pg.image.load(f"assets/battle/main_display/health_bar/health_{colour}.png")
        health_bar = pg.transform.scale(health_bar, bar_rect.size)

        self.add_image(health_bar, pos=pg.Vector2(200, 49) * self.scale, scale=pg.Vector2(self.scale, self.scale))

    def get_surface(self, show_sprites=True):
        self.refresh(sprite_only=True)

        now = time.monotonic()
        if now - self.img_update > 0.15 and self.small_sprite is not None:
            self.small_sprite.toggle_image()
            self.img_update = now

        if show_sprites:
            self.sprites.draw(self)

        display_surf = self.base_surface.copy()
        display_surf.blit(self.surface, (0, 0))
        display_surf.blit(self.sprite_surface, (0, 0))

        return display_surf


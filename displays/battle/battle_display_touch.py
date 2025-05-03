from screen_V2 import Colours, FontOption, Screen, BlitLocation
from sprite_screen import SpriteScreen
import pygame as pg
from enum import Enum


MOVE_CONTAINER_POSITIONS = [(2, 25), (130, 25), (2, 85), (130, 85)]


class TouchDisplayTypes(Enum):
    home = 0
    fight = 1
    team = 2
    bag = 3


class BagDisplayTypes(Enum):
    home = 0
    restore = 1
    pokeball = 2
    healers = 3
    items = 4


class DisplayContainer(pg.sprite.Sprite):
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

        self.screen = Screen(self.image.get_size())
        self.screen.load_image(img_path, base=True, scale=pg.Vector2(scale, scale))
        self.screen.addText(move.name, pg.Vector2((int(62 * scale), int(13 * scale))), base=True, location=BlitLocation.midTop)

        self.screen.addText("PP", pg.Vector2((int(56 * scale), int(31 * scale))),
                             colour=pg.Color(63, 48, 41), shadowColour=pg.Color(153, 158, 136), base=True,
                             location=BlitLocation.midTop)

        self.image = self.screen.get_surface()

        self.scale = scale

    def update_info(self, move):
        self.screen.refresh()
        self.screen.addText(f"{move.PP}/{move.maxPP}", pg.Vector2((int(108 * self.scale), int(34 * self.scale))),
                             fontOption=FontOption.level, location=BlitLocation.topRight)

        self.image = self.screen.get_surface()


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

        self.display_type = TouchDisplayTypes.home

        self.window = window

        self.scale = scale

        self.load_image("assets/battle/touch_display/home/background.png", base=True, scale=pg.Vector2(self.scale, self.scale))

        fight_container = DisplayContainer("assets/containers/battle_fight.png", TouchDisplayTypes.fight, pos=(20, 35), scale=self.scale)
        bag_container = DisplayContainer("assets/containers/battle_bag.png", TouchDisplayTypes.bag, pos=(1, 145), scale=self.scale)
        run_container = DisplayContainer("assets/containers/battle_run.png", "run", pos=(89, 153), scale=self.scale)
        team_container = DisplayContainer("assets/containers/battle_team.png", TouchDisplayTypes.team, pos=(177, 145), scale=self.scale)

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
        self.display_type = TouchDisplayTypes.fight

        self.window = window

        self.scale = scale

        self.load_image("assets/battle/touch_display/fight/background.png", base=True,
                        scale=pg.Vector2(self.scale, self.scale))

        cancel_container = DisplayContainer("assets/containers/fight_cancel.png", TouchDisplayTypes.home, pos=(9, 153),
                                           scale=self.scale)

        self.sprites.add([cancel_container])

    def load_move_sprites(self, moves):

        containers = [
            MoveContainer(move, pos=MOVE_CONTAINER_POSITIONS[idx], scale=self.scale)
            for idx, move in enumerate(moves)
        ]

        for idx, container in enumerate(containers):
            container.update_info(moves[idx])

        self.sprites.add(containers)

    def update_container(self, move):
        self.get_object(move).update_info(move)


class BattleDisplayBag(SpriteScreen):
    def __init__(self, window, size, scale):
        """
        This is the main battle display. The native screen size is 256x192 px
        :param window: The pygame surface to blit the display onto
        :param size: the size of the display
        :param time: the time of day, used to configure the battle background option
        :param environment:
        """
        super().__init__(size, colour=Colours.black)
        self.display_type = TouchDisplayTypes.bag

        self.window = window

        self.scale = scale

        self.load_image("assets/battle/touch_display/bag/background_home.png", base=True, scale=pg.Vector2(self.scale, self.scale))

        return_container = DisplayContainer("assets/containers/bag_return.png", TouchDisplayTypes.home, pos=(217, 152),
                                           scale=self.scale)

        restore_container = DisplayContainer("assets/containers/bag_restore.png", BagDisplayTypes.restore, pos=(1, 8), scale=self.scale)
        pokeball_container = DisplayContainer("assets/containers/bag_pokeball.png", BagDisplayTypes.pokeball, pos=(129, 8),scale=self.scale)
        healer_container = DisplayContainer("assets/containers/bag_healers.png", BagDisplayTypes.healers, pos=(1, 80),
                                             scale=self.scale)
        item_container = DisplayContainer("assets/containers/bag_items.png", BagDisplayTypes.items, pos=(129, 80),
                                             scale=self.scale)

        self.sprites.add([return_container, restore_container, pokeball_container, healer_container, item_container])

        self.sub_displays = {
            BagDisplayTypes.restore: BattleDisplayBagItem(self.window, size, scale),
            BagDisplayTypes.pokeball: BattleDisplayBagItem(self.window, size, scale),
            BagDisplayTypes.healers: BattleDisplayBagItem(self.window, size, scale),
            BagDisplayTypes.items: BattleDisplayBagItem(self.window, size, scale),
        }

    # def load_item_sprites(self, items):
    #
    #     containers = [
    #         MoveContainer(move, pos=MOVE_CONTAINER_POSITIONS[idx], scale=self.scale)
    #         for idx, move in enumerate(moves)
    #     ]
    #
    #     for idx, container in enumerate(containers):
    #         container.update_info(moves[idx])
    #
    #     self.sprites.add(containers)
    #
    # def update_container(self, move):
    #     self.get_object(move).update_info(move)


class BattleDisplayBagItem(SpriteScreen):
    def __init__(self, window, size, scale):
        super().__init__(size, colour=Colours.black)
        self.display_type = TouchDisplayTypes.bag

        self.window = window

        self.scale = scale

        self.load_image("assets/battle/touch_display/bag/background_item.png", base=True, scale=pg.Vector2(self.scale, self.scale))
        return_container = DisplayContainer("assets/containers/bag_return.png", TouchDisplayTypes.bag, pos=(217, 152), scale=self.scale)

        self.sprites.add([return_container])
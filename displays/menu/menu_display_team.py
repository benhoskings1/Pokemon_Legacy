import time
from enum import Enum

import pygame as pg

from pokemon import Pokemon, getImages
from general.utils import Colours
from screen_V2 import FontOption, BlitLocation
from sprite_screen import SpriteScreen, DisplayContainer, GameObjects
from pokemon import PokemonSpriteSmall


CONTAINER_POSITIONS = [(1, 3), (129, 12), (1, 52), (129, 60), (1, 100), (129, 108)]


class MenuTeamDisplayStates(Enum):
    home = 0
    summary = 1
    pokemon_info = 1
    trainer_memo = 2
    pokemon_skills = 3
    battle_moves = 4


class PokemonSummaryStates(Enum):
    info = "info"


class PokemonContainer(DisplayContainer):
    def __init__(self, pokemon, pos, primary=False, selected=False, scale=1):
        """

        :param pokemon:
        :param pos:
        :param scale:
        """
        container_type, selected_ext = "primary" if primary else "secondary", '_selected' if selected else ''

        DisplayContainer.__init__(
            self, f"assets/containers/menu/team/pokemon_container_{container_type}{selected_ext}.png",
            pokemon, pos if not selected else pg.Vector2(pos) - pg.Vector2(0, 2)*scale, scale=scale
        )

        self.pokemon = pokemon
        self.sprite_type = "pokemon_container"
        self.small_sprite = None

        if pokemon:
            self.small_sprite = PokemonSpriteSmall(pokemon.small_animation)
            self.small_sprite.rect.center = pg.Vector2(28, 19) * self.scale
            self.addText(pokemon.name, pg.Vector2(47, 9) * self.scale, base=True, colour=Colours.white.value, shadowColour=Colours.darkGrey.value,)
            self.addText(f"{pokemon.health}/{pokemon.stats.health}", pg.Vector2(72, 32) * self.scale,
                         colour=Colours.white.value,shadowColour=Colours.white.value, fontOption=FontOption.level)
            self.addText(f"Lv{pokemon.level}", pg.Vector2(12, 32) * self.scale,
                         colour=Colours.white.value, shadowColour=Colours.white.value, fontOption=FontOption.level, base=True,)

            self.sprites.add(self.small_sprite)

        self.img_update = time.monotonic()
        self.image_idx = 0

    def toggle_mini(self):
        now = time.monotonic()
        if now - self.img_update > 0.15:
            self.refresh(sprite_only=True)
            self.small_sprite.toggle_image()
            self.img_update = time.monotonic()

    def get_surface(self, show_sprites=True):
        if self.power_off:
            return self.power_off_surface

        self.toggle_mini()
        if show_sprites:
            self.sprites.draw(self)

        display_surf = self.base_surface.copy()
        display_surf.blit(self.surface, (0, 0))
        display_surf.blit(self.sprite_surface, (0, 0))

        return display_surf


class PokemonInfoContainer(DisplayContainer):
    def __init__(self, scale=1):
        DisplayContainer.__init__(
            self,"assets/containers/menu/team/info_container.png", PokemonSummaryStates.info, (104, 30),
            scale=scale
        )

        labels = ["Pokedex No.", "Name", "Type", "OT", "ID No.", "Exp. Points", "", "To Next Lv."]
        for idx, label in enumerate(labels):
            self.add_text_2(
                label, pg.Rect(pg.Vector2(8, 13 + 16*idx) * self.scale, pg.Vector2(80, 12)*self.scale),
                colour=Colours.white, shadow_colour=Colours.darkGrey, base=True
            )

    def load_pokemon_details(self, pokemon: Pokemon):
        values = [f"{pokemon.ID:03}", pokemon.name, "", "Ben", "46649", "",
                  f"{pokemon.exp}", "", f"{pokemon.level_up_exp - pokemon.exp}"]
        for idx, value in enumerate(values):
            self.addText(
                value, pg.Vector2(pg.Vector2(112, 13 + 16 * idx))* self.scale,
                colour=Colours.black.value, shadowColour=Colours.lightGrey.value, base=True, location=BlitLocation.midTop
            )


class MenuTeamDisplayHome(SpriteScreen):
    def __init__(self, size, scale, team):
        SpriteScreen.__init__(self, size)
        self.scale = scale
        self.team = team

        self.load_image("assets/menu/team/home_background.png", base=True, scale=scale)

        self.pk_containers = [
            PokemonContainer(pk, CONTAINER_POSITIONS[idx], primary=idx == 0, scale=scale)
            for idx, pk in enumerate(team.pokemon)
        ]

        self.sprites.add(self.pk_containers)

        self.selected_idx = None

    def update_containers(self, selected_idx: int):
        """
        This function updates the screen by replacing the active display, but only updating the container to be
        deselected, and the new one to be selected.

        :param selected_idx:
        :return:
        """
        if self.selected_idx is None:
            self.selected_idx = 0
        else:
            self.get_object(self.pk_containers[self.selected_idx].pokemon).kill()
            # self.pk_containers[self.selected_idx].kill()
            deselected_container = PokemonContainer(
                self.team.pokemon[self.selected_idx], CONTAINER_POSITIONS[self.selected_idx], primary=selected_idx == 0,
                scale=self.scale
            )
            self.sprites.add(deselected_container)

        self.get_object(self.pk_containers[selected_idx].pokemon).kill()
        selected_container = PokemonContainer(
            self.team.pokemon[selected_idx], CONTAINER_POSITIONS[selected_idx], primary=selected_idx == 0, selected=True,
            scale=self.scale
        )
        self.sprites.add(selected_container)
        self.selected_idx = selected_idx

        self.refresh()

    def process_input(self, key, controller) -> None | Pokemon | str:
        """
        Process a user input.

        :param key: user input.
        :param controller: controller object
        :return:
        """
        # ======= Processing Functions ========
        if key == controller.a:
            print(repr(self.pk_containers[self.selected_idx].pokemon))
            return self.pk_containers[self.selected_idx].pokemon
        elif key == controller.b:
            return "back"

        # ======= Move Selector ========
        elif self.selected_idx is None:
            self.update_containers(selected_idx=0)

        elif key == controller.down:
            self.update_containers(min([self.selected_idx + 1, len(self.sprites) - 1]))
        elif key == controller.up:
            self.update_containers(max([self.selected_idx - 1, 0]))

        return None


class MenuTeamDisplaySummary(SpriteScreen):
    def __init__(self, size, pokemon, scale=1):
        SpriteScreen.__init__(self, size)
        self.scale = scale
        self.pokemon = pokemon

        self.load_image("assets/menu/team/summary_background.png", base=True, scale=scale)

        front_image, _, _ = getImages(pokemon.ID, crop=False)
        self.add_image(front_image, pg.Vector2(53, 106)*self.scale, base=True, location=BlitLocation.centre)

        self.containers = {
            PokemonSummaryStates.info: PokemonInfoContainer(scale=scale),
        }

        for container in self.containers.values():
            container.load_pokemon_details(pokemon)

        self.sprites.add(self.containers[PokemonSummaryStates.info])

    def process_input(self, key, controller):
        ...


class MenuTeamDisplay:
    def __init__(self, size, scale, game):
        self.game = game

        self.displays = {
            MenuTeamDisplayStates.home: MenuTeamDisplayHome(size, scale, game.team),
            MenuTeamDisplayStates.summary: MenuTeamDisplaySummary(size, game.team.pokemon[0], scale=scale),
        }

        self.active_display_state = MenuTeamDisplayStates.home
        self.active_display = self.displays[self.active_display_state ]

    def update_display(self):
        self.game.topSurf.blit(self.active_display.get_surface(), (0, 0))
        pg.display.flip()

    def loop(self):
        self.update_display()
        controller = self.game.controller

        while True:
            for event in pg.event.get():
                if event.type == pg.KEYDOWN:
                    if event.key in controller.keys:
                        action = self.active_display.process_input(event.key, controller)

                        if isinstance(action, Pokemon):
                            self.active_display = self.displays[MenuTeamDisplayStates.summary]

                        elif action == "back":
                            return None

            self.update_display()






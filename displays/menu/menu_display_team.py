import time
from enum import Enum

import pygame as pg

from general.utils import Colours
from screen_V2 import FontOption
from sprite_screen import SpriteScreen, DisplayContainer
from pokemon import PokemonSpriteSmall


CONTAINER_POSITIONS = [(1, 3), (129, 12), (1, 52), (129, 60), (1, 100), (129, 108)]


class MenuTeamDisplayStates(Enum):
    home = 0
    pokemon_info = 1
    trainer_memo = 2
    pokemon_skills = 3
    battle_moves = 4


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

    def update_containers(self, selected_idx):
        if self.selected_idx is None:
            self.selected_idx = 0
        else:
            # handle killing of previous
            ...
        self.pk_containers[self.selected_idx].kill()
        deselected_container = PokemonContainer(
            self.team.pokemon[self.selected_idx], CONTAINER_POSITIONS[self.selected_idx], primary=selected_idx == 0,
            scale=self.scale
        )
        self.pk_containers.insert(self.selected_idx, deselected_container)

        self.pk_containers[selected_idx].kill()
        selected_container = PokemonContainer(
            self.team.pokemon[selected_idx], CONTAINER_POSITIONS[selected_idx], primary=selected_idx == 0, selected=True,
            scale=self.scale
        )
        self.pk_containers.insert(selected_idx, selected_container)
        self.selected_idx = selected_idx

        self.refresh()
        self.sprites.add(selected_container)


class MenuTeamDisplay:
    def __init__(self, size, scale, game):
        self.game = game

        self.displays = {
            MenuTeamDisplayStates.home: MenuTeamDisplayHome(size, scale, game.team),
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
                    if (
                        event.key in controller.keys and
                        self.active_display_state == MenuTeamDisplayStates.home and
                        self.active_display.selected_idx is None
                    ):
                        self.active_display.update_containers(selected_idx=0)

                    elif event.key == controller.down:
                        self.active_display.update_containers(
                            selected_idx=min([self.active_display.selected_idx+1, len(self.active_display.sprites)-1])
                        )
                    elif event.key == controller.up:
                        self.active_display.update_containers(
                            selected_idx=min(
                                [self.active_display.selected_idx - 1, 0])
                        )

            self.update_display()






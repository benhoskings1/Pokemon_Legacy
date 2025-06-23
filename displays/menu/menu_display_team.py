import time
from enum import Enum

import pygame as pg

import team
from pokemon import Pokemon, getImages
from general.utils import Colours, create_display_bar
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
    exit = 6


class PokemonSummaryStates(Enum):
    info = 0
    memo = 1
    skills = 2
    moves = 3


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
            pokemon, pos if not selected else pg.Vector2(pos) - pg.Vector2(0, 2) * scale, scale=scale
        )

        self.pokemon = pokemon
        self.sprite_type = "pokemon_container"
        self.small_sprite = None

        if pokemon:
            self.small_sprite = PokemonSpriteSmall(pokemon.small_animation)
            self.small_sprite.rect.center = pg.Vector2(28, 19) * self.scale
            self.addText(pokemon.name, pg.Vector2(47, 9) * self.scale, base=True, colour=Colours.white.value,
                         shadowColour=Colours.darkGrey.value, )
            self.addText(f"{pokemon.health}/{pokemon.stats.health}", pg.Vector2(72, 32) * self.scale,
                         colour=Colours.white.value, shadowColour=Colours.white.value, fontOption=FontOption.level)
            self.addText(f"Lv{pokemon.level}", pg.Vector2(12, 32) * self.scale,
                         colour=Colours.white.value, shadowColour=Colours.white.value, fontOption=FontOption.level,
                         base=True, )

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
            self, "assets/containers/menu/team/info_container.png", PokemonSummaryStates.info, (104, 30),
            scale=scale
        )

        labels = ["Pokedex No.", "Name", "Type", "OT", "ID No.", "Exp. Points", "", "To Next Lv."]
        for idx, label in enumerate(labels):
            self.add_text_2(
                label, pg.Rect(pg.Vector2(8, 13 + 16 * idx) * self.scale, pg.Vector2(80, 12) * self.scale),
                colour=Colours.white, shadow_colour=Colours.darkGrey, base=True, sep=0
            )

    def load_pokemon_details(self, pokemon: Pokemon):
        values = [f"{pokemon.ID:03}", pokemon.name, "", "Ben", "46649", "",
                  f"{pokemon.exp}", "", f"{pokemon.level_up_exp - pokemon.exp}"]
        for idx, value in enumerate(values):
            self.addText(
                value, pg.Vector2(pg.Vector2(112, 13 + 16 * idx)) * self.scale,
                colour=Colours.black.value, shadowColour=Colours.lightGrey.value, location=BlitLocation.midTop,
            )

        exp_bar = create_display_bar(pokemon.exp - pokemon.level_exp, pokemon.level_up_exp - pokemon.level_exp,
                                     bar_type="exp")
        self.add_image(exp_bar, pos=pg.Vector2(80, 156) * self.scale, scale=pg.Vector2(self.scale, self.scale))


class PokemonMemoContainer(DisplayContainer):
    def __init__(self, scale=1):
        DisplayContainer.__init__(
            self, "assets/containers/menu/team/memo_container.png", PokemonSummaryStates.memo, (104, 30),
            scale=scale
        )

    def load_pokemon_details(self, pokemon: Pokemon):
        values = [f"{pokemon.nature} nature.", f"{pokemon.catchLocation if pokemon.catchLocation is not None else ''}",
                  f"Met at Lv. {pokemon.catchLevel}", "", "Proud of its power", "Happily Eats"]
        for idx, value in enumerate(values):
            self.addText(
                value, pg.Vector2(pg.Vector2(8, 13 + 16 * idx)) * self.scale,
                colour=Colours.black.value, shadowColour=Colours.lightGrey.value,
            )


class PokemonSkillContainer(DisplayContainer):
    def __init__(self, scale=1):
        DisplayContainer.__init__(
            self, "assets/containers/menu/team/skills_container.png", PokemonSummaryStates.skills, (104, 30),
            scale=scale
        )

        self.add_text_2("HP", pg.Rect(pg.Vector2(40, 5) * self.scale, pg.Vector2(80, 12) * self.scale),
                        colour=Colours.white, shadow_colour=Colours.darkGrey, base=True, sep=0)

        labels = ["Attack", "Defence", "Sp. Atk", "Sp. Def", "Speed"]
        for idx, label in enumerate(labels):
            self.add_text_2(
                label, pg.Rect(pg.Vector2(24, 29 + 16 * idx) * self.scale, pg.Vector2(80, 12) * self.scale),
                colour=Colours.white, shadow_colour=Colours.darkGrey, base=True, sep=0
            )

        self.add_text_2("Ability", pg.Rect(pg.Vector2(8, 117) * self.scale, pg.Vector2(80, 12) * self.scale),
                        colour=Colours.white, shadow_colour=Colours.darkGrey, base=True, sep=0)

    def load_pokemon_details(self, pokemon: Pokemon):
        self.refresh()
        self.addText(f"{pokemon.health}/{pokemon.stats.health}", pg.Vector2(108, 5) * self.scale,
                     location=BlitLocation.midTop, colour=Colours.black.value, shadowColour=Colours.lightGrey.value,)

        values = [f"{stat}" for stat in pokemon.stats[1:]]
        for idx, value in enumerate(values):
            self.addText(
                value, pg.Vector2(pg.Vector2(114, 29 + 16 * idx)) * self.scale,
                colour=Colours.black.value, shadowColour=Colours.lightGrey.value, location=BlitLocation.midTop,
            )

        self.addText(f"{pokemon.ability.name}", pg.Vector2(64, 117) * self.scale, colour=Colours.black.value,
                     shadowColour=Colours.lightGrey.value,)

        if pokemon.ability.description:
            self.add_text_2(pokemon.ability.description, pg.Rect(pg.Vector2(8, 133) * self.scale, pg.Vector2(142, 28) * self.scale),
                            colour=Colours.black.value, shadow_colour=Colours.lightGrey.value, sep=0)

        health_bar = create_display_bar(pokemon.health, pokemon.stats.health, "HP")
        self.add_image(health_bar, pos=pg.Vector2(88, 20) * self.scale, scale=pg.Vector2(self.scale, self.scale))


class PokemonMovesContainer(DisplayContainer):
    def __init__(self, scale=1):
        DisplayContainer.__init__(
            self, "assets/containers/menu/team/moves_container.png", PokemonSummaryStates.moves, (104, 30),
            scale=scale
        )

    def load_pokemon_details(self, pokemon: Pokemon):
        ...


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
            self.team.pokemon[selected_idx], CONTAINER_POSITIONS[selected_idx], primary=selected_idx == 0,
            selected=True,
            scale=self.scale
        )
        self.sprites.add(selected_container)
        self.selected_idx = selected_idx

        self.refresh()

    def process_input(self, key, controller) -> None | Pokemon | MenuTeamDisplayStates:
        """
        Process a user input.

        :param key: user input.
        :param controller: controller object
        :return:
        """
        # ======= Processing Functions ========
        if key == controller.a:
            # print(repr(self.pk_containers[self.selected_idx].pokemon))
            return self.pk_containers[self.selected_idx].pokemon
        elif key == controller.b:
            return MenuTeamDisplayStates.exit

        # ======= Move Selector ========
        elif self.selected_idx is None:
            self.update_containers(selected_idx=0)

        elif key == controller.down:
            self.update_containers(min([self.selected_idx + 1, len(self.sprites) - 1]))
        elif key == controller.up:
            self.update_containers(max([self.selected_idx - 1, 0]))

        return None


class MenuTeamDisplaySummary(SpriteScreen):
    def __init__(self, size, team, scale=1):
        SpriteScreen.__init__(self, size)
        self.scale = scale
        self.team = team

        self.load_image("assets/menu/team/summary_background.png", base=True, scale=scale)

        self.addText(
            "POKeMON INFO", pg.Vector2(pg.Vector2(8, 3)) * self.scale,
            colour=Colours.white.value, shadowColour=Colours.darkGrey.value, base=True
        )

        self.addText(
            "Item", pg.Vector2(pg.Vector2(9, 163)) * self.scale,
            colour=Colours.white.value, shadowColour=Colours.darkGrey.value, base=True
        )

        self.addText(
            "Lv", pg.Vector2(pg.Vector2(12, 46)) * self.scale,
            colour=Colours.white.value, shadowColour=Colours.darkGrey.value, base=True, fontOption=FontOption.level
        )

        self.load_image("assets/menu/team/pokeball.png", pg.Vector2(8, 25) * self.scale, base=True, scale=scale)

        self.containers = {
            PokemonSummaryStates.info: PokemonInfoContainer(scale=scale),
            PokemonSummaryStates.memo: PokemonMemoContainer(scale=scale),
            PokemonSummaryStates.skills: PokemonSkillContainer(scale=scale),
            PokemonSummaryStates.moves: PokemonMovesContainer(scale=scale),
        }

        self.selected_idx, self.active_screen_idx = 0, 0

        self.sprites.add(self.containers[PokemonSummaryStates(self.active_screen_idx)])

        self.load_pokemon_details(team.pokemon[0])

    def load_pokemon_details(self, pokemon: Pokemon):
        self.refresh()

        front_image, _, _ = getImages(pokemon.ID, crop=False)

        self.addText(
            pokemon.name.upper(), pg.Vector2(pg.Vector2(24, 27)) * self.scale,
            colour=Colours.white.value, shadowColour=Colours.darkGrey.value
        )
        self.addText(f"{pokemon.level}", pg.Vector2(25, 43) * self.scale)
        self.add_image(front_image, pg.Vector2(52, 104) * self.scale, location=BlitLocation.centre)
        self.load_image(f"assets/general/{pokemon.gender}.png", pos=pg.Vector2(90, 27) * self.scale, scale=self.scale)
        self.addText("None" if pokemon.item is None else pokemon.item.name, pg.Vector2(8, 179) * self.scale)

        for container in self.containers.values():
            container.refresh()
            container.load_pokemon_details(pokemon)

    def process_input(self, key, controller):
        # ======= Processing Functions ========
        if key == controller.a:
            ...

        elif key == controller.b:
            return MenuTeamDisplayStates.home

        elif key == controller.right or key == controller.left:
            # self.active_screen
            self.get_object(PokemonSummaryStates(self.active_screen_idx)).kill()
            self.active_screen_idx = (self.active_screen_idx + (1 if key == controller.right else - 1)) % len(PokemonSummaryStates)
            self.sprites.add(self.containers[PokemonSummaryStates(self.active_screen_idx)])
            self.refresh()
            self.load_pokemon_details(self.team.pokemon[self.selected_idx])

        # ======= Move Selector ========
        # elif self.selected_idx is None:
        #     self.update_containers(selected_idx=0)
        #
        elif key == controller.down:
            self.selected_idx = (self.selected_idx + 1) % len(self.team)
            self.load_pokemon_details(self.team.pokemon[self.selected_idx])
            # self.update_containers(min([self.selected_idx + 1, len(self.sprites) - 1]))
        # elif key == controller.up:
        #     self.update_containers(max([self.selected_idx - 1, 0]))

        return None


class MenuTeamDisplay:
    def __init__(self, size, scale, game):
        self.game = game

        self.displays = {
            MenuTeamDisplayStates.home: MenuTeamDisplayHome(size, scale, game.team),
            MenuTeamDisplayStates.summary: MenuTeamDisplaySummary(size, game.team, scale=scale),
        }

        self.active_display_state = MenuTeamDisplayStates.home
        self.active_display = self.displays[self.active_display_state]

        self.selected_idx = None

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

                        if isinstance(action, MenuTeamDisplayStates):
                            if action == MenuTeamDisplayStates.exit:
                                return None
                            elif action == MenuTeamDisplayStates.home:
                                self.displays[action].selected_idx = self.active_display.selected_idx
                                self.displays[action].update_containers(selected_idx=self.active_display.selected_idx)
                            self.active_display = self.displays[action]

                        if isinstance(action, Pokemon):
                            self.active_display = self.displays[MenuTeamDisplayStates.summary]
                            self.active_display.selected_idx = self.game.team.get_index(action)
                            self.active_display.load_pokemon_details(action)
                            # for container in self.active_display.containers.values():
                            #     container.load_pokemon_details(action)

            self.update_display()

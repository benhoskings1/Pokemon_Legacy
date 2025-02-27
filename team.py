from pokemon import Pokemon


class Team:
    def __init__(self, data):
        self.pokemon = []
        for pkData in data:
            pokemon = Pokemon(**pkData)
            self.pokemon.append(pokemon)

import pandas as pd

ABIlITIES = pd.read_csv("game_data/abilities.tsv", sep="\t", index_col=0)


class Ability:
    def __init__(self, ability_id):
        data = ABIlITIES.loc[ability_id]
        self.id = ability_id


if __name__ == "__main__":
    ability = Ability(ability_id=1)
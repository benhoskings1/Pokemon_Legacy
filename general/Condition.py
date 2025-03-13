from enum import Enum

from general.Status_Conditions.Burn import Burn
from general.Status_Conditions.Poison import Poison


class StatusCondition(Enum):
    poison = Poison()
    burn = Burn()

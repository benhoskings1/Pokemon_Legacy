from enum import Enum

from General.Status_Conditions.Burn import Burn
from General.Status_Conditions.Poison import Poison


class StatusCondition(Enum):
    poison = Poison()
    burn = Burn()

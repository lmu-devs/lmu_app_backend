from enum import Enum
from typing import List
from pydantic import BaseModel

from shared.src.models import Timeframe


class SemesterTypeEnum(str, Enum):
    SUMMER = "SUMMER"
    WINTER = "WINTER"

class Semester(BaseModel):
    timeframe: Timeframe
    type: SemesterTypeEnum
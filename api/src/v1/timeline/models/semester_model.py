from pydantic import BaseModel

from shared.src.enums.courses_enums import SemesterEnum
from shared.src.models import Timeframe


class Semester(BaseModel):
    timeframe: Timeframe
    type: SemesterEnum

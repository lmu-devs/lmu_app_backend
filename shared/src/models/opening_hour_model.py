from datetime import time
from typing import List, Optional

from pydantic import BaseModel, ConfigDict

from shared.src.enums.weekday_enum import WeekdayEnum
from shared.src.tables.food.canteen_table import CanteenOpeningHoursTable


class OpeningHour(BaseModel):
    day: WeekdayEnum
    start_time: Optional[time]
    end_time: Optional[time]

    model_config = ConfigDict(arbitrary_types_allowed=True)

    @classmethod
    def from_table(cls, opening_hour: CanteenOpeningHoursTable) -> "OpeningHour":
        return OpeningHour(
            day=opening_hour.day,
            start_time=opening_hour.start_time,
            end_time=opening_hour.end_time,
        )


class ActiveOpeningHours(BaseModel):
    opening_hours: List[OpeningHour] | None
    serving_hours: List[OpeningHour] | None


class OpeningHours(ActiveOpeningHours):
    lecture_free_hours: List[OpeningHour] | None
    lecture_free_serving_hours: List[OpeningHour] | None

from datetime import time as datetime_time
from typing import List, Optional

from pydantic import BaseModel, ConfigDict

from shared.src.enums.weekday_enum import WeekdayEnum


class OpeningHour(BaseModel):
    day: WeekdayEnum
    start_time: Optional[datetime_time]
    end_time: Optional[datetime_time]
    
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
# class ActiveOpeningHours(BaseModel):
#     opening_hours: List[OpeningHour] | None
#     serving_hours: List[OpeningHour] | None

class OpeningHours(BaseModel):
    opening_hours: List[OpeningHour] | None
    serving_hours: List[OpeningHour] | None
    lecture_free_hours: List[OpeningHour] | None
    lecture_free_serving_hours: List[OpeningHour] | None    
    
    

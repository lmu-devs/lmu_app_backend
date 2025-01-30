from enum import Enum
from typing import List
from pydantic import BaseModel

from shared.src.models import Location, Timeframe


class EventTypeEnum(str, Enum):
    EVENT = "EVENT"
    HOLIDAY = "HOLIDAY"
    EXAM = "EXAM"
    SPORT = "SPORT"
    SEMESTER = "SEMESTER"
    EXCHANGE = "EXCHANGE"
    HOUSING = "HOUSING"
    OTHER = "OTHER"

class Event(BaseModel):
    title: str
    type: EventTypeEnum
    timeframe: Timeframe
    description: str | None = None
    location: Location | None = None
    url: str | None = None
    

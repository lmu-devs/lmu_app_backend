from datetime import time
from typing import Dict, List, Optional, Union

from pydantic import BaseModel

from shared.src.enums import WeekdayEnum
from shared.src.models.link_model import Link
from shared.src.models.location_model import Location
from shared.src.models.phone_model import Phones


class TimeSlot(BaseModel):
    day: WeekdayEnum
    start_time: time
    end_time: time


class Equipment(BaseModel):
    name: str
    url: Optional[Link] = None


class Contact(BaseModel):
    location: Optional[Location] = None
    email: Optional[List[str]] = None
    phone: Optional[Phones] = None
    website: Optional[Link] = None


class TimeRange(BaseModel):
    start_time: time
    end_time: time


class OpeningHoursDays(BaseModel):
    day: WeekdayEnum
    time_ranges: List[TimeRange]


class OpeningHours(BaseModel):
    days: List[OpeningHoursDays]


class Library(BaseModel):
    id: str
    name: str
    hash: str
    url: Link | None = None
    reservation_url: Link | None = None
    details: Dict[str, Union[str, Dict, List]] | None = None
    contact: Contact | None = None
    opening_hours: OpeningHours | None = None
    services: List[Link] | None = []
    equipment: List[Equipment] | None = []
    subject_areas: List[str] | None = []
    search_hints: List[Link] | None = []
    transportation: str | None = None

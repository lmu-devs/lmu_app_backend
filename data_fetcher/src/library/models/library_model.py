from datetime import time
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field, RootModel

from shared.src.enums import WeekdayEnum
from shared.src.models.image_model import Images
from shared.src.models.link_model import Link, TextsWithLink, TextWithLink
from shared.src.models.location_model import Location
from shared.src.models.phone_model import Phones


class EquipmentEnum(str, Enum):
    ACCESSIBILITY = "ACCESSIBILITY"
    LOCKERS = "LOCKERS"
    GROUP_WORK_ROOMS = "GROUP_WORK_ROOMS"
    INDIVIDUAL_WORK_ROOMS = "INDIVIDUAL_WORK_ROOMS"
    PARENTING = "PARENTING"
    COPIER = "COPIER"
    BOOK_SCANNER = "BOOK_SCANNER"
    BEAMER_RENTAL = "BEAMER_RENTAL"
    WIFI = "WIFI"
    FOOD_AND_DRINKS = "FOOD_AND_DRINKS"
    OTHER_ROOMS = "OTHER_ROOMS"
    MISC = "MISC"


class Equipment(TextWithLink):
    type: EquipmentEnum = Field(..., description="The type of equipment")
    description: str | None = Field(
        None,
        description="The description of the equipment, if there is additional information. Make it concise.",
    )


class Equipments(RootModel):
    root: List[Equipment] = Field(
        default_factory=list,
        description="A list of equipments, Include locker when it is mentioned.",
    )


class TimeSlot(BaseModel):
    day: WeekdayEnum
    start_time: time
    end_time: time


class Contact(BaseModel):
    email: Optional[List[str]] = None
    phone: Optional[Phones] = None
    website: Optional[Link] = None


class TimeRange(BaseModel):
    start_time: time
    end_time: time


class OpeningHoursDays(BaseModel):
    day: WeekdayEnum = Field(
        ..., description="The day of the week, ONLY USE MONDAY, TUESDAY, WEDNESDAY, THURSDAY, FRIDAY, SATURDAY, SUNDAY"
    )
    time_ranges: List[TimeRange]


class OpeningHours(BaseModel):
    days: List[OpeningHoursDays]


class Area(BaseModel):
    name: str = Field("DEFAULT", description="The name of the area, if there is no name, use DEFAULT")
    opening_hours: OpeningHours | None = Field(
        None,
        description="The opening hours for the area, if there are any.",
    )
    lecture_free_hours: OpeningHours | None = Field(
        None,
        description="The lecture free hours for the area, if there are any.",
    )


class Areas(BaseModel):
    areas: List[Area] = Field(
        default=[],
        description="""A list of library areas with different opening hours. 
        If there is only one area, use the name DEFAULT.
        If there is no area/opening hours, return an empty list.
        """,
    )


class Library(BaseModel):
    id: str
    title: str
    hash: str
    areas: List[Area] = []
    images: Images = Images([])
    url: str | None = None
    reservation_url: str | None = None
    location: Optional[Location] = None
    contact: Contact | None = None
    services: TextsWithLink | None = None
    equipment: Equipments | None = None
    subject_areas: List[str] | None = []
    # search_hints: List[Link] | None = []
    # transportation: str | None = None

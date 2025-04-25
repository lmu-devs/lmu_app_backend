from datetime import time
from enum import Enum
from typing import Dict, List, Optional, Union

from pydantic import BaseModel

from shared.src.enums import WeekdayEnum
from shared.src.models.link_model import Link
from shared.src.models.location_model import Location
from shared.src.models.phone_model import Phones


class Equipment(str, Enum):
    ACCESSIBILITY = "Barrierefreier Zugang"
    GROUP_WORK_ROOMS = "Gruppenarbeitsräume"
    INDIVIDUAL_WORK_ROOMS = "Einzelcarrels"
    SEH_BEHINDERED_WORK_PLACE = "Sehbehindertenarbeitsplatz"
    PARENT_CHILD_ROOM = "Eltern-Kind-Raum"
    WHEELCHAIR_ROOM = "Wickelraum (3. OG im Behinderten-WC)"
    GALLERY = "Ausstellungsfläche"
    EVENT_ROOM = "Veranstaltungsraum"
    MULTI_FUNCTION_ROOM = "Multifunktionsraum"
    COPIER = "Kopierer"
    BOOK_SCANNER = "Buchscanner (bitte eigenen USB-Stick mitbringen)"
    BEAMER_RENTAL = "Beamerausleihe"
    WIFI = "WLAN"
    LMU_SHOP_AUTOMAT = "LMU-Shop-Automat"
    CAFE = "Cafés"
    SNACK_AND_DRINK_AUTOMAT = "Snack- und Getränkeautomaten"


class TimeSlot(BaseModel):
    day: WeekdayEnum
    start_time: time
    end_time: time


class TextWithLink(BaseModel):
    title: str
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
    url: str | None = None
    reservation_url: str | None = None
    contact: Contact | None = None
    opening_hours: OpeningHours | None = None
    services: List[TextWithLink] | None = []
    equipment: List[TextWithLink] | None = []
    subject_areas: List[str] | None = []
    search_hints: List[Link] | None = []
    transportation: str | None = None

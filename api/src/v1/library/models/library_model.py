from typing import List, Optional

from pydantic import BaseModel, RootModel

from shared.src.models.image_model import Images
from shared.src.models.location_model import Location


class TimeRange(BaseModel):
    start_time: str
    end_time: str


class OpeningDay(BaseModel):
    day: str
    time_ranges: List[TimeRange]


class OpeningHours(BaseModel):
    days: List[OpeningDay]


class PhoneContact(BaseModel):
    number: str
    recipient: Optional[str] = None


class Website(BaseModel):
    title: str
    url: str


class Contact(BaseModel):
    phone: List[PhoneContact] = []
    website: Optional[Website] = None


class Service(BaseModel):
    title: str


class Equipment(BaseModel):
    title: str
    url: Optional[str] = None
    type: Optional[str] = None
    description: Optional[str] = None


class Library(BaseModel):
    id: str
    name: str
    hash: str
    url: str
    images: Images | None = Images(root=[])
    location: Location | None = None
    contact: Contact | None = None
    opening_hours: OpeningHours | None = None
    services: List[Service] = []
    equipment: List[Equipment] = []
    subject_areas: List[str] = []


class Libraries(RootModel):
    root: List[Library]

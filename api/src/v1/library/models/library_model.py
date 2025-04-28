from typing import List

from pydantic import BaseModel, RootModel

from shared.src.models.image_model import Images
from shared.src.models.link_model import Link
from shared.src.models.location_model import Location
from shared.src.models.timeframe_model import Timeframe


class OpeningDay(BaseModel):
    day: str
    timeframes: List[Timeframe]


class OpeningHours(BaseModel):
    days: List[OpeningDay]


class PhoneContact(BaseModel):
    number: str
    recipient: str | None = None


class Contact(BaseModel):
    phone: List[PhoneContact] = []
    website: Link | None = None


class Service(BaseModel):
    title: str
    description: str | None = None


class Equipment(BaseModel):
    title: str
    url: str | None = None
    type: str | None = None
    description: str | None = None


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

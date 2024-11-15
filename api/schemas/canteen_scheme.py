import enum

from datetime import time as datetime_time
from typing import List, Optional
from pydantic import BaseModel, ConfigDict, RootModel

from api.schemas.image_scheme import Image
from api.schemas.rating_scheme import Rating


class Weekday(str, enum.Enum):
    MONDAY = "MONDAY"
    TUESDAY = "TUESDAY"
    WEDNESDAY = "WEDNESDAY"
    THURSDAY = "THURSDAY"
    FRIDAY = "FRIDAY"
    SATURDAY = "SATURDAY"
    SUNDAY = "SUNDAY"
    
class CanteenType(str, enum.Enum):
    MENSA = "MENSA"
    STUBISTRO = "STUBISTRO"
    STUCAFE = "STUCAFE"
    

class Location(BaseModel):
    address: str
    latitude: float
    longitude: float
    
class OpeningHours(BaseModel):
    day: Weekday
    start_time: Optional[datetime_time]
    end_time: Optional[datetime_time]
    
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    
class Canteen(BaseModel):
    id: str
    name: str
    type: CanteenType
    location: Location
    rating: Rating
    opening_hours: List[OpeningHours]
    images: List[Image]
    
class Canteens(RootModel):
    root: List[Canteen]


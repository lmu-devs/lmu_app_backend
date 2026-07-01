from typing import List, Optional
from pydantic import BaseModel

from api.src.v2.core.models.image_model import Image
from shared.src.models.location_model import Location


class ClubCategory(BaseModel):
    id: str
    title: str
    emoji: str
    club_ids: List[str]


class Club(BaseModel):
    id: str
    university_id: Optional[str] = None
    type: str
    image: Image
    title: str
    description: str
    content: Optional[str] = None
    url: Optional[str] = None
    email: Optional[str] = None
    instagram_url: Optional[str] = None
    linkedin_url: Optional[str] = None
    location: Optional[Location] = None 
    founding_year: int


class ClubsResponse(BaseModel):
    club_categories: List[ClubCategory]
    clubs: List[Club]
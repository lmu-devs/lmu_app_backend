from pydantic import BaseModel

from api.src.v2.core.models.image_model import Image
from shared.src.models.location_model import Location


class Club(BaseModel):
    id: str
    university_id: str | None = None
    type: str
    image: Image
    title: str
    description: str
    content: str | None = None
    url: str | None = None
    email: str | None = None
    instagram_url: str | None = None
    linkedin_url: str | None = None
    category: str
    location: Location | None = None 
    founding_year: int

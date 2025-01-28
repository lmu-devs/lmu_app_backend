from typing import List
from pydantic import BaseModel

from shared.src.tables import CinemaTable
from shared.src.models.location_model import Location
    
class Cinema(BaseModel):
    id: str
    title: str
    descriptions: List[dict]
    external_link: str | None
    instagram_link: str | None
    location: Location | None
    
    @classmethod
    def from_table(cls, cinema: CinemaTable) -> 'Cinema':
        title = cinema.translations[0].title if cinema.translations else "not translated"
        descriptions = cinema.translations[0].description if cinema.translations else "not translated"
        location = Location.from_table(cinema.location) if cinema.location else None
        return Cinema(
            id=cinema.id,
            title=title,
            descriptions=descriptions,
            external_link=cinema.external_link,
            instagram_link=cinema.instagram_link,
            location=location,
        )


class Cinemas(BaseModel):
    cinemas: List[Cinema]
    
    @classmethod
    def from_table(cls, cinemas: List[CinemaTable]) -> 'Cinemas':
        return Cinemas(cinemas=[Cinema.from_table(cinema) for cinema in cinemas])

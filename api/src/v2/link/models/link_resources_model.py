from typing import List

from pydantic import BaseModel

from api.src.v1.university.models.faculty_model import Faculty
from shared.src.models.rating_model import Rating
from shared.src.tables.link import LinkType


class LinkResource(BaseModel):
    id: str
    title: str
    description: str
    url: str
    favicon_url: str | None = None
    faculties: List[str] = []
    types: List[LinkType] = []
    # aliases: str
    rating: Rating


class LinkResourceResponse(BaseModel):
    links: List[LinkResource]
    faculties: List[Faculty]

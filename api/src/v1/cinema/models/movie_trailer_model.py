import uuid

from typing import List
from datetime import datetime
from pydantic import BaseModel

from shared.src.tables import MovieTrailerTable, MovieTrailerTranslationTable
from shared.src.models.image_model import Image


class MovieTrailer(BaseModel):
    id: uuid.UUID
    title: str
    published_at: datetime
    url: str
    thumbnail: Image
    site: str
    
    @classmethod
    def from_table(cls, trailer: MovieTrailerTable) -> 'MovieTrailer':
        trailer_translations: MovieTrailerTranslationTable = trailer.translations[0] if trailer.translations else None
        title = trailer_translations.title if trailer_translations else "not translated"
        key = trailer_translations.key if trailer_translations else "not translated"
        
        url = f"https://www.youtube.com/watch?v={key}" if key else None
        thumbnail_url = f"https://img.youtube.com/vi/{key}/hqdefault.jpg" if key else None
        
        thumbnail = Image.from_params(thumbnail_url, f"YouTube Thumbnail for {title}") if thumbnail_url else None
        
        return MovieTrailer(
            id=trailer.id,
            title=title,
            published_at=trailer.published_at,
            url=url,    
            thumbnail=thumbnail,
            site=trailer.site,
        )


class MovieTrailers(BaseModel):
    trailers: List[MovieTrailer]
    
    @classmethod
    def from_table(cls, trailers: List[MovieTrailerTable]) -> 'MovieTrailers':
        return MovieTrailers(trailers=[MovieTrailer.from_table(trailer) for trailer in trailers])

import uuid
from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session, contains_eager, joinedload

from shared.src.enums import LanguageEnum
from shared.src.tables import (
    CinemaTable,
    CinemaTranslationTable,
    MovieScreeningTable,
    MovieTable,
    MovieTrailerTable,
    MovieTrailerTranslationTable,
    MovieTranslationTable,
    UniversityTable,
    UniversityTranslationTable,
)

from ...core.translation_utils import create_translation_order_case
from ..schemas.cinema_schema import Cinema, Movie, MovieScreening

class CinemaService:
    def __init__(self, db: AsyncSession, language: LanguageEnum):
        self.db = db
        self.language = language
        
    async def get_cinemas(self, cinema_id) -> List[Cinema]:
        query = self._get_cinemas_query(cinema_id)
        result = await self.db.execute(query)
        return result.scalars().unique().all()
    
    def _get_cinemas_query(self, cinema_id: Optional[str] = None):
        query = (select(CinemaTable)
        .outerjoin(CinemaTable.location)
        .join(CinemaTable.translations)
        .options(
            contains_eager(CinemaTable.location),
            contains_eager(CinemaTable.translations),
                )
        )
        if cinema_id:
            query = query.filter(CinemaTable.id == cinema_id)
            
        return query.order_by(
            create_translation_order_case(CinemaTranslationTable, self.language)
        )

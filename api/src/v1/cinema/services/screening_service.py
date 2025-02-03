import uuid
from typing import Optional

from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import contains_eager, selectinload

from api.src.v1.core.service.like_service import LikeService
from shared.src.enums import LanguageEnum
from shared.src.tables import (
    CinemaTable,
    CinemaTranslationTable,
    MovieScreeningLikeTable,
    MovieScreeningTable,
    MovieTable,
    MovieTrailerTable,
    MovieTrailerTranslationTable,
    MovieTranslationTable,
    UniversityTable,
    UniversityTranslationTable,
)

from ...core.translation_utils import create_translation_order_case


class ScreeningService:
    def __init__(self, db: AsyncSession, language: LanguageEnum = LanguageEnum.GERMAN):
        self.db = db
        self.language = language
        self.like_service = LikeService(db)
        
    async def get_movie_screenings(self, user_id: Optional[uuid.UUID] = None):
        query = self._get_movie_screenings_query(user_id)
        result = await self.db.execute(query)
        return result.scalars().unique().all()
    
    async def toggle_like(self, screening_id: str, user_id: uuid.UUID) -> bool:
        return await self.like_service.toggle_like(MovieScreeningLikeTable, screening_id, user_id)
    
    def _get_movie_screenings_query(self, user_id: Optional[uuid.UUID] = None):
        # Base query with essential joins
        query = (select(MovieScreeningTable)
                 .options(selectinload(MovieScreeningTable.likes))
                 .options(
                     selectinload(MovieScreeningTable.movie).selectinload(MovieTable.translations),
                     selectinload(MovieScreeningTable.movie).selectinload(MovieTable.ratings),
                     selectinload(MovieScreeningTable.movie).selectinload(MovieTable.genres),
                     selectinload(MovieScreeningTable.movie).selectinload(MovieTable.trailers).selectinload(MovieTrailerTable.translations),
                 )
                 .options(
                     selectinload(MovieScreeningTable.university).selectinload(UniversityTable.translations)
                 )
                 .options(
                     selectinload(MovieScreeningTable.cinema).selectinload(CinemaTable.translations),
                     selectinload(MovieScreeningTable.cinema).selectinload(CinemaTable.location),
                     selectinload(MovieScreeningTable.cinema).selectinload(CinemaTable.images)
                 )
                 .options(selectinload(MovieScreeningTable.location))
        )
        
        # Add likes filtering if user_id is provided
        if user_id:
            query = query.outerjoin(
                MovieScreeningLikeTable,
                and_(
                    MovieScreeningTable.id == MovieScreeningLikeTable.movie_screening_id,
                    MovieScreeningLikeTable.user_id == user_id
                )
            )
        
        # Simplified ordering
        return query.order_by(MovieScreeningTable.date)

    

    
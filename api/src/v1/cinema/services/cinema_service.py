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
from ..schemas.cinema_schema import Movie, MovieScreening


class MovieService:
    def __init__(self, db: AsyncSession):
        self.db = db
        
    async def _get_movie(self, movie_id: uuid.UUID) -> Movie:
        stmt = select(MovieTable).filter(MovieTable.id == movie_id)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()
    
    async def get_movies(self, language: LanguageEnum, movie_id: Optional[uuid.UUID] = None) -> List[Movie]:
        stmt = self._get_movies_query(language, movie_id)
        result = await self.db.execute(stmt)
        return result.scalars().unique().all()
    
    def _get_movies_query(self, language: LanguageEnum, movie_id: Optional[uuid.UUID] = None):
        query = (select(MovieTable)
        # Join and load translations
        .join(MovieTable.translations)
        .options(contains_eager(MovieTable.translations))
        
        # Join and load trailers with translations
        .outerjoin(MovieTable.trailers)
        .outerjoin(MovieTrailerTable.translations)
        .options(
            contains_eager(MovieTable.trailers)
            .contains_eager(MovieTrailerTable.translations)
        )
        
        # Add ratings relationship
        .outerjoin(MovieTable.ratings)
        .options(contains_eager(MovieTable.ratings))
        
        # Add genres relationship
        .outerjoin(MovieTable.genres)
        .options(contains_eager(MovieTable.genres))
        )
        
        if movie_id:
            query = query.filter(MovieTable.id == movie_id)
        
        return query.order_by(
            create_translation_order_case(MovieTranslationTable, language),
            create_translation_order_case(MovieTrailerTranslationTable, language)
        )
        
    async def get_movie_screenings(self, language: LanguageEnum):
        query = self._get_movie_screenings_query(language)
        result = await self.db.execute(query)
        return result.scalars().unique().all()
    
    def _get_movie_screenings_query(self, language: LanguageEnum):
        query = (select(MovieScreeningTable)
        # Movie and its relationships
        .join(MovieScreeningTable.movie)
        .outerjoin(MovieTable.translations)
        .outerjoin(MovieTable.ratings)
        .outerjoin(MovieTable.genres)
        .outerjoin(MovieTable.trailers)
        .outerjoin(MovieTrailerTable.translations)
        .options(
            contains_eager(MovieScreeningTable.movie).contains_eager(MovieTable.translations),
            contains_eager(MovieScreeningTable.movie).contains_eager(MovieTable.ratings),
            contains_eager(MovieScreeningTable.movie).contains_eager(MovieTable.genres),
            contains_eager(MovieScreeningTable.movie)
            .contains_eager(MovieTable.trailers)
            .contains_eager(MovieTrailerTable.translations)
        )
        
        # University and its relationships
        .join(MovieScreeningTable.university)
        .outerjoin(UniversityTable.translations)
        .options(
            contains_eager(MovieScreeningTable.university).contains_eager(UniversityTable.translations)
        )
        
        # Cinema and its relationships
        .join(MovieScreeningTable.cinema)
        .outerjoin(CinemaTable.translations)
        .outerjoin(CinemaTable.location)
        .options(
            contains_eager(MovieScreeningTable.cinema).contains_eager(CinemaTable.translations),
            contains_eager(MovieScreeningTable.cinema).contains_eager(CinemaTable.location)
        )
        
        # Screening location
        .outerjoin(MovieScreeningTable.location)
        .options(contains_eager(MovieScreeningTable.location))
        )
        
        # Order by screening date and translations
        return query.order_by(
            MovieScreeningTable.date,
            create_translation_order_case(MovieTranslationTable, language),
            create_translation_order_case(UniversityTranslationTable, language),
            create_translation_order_case(MovieTrailerTranslationTable, language),
            create_translation_order_case(CinemaTranslationTable, language)
        )

    

    
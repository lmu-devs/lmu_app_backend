import uuid
from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import contains_eager

from shared.src.enums import LanguageEnum
from shared.src.tables import (
    MovieTable,
    MovieTrailerTable,
    MovieTrailerTranslationTable,
    MovieTranslationTable,
)

from ...core.translation_utils import create_translation_order_case
from ..schemas.cinema_schema import Movie


class MovieService:
    def __init__(self, db: AsyncSession, language: LanguageEnum):
        self.db = db
        self.language = language
        
    async def _get_movie(self, movie_id: uuid.UUID) -> Movie:
        stmt = select(MovieTable).filter(MovieTable.id == movie_id)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()
    
    async def get_movies(self, movie_id: Optional[uuid.UUID] = None) -> List[Movie]:
        stmt = self._get_movies_query(self.language, movie_id)
        result = await self.db.execute(stmt)
        return result.scalars().unique().all()
    
    def _get_movies_query(self, movie_id: Optional[uuid.UUID] = None):
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
            create_translation_order_case(MovieTranslationTable, self.language),
            create_translation_order_case(MovieTrailerTranslationTable, self.language)
        )

    

    
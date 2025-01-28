from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import contains_eager

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


class ScreeningService:
    def __init__(self, db: AsyncSession, language: LanguageEnum):
        self.db = db
        self.language = language
        
    async def get_movie_screenings(self):
        query = self._get_movie_screenings_query()
        result = await self.db.execute(query)
        return result.scalars().unique().all()
    
    def _get_movie_screenings_query(self):
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
            create_translation_order_case(MovieTranslationTable, self.language),
            create_translation_order_case(UniversityTranslationTable, self.language),
            create_translation_order_case(MovieTrailerTranslationTable, self.language),
            create_translation_order_case(CinemaTranslationTable, self.language)
        )

    

    
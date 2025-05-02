import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import contains_eager

from api.src.v1.core.service.like_service import LikeService
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
from shared.src.tables.cinema.screening_table import ScreeningLikeTable

from ...core.translation_utils import create_translation_order_case


class ScreeningService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.like_service = LikeService(db)

    async def get_movie_screenings(self, language: LanguageEnum) -> list[MovieScreeningTable]:
        query = self._get_movie_screenings_query(language)
        result = await self.db.execute(query)
        return result.scalars().unique().all()

    def _get_movie_screenings_query(self, language: LanguageEnum):
        query = (
            select(MovieScreeningTable)
            # Movie and its relationships
            .join(MovieScreeningTable.movie)
            .outerjoin(MovieTable.translations)
            .outerjoin(MovieTable.ratings)
            .outerjoin(MovieTable.trailers)
            .outerjoin(MovieTrailerTable.translations)
            .options(
                contains_eager(MovieScreeningTable.movie).contains_eager(MovieTable.translations),
                contains_eager(MovieScreeningTable.movie).contains_eager(MovieTable.ratings),
                contains_eager(MovieScreeningTable.movie)
                .contains_eager(MovieTable.trailers)
                .contains_eager(MovieTrailerTable.translations),
            )
            # University and its relationships
            .join(MovieScreeningTable.university)
            .outerjoin(UniversityTable.translations)
            .options(contains_eager(MovieScreeningTable.university).contains_eager(UniversityTable.translations))
            # Cinema and its relationships
            .join(MovieScreeningTable.cinema)
            .outerjoin(CinemaTable.translations)
            .outerjoin(CinemaTable.location)
            .outerjoin(CinemaTable.images)
            .options(
                contains_eager(MovieScreeningTable.cinema).contains_eager(CinemaTable.translations),
                contains_eager(MovieScreeningTable.cinema).contains_eager(CinemaTable.location),
                contains_eager(MovieScreeningTable.cinema).contains_eager(CinemaTable.images),
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
            create_translation_order_case(CinemaTranslationTable, language),
        )

    async def toggle_like(self, screening_id: str, user_id: uuid.UUID) -> bool:
        """Toggle like status for a cinema by user.

        Returns:
            bool: True if cinema is now liked, False if unliked
        """
        return await self.like_service.toggle_like(ScreeningLikeTable, screening_id, user_id)

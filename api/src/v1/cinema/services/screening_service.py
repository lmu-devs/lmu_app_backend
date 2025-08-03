import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import contains_eager, selectinload

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
)
from shared.src.tables.cinema.screening_table import ScreeningLikeTable

from ...core.translation_utils import create_translation_order_case


class ScreeningService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.like_service = LikeService(db)

    async def get_movie_screenings(
        self, language: LanguageEnum, user_id: str | None = None
    ) -> list[MovieScreeningTable]:
        query = self._get_movie_screenings_query(language)
        result = await self.db.execute(query)
        screenings = result.scalars().unique().all()

        # Add is_liked property if user_id is provided
        if user_id:
            liked_ids = await self.like_service.get_user_likes(ScreeningLikeTable, user_id)
            for screening in screenings:
                screening.is_liked = screening.id in liked_ids

        return screenings

    def _get_movie_screenings_query(self, language: LanguageEnum):
        query = (
            select(MovieScreeningTable)
            # Load likes relationship for counting
            .options(
                selectinload(MovieScreeningTable.likes),
            )
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
            .options(contains_eager(MovieScreeningTable.university_id).contains_eager(UniversityTable.abbreviation))
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
            create_translation_order_case(MovieTrailerTranslationTable, language),
            create_translation_order_case(CinemaTranslationTable, language),
        )

    async def toggle_like(self, screening_id: str, user_id: uuid.UUID) -> bool:
        """Toggle like status for a cinema by user.

        Returns:
            bool: True if cinema is now liked, False if unliked
        """
        return await self.like_service.toggle_like(ScreeningLikeTable, screening_id, user_id)

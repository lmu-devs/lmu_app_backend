from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import contains_eager

from shared.src.enums import LanguageEnum
from shared.src.tables import CinemaTable, CinemaTranslationTable

from ...core.translation_utils import create_translation_order_case
from ..models import Cinema


class CinemaService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_cinemas(
        self, cinema_id: Optional[str] = None, language: LanguageEnum = LanguageEnum.GERMAN
    ) -> List[Cinema]:
        query = self._get_cinemas_query(cinema_id, language)
        result = await self.db.execute(query)
        return result.scalars().unique().all()

    def _get_cinemas_query(self, cinema_id: Optional[str] = None, language: LanguageEnum = LanguageEnum.GERMAN):
        query = (
            select(CinemaTable)
            .outerjoin(CinemaTable.images)
            .outerjoin(CinemaTable.location)
            .join(CinemaTable.translations)
            .options(
                contains_eager(CinemaTable.translations),
                contains_eager(CinemaTable.images),
                contains_eager(CinemaTable.location),
            )
        )
        if cinema_id:
            query = query.filter(CinemaTable.id == cinema_id)

        return query.order_by(create_translation_order_case(CinemaTranslationTable, language))

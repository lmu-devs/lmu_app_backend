import uuid
from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import contains_eager

from shared.src.tables.sport.sport_table import SportCourseLikeTable
from shared.src.enums import LanguageEnum
from shared.src.tables.sport import (
    SportCourseTable,
    SportTypeTable,
    SportTypeTranslationTable,
)

from api.src.v1.core.service.like_service import LikeService
from ...core.translation_utils import create_translation_order_case


class SportService:
    def __init__(self, db: AsyncSession, language: LanguageEnum):
        self.db = db
        self.language = language
        self.like_service = LikeService(db)
        
    async def toggle_like(self, sport_course_id: str, user_id: uuid.UUID) -> bool:
        return await self.like_service.toggle_like(SportCourseLikeTable, sport_course_id, user_id)
    
    async def get_sports(self, sport_type_id: Optional[str] = None) -> List[SportTypeTable]:
        query = self._get_sports_query(sport_type_id)
        result = await self.db.execute(query)
        return result.scalars().unique().all()
    
    def _get_sports_query(self, sport_type_id: Optional[str] = None):
        query = (
            select(SportTypeTable)
            .outerjoin(SportTypeTable.translations)
            .outerjoin(SportTypeTable.sport_courses)
            .outerjoin(SportCourseTable.translations)
            .outerjoin(SportCourseTable.time_slots)
            .outerjoin(SportCourseTable.location)
            .options(
                contains_eager(SportTypeTable.translations),
                contains_eager(SportTypeTable.sport_courses).contains_eager(SportCourseTable.translations),
                contains_eager(SportTypeTable.sport_courses).contains_eager(SportCourseTable.time_slots),
                contains_eager(SportTypeTable.sport_courses).contains_eager(SportCourseTable.location),
            )
        )
        
        if sport_type_id:
            query = query.filter(SportTypeTable.id == sport_type_id)
            
        return query.order_by(
            create_translation_order_case(SportTypeTranslationTable, self.language)
        )

import uuid
from typing import Dict, List, Optional

from sqlalchemy import and_, select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from api.src.v1.core.service.like_service import LikeService
from shared.src.core.exceptions import DatabaseError
from shared.src.core.logging import get_sport_logger
from shared.src.enums import LanguageEnum
from shared.src.tables.sport import SportCourseTable, SportTypeTable, SportTypeTranslationTable
from shared.src.tables.sport.sport_table import SportCourseLikeTable

from ...core.translation_utils import create_translation_order_case


logger = get_sport_logger(__name__)

class SportService:
    def __init__(self, db: AsyncSession, language: LanguageEnum):
        self.db = db
        self.language = language
        self.like_service = LikeService(db)
        
    async def toggle_like(self, sport_course_id: str, user_id: uuid.UUID) -> bool:
        return await self.like_service.toggle_like(SportCourseLikeTable, sport_course_id, user_id)
    
    async def get_sports(self, user_id: Optional[uuid.UUID] = None) -> List[SportTypeTable]:
        """Retrieve sports with nested course information and likes."""
        try:
            # Start with base query for SportTypeTable
            query = (
                select(SportTypeTable)
                # Join with translations for ordering
                .join(SportTypeTranslationTable)
                .options(
                    selectinload(SportTypeTable.translations),
                    selectinload(SportTypeTable.sport_courses).options(
                        selectinload(SportCourseTable.translations),
                        selectinload(SportCourseTable.time_slots),
                        selectinload(SportCourseTable.location),
                        selectinload(SportCourseTable.likes)
                    )
                )
            )

            # If user_id is provided, add likes filtering on the sport_courses relationship
            if user_id:
                query = (
                    query.options(
                        selectinload(SportTypeTable.sport_courses).options(
                            selectinload(SportCourseTable.likes.and_(
                                SportCourseLikeTable.user_id == user_id
                            ))
                        )
                    )
                )

            # Add ordering after the join
            query = query.order_by(
                create_translation_order_case(SportTypeTranslationTable, self.language)
            )

            result = await self.db.execute(query)
            return result.scalars().unique().all()

        except SQLAlchemyError as e:
            logger.error(f"Failed to fetch sports with likes: {str(e)}")
            raise DatabaseError(
                detail="Failed to fetch sports with likes",
                extra={"original_error": str(e)}
            ) from e

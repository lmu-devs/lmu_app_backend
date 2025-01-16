import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError

from shared.src.core.exceptions import DatabaseError
from shared.src.core.logging import get_feedback_logger
from shared.src.services.telegram_service import TelegramService
from shared.src.tables import FeedbackTable, FeedbackType

logger = get_feedback_logger(__name__)

class FeedbackService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.telegram_service = TelegramService()
    async def create_feedback(self, user_id: uuid.UUID, feedback_data: dict) -> FeedbackTable:
        try:
            new_feedback = FeedbackTable(
                id=uuid.uuid4(),
                user_id=user_id,
                type=feedback_data['type'],
                rating=feedback_data.get('rating'),
                message=feedback_data.get('message'),
                screen=feedback_data['screen'],
                tags=feedback_data.get('tags', []),
                app_version=feedback_data.get('app_version'),
                system_version=feedback_data.get('system_version'),
            )
            
            self.db.add(new_feedback)
            await self.db.commit()
            
            logger.info(f"Created new feedback for user {user_id}, screen: {feedback_data['screen']}, rating: {feedback_data['rating']}, app_version: {feedback_data['app_version']} on {feedback_data['system_version']}")
            return new_feedback
            
        except SQLAlchemyError as e:
            logger.error(f"Failed to create feedback: {str(e)}")
            await self.db.rollback()
            raise DatabaseError(
                detail="Failed to create feedback",
                extra={"original_error": str(e)}
            ) 
            
    async def send_telegram_notification(self, feedback: FeedbackTable):
        await self.telegram_service.send_feedback_notification(
            feedback_type=FeedbackType(feedback.type).value ,
            rating=feedback.rating,
            screen=feedback.screen,
            message=feedback.message,
            tags=feedback.tags
        )
import uuid
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from shared.src.core.exceptions import DatabaseError
from shared.src.core.logging import get_feedback_logger
from shared.src.tables import FeedbackTable

logger = get_feedback_logger(__name__)

class FeedbackService:
    def __init__(self, db: Session):
        self.db = db

    def create_feedback(self, user_id: uuid.UUID, feedback_data: dict) -> FeedbackTable:
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
            self.db.commit()
            self.db.refresh(new_feedback)
            
            logger.info(f"Created new feedback for user {user_id}, screen: {feedback_data['screen']}, rating: {feedback_data['rating']}, app_version: {feedback_data['app_version']} on {feedback_data['system_version']}")
            return new_feedback
            
        except SQLAlchemyError as e:
            logger.error(f"Failed to create feedback: {str(e)}")
            self.db.rollback()
            raise DatabaseError(
                detail="Failed to create feedback",
                extra={"original_error": str(e)}
            ) 
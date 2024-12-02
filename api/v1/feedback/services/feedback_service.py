import uuid
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from shared.core.exceptions import DatabaseError
from shared.tables.feedback_table import FeedbackTable
from shared.core.logging import get_feedback_logger

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
                rating=feedback_data['rating'],
                message=feedback_data.get('message'),
                screen=feedback_data['screen'],
                tags=feedback_data.get('tags', [])
            )
            
            self.db.add(new_feedback)
            self.db.commit()
            self.db.refresh(new_feedback)
            
            logger.info(f"Created new feedback for user {user_id}, screen: {feedback_data['screen']}, rating: {feedback_data['rating']}")
            return new_feedback
            
        except SQLAlchemyError as e:
            logger.error(f"Failed to create feedback: {str(e)}")
            self.db.rollback()
            raise DatabaseError(
                detail="Failed to create feedback",
                extra={"original_error": str(e)}
            ) 
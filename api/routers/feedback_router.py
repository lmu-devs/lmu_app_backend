from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from shared.database import get_db
from shared.models.user_model import UserTable
from api.core.api_key import APIKey
from api.schemas.feedback_scheme import FeedbackCreate, Feedback
from api.services.feedback_service import FeedbackService

router = APIRouter()

@router.post("/feedback", response_model=Feedback, description="Submit user feedback")
async def create_feedback(
    feedback_data: FeedbackCreate,
    db: Session = Depends(get_db),
    current_user: UserTable = Depends(APIKey.get_user_from_key)
):
    feedback_service = FeedbackService(db)
    feedback = feedback_service.create_feedback(current_user.id, feedback_data.model_dump())
    return feedback

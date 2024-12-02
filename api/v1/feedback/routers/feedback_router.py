from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from api.v1.core.api_key import APIKey
from ..schemas.feedback_scheme import Feedback, FeedbackCreate
from ..services.feedback_service import FeedbackService
from shared.database import get_db
from shared.tables.user_table import UserTable

router = APIRouter()

@router.post("/feedback", response_model=Feedback, description="Submit user feedback")
async def create_feedback(
    feedback_data: FeedbackCreate,
    db: Session = Depends(get_db),
    current_user: UserTable = Depends(APIKey.verify_user_api_key)
):
    feedback_service = FeedbackService(db)
    feedback = feedback_service.create_feedback(current_user.id, feedback_data.model_dump())
    return feedback

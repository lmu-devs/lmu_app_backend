import asyncio
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from shared.src.core.database import get_async_db
from shared.src.tables import UserTable

from api.src.v1.core.api_key import APIKey
from api.src.v1.feedback.models.feedback_model import Feedback, FeedbackCreate
from api.src.v1.feedback.services.feedback_service import FeedbackService

router = APIRouter()

@router.post("/feedback", response_model=Feedback, description="Submit user feedback")
async def create_feedback(
    feedback_data: FeedbackCreate,
    db: AsyncSession = Depends(get_async_db),
    user: UserTable = Depends(APIKey.verify_user_api_key)
):
    feedback_service = FeedbackService(db)
    feedback = await feedback_service.create_feedback(user.id, feedback_data.model_dump())
    asyncio.create_task(feedback_service.send_telegram_notification(feedback))
    return feedback
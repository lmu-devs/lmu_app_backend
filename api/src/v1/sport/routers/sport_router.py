from datetime import datetime
from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from shared.src.core.database import get_async_db
from shared.src.core.logging import get_places_logger
from shared.src.enums import LanguageEnum

from ..models.sport_model import (
    Price,
    Sport,
    SportCourse,
    SportCourses,
    SportType,
    SportTypes,
    TimeSlots,
)
from ..services.sport_service import SportService

router = APIRouter()
logger = get_places_logger(__name__)


@router.get("/sports", response_model=Sport, description="Get sports data")
async def get_sports(
    db: AsyncSession = Depends(get_async_db),
):
    sport_service = SportService(db, LanguageEnum.GERMAN)
    sports = await sport_service.get_sports()
    basis_ticket_type = await sport_service.get_basis_ticket()

    if basis_ticket_type:
        basic_ticket = SportType.from_table(basis_ticket_type)
    else:
        dummy_course = SportCourse(
            id="basic-ticket",
            title="Alle Kurse",
            is_available=True,
            start_date=datetime.now(),
            end_date=datetime.now(),
            instructor="ZHS",
            time_slots=TimeSlots(root=[]),
            price=Price(student_price=0, employee_price=0, external_price=0),
            location=None,
        )
        basic_ticket = SportType(
            title="Basic-Ticket",
            courses=SportCourses(root=[dummy_course]),
        )

    return Sport.model(
        sport_types=SportTypes.from_table(sports),
        basic_ticket=basic_ticket,
    )

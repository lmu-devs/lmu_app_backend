from datetime import date, datetime, timedelta
from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from api.v1.core.api_key import APIKey
from api.v1.core.language import get_language
from api.v1.pydantics.menu_pydantic import menu_days_to_pydantic
from api.v1.schemas.menu_scheme import Menus
from api.v1.services.menu_service import MenuService
from shared.enums.language_enums import Language
from shared.core.logging import get_menu_logger
from shared.core.timezone import TimezoneManager
from shared.database import get_db
from shared.enums.mensa_enums import CanteenID
from shared.models.user_model import UserTable

router = APIRouter()
menu_logger = get_menu_logger(__name__)

@router.get("/menus", response_model=Menus, description="Get all menus or a specific canteen by ID. Authenticated users can also get liked dishes.")
async def get_menu(
    date_from: Optional[date] = Query(
        default=None,
        description="Start date for menu search. Defaults to today",
        example=TimezoneManager.now_date()
    ),
    days_amount: int = Query(
        default=14,
        description="Number of days to fetch from start date",
        ge=1,
        le=31
    ),
    canteen_id: str = Query(
        default=None,
        description="Filter by canteen_id, if not provided, all canteens will be fetched",
        example="mensa-leopoldstr",
        enum=[canteen.value for canteen in CanteenID]
    ),
    current_user: UserTable = Depends(APIKey.verify_user_api_key_soft),
    only_liked_canteens: bool = Query(
        default=False,
        description="Filter menus by liked canteens"
    ),
    language: Language = Depends(get_language),
    db: Session = Depends(get_db)
):
    if date_from is None:
        date_from = TimezoneManager.now_date()

    date_to = date_from + timedelta(days=days_amount)
    user_id = current_user.id if current_user else None
    
    
    menu_service = MenuService(db)
    menu_days = menu_service.get_days(
        canteen_id, 
        date_from,
        date_to,
        current_user, 
        only_liked_canteens,
        language
    )
    
    return menu_days_to_pydantic(menu_days, user_id)


    

    
    





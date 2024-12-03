from datetime import date, timedelta
from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from api.v1.core.api_key import APIKey
from api.v1.core.language import get_language
from shared.core.logging import get_food_logger
from shared.core.timezone import TimezoneManager
from shared.database import get_db
from shared.enums.language_enums import LanguageEnum
from shared.enums.mensa_enums import CanteenEnum
from shared.tables.user_table import UserTable

from ..pydantics import menu_days_to_pydantic
from ..schemas import Menus
from ..services import MenuService

router = APIRouter()
food_logger = get_food_logger(__name__)

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
        enum=[canteen.value for canteen in CanteenEnum]
    ),
    current_user: UserTable = Depends(APIKey.verify_user_api_key_soft),
    only_liked_canteens: bool = Query(
        default=False,
        description="Filter menus by liked canteens"
    ),
    language: LanguageEnum = Depends(get_language),
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


    

    
    





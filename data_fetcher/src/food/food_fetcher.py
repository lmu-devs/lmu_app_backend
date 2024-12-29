import asyncio
import requests
import schedule

from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from shared.src.core.database import get_db
from shared.src.core.error_handlers import handle_error
from shared.src.core.logging import get_food_fetcher_logger
from shared.src.enums import CanteenEnum

from ..state import running_eat
from .service.canteen_service import CanteenService
from .service.menu_service import MenuFetcher

logger = get_food_fetcher_logger(__name__)


def fetch_scheduled_data(db: Session, days_amount: int = 21):
    """Fetches data for the next 21 days for all canteens"""
    
    try:
        CanteenService(db).update_canteen_database()

        date_from = datetime.now().date()

        logger.info(f"Fetching menu data for {days_amount} days, starting from {date_from}")

        # Update menu for each canteen
        for canteen in CanteenEnum.get_active_canteens():
            try:
                menu_service = MenuFetcher(db)
                menu_service.update_menu_database(
                    canteen_id=canteen.value,
                    date_from=date_from,
                    date_to=date_from + timedelta(days=days_amount -1)
                )
                logger.info(f"Successfully updated menu for {canteen.value}")
            except Exception as e:
                error_response = handle_error(e)
                logger.error(
                    f"Error updating menu for canteen {canteen.value}",
                    extra=error_response['error']['extra'],
                    exc_info=True
                )
                continue
                
    except requests.exceptions.RequestException as e:
        logger.error("Error fetching data:", e)
    except Exception as e:
        logger.error(f"Unexpected error during scheduled fetch: {str(e)}")


async def create_food_fetcher():
    logger.info("================================================")
    logger.info(f"Setting up {__name__}...")
    

    db = next(get_db())
    # fetch_scheduled_data(db, days_amount=20)
    CanteenService(db).update_canteen_database()
    
    schedule.every().day.at("08:08").do(fetch_scheduled_data)
    
    logger.info(f"Entering {__name__} loop...")
    while running_eat:
        schedule.run_pending()
        await asyncio.sleep(60)

    logger.info(f"Exiting {__name__} loop...")
    logger.info("================================================\n")

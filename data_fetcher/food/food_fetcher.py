import time
from datetime import datetime, timedelta

import requests
import schedule
from sqlalchemy.orm import Session

from data_fetcher.food.service.canteen_service import CanteenFetcher
from data_fetcher.food.service.menu_service import MenuFetcher
from data_fetcher.state import running_eat
from shared.core.error_handlers import handle_error
from shared.core.logging import get_food_fetcher_logger
from shared.database import get_db
from shared.enums.mensa_enums import CanteenID

logger = get_food_fetcher_logger(__name__)


# def fetch_data_current_year(db: Session):
#     """Fetches data for the next 14 days for all canteens"""
#     try:
#         logger.info("Starting data fetch for next 14 days")
#         # Update canteen information first
#         canteen_fetcher = CanteenFetcher(db)
#         canteen_fetcher.update_canteen_database()

#         # Get current date
#         date_from = datetime.now().date()
#         default_days_amount = 14
        
#         logger.info(f"Fetching data for {default_days_amount} days")
#         logger.info(f"Date from: {date_from}")

#         # Update menu for each canteen
#         for canteen in CanteenID:
#             try:
#                 menu_service = MenuFetcher(db)
#                 menu_service.update_menu_database(
#                     canteen_id=canteen.value,
#                     date_from=date_from,
#                     date_to=date_from + timedelta(days=default_days_amount)
#                 )
#                 logger.info(f"Successfully updated menu for {canteen.value}")
#             except (ExternalAPIError, DatabaseError, DataProcessingError) as e:
#                 error_response = handle_error(e)
#                 logger.error(
#                     f"Error updating menu for canteen {canteen.value}",
#                     extra=error_response['error']['extra'],
#                     exc_info=True
#                 )
#                 continue
            
#     except Exception as e:
#         error_response = handle_error(e)
#         logger.error(
#             "Unexpected error during data fetch",
#             extra=error_response['error']['extra'],
#             exc_info=True
#         )


def fetch_scheduled_data(db: Session, days_amount: int = 21):
    """Fetches data for the next 14 days for all canteens"""
    print("Attempting to fetch data for next 14 days...")
    
    try:
        # Update canteen database first
        canteen_fetcher = CanteenFetcher(db)
        canteen_fetcher.update_canteen_database()

        # Get current date
        date_from = datetime.now().date()

        logger.info(f"Fetching data for {days_amount} days")
        logger.info(f"Date from: {date_from}")

        # Update menu for each canteen
        for canteen in CanteenID:
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
        
def create_food_fetcher():
    logger.info("Setting up schedule...")
    
    # Initial fetch
    db = next(get_db())
    # fetch_scheduled_data(db, days_amount=7)
    CanteenFetcher(db).update_canteen_database()
    
    schedule.every().day.at("08:08").do(fetch_scheduled_data)
    
    logger.info("Entering data_fetcher loop...")
    while running_eat:
        schedule.run_pending()
        time.sleep(10)
    
    logger.info("Exiting main loop...")


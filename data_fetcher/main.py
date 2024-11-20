import signal
import sys
import time
import requests
import schedule

from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from shared.enums.mensa_enums import CanteenID
from shared.core.exceptions import DatabaseError, DataProcessingError, ExternalAPIError
from shared.core.error_handlers import handle_error
from shared.core.logging import setup_logger
from shared.database import Database, get_db
from shared.settings import get_settings
from data_fetcher.service.canteen_service import CanteenFetcher
from data_fetcher.service.menu_service import MenuFetcher

logger = setup_logger(__name__, "data_fetcher")

# ------ Needed for stopping docker container ------ #
# Global flag to control the main loop
running = True

def signal_handler(signum, frame):
    global running
    logger.info("Received shutdown signal. Stopping gracefully...")
    running = False

# Register the signal handler
signal.signal(signal.SIGTERM, signal_handler)
signal.signal(signal.SIGINT, signal_handler)
# ------ Needed for stopping docker container ------ #



def fetch_data_current_year(db: Session):
    """Fetches data for the next 14 days for all canteens"""
    try:
        logger.info("Starting data fetch for next 14 days")
        # Update canteen information first
        canteen_fetcher = CanteenFetcher(db)
        canteen_fetcher.update_canteen_database()

        # Get current date
        date_from = datetime.now().date()
        default_days_amount = 14

        # Update menu for each canteen
        for canteen in CanteenID:
            try:
                menu_service = MenuFetcher(db)
                menu_service.update_menu_database(
                    canteen_id=canteen.value,
                    date_from=date_from,
                    date_to=date_from + timedelta(days=default_days_amount)
                )
                logger.info(f"Successfully updated menu for {canteen.value}")
            except (ExternalAPIError, DatabaseError, DataProcessingError) as e:
                error_response = handle_error(e)
                logger.error(
                    f"Error updating menu for canteen {canteen.value}",
                    extra=error_response['error']['extra'],
                    exc_info=True
                )
                continue
            
    except Exception as e:
        error_response = handle_error(e)
        logger.error(
            "Unexpected error during data fetch",
            extra=error_response['error']['extra'],
            exc_info=True
        )


def fetch_scheduled_data(db: Session, days_amount: int = 14):
    """Fetches data for the next 14 days for all canteens"""
    print("Attempting to fetch data for next 14 days...")
    
    try:
        # Update canteen database first
        canteen_fetcher = CanteenFetcher(db)
        canteen_fetcher.update_canteen_database()

        # Get current date
        date_from = datetime.now().date()

        # Update menu for each canteen
        for canteen in CanteenID:
            try:
                menu_service = MenuFetcher(db)
                menu_service.update_menu_database(
                    canteen_id=canteen.value,
                    date_from=date_from,
                    date_to=date_from + timedelta(days=days_amount)
                )
                print(f"Successfully updated menu for {canteen.value}")
            except Exception as e:
                print(f"Error updating menu for canteen {canteen.value}: {str(e)}")
                continue
                
    except requests.exceptions.RequestException as e:
        logger.error("Error fetching data:", e)
    except Exception as e:
        logger.error(f"Unexpected error during scheduled fetch: {str(e)}")
        
def create_data_fetcher():
    logger.info("Setting up schedule...")
    
    # Initial fetch
    db = next(get_db())
    fetch_scheduled_data(db, days_amount=1)
    # CanteenFetcher(db).update_canteen_database()
    
    schedule.every().day.at("08:08").do(fetch_scheduled_data)
    
    logger.info("Entering data_fetcher loop...")
    while running:
        schedule.run_pending()
        time.sleep(1)
    
    logger.info("Exiting main loop...")

if __name__ == "__main__":
    logger.info("data_fetcher started")
    try:
        # Initialize the database
        settings = get_settings()
        Database(settings=settings)
        
        # Start the main loop
        create_data_fetcher()
    except Exception as e:
        logger.error(f"An error occurred: {e}")
    finally:
        logger.info("data_fetcher is shutting down")
    sys.exit(0)

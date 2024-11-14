import requests
import schedule
import time
import signal
import sys

from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from shared.database import Database, get_db
from data_fetcher.service.canteen_service import CanteenFetcher
from data_fetcher.service.menu_service import MenuService
from data_fetcher.enums.mensa_enums import CanteenID
from shared.settings import get_settings

# ------ Needed for stopping docker container ------ #
# Global flag to control the main loop
running = True

def signal_handler(signum, frame):
    global running
    print("Received shutdown signal. Stopping gracefully...")
    running = False

# Register the signal handler
signal.signal(signal.SIGTERM, signal_handler)
signal.signal(signal.SIGINT, signal_handler)
# ------ Needed for stopping docker container ------ #

def fetch_data_current_year(db: Session):
    """Fetches data for the next 14 days for all canteens"""
    try:
        # Update canteen information first
        canteen_fetcher = CanteenFetcher(db)
        canteen_fetcher.update_canteen_database()

        # Get current date
        date_from = datetime.now().date()
        days_amount = 14  # Default to 14 days

        # Update menu for each canteen
        for canteen in CanteenID:
            try:
                menu_service = MenuService(db)
                menu_service.update_menu_database(
                    canteen_id=canteen.value,
                    date_from=date_from,
                    date_to=date_from + timedelta(days=days_amount)
                )
            except Exception as e:
                print(f"Error updating menu for canteen {canteen.value}: {str(e)}")
                continue
        
    except Exception as e:
        print(f"An error occurred during data fetch: {str(e)}")

def fetch_scheduled_data(db: Session):
    """Fetches data for the next 14 days for all canteens"""
    print("Attempting to fetch data for next 14 days...")
    
    try:
        # Update canteen database first
        canteen_fetcher = CanteenFetcher(db)
        canteen_fetcher.update_canteen_database()

        # Get current date
        date_from = datetime.now().date()
        days_amount = 14  # Fetch 2 weeks worth of data

        # Update menu for each canteen
        for canteen in CanteenID:
            try:
                menu_service = MenuService(db)
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
        print("Error fetching data:", e)
    except Exception as e:
        print(f"Unexpected error during scheduled fetch: {str(e)}")
        
def create_data_fetcher():
    print("Setting up schedule...")
    
    # Initial fetch
    db = next(get_db())
    fetch_scheduled_data(db)
    
    # Schedule daily updates
    schedule.every().day.at("08:08").do(fetch_scheduled_data)
    
    print("Entering data_fetcher loop...")
    while running:
        schedule.run_pending()
        time.sleep(1)
    
    print("Exiting main loop...")

if __name__ == "__main__":
    print("Script started")
    try:
        # Initialize the database
        settings = get_settings()
        Database(settings=settings)
        
        # Start the main loop
        create_data_fetcher()
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        print("Script is shutting down")
    sys.exit(0)

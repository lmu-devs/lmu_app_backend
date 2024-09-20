import requests
import schedule
import time
import signal
import sys


from api.database import init_db
from data_fetcher.service.canteen_service import update_canteen_database
from data_fetcher.service.menu_service import update_date_range_menu_database

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



        
def fetch_scheduled_data():
    """
    Fetches data from the eat-api for the current month
    """
    print("Attempting to fetch data for next 4 weeks...")
    
    # Get the current date
    date = time.localtime()
    year = date.tm_year
    current_week = int(time.strftime("%V"))
    
    # Calculate the week 4 weeks in the future
    future_week = current_week + 4
    
    # Adjust for year wrap-around
    if future_week > 52:
        future_week = future_week - 52
        future_year = year + 1
    else:
        future_year = year
    
    try:
        update_canteen_database()
        update_date_range_menu_database(
            start_year=year, 
            start_week=str(current_week), 
            end_year=future_year, 
            end_week=str(future_week)
        )
        
    except requests.exceptions.RequestException as e:
        print("Error fetching data:", e)
    
        
        
def fetch_data_current_year():
    
    date = time.localtime()
    year = date.tm_year
    current_week = int(time.strftime("%V"))
    
    print(f"Attempting to fetch data for year {year}...")
    
    try:
        update_canteen_database()
        update_date_range_menu_database(start_year=year, start_week="02", end_year=year, end_week=str(current_week))
        
    except requests.exceptions.RequestException as e:
        print("Error fetching data:", e)
        





def create_data_fetcher():
    print("Setting up schedule...")
    
    # fetch_data_current_year()
    # fetch_scheduled_data()
    schedule.every().day.at("08:08").do(fetch_scheduled_data)
    
    print("Entering data_fecther loop...")
    while running:
        schedule.run_pending()
        time.sleep(1)
    
    print("Exiting main loop...")


if __name__ == "__main__":
    print("Script started")
    try:
        # Initialize the database
        init_db()
        
        # Start the main loop
        create_data_fetcher()
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        print("Script is shutting down")
    sys.exit(0)

import requests
import schedule
import time
import signal
import sys

import service.canteen_service
import service.menu_service

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



def fetch_data_from_api():
    print("Attempting to fetch data...")
    
    try:
        service.canteen_service.update_canteen_database()
        service.menu_service.update_menu_database(canteen_id="mensa-garching", year=2024, week="22")
        
    except requests.exceptions.RequestException as e:
        print("Error fetching data:", e)
        
def test_fetch_data_from_api():
    print("Running test for every 2 seconds...")
    # fetch_data_from_api()

def create_data_fetcher():
    print("Setting up schedule...")
    schedule.every(2).seconds.do(test_fetch_data_from_api)
    
    print("Entering main loop...")
    while running:
        schedule.run_pending()
        time.sleep(1)
    
    print("Exiting main loop...")

if __name__ == "__main__":
    print("Script started")
    try:
        create_data_fetcher()
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        print("Script is shutting down")
    sys.exit(0)

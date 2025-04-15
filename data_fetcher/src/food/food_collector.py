from datetime import datetime, timedelta

import requests
import schedule

from data_fetcher.src.core.base_collector import ScheduledCollector
from data_fetcher.src.food.service.canteen_service import CanteenService
from data_fetcher.src.food.service.menu_service import MenuFetcher
from shared.src.core.error_handlers import handle_error
from shared.src.core.logging import get_food_fetcher_logger
from shared.src.enums import CanteenEnum


class FoodCollector(ScheduledCollector):
    def __init__(self):
        super().__init__(job_schedule=schedule.every().day.at("09:08"))
        self.logger = get_food_fetcher_logger(__name__)
        self.days_amount = 28

    async def _collect_data(self, db):
        """Fetches data for the next 28 days for all canteens"""
        try:
            # Update canteen data
            CanteenService(db).update_canteen_database()

            menu_service = MenuFetcher(db)

            # Calculate date range
            date_from = datetime.now().date()
            date_to = date_from + timedelta(days=self.days_amount)
            self.logger.info(f"Fetching menu data for {self.days_amount} days, starting from {date_from}")

            # Store empty menu for each canteen
            for canteen in CanteenEnum:
                menu_service.store_menu_days(canteen, date_from, date_to)

            # Update menu dishes for each canteen
            for canteen in CanteenEnum.get_active_canteens():
                try:
                    menu_service.store_menus(canteen)
                    self.logger.info(f"Successfully updated menu for {canteen.value}")
                except Exception as e:
                    error_response = handle_error(e)
                    self.logger.error(
                        f"Error updating menu for canteen {canteen.value}",
                        extra=error_response["error"]["extra"],
                        exc_info=True,
                    )
                    continue

        except requests.exceptions.RequestException as e:
            self.logger.error("Error fetching data:", e)
        except Exception as e:
            self.logger.error(f"Unexpected error during scheduled fetch: {str(e)}")

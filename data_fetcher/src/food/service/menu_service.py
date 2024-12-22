from datetime import date, datetime, timedelta
from uuid import NAMESPACE_DNS, UUID, uuid5

import requests
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from data_fetcher.src.food.constants.canteens.canteen_opening_hours_constants import \
    CanteenOpeningHoursConstants
from data_fetcher.src.food.service.canteen_opening_status_service import \
    CanteenOpeningStatusService
from data_fetcher.src.food.service.simple_price_service import PriceService
from shared.src.core.exceptions import DatabaseError, DataProcessingError
from shared.src.core.logging import get_food_fetcher_logger
from shared.src.enums import (CanteenEnum, DishCategoryEnum, LanguageEnum, WeekdayEnum)
from shared.src.services import LectureFreePeriodService, TranslationService
from shared.src.tables import (DishPriceTable, DishTable, DishTranslationTable,
                               MenuDayTable, MenuDishAssociation)

logger = get_food_fetcher_logger(__name__)

class MenuFetcher:
    
    def __init__(self, db: Session):
        self.db = db
        self.translation_service = TranslationService()
        
    def fetch_menu_data(self, canteen_id: str, week: str, year: int):
        """Fetch menu data from TUM API, returns None if no data is available."""
        url = f"https://tum-dev.github.io/eat-api/{canteen_id}/{year}/{week}.json"
        
        try:
            response = requests.get(url)
            
            # Handle 404 (no data available) gracefully
            if response.status_code == 404:
                logger.debug(f"No menu data available for {canteen_id} (week {week}/{year})")
                return None
            
            response.raise_for_status()
            logger.info(f"Successfully fetched menu data from TUM API: {response.status_code}")
            return response.json()
            
        except requests.exceptions.HTTPError as e:
            logger.warning(
                f"HTTP error fetching menu data for {canteen_id} (week {week}/{year}): "
                f"status {e.response.status_code if e.response else 'unknown'}"
            )
            return None
            
        except requests.exceptions.RequestException as e:
            logger.warning(f"Connection error fetching menu data: {str(e)}")
            return None
        
    def store_menu_days(self, canteen_id: str, date_from: date, date_to: date):
        """Store menu days for a specific canteen within a date range"""
        lecture_free_service = LectureFreePeriodService()
        canteen_enum = CanteenEnum(canteen_id)
        opening_hours = CanteenOpeningHoursConstants.get_opening_hours(canteen_enum)
        
        current_date = date_from
        while current_date < date_to:
            is_lecture_free = lecture_free_service.is_lecture_free(current_date)
            weekday = WeekdayEnum(current_date.strftime("%A").upper())
            
            should_create = False
            if is_lecture_free and opening_hours.lecture_free_hours:
                should_create = any(oh.day == weekday for oh in opening_hours.lecture_free_hours)
            else:
                should_create = any(oh.day == weekday for oh in opening_hours.opening_hours)
            
            if should_create:
                menu_day_obj = self.db.merge(MenuDayTable(
                    date=current_date,
                    canteen_id=canteen_id,
                    is_closed=CanteenOpeningStatusService.is_closed(current_date)
                ))
            
            current_date += timedelta(days=1)
        
        self.db.commit()
        logger.info(f"Menu days stored successfully for {canteen_id} from {date_from} to {date_to}")

    def store_menu_data(self, data: dict, canteen_id: str):
        
        try:
            dish_amount = 0
            
            logger.info(f"Storing menu data for canteen {canteen_id} for week {data.get('week')} of year {data.get('year')}")
            
            days = data.get('days', [])
            
            # Process each weekday
            for day in days:
                date = datetime.strptime(day.get('date'), '%Y-%m-%d').date()
                
                # Clear existing dish associations for this day
                self.db.query(MenuDishAssociation).filter_by(
                    menu_day_date=date,
                    canteen_id=canteen_id
                ).delete()
                
                # Process dishes only if they exist
                dishes = day.get('dishes', [])
                for dish in dishes:
                    dish_name_de = dish.get('name', '')
                    dish_id = self._generate_dish_id(dish_name_de)
                    
                    # Try to get existing dish first
                    dish_obj = (
                        self.db.query(DishTable)
                        .filter(DishTable.id == dish_id)
                        .first()
                    )
                    
                    if dish_obj:
                        # Updating existing dish
                        # Update price_simple only if new price is not None
                        new_price = dish.get("prices", {}).get("students")
                        if new_price is not None:
                            dish_obj.price_simple = PriceService.calculate_simple_price(new_price)
                            self.db.add(dish_obj)
                            self.db.flush()
                            
                            prices = dish.get("prices", {})
                            for category, price_data in prices.items():
                                if price_data is not None:
                                    # Delete existing price for this category
                                    self.db.query(DishPriceTable).filter_by(
                                        dish_id=dish_obj.id,
                                        category=category.upper()
                                    ).delete()
                                    
                                    # Add new price record
                                    price_obj = DishPriceTable(
                                        dish_id=dish_obj.id,
                                        category=category.upper(),
                                        base_price=price_data.get('base_price'),
                                        price_per_unit=price_data.get('price_per_unit'),
                                        unit=price_data.get('unit')
                                    )
                                    self.db.add(price_obj)
                        else:
                            logger.warning(f"No price data for dish {dish_obj.translations[0].title} in canteen {canteen_id}")
                            
                            
                    else:
                        # Creating new dish
                        dish_type = dish.get('dish_type', '')
                        dish_category = self._map_dish_type_to_category(dish_type).value
                        
                        dish_obj = DishTable(
                            id=self._generate_dish_id(dish_name_de),
                            dish_type=dish_type,
                            dish_category=dish_category,
                            labels=dish.get('labels', []),
                            price_simple=PriceService.calculate_simple_price(dish.get("prices", {}).get("students", {})),
                        )
                        dish_amount += 1
                        self.db.add(dish_obj)
                        self.db.flush()
                        
                        # Create initial German translation
                        print(f"added german translation for dish {dish_name_de} to db")
                        german_translation = DishTranslationTable(
                            dish_id=dish_obj.id,
                            language=LanguageEnum.GERMAN,
                            title=dish_name_de
                        )
                        self.db.add(german_translation)
                        self.db.flush()

                        prices = dish.get("prices", {})
                        for category, price_data in prices.items():
                            if price_data is not None:
                                price_obj = DishPriceTable(
                                    dish_id=dish_obj.id,
                                    category=category.upper(),
                                    base_price=price_data.get('base_price'),
                                    price_per_unit=price_data.get('price_per_unit'),
                                    unit=price_data.get('unit')
                                )
                                self.db.add(price_obj)
                    
                    # Create new MenuDishAssociation
                    association = MenuDishAssociation(
                        dish_id=dish_obj.id,
                        menu_day_date=date,
                        canteen_id=canteen_id
                    )
                    self.db.add(association)
                    
                    # Add missing translations for existing and new dishes
                    translations = self.translation_service.create_missing_translations(dish_obj)
                    self.db.add_all(translations)
                    
            self.db.commit()
            logger.info(f"Menu dishes added & updated successfully. {dish_amount} dishes added.")
        except IntegrityError as e:
            logger.error(f"Database integrity error while storing menu data: {str(e)}")
            raise DatabaseError(
                detail="Database integrity error while storing menu data",
                extra={"error": str(e)}
            )
        except Exception as e:
            logger.debug(f"Failed to process menu data: {str(e)}")
            raise DataProcessingError(
                detail="Failed to process menu data",
                extra={"error": str(e)}
            )


    def update_menu_database(self, canteen_id: str, date_from: date, date_to: date):
        """Update menu data for a specific canteen within a date range"""
        logger.info(f"Updating menu data for canteen {canteen_id} from {date_from} to {date_to- timedelta(days=1)}...")
        
        try:
            # Store all menu days without dishes
            self.store_menu_days(canteen_id, date_from-timedelta(days=7), date_to)
            
            # Get the first day (Monday) of the week for date_from
            current_date = date_from - timedelta(days=date_from.weekday())
            
            # Process each week until we cover the entire date range
            while current_date < date_to:
                year = current_date.year
                week = current_date.strftime("%V")
                menu_data = self.fetch_menu_data(canteen_id, week, year)
                if menu_data:
                    self.store_menu_data(menu_data, canteen_id)
                current_date += timedelta(days=7)
        except Exception as e:
            logger.error(f"Failed to update menu database: {str(e)}")
            raise DataProcessingError(
                detail="Failed to update menu database",
                extra={"error": str(e)}
            )


    def get_last_week_of_year(self, year):
        last_day = date(year, 12, 31)
        return last_day.isocalendar()[1]
    
    
    def _map_dish_type_to_category(self, dish_type: str):
        words = dish_type.strip().split(",")[0].split()
        first_word = words[0].upper()
        
        dessert_types = ["SÜSSSPEISE", "DESSERT"]
        side_types = ["BEILAGEN", "SIDE"]
        soup_types = ["STUDITOPF", "TAGESSUPE"]
        
        # match case
        if first_word in dessert_types:
            return DishCategoryEnum.DESSERT
        elif first_word in side_types:
            return DishCategoryEnum.SIDE
        elif first_word in soup_types:
            return DishCategoryEnum.SOUP
        else:
            return DishCategoryEnum.MAIN

    def _generate_dish_id(self, title: str) -> UUID:
        """Generate a consistent UUID from a dish title."""
        return uuid5(NAMESPACE_DNS, title)

from datetime import date, datetime, timedelta

import requests
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from data_fetcher.food.service.simple_price_service import PriceService
from data_fetcher.food.service.translation.dish_translation_service import \
    DishTranslationService
from shared.core.exceptions import (DatabaseError, DataProcessingError,
                                    ExternalAPIError)
from shared.core.logging import get_food_fetcher_logger
from shared.enums.dish_category_enums import DishCategoryEnum
from shared.enums.language_enums import LanguageEnum
from shared.tables.food.dish_table import (DishPriceTable, DishTable,
                                      DishTranslationTable)
from shared.tables.food.menu_table import MenuDayTable, MenuDishAssociation

logger = get_food_fetcher_logger(__name__)

class MenuFetcher:
    
    def __init__(self, db: Session):
        self.db = db
        self.dish_translation_service = DishTranslationService()
        self.target_languages = [LanguageEnum.GERMAN]
        
    def fetch_menu_data(self, canteen_id: str, week: str, year: int):
        url = f"https://tum-dev.github.io/eat-api/{canteen_id}/{year}/{week}.json"
        
        try:
            response = requests.get(url)
            response.raise_for_status()
            logger.info(f"Successfully fetched menu data from TUM API: {response.status_code}")
            return response.json()
        except requests.exceptions.HTTPError as e:
            raise ExternalAPIError(
                detail="Failed to fetch menu data from TUM API",
                service="tum-dev-eat-api",
                extra={
                    "url": url,
                    "status_code": e.response.status_code if e.response else None,
                    "error": str(e)
                }
            )
        except requests.exceptions.RequestException as e:
            raise ExternalAPIError(
                detail="Connection error while fetching menu data",
                service="tum-dev-eat-api",
                extra={"url": url, "error": str(e)}
            )


    def store_menu_data(self, data: dict, canteen_id: str):
        
        try:
            dish_amount = 0
            week = data.get('number')
            year = data.get('year')
            
            if not week or not year:
                logger.error(f"Week or year data is missing: {data}")
                raise ValueError("Week or year data is missing")
            
            logger.info(f"Storing menu data for canteen {canteen_id} for week {week} of year {year}")
            
            # Get all days from the API response
            api_days = {day.get('date'): day for day in data.get('days', [])}
            
            # Calculate all weekdays for this week
            first_day_of_week = datetime.strptime(f"{year}-W{int(week):02d}-1", "%Y-W%W-%w").date()
            weekdays = [first_day_of_week + timedelta(days=i) for i in range(5)]  # Monday to Friday
            
            # Process each weekday
            for weekday in weekdays:
                date_str = weekday.strftime('%Y-%m-%d')
                day_data = api_days.get(date_str, {'date': date_str, 'dishes': []})
                
                # Create or update MenuDayTable entry for each weekday
                menu_day_obj = self.db.merge(MenuDayTable(
                    date=weekday,
                    canteen_id=canteen_id
                ))
                
                # Clear existing dish associations for this day
                self.db.query(MenuDishAssociation).filter_by(
                    menu_day_date=weekday,
                    menu_day_canteen_id=canteen_id
                ).delete()
                
                # Process dishes only if they exist
                dishes = day_data.get('dishes', [])
                for dish_data in dishes:
                    # Get or create the dish
                    dish_name_de = dish_data.get('name', '')
                    
                    dish_obj = (
                        self.db.query(DishTable)
                        .join(DishTranslationTable)
                        .filter(
                            DishTranslationTable.title == dish_name_de,
                            DishTranslationTable.language == LanguageEnum.GERMAN
                        )
                        .first()
                    )
                    
                    
                    if not dish_obj:
                        dish_type = dish_data.get('dish_type', '')
                        dish_category = self._map_dish_type_to_category(dish_type).value
                        
                        dish_obj = DishTable(
                            dish_type=dish_type,
                            dish_category=dish_category,
                            labels=dish_data.get('labels', []),
                            price_simple=PriceService.calculate_simple_price(dish_data.get("prices", {}).get("students", {}))
                        )
                        dish_amount += 1
                        self.db.add(dish_obj)
                        self.db.flush()
                        
                        fetched_dish = DishTranslationTable(
                            dish_id=dish_obj.id,
                            language=LanguageEnum.GERMAN,
                            title=dish_name_de
                        )
                        
                        translations = self.dish_translation_service.create_translations(
                            dish_obj=dish_obj,
                            target_languages=self.target_languages,
                            source_dish=fetched_dish
                        )
                        
                        self.db.add_all(translations)
                    
                    # Create new MenuDishAssociation
                    association = MenuDishAssociation(
                        dish_id=dish_obj.id,
                        menu_day_date=weekday,
                        menu_day_canteen_id=canteen_id
                    )
                    self.db.add(association)
                    
                    # Update prices
                    prices = dish_data.get("prices", {})
                    if prices:
                        # First, delete all existing price records for this dish
                        self.db.query(DishPriceTable).filter_by(dish_id=dish_obj.id).delete()
                        
                        # Then create new price records
                        for category, price_data in prices.items():
                            if isinstance(price_data, dict):
                                price_obj = DishPriceTable(
                                    dish_id=dish_obj.id,
                                    category=category.upper(),
                                    base_price=price_data.get('base_price'),
                                    price_per_unit=price_data.get('price_per_unit'),
                                    unit=price_data.get('unit')
                                )
                                self.db.add(price_obj)
            
            self.db.commit()
            logger.info(f"Menu data stored successfully. {dish_amount} dishes added.")
        except IntegrityError as e:
            logger.error(f"Database integrity error while storing menu data: {str(e)}")
            raise DatabaseError(
                detail="Database integrity error while storing menu data",
                extra={"error": str(e)}
            )
        except Exception as e:
            logger.error(f"Failed to process menu data: {str(e)}")
            raise DataProcessingError(
                detail="Failed to process menu data",
                extra={"error": str(e)}
            )


    def update_menu_database(self, canteen_id: str, date_from: date, date_to: date):
        """Update menu data for a specific canteen within a date range"""
        logger.info(f"Updating menu data for canteen {canteen_id} from {date_from} to {date_to- timedelta(days=1)}...")
        
        try:
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
            logger.info("Menu data updated successfully!")
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
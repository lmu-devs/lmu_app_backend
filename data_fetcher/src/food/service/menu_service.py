from datetime import date, timedelta
from uuid import NAMESPACE_DNS, UUID, uuid5

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from data_fetcher.src.food.constants.canteens.canteen_opening_hours_constants import (
    CanteenOpeningHoursConstants,
)
from data_fetcher.src.food.crawler.food_crawler import FoodCrawler
from data_fetcher.src.food.service.canteen_opening_status_service import (
    CanteenOpeningStatusService,
)
from data_fetcher.src.food.service.simple_price_service import PriceService
from shared.src.core.exceptions import DatabaseError, DataProcessingError
from shared.src.core.logging import get_food_fetcher_logger
from shared.src.enums import CanteenEnum, DishCategoryEnum, LanguageEnum, WeekdayEnum
from shared.src.services import LectureFreePeriodService, TranslationService
from shared.src.tables import (
    DishPriceTable,
    DishTable,
    DishTranslationTable,
    MenuDayTable,
    MenuDishAssociation,
)

logger = get_food_fetcher_logger(__name__)


class MenuFetcher:

    def __init__(self, db: Session):
        self.db = db
        self.translation_service = TranslationService()
        # self.dish_image_service = DishImageService()
        self.lecture_free_service = LectureFreePeriodService()
        self.food_crawler = FoodCrawler()

    def store_menu_days(self, canteen_id: CanteenEnum, date_from: date, date_to: date):
        """Store menu days for a specific canteen within a date range"""
        opening_hours = CanteenOpeningHoursConstants.get_opening_hours(canteen_id)

        current_date = date_from
        while current_date < date_to:
            is_lecture_free = self.lecture_free_service.is_lecture_free(current_date)
            weekday = WeekdayEnum(current_date.strftime("%A").upper())

            should_create = False
            if is_lecture_free and opening_hours.lecture_free_hours:
                should_create = any(oh.day == weekday for oh in opening_hours.lecture_free_hours or [])
            elif opening_hours.opening_hours:
                should_create = any(oh.day == weekday for oh in opening_hours.opening_hours or [])

            if should_create:
                self.db.merge(
                    MenuDayTable(
                        date=current_date,
                        canteen_id=canteen_id,
                        is_closed=CanteenOpeningStatusService.is_closed(current_date),
                    )
                )

            current_date += timedelta(days=1)

        self.db.commit()
        logger.info(f"Menu days stored successfully for {canteen_id} from {date_from} to {date_to}")

    def store_menus(self, canteen_id: CanteenEnum):
        try:
            logger.info(f"Storing menu data for canteen {canteen_id}")

            menus = self.food_crawler.get_menus(canteen_id)
            dish_amount = 0

            if menus is None:
                logger.error(f"No menus found for canteen {canteen_id}")
                return

            # Process each Menu object in the data
            for menu in menus:
                date = menu.menu_date
                # create menu day for edge cases where dishes exists but opneing hours dont match
                self.db.merge(
                    MenuDayTable(
                        date=date,
                        canteen_id=canteen_id,
                        is_closed=CanteenOpeningStatusService.is_closed(date),
                    )
                )

                # Clear existing dish associations for this day
                self.db.query(MenuDishAssociation).filter_by(menu_day_date=date, canteen_id=canteen_id).delete()

                # Process each dish
                for dish in menu.dishes:
                    dish_name_de = dish.title
                    dish_id = self._generate_dish_id(dish_name_de)

                    # Combine existing and missing labels
                    missing_labels: list[str] = self._generate_missing_labels(dish_name_de)
                    existing_labels = [label.name for label in dish.labels]  # Changed to access label.text
                    combined_labels = list(set(existing_labels + missing_labels))

                    # Try to get existing dish first
                    dish_obj = self.db.query(DishTable).filter(DishTable.id == dish_id).first()

                    if dish_obj:
                        dish_obj.labels = combined_labels
                        # Update prices whenever they exist, regardless of previous state
                        if dish.prices.students is not None:
                            dish_obj.price_simple = PriceService.calculate_simple_price(dish.prices)
                            self.db.add(dish_obj)
                            self.db.flush()

                            # Update prices
                            price_mapping = {
                                "STUDENTS": dish.prices.students,
                                "STAFF": dish.prices.staff,
                                "GUESTS": dish.prices.guests,
                            }

                            for category, price_data in price_mapping.items():
                                if price_data is not None:
                                    # Update or create price record
                                    price_obj = (
                                        self.db.query(DishPriceTable)
                                        .filter_by(dish_id=dish_obj.id, category=category)
                                        .first()
                                    )

                                    if price_obj:
                                        # Update existing price
                                        price_obj.base_price = price_data.base_price
                                        price_obj.price_per_unit = price_data.price_per_unit
                                        price_obj.unit = price_data.unit
                                    else:
                                        # Create new price record
                                        price_obj = DishPriceTable(
                                            dish_id=dish_obj.id,
                                            category=category,
                                            base_price=price_data.base_price,
                                            price_per_unit=price_data.price_per_unit,
                                            unit=price_data.unit,
                                        )
                                        self.db.add(price_obj)
                        else:
                            logger.warning(
                                f"No price data for dish {dish_obj.translations[0].title} in canteen {canteen_id}"
                            )

                    else:
                        # Creating new dish
                        dish_type = dish.dish_type
                        dish_category = self._map_dish_type_to_category(dish_type).value

                        dish_obj = DishTable(
                            id=self._generate_dish_id(dish_name_de),
                            dish_type=dish_type,
                            dish_category=dish_category,
                            labels=combined_labels,
                            price_simple=PriceService.calculate_simple_price(dish.prices),
                        )
                        dish_amount += 1
                        self.db.add(dish_obj)
                        self.db.flush()

                        # Create initial German translation
                        print(f"added german translation for dish {dish_name_de} to db")
                        german_translation = DishTranslationTable(
                            dish_id=dish_obj.id,
                            language=LanguageEnum.GERMAN,
                            title=dish_name_de,
                        )
                        self.db.add(german_translation)
                        self.db.flush()

                        # Add prices
                        price_mapping = {
                            "STUDENTS": dish.prices.students,
                            "STAFF": dish.prices.staff,
                            "GUESTS": dish.prices.guests,
                        }

                        for category, price_data in price_mapping.items():
                            if price_data is not None:
                                price_obj = DishPriceTable(
                                    dish_id=dish_obj.id,
                                    category=category,
                                    base_price=price_data.base_price,
                                    price_per_unit=price_data.price_per_unit,
                                    unit=price_data.unit,
                                )
                                self.db.add(price_obj)

                    # Create new MenuDishAssociation
                    association = MenuDishAssociation(dish_id=dish_obj.id, menu_day_date=date, canteen_id=canteen_id)
                    self.db.add(association)

                    # Add missing translations for existing and new dishes
                    translations = self.translation_service.create_missing_translations(dish_obj)
                    self.db.add_all(translations)
                    # image = self.dish_image_service.generate_dish_image_table(dish_obj)
                    # self.db.add(image)
            self.db.commit()
            logger.info(f"Menu dishes added & updated successfully. {dish_amount} dishes added.")

        except IntegrityError as e:
            logger.error(f"Database integrity error while storing menu data: {str(e)}")
            raise DatabaseError(
                detail="Database integrity error while storing menu data",
                extra={"error": str(e)},
            )
        except Exception as e:
            logger.debug(f"Failed to process menu data: {str(e)}")
            raise DataProcessingError(detail="Failed to process menu data", extra={"error": str(e)})

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

    def _generate_missing_labels(self, dish_name_de: str) -> list[str]:
        """Generate missing labels for a dish based on its German name.

        Args:
            dish_name_de (str): German dish name

        Returns:
            list[str]: List of detected labels
        """
        dish_name_lower = dish_name_de.lower()
        labels = set()

        # Poultry detection
        poultry_keywords = [
            "huhn",
            "hähnchen",
            "hahn",
            "chicken",
            "pute",
            "hühner",
            "ente",
            "hendl",
        ]
        if any(keyword in dish_name_lower for keyword in poultry_keywords):
            labels.add("POULTRY")

        # Pork detection
        if "schwein" in dish_name_lower:
            labels.add("PORK")

        # Beef detection
        if "rind" in dish_name_lower:
            labels.add("BEEF")

        # Wild meat detection
        if "hirsch" in dish_name_lower:
            labels.add("WILD_MEAT")

        # Lamb detection
        if "lamm" in dish_name_lower:
            labels.add("LAMB")

        # Veal detection
        if "kalb" in dish_name_lower:
            labels.add("VEAL")

        # Shellfish detection
        if "tintenfisch" in dish_name_lower:
            labels.add("SHELLFISH")

        return list(labels)

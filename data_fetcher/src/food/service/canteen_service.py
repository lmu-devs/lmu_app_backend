from typing import List, Tuple

from sqlalchemy.orm import Session

from data_fetcher.src.food.constants.canteens.canteens_constants import \
    CanteensConstants
from data_fetcher.src.food.service.canteen_images_service import \
    CanteenImageService
from data_fetcher.src.food.service.canteen_opening_status_service import \
    CanteenOpeningStatusService
from shared.src.core.database import Database, get_db
from shared.src.core.exceptions import DataProcessingError
from shared.src.core.logging import get_food_fetcher_logger
from shared.src.core.settings import get_settings
from shared.src.enums import CanteenEnum, OpeningHoursTypeEnum
from shared.src.tables import (CanteenImageTable, CanteenLocationTable,
                               CanteenStatusTable, CanteenTable,
                               OpeningHoursTable)

logger = get_food_fetcher_logger(__name__)


class CanteenService:
    
    def __init__(self, db: Session):
        self.db = db
        
    def store_canteen_data(self):
        """Store canteen data including locations, opening hours, and images."""
        logger.info("Storing canteen data...")
        
        for canteen in CanteensConstants.canteens:
            try:
                
                status_obj = CanteenStatusTable(
                    canteen_id=canteen.id,
                    is_closed=CanteenOpeningStatusService.is_closed(),
                    is_temporary_closed=CanteenOpeningStatusService.is_temp_closed(),
                    is_lecture_free=CanteenOpeningStatusService.is_lecture_free(),
                )
                
                location_obj = CanteenLocationTable(
                    canteen_id=canteen.id,
                    address=canteen.location.address,
                    latitude=canteen.location.latitude,
                    longitude=canteen.location.longitude,
                )
                
                canteen_obj = CanteenTable(
                    id=canteen.id,
                    name=canteen.name,
                    type=canteen.type,
                )
                
                self._store_opening_hours(canteen)
                self._store_images(canteen_obj)
                
                self.db.merge(canteen_obj)
                self.db.merge(location_obj)
                self.db.merge(status_obj)
                self.db.commit()
                
            except Exception as e:
                self.db.rollback()
                message = f"Error while storing canteen data: {str(e)}"
                logger.error(message)
                raise DataProcessingError(message)

    def _set_canteen_images(self, canteen_table: CanteenTable, files: List[Tuple[str, str]]):
        """
        Set or update the images associated with this canteen.
        """

        # Remove existing images
        self.db.query(CanteenImageTable).filter(CanteenImageTable.canteen_id == canteen_table.id).delete()

        # Add new images
        image_count = 0
        for location, url in files:
            # Check if the canteen's ID is in the image URL
            canteen_id = canteen_table.id
            # find exact enum value for the canteen
            enum_value = CanteenEnum(canteen_id).value
            
            if enum_value in url:
                image_count = image_count + 1
                new_image = CanteenImageTable(
                    canteen_id=canteen_table.id,
                    url=url,
                    name=f"{location} Image {image_count}",
                )
                self.db.add(new_image)
                
        logger.info(f"Added {image_count} canteen images for {canteen_table.name}")



    def _store_opening_hours(self, canteen):
        """Helper method to store opening hours for a canteen."""
        opening_hours_mapping = {
            OpeningHoursTypeEnum.OPENING_HOURS: canteen.opening_hours.opening_hours,
            OpeningHoursTypeEnum.SERVING_HOURS: canteen.opening_hours.serving_hours,
            OpeningHoursTypeEnum.LECTURE_FREE_HOURS: canteen.opening_hours.lecture_free_hours,
            OpeningHoursTypeEnum.LECTURE_FREE_SERVING_HOURS: canteen.opening_hours.lecture_free_serving_hours,
        }
        
        for hours_type, hours_list in opening_hours_mapping.items():
            if hours_list:
                for hour in hours_list:
                    self.db.merge(OpeningHoursTable(
                        canteen_id=canteen.id,
                        day=hour.day.value,
                        type=hours_type,
                        start_time=hour.start_time,
                        end_time=hour.end_time
                    ))

    def _store_images(self, canteen_obj: CanteenTable):
        """Helper method to store images for a canteen."""
        directory_path = "shared/src/assets/canteens/"
        settings = get_settings()
        image_url_prefix = f"{settings.IMAGES_BASE_URL_CANTEENS}/"
        files = CanteenImageService.generate_image_urls(directory_path, image_url_prefix)
        self._set_canteen_images(canteen_obj, files)

    def update_canteen_database(self):
        """Main method to update the entire canteen database."""
        logger.info("=" * 62)
        logger.info("Updating canteen data...")
        try:
            self.store_canteen_data()
            logger.info("Canteen data updated successfully!")
            logger.info("=" * 62 + "\n")
        except Exception as e:
            logger.error(f"Error while updating canteen database: {str(e)}")
        finally:
            self.db.close()


def main():
    settings = get_settings()
    Database(settings=settings)
    db = next(get_db())
    try:
        canteen_service = CanteenService(db)
        canteen_service.update_canteen_database()
    finally:
        db.close()


if __name__ == "__main__":
    main()
        
        

    
    
    


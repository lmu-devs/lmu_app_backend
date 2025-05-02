from sqlalchemy.orm import Session

from data_fetcher.src.food.constants.canteens.canteens_constants import (
    CanteensConstants,
)
from data_fetcher.src.food.service.canteen_images_service import CanteenImageService
from data_fetcher.src.food.service.canteen_opening_status_service import (
    CanteenOpeningStatusService,
)
from shared.src.core.database import Database, get_db
from shared.src.core.exceptions import DataProcessingError
from shared.src.core.logging import get_food_fetcher_logger
from shared.src.core.settings import get_settings
from shared.src.enums import OpeningHoursTypeEnum
from shared.src.models import Canteen
from shared.src.tables import (
    CanteenLocationTable,
    CanteenOpeningHoursTable,
    CanteenStatusTable,
    CanteenTable,
)

logger = get_food_fetcher_logger(__name__)


class CanteenService:

    def __init__(self, db: Session):
        self.db = db

    def delete_all_canteen_data(self):
        """Delete all canteen data from the database."""
        logger.info("Deleting all canteen data...")
        try:
            self.db.query(CanteenLocationTable).delete()
            self.db.query(CanteenStatusTable).delete()
            self.db.query(CanteenOpeningHoursTable).delete()
            self.db.commit()
        except Exception as e:
            logger.error(f"Error while deleting canteen data: {str(e)}")
            self.db.rollback()

    def store_canteen_data(self):
        """Store canteen data including locations, opening hours, and images."""
        logger.info("Storing canteen data...")
        try:
            for canteen in CanteensConstants.canteens:

                status_obj = CanteenStatusTable(
                    canteen_id=canteen.id,
                    is_closed=CanteenOpeningStatusService.is_closed(),
                    is_temporary_closed=CanteenOpeningStatusService.is_temp_closed(canteen.opening_hours),
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
                    location=location_obj,
                    status=status_obj,
                )

                self._store_opening_hours(canteen)
                self.db.merge(canteen_obj)

            self.db.commit()

            image_service = CanteenImageService(self.db)
            image_service.update_all_canteen_images()

        except Exception as e:
            self.db.rollback()
            message = f"Error while storing canteen data: {str(e)}"
            logger.error(message)
            raise DataProcessingError(message)

    def _store_opening_hours(self, canteen: Canteen):
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
                    self.db.merge(
                        CanteenOpeningHoursTable(
                            canteen_id=canteen.id,
                            day=hour.day.value,
                            type=hours_type,
                            start_time=hour.start_time,
                            end_time=hour.end_time,
                        )
                    )

    def update_canteen_database(self):
        """Main method to update the entire canteen database."""
        logger.info("Updating canteen data...")
        try:
            self.delete_all_canteen_data()
            self.store_canteen_data()
            logger.info("Canteen data updated successfully!")
            logger.info("=" * 40 + "\n")
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

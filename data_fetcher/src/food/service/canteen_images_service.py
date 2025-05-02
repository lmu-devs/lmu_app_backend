import os
from typing import List

from sqlalchemy.orm import Session

from shared.src.core.logging import get_food_fetcher_logger
from shared.src.core.settings import get_settings
from shared.src.enums import CanteenEnum
from shared.src.services.blurhash_service import BlurhashService
from shared.src.tables import CanteenImageTable

logger = get_food_fetcher_logger(__name__)


class CanteenImageService:
    def __init__(self, db: Session):
        self.db: Session = db
        self.blurhash_service = BlurhashService()
        self.settings = get_settings()
        self.directory_path = "shared/src/assets/canteens/"
        self.image_url_prefix = f"{self.settings.IMAGES_BASE_URL_CANTEENS}/"

    def generate_canteen_image_table(self) -> List[CanteenImageTable]:
        """
        Generates CanteenImageTable objects for all canteen images, including blurhash
        """
        logger.info("Generating canteen image table...")
        image_tables = []
        # Sort files to ensure consistent order
        files = sorted(os.listdir(self.directory_path))

        for file in files:
            # Get filename without extension
            name = os.path.splitext(file)[0]

            # Try to match the filename with a canteen enum
            try:
                canteen_enum = next(enum for enum in CanteenEnum if enum.value.lower() in name.lower())

                # Format display name with number
                base_name, number = name.rsplit("_", 1)
                display_name = f"{base_name.replace('-', ' ').title()} {number}"

                full_image_url = f"{self.image_url_prefix}{file}"

                image_table = CanteenImageTable(
                    canteen_id=canteen_enum,
                    url=full_image_url,
                    name=display_name,
                )
                image_tables.append(image_table)

            except StopIteration:
                logger.warning(f"Could not match image {file} to any canteen")
                continue

        return image_tables

    def update_all_canteen_images(self):
        """
        Updates all canteen images in the database
        """
        # Get all prepared image data
        image_tables = self.generate_canteen_image_table()
        self._delete_all_canteen_images()

        # Add all new images
        for image in image_tables:
            logger.info(f"Adding image for canteen {image.canteen_id.value}")
            self.db.add(image)

        self.db.commit()

    def _delete_all_canteen_images(self):
        """Deletes all existing canteen images"""
        self.db.query(CanteenImageTable).delete()


if __name__ == "__main__":
    service = CanteenImageService()
    print(service.generate_canteen_image_table())

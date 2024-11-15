import requests

from typing import List, Tuple
from sqlalchemy.orm import Session
from datetime import datetime

from shared.core.exceptions import DataFetchError, DataProcessingError
from shared.core.logging import get_data_fetcher_logger
from shared.database import get_db
from shared.models.canteen_model import CanteenImageTable, CanteenTable, CanteenType, LocationTable, OpeningHoursTable
from data_fetcher.service.images_service import ImageService
from shared.settings import get_settings

logger = get_data_fetcher_logger(__name__)
class CanteenFetcher:
    """
    Fetches canteen data from the tum-eat-api and stores it in the database.
    """
    
    def __init__(self, db: Session):
        self.db = db
        
    def fetch_canteen_data(self):
        try:
            url = "https://tum-dev.github.io/eat-api/enums/canteens.json"
            response = requests.get(url)
            response.raise_for_status()
            logger.info(f"Successfully fetched canteen data from TUM API: {response.status_code}")
            return response.json()
        except Exception as e:
            message = f"Error while fetching canteen data from TUM API: {str(e)}"
            logger.error(message)
            raise DataFetchError(message)


    def set_canteen_images(self, canteen_table: CanteenTable, files: List[Tuple[str, str]]):
        """
        Set or update the images associated with this canteen.
        """

        # Remove existing images
        self.db.query(CanteenImageTable).filter(CanteenImageTable.canteen_id == canteen_table.id).delete()


        # Add new images
        image_count = 0
        for location, url in files:
            # Check if the canteen's ID is in the image URL
            if str(canteen_table.id) in url:
                image_count = image_count + 1
                new_image = CanteenImageTable(
                    canteen_id=canteen_table.id,
                    url=url,
                    name=f"{location} Image {image_count}",
                )
                self.db.add(new_image)
                
        logger.info(f"Added {image_count} canteen images for {canteen_table.name}")


    def process_canteen_name(self, full_name: str) -> Tuple[str, CanteenType]:
        """
        Processes a canteen name and returns a tuple of (clean_name, type).
        
        Examples:
        "Mensa Garching" -> ("Garching", CanteenType.MENSA)
        "StuBistro Arcisstraße" -> ("Arcisstraße", CanteenType.STUBISTRO)
        "IPP Bistro Garching" -> ("Garching", CanteenType.STUBISTRO)
        "Mediziner Mensa" -> ("Mediziner", CanteenType.MENSA)
        """
        
        # Special cases first
        if full_name.startswith("IPP Bistro") or full_name.startswith("FMI Bistro"):
            clean_name = full_name.replace(" Bistro", "").strip()
            return (clean_name, CanteenType.STUBISTRO)
        
        if full_name.startswith("Mediziner Mensa"):
            return ("Mediziner", CanteenType.MENSA)

        # Regular cases
        if full_name.startswith("Mensa"):
            canteen_type = CanteenType.MENSA
            clean_name = full_name.replace("Mensa", "", 1).strip()
        elif full_name.startswith("StuBistro"):
            canteen_type = CanteenType.STUBISTRO
            clean_name = full_name.replace("StuBistro", "", 1).strip()
        elif full_name.startswith("StuCafé"):
            canteen_type = CanteenType.STUCAFE
            clean_name = full_name.replace("StuCafé", "", 1).strip()
        else:
            raise ValueError(f"Unknown canteen type in name: {full_name}")

        return (clean_name, canteen_type)
        

    def store_canteen_data(self, canteens: list):
        logger.info("Storing canteen data...")
        for canteen in canteens:
            try:
                # Update Canteen
                canteen_id = canteen['canteen_id']
                
                canteen_obj = self.db.query(CanteenTable).filter(CanteenTable.id == canteen_id).first()
                if not canteen_obj:
                    canteen_obj = CanteenTable(id=canteen_id)
                
                # Update Name
                clean_name, canteen_type = self.process_canteen_name(canteen['name'])
                canteen_obj.name = clean_name
                canteen_obj.type = canteen_type

                # Update Location
                location = canteen['location']
                address = location['address']
                latitude = location['latitude']
                longitude = location['longitude']
                
                canteen_obj.location = LocationTable(canteen_id=canteen_obj.id, address=address, latitude=latitude, longitude=longitude)

                # Update Opening Hours
                open_hours = canteen['open_hours']
                
                # Update Canteen Images
                directory_path = "shared/images/canteens/"
                settings = get_settings()
                image_url_prefix = f"{settings.BASE_URL}{settings.BASE_PREFIX_EAT}/images/"
                files = ImageService.generate_image_urls(directory_path, image_url_prefix)
                self.set_canteen_images(canteen_obj, files)
                
                opening_hours = []
                for day, hours in open_hours.items():
                    start_time = datetime.strptime(hours['start'], '%H:%M').time()
                    end_time = datetime.strptime(hours['end'], '%H:%M').time()
                    
                    opening_hour = OpeningHoursTable(
                        canteen_id=canteen_id,
                        day=day,
                        start_time=start_time,
                        end_time=end_time
                    )
                    opening_hours.append(opening_hour)
                    
                canteen_obj.opening_hours = opening_hours
                
                # Save to database
                self.db.add(canteen_obj)
                self.db.add(canteen_obj.location)
                self.db.add_all(canteen_obj.opening_hours)
                
                # Commit changes
                self.db.commit()
            except Exception as e:
                message = f"Error while storing canteen data: {str(e)}"
                logger.error(message)
                raise DataProcessingError(message)


    def update_canteen_database(self):
        print("\n==============================================================")
        logger.info("Updating canteen data...")
        try:
            canteen_data = self.fetch_canteen_data()
            self.store_canteen_data(canteen_data)
            logger.info("Canteen data updated successfully!")
            print("==============================================================\n")
        except Exception as e:
            logger.error(f"Error while updating canteen database: {str(e)}")
        finally:
            self.db.close()

if __name__ == "__main__":
    db = next(get_db())
    try:
        canteen_service = CanteenFetcher(db)
        canteen_service.update_canteen_database()
    finally:
        db.close()
    
    
    


from typing import List, Tuple
import requests
from sqlalchemy.orm import Session
from api.models.canteen_model import CanteenImageTable, CanteenTable, CanteenType, LocationTable, OpeningHoursTable
from datetime import datetime
from api.database import get_db
from data_fetcher.service.images_service import generate_image_urls
from data_fetcher.static.constants import base_url

def fetch_canteen_data():
    url = "https://tum-dev.github.io/eat-api/enums/canteens.json"
    response = requests.get(url)
    response.raise_for_status()
    print("Response tum-dev eat-api: ", response.status_code)
    return response.json()


def set_canteen_images(canteen_table: CanteenTable, files: List[Tuple[str, str]], db: Session):
    """
    Set or update the images associated with this canteen.
    """

    # Remove existing images
    db.query(CanteenImageTable).filter(CanteenImageTable.canteen_id == canteen_table.id).delete()


    # Add new images
    image_count = 0
    for location, url in files:
        # Check if the canteen's ID is in the image URL
        if str(canteen_table.id) in url:
            print(f"Image found for {canteen_table.name}")
            image_count = image_count + 1
            new_image = CanteenImageTable(
                canteen_id=canteen_table.id,
                url=url,
                name=f"{canteen_table.name} Image {len(canteen_table.images)} {image_count}",
            )
            db.add(new_image)
            
    print("Finished adding canteen images")


def process_canteen_name(full_name: str) -> Tuple[str, CanteenType]:
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
        clean_name = full_name.replace("IPP Bistro", "").replace("FMI Bistro", "").strip()
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
    

def store_canteen_data(canteens: list, db: Session):
    print("Storing canteen data...")
    for canteen in canteens:
        # Update Canteen
        canteen_id = canteen['canteen_id']
        
        canteen_obj = db.query(CanteenTable).filter(CanteenTable.id == canteen_id).first()
        if not canteen_obj:
            canteen_obj = CanteenTable(id=canteen_id)
        
        # Update Name
        name = canteen['name']
        
        clean_name, canteen_type = process_canteen_name(canteen['name'])
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
        directory_path = "data_fetcher/assets/canteens/"
        image_url_prefix = f"{base_url}/images/"
        files = generate_image_urls(directory_path, image_url_prefix)
        set_canteen_images(canteen_obj, files, db)
        
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
        db.add(canteen_obj)
        db.add(canteen_obj.location)
        db.add_all(canteen_obj.opening_hours)
        
    # Commit changes
    db.commit()


def update_canteen_database():
    print("\n==============================================================")
    print("Updating canteen data...")
    try:
        db = next(get_db())
        canteen_data = fetch_canteen_data()
        store_canteen_data(canteen_data, db)
        print("canteen data updated successfully!")
        print("==============================================================\n")
    except Exception as e:
        print(f"Error while updating canteen database: {str(e)}")
    finally:
        db.close()

if __name__ == "__main__":
    update_canteen_database()
    
    
    


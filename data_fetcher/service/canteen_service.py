import requests
from sqlalchemy.orm import Session
from api.models.canteen_model import CanteenTable, LocationTable, OpeningHoursTable, Base
from datetime import datetime
from api.database import get_db

def fetch_canteen_data():
    url = "https://tum-dev.github.io/eat-api/enums/canteens.json"
    response = requests.get(url)
    response.raise_for_status()
    print("Response tum-dev eat-api: ", response.status_code)
    return response.json()
    

def store_canteen_data(data: list, db: Session):
    print("Storing canteen data...")
    for item in data:
        # Update Canteen
        canteen_id = item['canteen_id']
        
        canteen_obj = db.query(CanteenTable).filter(CanteenTable.canteen_id == canteen_id).first()
        if not canteen_obj:
            canteen_obj = CanteenTable(canteen_id=canteen_id)
        
        # Update Name
        name = item['name']
        
        canteen_obj.name = name

        # Update Location
        location = item['location']
        address = location['address']
        latitude = location['latitude']
        longitude = location['longitude']
        
        canteen_obj.location = LocationTable(canteen_id=canteen_obj.canteen_id, address=address, latitude=latitude, longitude=longitude)

        # Update Opening Hours
        open_hours = item['open_hours']
        
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
    except Exception as e:
        print(f"Error while updating canteen database: {str(e)}")
    finally:
        db.close()

if __name__ == "__main__":
    update_canteen_database()

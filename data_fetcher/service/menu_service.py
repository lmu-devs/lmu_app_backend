import requests
from sqlalchemy.orm import Session
from api.database import Base, get_session, engine
from datetime import datetime

from api.models.dish_model import DishPriceTable, DishTable
from api.models.menu_model import MenuDayTable, MenuWeekTable


def fetch_menu_data(canteen_id: str, week: str, year: int):
    url = f"https://tum-dev.github.io/eat-api/{canteen_id}/{year}/{week}.json"
    response = requests.get(url)
    response.raise_for_status()
    print("Response tum-dev eat-api: ", response.status_code)
    return response.json()

def fetch_all_menu_data():
    url = "https://tum-dev.github.io/eat-api/all.json"
    response = requests.get(url)
    response.raise_for_status()
    print("Response tum-dev eat-api: ", response.status_code)
    return response.json()

def store_menu_data(data: dict, db: Session, canteen_id: str):
    print("Storing menu data...")
    week = data['number']
    year = data['year']
    
    print(f"Storing menu data for canteen {canteen_id} for week {week} of year {year}")
    
    # Try to get existing MenuWeekTable or create a new one
    menu_week_obj = db.query(MenuWeekTable).filter(
        MenuWeekTable.canteen_id == canteen_id,
        MenuWeekTable.year == year,
        MenuWeekTable.week == week
    ).first()
    
    if not menu_week_obj:
        menu_week_obj = MenuWeekTable(canteen_id=canteen_id, year=year, week=week)
        db.add(menu_week_obj)
    
    days = data['days']
    for day in days:
        date = datetime.strptime(day['date'], '%Y-%m-%d').date()
        
        # Try to get existing MenuDayTable or create a new one
        menu_day_obj = db.query(MenuDayTable).filter(
            MenuDayTable.date == date,
            MenuDayTable.menu_week_week == week,
            MenuDayTable.menu_week_year == year
        ).first()
        
        if not menu_day_obj:
            menu_day_obj = MenuDayTable(
                date=date,
                menu_week_week=week,
                menu_week_year=year
            )
            menu_week_obj.menu_days.append(menu_day_obj)
        
        # Clear existing dishes for this day
        menu_day_obj.dishes = []
        
        
        # Add dishes to menu day
        dishes = day['dishes']
        for dish in dishes:
            dish_obj = DishTable(
                name=dish['name'],
                dish_type=dish['dish_type'],
                labels=dish['labels']
            )
            menu_day_obj.dishes.append(dish_obj)
            
            # Add prices to dish
            prices = dish["prices"]

            for category, price_data in prices.items():
                price_obj = DishPriceTable(
                    category=category,
                    base_price=price_data['base_price'],
                    price_per_unit=price_data['price_per_unit'],
                    unit=price_data['unit']
                )
                dish_obj.prices.append(price_obj)
            
            
            
            
    
    db.add(menu_week_obj)
    db.commit()
    print("Menu data stored successfully.")
    
    
def store_all_menu_data(data: dict, db: Session):
    print("Storing menu data...")
    canteen_id = data['canteen_id'] # is this right?
    week = data['number']
    year = data['year']
    
    print(f"Storing all menu data for week all coming weeks")
    
    # Try to get existing MenuWeekTable or create a new one
    menu_week_obj = db.query(MenuWeekTable).filter(
        MenuWeekTable.canteen_id == canteen_id,
        MenuWeekTable.year == year,
        MenuWeekTable.week == week
    ).first()
    
    if not menu_week_obj:
        menu_week_obj = MenuWeekTable(canteen_id=canteen_id, year=year, week=week)
        db.add(menu_week_obj)
    
    days = data['days']
    for day in days:
        date = datetime.strptime(day['date'], '%Y-%m-%d').date()
        
        # Try to get existing MenuDayTable or create a new one
        menu_day_obj = db.query(MenuDayTable).filter(
            MenuDayTable.date == date,
            MenuDayTable.menu_week_week == week,
            MenuDayTable.menu_week_year == year
        ).first()
        
        if not menu_day_obj:
            menu_day_obj = MenuDayTable(
                date=date,
                menu_week_week=week,
                menu_week_year=year
            )
            menu_week_obj.menu_days.append(menu_day_obj)
        
        # Clear existing dishes for this day
        menu_day_obj.dishes = []
        
        
        # Add dishes to menu day
        dishes = day['dishes']
        for dish in dishes:
            dish_obj = DishTable(
                name=dish['name'],
                dish_type=dish['dish_type'],
                labels=dish['labels']
            )
            menu_day_obj.dishes.append(dish_obj)
            
            # Add prices to dish
            prices = dish["prices"]

            for category, price_data in prices.items():
                price_obj = DishPriceTable(
                    category=category,
                    base_price=price_data['base_price'],
                    price_per_unit=price_data['price_per_unit'],
                    unit=price_data['unit']
                )
                dish_obj.prices.append(price_obj)
            
            
            
            
    
    db.add(menu_week_obj)
    db.commit()
    print("Menu data stored successfully.")
    
    


def update_menu_database(canteen_id: str, year: int, week: str, ):
    assert len(week) == 2, "Week must be a two-digit number"
    print("Updating menu data...")
    Base.metadata.create_all(bind=engine)
    db = get_session()
    
    try:
        menu_data = fetch_menu_data(canteen_id, week, year)
        store_menu_data(menu_data, db, canteen_id)
        print(menu_data)
        print("menu data updated successfully!")
    except Exception as e:
        print(f"Error while updating menu database: {str(e)}")
    finally:
        db.close()
        
        
        
        
        
def update_all_menu_items():
    # 1. get all canteen_id from database
    
    # 2. for each canteen_id, get the menu data
    
    pass
    

if __name__ == "__main__":
    update_menu_database()
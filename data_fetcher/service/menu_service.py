import requests
from requests.exceptions import HTTPError, RequestException
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from shared.database import get_db
from datetime import datetime, date, timedelta

from api.models.dish_model import DishPriceTable, DishTable
from api.models.menu_model import MenuDayTable, MenuDishAssociation
from data_fetcher.enums.mensa_enums import CanteenID
from data_fetcher.service.price_service import calculate_simple_price


def fetch_menu_data(canteen_id: str, week: str, year: int):
    url = f"https://tum-dev.github.io/eat-api/{canteen_id}/{year}/{week}.json"
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        print("Response tum-dev eat-api: ", response.status_code)
        return response.json()
    except HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")
    except RequestException as req_err:
        print(f"Request error occurred: {req_err}")
    except Exception as err:
        print(f"An error occurred: {err}")
    return None


def store_menu_data(data: dict, db: Session, canteen_id: str):
    print("Storing menu data...")
    
    try:
        week = data.get('number')
        year = data.get('year')
        
        if not week or not year:
            raise ValueError("Week or year data is missing")
        
        print(f"Storing menu data for canteen {canteen_id} for week {week} of year {year}")
        
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
            menu_day_obj = db.merge(MenuDayTable(
                date=weekday,
                canteen_id=canteen_id
            ))
            
            # Clear existing dish associations for this day
            db.query(MenuDishAssociation).filter_by(
                menu_day_date=weekday,
                menu_day_canteen_id=canteen_id
            ).delete()
            
            # Process dishes only if they exist
            dishes = day_data.get('dishes', [])
            for dish_data in dishes:
                # Get or create the dish
                dish_name = dish_data.get('name', '')
                dish_obj = db.query(DishTable).filter_by(name=dish_name).first()
                if not dish_obj:
                    dish_obj = DishTable(
                        name=dish_name,
                        dish_type=dish_data.get('dish_type', ''),
                        labels=dish_data.get('labels', []),
                        price_simple=calculate_simple_price(dish_data.get("prices", {}).get("students", {}))
                    )
                    db.add(dish_obj)
                    db.flush()
                
                # Create new MenuDishAssociation
                association = MenuDishAssociation(
                    dish_id=dish_obj.id,
                    menu_day_date=weekday,
                    menu_day_canteen_id=canteen_id
                )
                db.add(association)
                
                # Update prices
                prices = dish_data.get("prices", {})
                if prices:
                    for category, price_data in prices.items():
                        if isinstance(price_data, dict):
                            price_obj = db.query(DishPriceTable).filter_by(
                                dish_id=dish_obj.id,
                                category=category
                            ).first()
                            
                            if not price_obj:
                                price_obj = DishPriceTable(
                                    dish_id=dish_obj.id,
                                    category=category
                                )
                                db.add(price_obj)
                            
                            price_obj.base_price = price_data.get('base_price')
                            price_obj.price_per_unit = price_data.get('price_per_unit')
                            price_obj.unit = price_data.get('unit')
        
        db.commit()
        print("Menu data stored successfully.")
    except IntegrityError as e:
        db.rollback()
        print(f"Error while updating menu database: {str(e)}")
    except Exception as e:
        db.rollback()
        print(f"Unexpected error while updating menu database: {str(e)}")
        print(f"Error details: {type(e).__name__}, {str(e)}")


def update_menu_database(canteen_id: str, date_from: date, date_to: date):
    """Update menu data for a specific canteen within a date range"""
    print(f"Updating menu data for canteen {canteen_id} from {date_from} to {date_to}...")
    
    try:
        db = next(get_db())
        current_date = date_from
        while current_date <= date_to:
            year = current_date.year
            week = current_date.strftime("%V")
            menu_data = fetch_menu_data(canteen_id, week, year)
            if menu_data:
                store_menu_data(menu_data, db, canteen_id)
            current_date += timedelta(days=7)
        print("Menu data updated successfully!")
    except Exception as e:
        print(f"Error while updating menu database: {str(e)}")
    finally:
        db.close()


def get_last_week_of_year(year):
    last_day = date(year, 12, 31)
    return last_day.isocalendar()[1]


if __name__ == "__main__":
    update_menu_database()
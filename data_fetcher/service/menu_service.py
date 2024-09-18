import requests
from requests.exceptions import HTTPError, RequestException
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from api.database import get_db
from datetime import datetime, date

from api.models.dish_model import DishPriceTable, DishTable
from api.models.menu_model import MenuDayTable, MenuDishAssociation, MenuWeekTable
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
        
        # Use merge to either insert or update the MenuWeekTable entry
        menu_week_obj = db.merge(MenuWeekTable(canteen_id=canteen_id, year=year, week=week))
        
        days = data.get('days', [])
        for day in days:
            date_str = day.get('date')
            if not date_str:
                print(f"Skipping day with missing date")
                continue
            
            date = datetime.strptime(date_str, '%Y-%m-%d').date()
            
            # Use merge for MenuDayTable
            menu_day_obj = db.merge(MenuDayTable(
                date=date,
                menu_week_week=week,
                menu_week_year=year,
                menu_week_canteen_id=canteen_id
            ))
            
            # Process dishes for this day
            dishes = day.get('dishes', [])
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
                    db.flush()  # This will assign an ID to the new dish
                
                # Create or update the MenuDishAssociation
                association = db.query(MenuDishAssociation).filter_by(
                    dish_id=dish_obj.id,
                    menu_day_date=date,
                    menu_day_canteen_id=canteen_id
                ).first()
                
                if not association:
                    association = MenuDishAssociation(
                        dish_id=dish_obj.id,
                        menu_day_date=date,
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
                        else:
                            print(f"Skipping invalid price data for category {category}")
        
        db.commit()
        print("Menu data stored successfully.")
    except IntegrityError as e:
        db.rollback()
        print(f"Error while updating menu database: {str(e)}")
    except Exception as e:
        db.rollback()
        print(f"Unexpected error while updating menu database: {str(e)}")
        print(f"Error details: {type(e).__name__}, {str(e)}")


    
    



def update_menu_database(canteen_id: str, year: int, week: str, ):
    assert len(week) == 2, "Week must be a two-digit number"
    print("Updating menu data...")
    
    try:
        db = next(get_db())
        menu_data = fetch_menu_data(canteen_id, week, year)
        store_menu_data(menu_data, db, canteen_id)
        print(menu_data)
        print("menu data updated successfully!")
    except Exception as e:
        print(f"Error while updating menu database: {str(e)}")
    finally:
        db.close()
        
        


def update_date_range_menu_database(start_year: int, start_week: str, end_year: int, end_week: str):
    """
    Fills the eat database with menu data for a specified date range.
    
    :param start_year: The starting year as an integer
    :param start_week: The starting week as a string (2 digits)
    :param end_year: The ending year as an integer
    :param end_week: The ending week as a string (2 digits)
    """
    assert len(start_week) == 2, "Week must be a two-digit number"
    assert len(end_week) == 2, "Week must be a two-digit number"
    print(f"Updating menu data range from week {start_week} of year {start_year} to week {end_week} of year {end_year}...")
    
    try:
        db = next(get_db())
        
        for year in range(start_year, end_year + 1):
            start_week_num = int(start_week) if year == start_year else 1
            end_week_num = int(end_week) if year == end_year else get_last_week_of_year(year)
            
            for week in range(start_week_num, end_week_num + 1):
                # skip week 1 because it doesnt exist in tum api
                if week == 1:
                    continue
                week_str = f"{week:02d}"
                
                for canteen in CanteenID:
                    menu_data = fetch_menu_data(canteen.value, week_str, year)
                    if not menu_data:
                        continue
                    store_menu_data(menu_data, db, canteen.value)
                    print(f"Updated menu data for {canteen.name} - Year: {year}, Week: {week_str} \n")
        
        print("Menu data updated successfully for all canteens within the specified date range! ")
        print("==============================================================\n")
    except Exception as e:
        print(f"Error while updating menu database: {str(e)}")
    finally:
        db.close()

def get_last_week_of_year(year):
    last_day = date(year, 12, 31)
    return last_day.isocalendar()[1]

        
        

    

if __name__ == "__main__":
    update_menu_database()

from sqlalchemy.orm import Session
from api.models.user_model import UserDto, UserTable


def store_user_data(user_data, db: Session):
    print("Storing user data of one user...")
    # TODO: Implement this function
    
    
    

def update_user_data(user_data, db: Session):
    print("\n==============================================================")
    print("Updating user data...")
    try:
        store_user_data(user_data, db)
        print("user data updated successfully!")
    except Exception as e:
        print(f"Error while updating user database: {str(e)}")
    finally:
        db.close()
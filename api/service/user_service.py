from sqlalchemy.orm import Session
from api.api_key import generate_user_api_key
from api.models.user_model import UserTable
from datetime import datetime

def store_user_data(user_data, db: Session):
    print("Storing user data of one user...")
    new_user = UserTable(
        device_id=user_data['device_id'],
        # name=user_data.get('name'),
        # email=user_data.get('email'),
        # password=user_data.get('password'),
        api_key=generate_user_api_key()
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

def create_user_data(device_id: str, db: Session):
    print("\n==============================================================")
    print("Updating user data...")
    try:
        user_data = {
            'device_id': device_id,
            # 'name': "Default Name",  # Replace with actual data
            # 'email': "default@example.com",  # Replace with actual data
            # 'password': "defaultpassword"  # Replace with actual data
        }
        new_user = store_user_data(user_data, db)
        print("User data updated successfully!")
        return new_user
    except Exception as e:
        print(f"Error while updating user database: {str(e)}")
        db.rollback()
        raise e
    finally:
        db.close()
        print("==============================================================\n")
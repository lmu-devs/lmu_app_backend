from sqlalchemy.orm import Session

from api.core.api_key import generate_user_api_key
from api.models.user_model import UserTable


def get_user_from_db(user_id: int, db: Session) -> UserTable | None:
    """Get user from database by user_id"""
    user = db.query(UserTable).filter(UserTable.id == user_id).first()
    if not user:
        raise Exception("User not found")
    return user


def store_user_data(user_data, db: Session) -> UserTable:
    """Store user data in the database"""
    print("Storing user data of one user...")
    new_user = UserTable(
        device_id=user_data['device_id'],
        api_key=generate_user_api_key()
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


def create_user_data(device_id: str, db: Session) -> UserTable:
    """Prepare and store user data in the database"""
    print("\n==============================================================")
    print("Updating user data...")
    try:
        user_data = {
            'device_id': device_id,
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
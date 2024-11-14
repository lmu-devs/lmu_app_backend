from sqlalchemy.orm import Session

from api.core.api_key import generate_user_api_key
from api.models.user_model import UserTable




class UserService:
    def __init__(self, db: Session):
        """Initialize the UserService with a database session."""
        self.db = db

    def get_user(self, user_id: int) -> UserTable | None:
        """Get user from database by user_id"""
        user = self.db.query(UserTable).filter(UserTable.id == user_id).first()
        if not user:
            raise Exception("User not found")
        return user


    def store_user(self, user_data) -> UserTable:
        """Store user data in the database"""
        print("Storing user data of one user...")
        new_user = UserTable(
            device_id=user_data['device_id'],
            api_key=generate_user_api_key()
        )
        self.db.add(new_user)
        self.db.commit()
        self.db.refresh(new_user)
        return new_user


    def create_user(self, device_id: str) -> UserTable:
        """Prepare and store user data in the database"""
        print("\n==============================================================")
        print("Updating user data...")
        try:
            user_data = {
                'device_id': device_id,
            }
            new_user = self.store_user(user_data)
            print("User data updated successfully!")
            return new_user
        except Exception as e:
            print(f"Error while updating user database: {str(e)}")
            self.db.rollback()
            raise e
        finally:
            self.db.close()
            print("==============================================================\n")

from sqlalchemy.orm import Session

from api.core.api_key import APIKey
from shared.core.exceptions import DatabaseError, NotFoundError
from shared.core.logging import get_user_logger
from shared.models.user_model import UserTable

logger = get_user_logger(__name__)

class UserService:
    def __init__(self, db: Session):
        """Initialize the UserService with a database session."""
        self.db = db
        
    def get_user(self, user_id: int) -> UserTable | None:
        """Get user from database by user_id"""
        user = self.db.query(UserTable).filter(UserTable.id == user_id).first()
        if not user:
            raise NotFoundError(
                detail="User not found",
                extra={"user_id": user_id}
            )
        logger.info(f"Found user with id {user_id}")
        return user


    def store_user(self, user_data) -> UserTable:
        """Store user data in the database"""
        logger.info(f"Storing user data of one user with device_id: {user_data['device_id']}")
        new_user = UserTable(
            device_id=user_data['device_id'],
            api_key=APIKey.generate_user_key()
        )
        self.db.add(new_user)
        self.db.commit()
        self.db.refresh(new_user)
        return new_user


    def create_user(self, device_id: str) -> UserTable:
        """Prepare and store user data in the database"""
        logger.info(f"Updating user data with device_id: {device_id}")
        try:
            user_data = {
                'device_id': device_id,
            }
            new_user = self.store_user(user_data)
            logger.info(f"User data for device_id {device_id} updated successfully!\n")
            return new_user
        except Exception as e:
            logger.error(f"Error while updating user database: {str(e)}\n")
            self.db.rollback()
            raise DatabaseError(
                detail="Failed to create user",
                extra={"original_error": str(e)}
            )
        finally:
            self.db.close()
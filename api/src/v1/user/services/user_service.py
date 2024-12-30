from sqlalchemy.orm import Session

from shared.src.core.exceptions import DatabaseError, NotFoundError
from shared.src.core.logging import get_user_logger
from shared.src.tables import UserTable

from ...core import APIKey
from ..schemas.user_scheme import UserUpdate

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


    def store_user(self) -> UserTable:
        """Store user data in the database"""
        logger.info(f"Storing user data of one user")
        new_user = UserTable(
            api_key=APIKey.generate_user_key()
        )
        self.db.add(new_user)
        self.db.commit()
        self.db.refresh(new_user)
        return new_user


    def create_user(self) -> UserTable:
        """Prepare and store user data in the database"""
        logger.info(f"Creating new user")
        try:
            new_user = self.store_user()
            logger.info(f"User data updated successfully!\n")
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
            
    def update_user(self, user: UserTable, update_data: UserUpdate) -> None:
        """Update user in database"""
        logger.info(f"Updating user with user_id: {user.id}")
        try:
            for key, value in update_data.model_dump().items():
                setattr(user, key, value)
            self.db.commit()
            logger.info(f"User with user_id: {user.id} updated successfully")
        except Exception as e:
            logger.error(f"Error while updating user in database: {str(e)}")
            self.db.rollback()
            raise DatabaseError(
                detail="Failed to update user",
                extra={"original_error": str(e)}
            )
        
    def delete_user(self, user: UserTable) -> None:
        """Delete user from database by user_id"""
        logger.info(f"Deleting user with user_id: {user.id}")
        try:
            self.db.delete(user)
            self.db.commit()
            logger.info(f"User with user_id: {user.id} deleted successfully")
        except Exception as e:
            logger.error(f"Error while deleting user from database: {str(e)}")
            self.db.rollback()
            raise DatabaseError(
                detail="Failed to delete user",
                extra={"original_error": str(e)}
            )
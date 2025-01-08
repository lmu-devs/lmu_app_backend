from sqlalchemy import Result, select
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
    
    async def get_user_by_device_id(self, device_id: str) -> UserTable:
        """Get user from database by device_id"""
        stmt = select(UserTable).filter(UserTable.device_id == device_id)
        result: Result = await self.db.execute(stmt)
        user = result.scalar_one_or_none()
        if not user:
            raise NotFoundError(
                detail="User not found",
                extra={"device_id": device_id}
            )
        logger.info(f"Found user with device_id {device_id}")
        return user
    
    async def is_existing_user(self, device_id: str) -> bool:
        """Check if user exists in database by device_id"""
        stmt = select(UserTable).filter(UserTable.device_id == device_id)
        result: Result = await self.db.execute(stmt)
        return bool(result.scalar_one_or_none())

    async def store_user(self, device_id: str) -> UserTable:
        """Store user data in the database"""
        logger.info("Storing user data")
        new_user = UserTable(
            api_key=APIKey.generate_user_key(device_id),
            device_id=device_id
        )
        self.db.add(new_user)
        await self.db.commit()
        return new_user

    async def create_user(self, device_id: str) -> UserTable:
        """Prepare and store user data in the database"""
        logger.info("Creating new user")
        try:
            return await self.store_user(device_id)
        except Exception as e:
            logger.error(f"Error creating user: {str(e)}")
            await self.db.rollback()
            raise DatabaseError(
                detail="Failed to create user",
                extra={"original_error": str(e)}
            )
        finally:
            self.db.close()
            
    async def update_user(self, user: UserTable, update_data: UserUpdate) -> None:
        """Update user in database"""
        logger.info(f"Updating user with user_id: {user.id}")
        try:
            for key, value in update_data.model_dump().items():
                setattr(user, key, value)
            await self.db.commit()
            logger.info(f"User with user_id: {user.id} updated successfully")
        except Exception as e:
            logger.error(f"Error while updating user in database: {str(e)}")
            self.db.rollback()
            raise DatabaseError(
                detail="Failed to update user",
                extra={"original_error": str(e)}
            )
        
    async def delete_user(self, user: UserTable) -> None:
        """Delete user from database by user_id"""
        logger.info(f"Deleting user with user_id: {user.id}")
        try:
            await self.db.delete(user)
            await self.db.commit()
            logger.info(f"User with user_id: {user.id} deleted successfully")
        except Exception as e:
            logger.error(f"Error while deleting user from database: {str(e)}")
            await self.db.rollback()
            raise DatabaseError(
                detail="Failed to delete user",
                extra={"original_error": str(e)}
            )
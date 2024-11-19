import secrets

from requests import Session
from fastapi import Depends, Security
from fastapi.security.api_key import APIKeyHeader

from shared.core.exceptions import AuthenticationError, AuthorizationError
from shared.core.logging import get_api_logger
from shared.database import get_db
from shared.models.user_model import UserTable
from shared.settings import get_settings

logger = get_api_logger(__name__)

user_api_key = APIKeyHeader(
    name="user-api-key", 
    auto_error=False,
    description="User API key for authenticated user operations"
)
system_api_key = APIKeyHeader(
    name="system-api-key", 
    auto_error=False,
    description="System API key for creating users"
)
admin_api_key = APIKeyHeader(
    name="admin-api-key", 
    auto_error=False,
    description="Admin API key for administrative operations"
)

class APIKey:
    def __init__(self):
        pass
    
    @staticmethod
    async def verify_admin_api_key(api_key: str = Security(admin_api_key)) -> bool:
        """Verify the admin API key."""
        settings = get_settings()
        if api_key != settings.ADMIN_API_KEY:
            logger.warning("Invalid API key used for admin access")
            raise AuthenticationError(
                detail="Invalid API key",
                extra={"admin-api-key": api_key},
            )
        logger.info("Successfully validated admin API key")
        return True

    @staticmethod
    async def verify_system_api_key(api_key: str = Security(system_api_key)) -> bool:
        """Verify the system API key."""
        settings = get_settings()
        if api_key != settings.SYSTEM_API_KEY:
            logger.warning("Invalid API key used for log access")
            raise AuthenticationError(
                detail="Invalid API key",
                extra={"system-api-key": api_key},
            )
        logger.info("Successfully validated system API key")
        return True

    @staticmethod
    def generate_user_key() -> str:
        return secrets.token_urlsafe(32)

    @staticmethod
    async def get_user_from_key(
        api_key_header: str = Security(user_api_key), 
        db: Session = Depends(get_db)
    ) -> UserTable:
        user: UserTable = db.query(UserTable).filter(UserTable.api_key == api_key_header).first()
        if user is None:
            raise AuthorizationError(
                detail="Could not validate user credentials. ",
                extra={"user-api-key": api_key_header}
            )
        logger.info(f"Successfully validated user API key for {str(user.id)}")
        return user

    @staticmethod
    async def get_user_from_key_soft(
        api_key_header: str = Security(user_api_key), 
        db: Session = Depends(get_db)
    ) -> UserTable:
        user: UserTable = db.query(UserTable).filter(UserTable.api_key == api_key_header).first()
        logger.info(f"Checked user API key for {str(user.id) if user else 'unknown (no match)'}")
        return user

import hashlib
import secrets

from fastapi import Depends, Security
from fastapi.security.api_key import APIKeyHeader
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from shared.src.core.database import get_async_db
from shared.src.core.exceptions import AuthenticationError, AuthorizationError
from shared.src.core.logging import get_main_logger
from shared.src.core.settings import get_settings
from shared.src.tables import UserTable

logger = get_main_logger(__name__)

user_api_key = APIKeyHeader(
    name="user-api-key",
    auto_error=False,
    description="User API key for authenticated user operations",
)
system_api_key = APIKeyHeader(
    name="system-api-key",
    auto_error=False,
    description="System API key for creating users",
)
admin_api_key = APIKeyHeader(
    name="admin-api-key",
    auto_error=False,
    description="Admin API key for administrative operations",
)


class APIKey:
    """A class to handle API key generation and verification for different types of users.

    This class provides functionality for:
    - Verifying admin API keys
    - Verifying system API keys
    - Generating user API keys (both deterministic and random)
    - Verifying user API keys (strict and soft verification)
    """

    def __init__(self):
        """Initialize an APIKey instance."""
        pass

    @staticmethod
    async def verify_admin_api_key(api_key: str = Security(admin_api_key)) -> bool:
        """Verify if the provided admin API key is valid.

        Args:
            api_key (str): The admin API key to verify, obtained from request header.

        Returns:
            bool: True if the API key is valid.

        Raises:
            AuthenticationError: If the provided API key is invalid.
        """
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
        """Verify if the provided system API key is valid.

        Args:
            api_key (str): The system API key to verify, obtained from request header.

        Returns:
            bool: True if the API key is valid.

        Raises:
            AuthenticationError: If the provided API key is invalid.
        """
        settings = get_settings()
        if api_key != settings.SYSTEM_API_KEY:
            logger.warning("Invalid API key used for system access")
            raise AuthenticationError(
                detail="Invalid API key",
                extra={"system-api-key": api_key},
            )
        logger.info("Successfully validated system API key")
        return True

    @staticmethod
    def generate_user_key(device_id: str | None) -> str:
        """Generate a user API key.

        Args:
            device_id (str | None): The device ID to generate a deterministic key for.
                                  If None, generates a random key.

        Returns:
            str: A generated API key. If device_id is provided, returns a deterministic
                 hash based on the device_id and system API key. Otherwise, returns
                 a random URL-safe token.
        """
        if device_id:
            # Generate deterministic token based on device id
            hash_input = f"{device_id}{get_settings().SYSTEM_API_KEY}"
            hash_object = hashlib.sha256(hash_input.encode())
            return hash_object.hexdigest()
        else:
            return secrets.token_urlsafe(48)

    @staticmethod
    async def verify_user_api_key(
        api_key_header: str = Security(user_api_key),
        db: AsyncSession = Depends(get_async_db),
    ) -> UserTable:
        """Verify a user API key with strict validation.

        Args:
            api_key_header (str): The user API key to verify, obtained from request header.
            db (AsyncSession): The database session for querying user information.

        Returns:
            UserTable: The user record if the API key is valid.

        Raises:
            AuthorizationError: If the user API key is invalid or not found.
        """
        user: UserTable = (
            await db.execute(select(UserTable).filter(UserTable.api_key == api_key_header))
        ).scalar_one_or_none()
        if user is None:
            raise AuthorizationError(
                detail="Could not validate user credentials. ",
                extra={"user-api-key": api_key_header},
            )
        logger.info(f"Successfully validated user API key for {str(user.id)}")
        return user

    @staticmethod
    async def verify_user_api_key_soft(
        api_key_header: str = Security(user_api_key),
        db: AsyncSession = Depends(get_async_db),
    ) -> UserTable:
        """Verify a user API key with soft validation (no error raising).

        Args:
            api_key_header (str): The user API key to verify, obtained from request header.
            db (AsyncSession): The database session for querying user information.

        Returns:
            UserTable: The user record if found, None otherwise.
        """
        user: UserTable = (
            await db.execute(select(UserTable).filter(UserTable.api_key == api_key_header))
        ).scalar_one_or_none()
        logger.info(f"Checked user API key for {str(user.id) if user else 'unknown (no match)'}")
        return user


if __name__ == "__main__":
    print(APIKey.generate_user_key(None))

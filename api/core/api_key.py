import os
import secrets
from fastapi import Depends, Security
from fastapi.security.api_key import APIKeyHeader
from requests import Session

from shared.core.exceptions import AuthorizationError
from shared.database import get_db
from shared.models.user_model import UserTable

api_key_header = APIKeyHeader(name="x-api-key", auto_error=False)
API_KEY = os.environ.get('API_KEY')

class APIKey:
    def __init__(self):
        pass

    @staticmethod
    async def get_system_key_header(api_key_header: str = Security(api_key_header)) -> bool:
        print("Checking API key...")
        if api_key_header == API_KEY:
            return True
        raise AuthorizationError(
            detail="Could not validate system credentials",
            extra={"header": "x-api-key"}
        )

    @staticmethod
    def generate_user_key() -> str:
        return secrets.token_urlsafe(32)

    @staticmethod
    async def get_user_from_key(
        api_key_header: str = Security(api_key_header), 
        db: Session = Depends(get_db)
    ) -> UserTable:
        print("Checking user API key and UUID...")
        user = db.query(UserTable).filter(UserTable.api_key == api_key_header).first()
        if user is None:
            raise AuthorizationError(
                detail="Could not validate user credentials",
                extra={"header": "x-api-key"}
            )
        return user

    @staticmethod
    async def get_user_from_key_soft(
        api_key_header: str = Security(api_key_header), 
        db: Session = Depends(get_db)
    ) -> UserTable:
        print("Checking user API key and UUID...")
        user = db.query(UserTable).filter(UserTable.api_key == api_key_header).first()
        return user
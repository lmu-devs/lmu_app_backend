import os
import secrets
from fastapi import Depends, HTTPException, Security
from fastapi.security.api_key import APIKeyHeader
from requests import Session

from api.core.database import get_db
from api.models.user_model import UserTable

api_key_header = APIKeyHeader(name="x-api-key", auto_error=False)


# System API key
API_KEY = os.environ.get('API_KEY')

async def get_system_api_key_header(api_key_header: str = Security(api_key_header)) -> bool:
    print("Checking API key...")
    if api_key_header == API_KEY:
        return True
    raise HTTPException(status_code=403, detail="Could not validate credentials")


# User API key
def generate_user_api_key() -> str:
    return secrets.token_urlsafe(32)

async def get_user_from_api_key(api_key_header: str = Security(api_key_header), db: Session = Depends(get_db)) -> UserTable:
    print("Checking user API key and UUID...")
    user = db.query(UserTable).filter(UserTable.api_key == api_key_header).first()
    if user is None:
        raise HTTPException(status_code=403, detail="Could not validate user credentials")
    return user

async def get_user_from_api_key_soft(api_key_header: str = Security(api_key_header), db: Session = Depends(get_db)) -> UserTable:
    print("Checking user API key and UUID...")
    user = db.query(UserTable).filter(UserTable.api_key == api_key_header).first()
    return user
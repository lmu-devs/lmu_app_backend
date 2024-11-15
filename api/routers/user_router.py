from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from fastapi.security.api_key import APIKey as APIKeyHeader

from shared.database import get_db
from shared.models.user_model import UserTable
from api.core.api_key import APIKey
from api.pydantics.user_pydantic import user_to_pydantic
from api.schemas.user_scheme import User
from api.services.user_service import UserService


router = APIRouter()

@router.post("/users/create", response_model=User)
def create_user(device_id: str, db: Session = Depends(get_db), api_key: APIKeyHeader = Depends(APIKey.get_system_key_header)):
    existing_user = db.query(UserTable).filter(UserTable.device_id == device_id).first()
    if existing_user:
        user = user_to_pydantic(existing_user)
        return user
    
    new_user = UserService(db).create_user(device_id)
    return user_to_pydantic(new_user)

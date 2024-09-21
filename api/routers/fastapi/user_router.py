from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from fastapi.security.api_key import APIKey

from api.api_key import get_system_api_key_header
from api.database import get_db
from api.models.user_model import UserDto, UserTable
from api.routers.models.user_pydantic import user_to_pydantic
from api.service.user_service import create_user_data


router = APIRouter()

@router.post("/users/create", response_model=UserDto)
def create_user(device_id: str, db: Session = Depends(get_db), api_key: APIKey = Depends(get_system_api_key_header)):
    existing_user = db.query(UserTable).filter(UserTable.device_id == device_id).first()
    if existing_user:
        user = user_to_pydantic(existing_user)
        return user
    
    new_user = create_user_data(device_id, db)
    return user_to_pydantic(new_user)

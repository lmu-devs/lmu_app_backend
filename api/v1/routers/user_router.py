import uuid
from fastapi import APIRouter, Depends
from fastapi.security.api_key import APIKey as APIKeyHeader
from sqlalchemy.orm import Session

from shared.core.logging import get_user_logger
from shared.database import get_db
from shared.models.user_model import UserTable
from api.v1.core.api_key import APIKey
from api.v1.pydantics.user_pydantic import user_to_pydantic
from api.v1.schemas.user_scheme import User, UserUpdate
from api.v1.services.user_service import UserService

router = APIRouter()
user_logger = get_user_logger(__name__)

@router.post("/users", response_model=User, description="Create a new user and return the user object. Returns the user object if the user already exists.")
def create_user(device_id: str, db: Session = Depends(get_db), api_key: APIKeyHeader = Depends(APIKey.verify_system_api_key)):
    existing_user = db.query(UserTable).filter(UserTable.device_id == device_id).first()
    if existing_user:
        user = user_to_pydantic(existing_user)
        return user
    
    new_user = UserService(db).create_user(device_id)
    user_logger.info(f"Created new user with device_id: {device_id}")
    return user_to_pydantic(new_user)


@router.put("/users", description="Update user in database")
def update_user(
    update_data: UserUpdate, 
    db: Session = Depends(get_db), 
    user: UserTable = Depends(APIKey.verify_user_api_key)
):
    UserService(db).update_user(user, update_data)
    return {"message": "User updated successfully"}


@router.delete("/users", description="Delete user from database")
def delete_user(db: Session = Depends(get_db), user: UserTable = Depends(APIKey.verify_user_api_key)):
    UserService(db).delete_user(user)
    return {"message": "User deleted successfully"}
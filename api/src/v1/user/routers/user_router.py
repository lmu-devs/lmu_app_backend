from fastapi import APIRouter, Depends, Query
from fastapi.security.api_key import APIKey as APIKeyHeader
from sqlalchemy.ext.asyncio import AsyncSession

from shared.src.core.database import get_async_db
from shared.src.core.logging import get_user_logger
from shared.src.tables import UserTable

from ...core import APIKey
from ..pydantics.user_pydantic import user_to_pydantic
from ..schemas.user_scheme import User, UserUpdate
from ..services.user_service import UserService


router = APIRouter()
user_logger = get_user_logger(__name__)

@router.post("/users", response_model=User)
async def create_user(
    db: AsyncSession = Depends(get_async_db),
    api_key: APIKeyHeader = Depends(APIKey.verify_system_api_key),
    device_id: str | None = Query(None, description="Device ID for deterministic API key generation")
):
    service = UserService(db)
    if device_id and await service.is_existing_user(device_id):
        return user_to_pydantic(await service.get_user_by_device_id(device_id))
    
    new_user = await service.create_user(device_id)
    user_logger.info("Created new user")
    return user_to_pydantic(new_user)


@router.put("/users", description="Update user in database")
async def update_user(
    update_data: UserUpdate, 
    db: AsyncSession = Depends(get_async_db), 
    user: UserTable = Depends(APIKey.verify_user_api_key)
):
    await UserService(db).update_user(user, update_data)
    return {"message": "User updated successfully"}


@router.delete("/users", description="Delete user from database")
async def delete_user(
    db: AsyncSession = Depends(get_async_db), 
    user: UserTable = Depends(APIKey.verify_user_api_key)
):
    await UserService(db).delete_user(user)
    return {"message": "User deleted successfully"}
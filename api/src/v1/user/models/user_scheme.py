import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field

from shared.src.tables.user_table import UserTable


class User(BaseModel):
    id: uuid.UUID
    api_key: str
    device_id: str | None
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    email: Optional[EmailStr] = None
    password: Optional[str] = Field(None, min_length=8)
    created_at: datetime
    updated_at: datetime

    @staticmethod
    def from_table(user: UserTable) -> "User":
        return User(
            id=user.id,
            device_id=user.device_id,
            name=user.name,
            email=user.email,
            password=user.password,
            api_key=user.api_key,
            created_at=user.created_at,
            updated_at=user.updated_at,
        )


# class UserCreate(BaseModel):
#     device_id: str
#     name: Optional[str] = Field(None, min_length=1, max_length=100)
#     email: Optional[EmailStr] = None
#     password: Optional[str] = Field(None, min_length=8)


class UserUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    email: Optional[EmailStr] = None
    password: Optional[str] = Field(None, min_length=8)

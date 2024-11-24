import uuid
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field


class User(BaseModel):
    id: uuid.UUID
    device_id: str
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    email: Optional[EmailStr] = None
    password: Optional[str] = Field(None, min_length=8)
    api_key: str
    created_at: datetime
    updated_at: datetime


# class UserCreate(BaseModel):
#     device_id: str
#     name: Optional[str] = Field(None, min_length=1, max_length=100)
#     email: Optional[EmailStr] = None
#     password: Optional[str] = Field(None, min_length=8)


class UserUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    email: Optional[EmailStr] = None
    password: Optional[str] = Field(None, min_length=8)

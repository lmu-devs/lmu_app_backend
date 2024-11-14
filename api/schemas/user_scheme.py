import uuid

from datetime import datetime
from pydantic import BaseModel


class User(BaseModel):
    id: uuid.UUID
    device_id: str
    name: str | None
    email: str | None
    password: str | None
    api_key: str
    creation_date: datetime
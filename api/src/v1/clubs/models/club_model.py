from typing import Optional

from pydantic import BaseModel


class Club(BaseModel):
    id: str
    university_id: Optional[str] = None
    type: str
    logo_url: Optional[str] = None
    title: str
    description: str
    content: Optional[str] = None
    url: Optional[str] = None
    email: Optional[str] = None
    instagram_url: Optional[str] = None
    linkedin_url: Optional[str] = None
    is_shown: bool = False
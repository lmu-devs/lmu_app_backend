from pydantic import BaseModel


class Club(BaseModel):
    id: str
    university_id: str | None = None
    type: str
    logo_url: str | None = None
    title: str
    description: str
    content: str | None = None
    url: str | None = None
    email: str | None = None
    instagram_url: str | None = None
    linkedin_url: str | None = None
    category: str

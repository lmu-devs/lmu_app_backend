from pydantic import BaseModel


class CinemaDescription(BaseModel):
    emoji: str
    description: str

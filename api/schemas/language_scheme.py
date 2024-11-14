from pydantic import BaseModel

class Language(BaseModel):
    country_code: str
    flag_emoji: str
    written: float
from pydantic import BaseModel


class LabelTextDto(BaseModel):
    DE: str
    EN: str

class LabelDto(BaseModel):
    enum_name: str
    text: LabelTextDto
    emoji_abbreviation: str | None
    text_abbreviation: str | None

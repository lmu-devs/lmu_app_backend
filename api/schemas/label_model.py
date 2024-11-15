from pydantic import BaseModel


class LabelText(BaseModel):
    DE: str
    EN: str

class Label(BaseModel):
    enum_name: str
    text: LabelText
    emoji_abbreviation: str | None
    text_abbreviation: str | None

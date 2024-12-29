from pydantic import BaseModel

class Image(BaseModel):
    url: str
    name: str
    blurhash: str | None = None
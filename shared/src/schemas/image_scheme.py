from typing import List
from pydantic import BaseModel, RootModel

class Image(BaseModel):
    url: str
    name: str
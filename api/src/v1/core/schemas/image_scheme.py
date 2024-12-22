from typing import List
from pydantic import BaseModel

class Image(BaseModel):
    url: str
    name: str
    
class Images(BaseModel):
    images: List[Image]


from typing import List
from pydantic import BaseModel, RootModel

class Person(BaseModel):
    id: str
    first_name: str
    last_name: str
    role: str
    email: str | None = None

class People(RootModel):
    root: List[Person] | list = []
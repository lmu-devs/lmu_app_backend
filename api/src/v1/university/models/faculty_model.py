from typing import List
from pydantic import BaseModel, RootModel


class Faculty(BaseModel):
    id: int
    title: str


class Faculties(RootModel):
    root: List[Faculty] | list = []

from typing import List
from pydantic import BaseModel

class Link(BaseModel):
    title: str
    url: str

class Home(BaseModel):
    submissionFee: str
    lectureFreeTime: str
    lectureTime: str
    links: List[Link]
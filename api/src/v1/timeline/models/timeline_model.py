from typing import List

from pydantic import BaseModel

from .event_model import Event
from .semester_model import Semester


class Timeline(BaseModel):
    semesters: List[Semester]
    events: List[Event] 
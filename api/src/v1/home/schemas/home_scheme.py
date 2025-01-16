from pydantic import BaseModel
from datetime import datetime

class Link(BaseModel):
    title: str
    url: str
    
class TimePeriod(BaseModel):
    start_date: datetime
    end_date: datetime
    
class SemesterFee(BaseModel):
    fee: float
    time_period: TimePeriod
    iban: str
    bic: str
    reference: str
    receiver: str

class Home(BaseModel):
    semester_fee: SemesterFee
    lecture_free_time: TimePeriod
    lecture_time: TimePeriod
    links: list[Link]
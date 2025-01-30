from pydantic import BaseModel
from datetime import datetime

class Timeframe(BaseModel):
    start: datetime
    end: datetime
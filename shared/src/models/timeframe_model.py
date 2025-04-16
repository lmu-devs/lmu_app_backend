from datetime import datetime

from pydantic import BaseModel


class Timeframe(BaseModel):
    start: datetime
    end: datetime

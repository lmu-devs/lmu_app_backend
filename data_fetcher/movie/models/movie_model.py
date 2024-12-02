from datetime import datetime

class LmuMovie:
    def __init__(self, date: datetime, title: str, aka_name: str | None, year: int | None):
        self.date = date
        self.title = title
        self.aka_name = aka_name
        self.year = year
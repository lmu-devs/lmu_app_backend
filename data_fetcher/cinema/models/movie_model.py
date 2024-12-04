from datetime import datetime


class ScreeningCrawl:
    def __init__(
        self, 
        date: datetime, 
        title: str, 
        address: str,     
        longitude: float,   
        latitude: float,   
        is_ov:          bool    | None = None, # OV = Original Version
        aka_name:       str     | None = None, 
        year:           int     | None = None,
        external_link:  str     | None = None,
        booking_link:   str     | None = None,
        price:          float   | None = None, # 0 when "Free Entrance"
        university_id:  str     | None = None,
        subtitles:      str     | None = None # OmdU = Original German with Subtitles, OmeU = Original English with Subtitles, OmU = Original Multilingual with Subtitles
        
    ):
        self.date = date
        self.title = title
        self.aka_name = aka_name
        self.year = year
        self.external_link = external_link
        self.ticket_link = booking_link
        self.price = price
        self.address = address
        self.longitude = longitude
        self.latitude = latitude
        self.university_id = university_id
        self.is_ov = is_ov
        self.subtitles = subtitles

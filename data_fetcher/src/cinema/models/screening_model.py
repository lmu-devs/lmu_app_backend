from datetime import datetime


class ScreeningCrawl:
    def __init__(
        self,
        is_edge_case: bool,
        date: datetime,
        title: str,
        address: str,
        longitude: float | None = None,
        latitude: float | None = None,
        year: int | None = None,
        tagline: str | None = None,
        overview: str | None = None,
        is_ov: bool | None = None,  # OV = Original Version
        aka_name: str | None = None,
        price: float | None = None,  # 0 when "Free Entrance"
        cinema_id: str | None = None,
        university_id: str | None = None,
        subtitles: (
            str | None
        ) = None,  # OmdU = Original German with Subtitles, OmeU = Original English with Subtitles, OmU = Original Multilingual with Subtitles
        external_url: str | None = None,
        booking_url: str | None = None,
        runtime: int | None = None,
        note: str | None = None,
        custom_poster_url: str | None = None,
    ):
        self.is_edge_case = is_edge_case
        self.date = date
        self.title = title
        self.aka_name = aka_name
        self.year = year
        self.tagline = tagline
        self.overview = overview
        self.price = price
        self.address = address
        self.longitude = longitude
        self.latitude = latitude
        self.cinema_id = cinema_id
        self.university_id = university_id
        self.is_ov = is_ov
        self.subtitles = subtitles
        self.external_url = external_url
        self.booking_url = booking_url
        self.custom_poster_url = custom_poster_url
        self.runtime = runtime
        self.note = note

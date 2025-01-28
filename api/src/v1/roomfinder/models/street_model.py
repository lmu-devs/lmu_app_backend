from pydantic import BaseModel

from shared.src.tables.roomfinder.street_table import StreetTable

from data_fetcher.src.roomfinder.models.city_model import City


class Street(BaseModel):
    code: str
    name: str
    city: City

    @classmethod
    def from_db(cls, data: StreetTable) -> "Street":
        return cls(**data)

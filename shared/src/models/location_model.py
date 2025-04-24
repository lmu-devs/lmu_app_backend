from pydantic import BaseModel, RootModel

from shared.src.tables import LocationTable


class Location(BaseModel):
    address: str
    latitude: float | None
    longitude: float | None

    @classmethod
    def from_table(cls, location: LocationTable) -> "Location":
        return Location(
            address=location.address,
            latitude=location.latitude,
            longitude=location.longitude,
        )


class Locations(RootModel):
    root: list[Location]

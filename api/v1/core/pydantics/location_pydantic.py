from shared.tables import LocationTable

from ..schemas import Location


def location_to_pydantic(location: LocationTable) -> Location:
    return Location(
        address=location.address,
        latitude=location.latitude,
        longitude=location.longitude
    )
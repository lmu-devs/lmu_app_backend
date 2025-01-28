from shared.src.tables import LocationTable

from shared.src.models import Location


def location_to_pydantic(location: LocationTable) -> Location:
    return Location(
        address=location.address,
        latitude=location.latitude,
        longitude=location.longitude
    )
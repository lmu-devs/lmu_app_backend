import time
from typing import Optional

from geopy.exc import GeocoderServiceError, GeocoderTimedOut
from geopy.geocoders import Nominatim

from shared.src.core.logging import get_service_logger
from shared.src.models.location_model import Location

logger = get_service_logger(__name__)


class GeocodingService:
    """Service for converting addresses to coordinates using Nominatim."""

    def __init__(self, user_agent: str = "LMUAppGeocoder/1.0"):
        """Initialize the geocoding service with Nominatim."""
        self.geolocator = Nominatim(user_agent=user_agent)

    def get_location(self, address: str, retries: int = 2) -> Optional[Location]:
        """
        Convert an address to a Location model with coordinates.

        Args:
            address: The address to geocode
            retries: Number of retries on failure

        Returns:
            Location model with coordinates if successful, None otherwise
        """
        if not address:
            return None

        for attempt in range(retries):
            try:
                logger.debug(f"Geocoding attempt {attempt + 1}/{retries} for: {address}")
                location = self.geolocator.geocode(address, timeout=10)

                if location:
                    logger.debug(f"Geocoded successfully: {location.latitude}, {location.longitude}")
                    return Location(
                        address=address,
                        latitude=location.latitude,
                        longitude=location.longitude,
                    )

                # If geocode returns None, it means not found
                logger.warning(f"Could not geocode address: {address}")
                return None

            except GeocoderTimedOut:
                logger.warning(f"Geocoding timed out for address: {address}. Retrying ({attempt + 1}/{retries})...")
                time.sleep(2 + attempt)  # Exponential backoff slightly
            except GeocoderServiceError as e:
                logger.error(f"Geocoding service error for {address}: {str(e)}. Retrying ({attempt + 1}/{retries})...")
                time.sleep(3 + attempt)
            except Exception as e:
                logger.error(f"Unexpected error geocoding address {address}: {str(e)}")
                return None  # Don't retry on unexpected errors

        logger.error(f"Could not geocode address after {retries} attempts: {address}")
        return None

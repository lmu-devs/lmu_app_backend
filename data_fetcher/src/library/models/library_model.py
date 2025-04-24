from enum import Enum
from typing import Dict, List, Optional, Union

from pydantic import BaseModel


class CityEnum(Enum):
    MUENCHEN = "München"
    PLANEGG_MARTINSRIED = "Planegg-Martinsried"  # Combine as it often appears together
    GAIMERSHEIM = "Gaimersheim"  # Add any other cities encountered
    FUERSTENFELDBRUCK = "Fürstenfeldbruck"
    GARCHING = "Garching"
    OBERSCHLEISSHEIM = "Oberschleißheim"
    # Add more cities as needed

    @classmethod
    def from_string(cls, city_string: str) -> Optional["CityEnum"]:
        """
        Case-insensitive matching for city strings with fuzzy matching capabilities.
        Handles partial matches to find the most fitting enum.
        """
        if not city_string:
            return None

        city_string_lower = city_string.strip().lower()

        # First try exact match
        for city_enum in cls:
            if city_enum.value.lower() == city_string_lower:
                return city_enum

        # Handle special cases
        if "planegg" in city_string_lower or "martinsried" in city_string_lower:
            return cls.PLANEGG_MARTINSRIED

        # If no exact match, try prefix matching (find the most fitting enum)
        # For "München 00.23a" -> match with "München"
        best_match = None
        best_match_length = 0

        for city_enum in cls:
            enum_value_lower = city_enum.value.lower()
            # Check if enum_value is a prefix of city_string
            if city_string_lower.startswith(enum_value_lower):
                if len(enum_value_lower) > best_match_length:
                    best_match = city_enum
                    best_match_length = len(enum_value_lower)
            # Check if city_string is a prefix of enum_value
            elif enum_value_lower.startswith(city_string_lower):
                if len(city_string_lower) > best_match_length:
                    best_match = city_enum
                    best_match_length = len(city_string_lower)

        # Return best match if found
        if best_match:
            return best_match

        # Still no match found, try word-by-word matching
        # For cases like "München Something Else"
        for city_enum in cls:
            enum_value_lower = city_enum.value.lower()
            city_words = city_string_lower.split()
            # Check if any enum value is a complete word within the city string
            for word in city_words:
                if word == enum_value_lower or enum_value_lower.startswith(word + " "):
                    return city_enum

        # No match found
        return None


class DaySchedule(BaseModel):
    days: List[str]
    times: List[Dict[str, str]]


class Address(BaseModel):
    street: Optional[str] = None
    house_number: Optional[str] = None
    postal_code: Optional[str] = None
    city: Optional[CityEnum] = None  # Use the Enum type
    room: Optional[str] = None
    full_address: Optional[str] = None
    coordinates: Optional[tuple[float, float]] = None


class ContactInfo(BaseModel):
    address: Optional[Address] = None
    email: Optional[List[str]] = None
    phone: Optional[Dict[str, Union[str, List[str]]]] = None
    fax: Optional[str] = None
    website: Optional[str] = None


class OpeningHours(BaseModel):
    semester: Optional[List[DaySchedule]] = None
    semester_break: Optional[List[DaySchedule]] = None
    notes: Optional[str] = None
    raw_text: Optional[str] = None


class Library(BaseModel):
    name: str
    location_number: List[str]
    url: str
    details: Optional[Dict[str, Union[str, Dict, List]]] = None
    contact: Optional[ContactInfo] = None
    opening_hours: Optional[OpeningHours] = None
    services: Optional[List[str]] = []
    subject_areas: Optional[List[str]] = []
    transportation: Optional[str] = None
    notes: Optional[str] = None

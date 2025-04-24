# Add this to publictransport/models/mvv_models.py

import re  # Needed for validator in model
from typing import Optional

from pydantic import BaseModel, Field, ValidationError, validator

# ... (keep existing imports and MvvLine model) ...


class MvvStop(BaseModel):
    """
    Pydantic model representing a single MVV stop (Haltestelle).
    """

    hst_nummer: int = Field(..., alias="HstNummer")
    name_ohne_ort: str = Field(..., alias="Name ohne Ort")
    ort: str = Field(..., alias="Ort")
    globale_id: str = Field(..., alias="Globale ID")
    longitude: float = Field(..., alias="WGS84 X")  # Assuming X is Longitude
    latitude: float = Field(..., alias="WGS84 Y")  # Assuming Y is Latitude
    # Add other fields from CSV if needed, e.g., 'Nummer TBN', 'Gemeinde Code', etc.

    class Config:
        allow_population_by_field_name = True  # Allows using original CSV headers directly if needed
        anystr_strip_whitespace = True

    # Add these validators to handle comma decimals BEFORE standard validation
    @validator("latitude", "longitude", pre=True)
    def replace_comma_with_period(cls, value):
        if isinstance(value, str):
            return value.replace(",", ".", 1)  # Replace first comma with period
        return value  # Return original value if not a string

    @validator("globale_id")
    def check_globale_id_format(cls, v):
        # Example validation: Ensure it follows the 'de:XXXXX:YYYY' pattern
        if not re.match(r"^(de|at):\d+:\w+$", v):  # Allow 'at:' prefix now
            # Log a warning instead of raising an error, as format might vary
            # Use logger if configured, otherwise print
            print(f"Warning: Globale ID '{v}' does not match expected 'de:' or 'at:' prefix pattern.")
            # raise ValueError("Globale ID must follow the format 'de:XXXXX:YYYY'")
        return v

    # Keep existing lat/lon range validators (they run AFTER pre-validator)
    @validator("latitude")
    def check_latitude_range(cls, v):
        # This validator now receives a float after pre-validator runs
        if not -90 <= v <= 90:
            raise ValueError("Latitude must be between -90 and 90")
        return v

    @validator("longitude")
    def check_longitude_range(cls, v):
        # This validator now receives a float after pre-validator runs
        if not -180 <= v <= 180:
            raise ValueError("Longitude must be between -180 and 180")
        return v

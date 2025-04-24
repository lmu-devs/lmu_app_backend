from pydantic import BaseModel, Field
from typing import Optional

class MvvLine(BaseModel):
    """Represents a single MVV public transport line."""
    liniennr_efa: str = Field(..., description="The unique identifier for the line (e.g., 'U1', '50', '211V').")
    verkehrsmittel: str = Field(..., description="The type of transport (e.g., 'U-Bahn', 'MetroBus', 'RegionalBus').")
    branch_nr: str = Field(..., description="Branch number, used in constructing image URLs.")
    image_url: Optional[str] = Field(None, description="The URL to the line icon SVG on the MVV website.")
    fallback_svg: Optional[str] = Field(None, description="A fallback SVG generated if the URL pattern doesn't match or isn't applicable.")
    # Add any other relevant fields from the CSV if needed 
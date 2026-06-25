from typing import Any, Dict, Optional

def map_directus_location(address: Optional[str], raw_location: Any) -> Optional[Dict[str, Any]]:
    """
    Transforms Directus address and GeoJSON location into the shared Location schema.
    Returns None (null) if either the address or the location is missing/invalid.
    """
    
    if not address or not raw_location:
        return None

    clean_address = address.strip()
    if not clean_address:
        return None

    if isinstance(raw_location, dict) and raw_location.get("type") == "Point":
        coords = raw_location.get("coordinates")
        
        if isinstance(coords, list) and len(coords) == 2:
            return {
                "address": clean_address,
                "latitude": float(coords[1]),
                "longitude": float(coords[0]),
            }

    return None

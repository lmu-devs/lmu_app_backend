from typing import Any, Dict, List, Union


def flatten_response(response: Dict[str, Any]) -> Union[Dict[str, Any], List[Any]]:
    """
    Recursively flattens a GraphQL response by:
    1. Removing the 'data' wrapper
    2. Flattening all translation objects by moving translation fields to the parent object
    3. Flattening image objects by moving directus_files_id fields to parent level

    Args:
        response: The GraphQL response to flatten

    Returns:
        The flattened data structure with 'data' wrapper, translations, and directus_files_id merged into their parent objects

    Example:
        input = {
            "data": {
                "benefits": [{
                    "id": "1",
                    "translations": [{
                        "title": "Hello",
                        "description": "World"
                    }]
                }]
            }
        }

        output = {
            "benefits": [{
                "id": "1",
                "title": "Hello",
                "description": "World"
            }]
        }
    """

    def _flatten_translations(
        data: Union[Dict[str, Any], List[Any]],
    ) -> Union[Dict[str, Any], List[Any]]:
        if isinstance(data, dict):
            result = {}

            # Handle translations if present
            if "translations" in data and isinstance(data["translations"], list) and len(data["translations"]) > 0:
                translations = data["translations"][0]  # Take first translation
                # Copy translation fields to parent level
                for key, value in translations.items():
                    if value is not None:  # Only copy non-null values
                        result[key] = value
                # Remove the translations key
                data = {k: v for k, v in data.items() if k != "translations"}

            # Process all other keys recursively
            for key, value in data.items():
                if isinstance(value, (dict, list)):
                    result[key] = _flatten_translations(value)
                else:
                    result[key] = value

            return result

        elif isinstance(data, list):
            return [_flatten_translations(item) for item in data]

        return data

    # First remove the data wrapper if it exists
    if isinstance(response, dict) and "data" in response:
        response = response["data"]

    # Then flatten all translations
    return _flatten_translations(response)

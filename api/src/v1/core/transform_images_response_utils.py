from typing import Any, Dict, List, Union

from shared.src.core.settings import get_settings


def transform_images_response(
    response: Dict[str, Any],
) -> Union[Dict[str, Any], List[Any]]:
    """
    Recursively transforms a GraphQL response by:
    1. Removing the 'data' wrapper
    2. Flattening all translation objects by moving translation fields to the parent object
    3. Flattening image objects by moving directus_files_id fields to parent level
    4. Converting image IDs to full URLs with the correct base URL

    Args:
        response: The GraphQL response to transform

    Returns:
        The transformed data structure with image IDs converted to URLs and other flattening

    Example:
        input = {
            "data": {
                "benefits": [{
                    "images": [{
                        "directus_files_id": {
                            "id": "123e4567-e89b-12d3-a456-426614174000",
                            "title": "My Image"
                        }
                    }],
                    "translations": [{
                        "title": "Hello",
                        "description": "World"
                    }]
                }]
            }
        }

        output = {
            "benefits": [{
                "title": "Hello",
                "description": "World",
                "images": [{
                    "id": "123e4567-e89b-12d3-a456-426614174000",
                    "title": "My Image",
                    "url": "https://cms.lmu-dev.org/assets/123e4567-e89b-12d3-a456-426614174000"
                }]
            }]
        }
    """
    settings = get_settings()
    base_url = settings.DIRECTUS_BASE_URL.rstrip("/")

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

    def _transform_images(
        data: Union[Dict[str, Any], List[Any]],
    ) -> Union[Dict[str, Any], List[Any]]:
        if isinstance(data, dict):
            result = {}

            # Handle directus_files_id if present
            if "directus_files_id" in data and isinstance(data["directus_files_id"], dict):
                # Copy directus_files_id fields to parent level
                for key, value in data["directus_files_id"].items():
                    if value is not None:  # Only copy non-null values
                        result[key] = value

                # Add URL for the image
                if "id" in result:
                    result["url"] = f"{base_url}/assets/{result['id']}"
                    result["blurhash"] = None
                    # Remove ID after creating URL
                    del result["id"]

                # Remove the directus_files_id key
                data = {k: v for k, v in data.items() if k != "directus_files_id"}

            # Process all other keys recursively
            for key, value in data.items():
                if key == "images" and isinstance(value, list):
                    # Process images list specially
                    result[key] = [_transform_images(img) for img in value]
                elif key == "image" and isinstance(value, dict):
                    # Process single image object
                    if value is None:
                        result[key] = None
                    else:
                        transformed_image = _transform_images(value)
                        # Add URL if there's an ID but no URL yet
                        if "id" in transformed_image and "url" not in transformed_image:
                            transformed_image["url"] = f"{base_url}/assets/{transformed_image['id']}"
                            transformed_image["blurhash"] = None
                        result[key] = transformed_image
                elif isinstance(value, (dict, list)):
                    result[key] = _transform_images(value)
                else:
                    result[key] = value

            return result

        elif isinstance(data, list):
            return [_transform_images(item) for item in data]

        return data

    # First remove the data wrapper if it exists
    if isinstance(response, dict) and "data" in response:
        response = response["data"]

    # Then flatten all translations
    flattened_translations = _flatten_translations(response)

    # Then transform all image objects
    return _transform_images(flattened_translations)

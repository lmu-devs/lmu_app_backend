from typing import Any, List
from uuid import UUID

from shared.src.core.settings import get_settings
from shared.src.models.image_model import Image, Images


def transform_directus_files_to_images(
    files: List[Any],
    file_id_attr: str = "directus_files_id",
    name_prefix: str = "image",
) -> Images:
    """
    Transform SQL table records with directus_files_id to Images model.

    This is a general utility that can be used across different entities that have
    files stored in directus. It converts file records to properly formatted Image objects
    with URLs, empty blurhash, and generic names.

    Args:
        files: List of table records that have directus_files_id field
        file_id_attr: Name of the attribute containing the directus file UUID (default: "directus_files_id")
        name_prefix: Prefix for generated image names (default: "image")

    Returns:
        Images model containing transformed Image objects

    Example:
        # For library files
        images = transform_directus_files_to_images(
            library.files,
            name_prefix="library_image"
        )

        # For canteen files
        images = transform_directus_files_to_images(
            canteen.files,
            name_prefix="canteen_image"
        )
    """
    if not files:
        return Images(root=[])

    settings = get_settings()
    base_url = settings.DIRECTUS_EXTERNAL_URL.rstrip("/")

    image_list = []
    for file in files:
        # Get the directus file ID from the specified attribute
        directus_file_id = getattr(file, file_id_attr, None)

        if directus_file_id:
            # Ensure it's a UUID (handle both string and UUID types)
            file_id_str = str(directus_file_id)

            # Create URL from directus file ID
            url = f"{base_url}/assets/{file_id_str}"

            # Create image with empty blurhash and generic name
            image = Image.from_params(url=url, name=f"{name_prefix}_{file.id}", blurhash=None)
            image_list.append(image)

    return Images(root=image_list)


def transform_library_files_to_images(files: List[Any]) -> Images:
    """
    Convenience function specifically for library files.

    Args:
        files: List of LibraryFilesTable records

    Returns:
        Images model containing transformed library images
    """
    return transform_directus_files_to_images(files, name_prefix="library_image")

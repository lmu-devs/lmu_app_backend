from typing import List

from shared.src.schemas import Image
from shared.src.tables import ImageTable


def image_to_pydantic(url: str, name: str) -> Image:
    return Image(
        url=url,
        name=name
    )


def image_table_to_pydantic(image: ImageTable) -> Image:
    return Image(
        url=image.url,
        name=image.name
    )
    
def images_table_to_pydantic(images: ImageTable) -> List[Image]:
    return [image_table_to_pydantic(image) for image in images]
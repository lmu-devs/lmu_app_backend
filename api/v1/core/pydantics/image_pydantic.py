from api.v1.core import Image

def image_to_pydantic(image: str, name: str) -> Image:
    return Image(
        url=image,
        name=name
    )
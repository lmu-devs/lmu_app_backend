from shared.src.schemas import Image

def image_to_pydantic(image: str, name: str) -> Image:
    return Image(
        url=image,
        name=name
    )
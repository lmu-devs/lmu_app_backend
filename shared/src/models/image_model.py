from typing import List

from pydantic import BaseModel, RootModel

from shared.src.tables import ImageTable


class Image(BaseModel):
    url: str
    name: str
    blurhash: str | None = None

    @classmethod
    def from_table(cls, image: ImageTable) -> "Image":
        return Image(
            url=image.url,
            name=image.name,
            blurhash=image.blurhash if image.blurhash else None,
        )

    @classmethod
    def from_params(cls, url: str, name: str, blurhash: str | None = None) -> "Image":
        return Image(
            url=url,
            name=name,
            blurhash=blurhash,
        )


class Images(RootModel):
    root: List[Image]

    @classmethod
    def from_table(cls, images: ImageTable) -> "Images":
        return Images(root=[Image.from_table(image) for image in images])

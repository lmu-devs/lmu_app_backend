from typing import Dict, List

from pydantic import BaseModel, RootModel

from shared.src.core.settings import get_settings


class Image(BaseModel):
    url: str
    title: str

    @classmethod
    def from_params(cls, url: str, title: str) -> "Image":
        return Image(
            url=url,
            title=title,
        )

    @classmethod
    def from_directus(cls, image: Dict) -> "Image":
        return Image(
            url=f"{get_settings().DIRECTUS_BASE_URL}/assets/{image.get('id')}",
            title=image.get("title"),
        )


class Images(RootModel):
    root: List[Image]

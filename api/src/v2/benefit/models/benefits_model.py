from typing import List

from pydantic import BaseModel, RootModel

from api.src.v2.core.models.image_model import Image


class Benefit(BaseModel):
    id: str
    title: str
    description: str
    url: str
    favicon_url: str | None = None
    image: Image | None = None
    # types: List = []
    # faculties: List = []
    # aliases: List[str] = []


class Benefits(RootModel):
    root: List[Benefit]


class BenefitType(BaseModel):
    id: str
    title: str
    description: str | None = None
    emoji: str
    benefit_ids: List[str]


class BenefitTypes(RootModel):
    root: List[BenefitType]


class BenefitResponse(BaseModel):
    benefit_types: BenefitTypes
    benefits: Benefits

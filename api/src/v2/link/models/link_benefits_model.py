from typing import List

from pydantic import BaseModel, RootModel

from api.src.v2.core.models.image_model import Image


class LinkBenefit(BaseModel):
    id: str
    title: str
    description: str
    url: str
    favicon_url: str | None = None
    image: Image | None = None
    # types: List = []
    # faculties: List = []
    # aliases: List[str] = []


class LinkBenefits(RootModel):
    root: List[LinkBenefit]


class LinkBenefitType(BaseModel):
    id: str
    title: str
    description: str | None = None
    emoji: str
    benefit_ids: List[str]


class LinkBenefitTypes(RootModel):
    root: List[LinkBenefitType]


class LinkBenefitResponse(BaseModel):
    benefit_types: LinkBenefitTypes
    benefits: LinkBenefits

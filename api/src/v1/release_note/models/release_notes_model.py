from typing import List

from pydantic import BaseModel


class ReleaseNoteHighlight(BaseModel):
    emoji: str
    title: str
    description: str


class ReleaseNoteDetail(BaseModel):
    title: str


class ReleaseNoteResponse(BaseModel):
    highlights: List[ReleaseNoteHighlight] | None = None
    details: List[ReleaseNoteDetail] | None = None
    show_privacy_policy: bool | None = None

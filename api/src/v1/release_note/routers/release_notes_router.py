from fastapi import APIRouter, Depends
from fastapi.params import Query

from api.src.v1.core.language import get_language
from api.src.v1.release_note.models.release_notes_model import ReleaseNoteResponse
from api.src.v1.release_note.services.release_notes_service import ReleaseNoteService
from shared.src.enums.language_enums import LanguageEnum

router = APIRouter()


@router.get(
    "/release-notes",
    response_model=ReleaseNoteResponse,
    description="Get all release notes",
)
async def get_all_resources(
    version: str = Query(..., description="The version of the feature flag"),
    language: LanguageEnum = Depends(get_language),
):
    release_note_service = ReleaseNoteService(version, language)
    release_note = await release_note_service.get_release_note()
    return release_note

from pathlib import Path

from api.src.v1.core.flatten_response_util import flatten_response
from api.src.v1.release_note.models.release_notes_model import ReleaseNoteResponse
from shared.src.core.settings import get_settings
from shared.src.services.directus_service import DirectusService


class ReleaseNoteService:
    def __init__(self, version: str, language_code: str):
        self.version = version
        self.language_code = language_code
        self.settings = get_settings()
        self.directus = DirectusService()

    async def get_release_note(self) -> ReleaseNoteResponse:
        try:
            query_path = Path(__file__).parent.parent / "graphql" / "release_notes_query.graphql"
            response = self.directus.execute_query_file(
                query_file_path=query_path,
                variables={"languageCode": self.language_code, "version": self.version},
            )

            release_note = flatten_response(response)
            print(release_note)
            if "release_notes" not in release_note or not release_note["release_notes"]:
                return ReleaseNoteResponse(highlights=None, details=None)

            release_note = release_note["release_notes"][0]
            return ReleaseNoteResponse(**release_note)
        except Exception as e:
            raise e

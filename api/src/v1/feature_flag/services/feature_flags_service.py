from pathlib import Path
from typing import List

from packaging import version

from api.src.v1.feature_flag.models.feature_flags_model import FeatureFlagResponse
from shared.src.core.settings import get_settings
from shared.src.services.directus_service import DirectusService


class FeatureFlagService:
    def __init__(self, version: str):
        self.version = version
        self.settings = get_settings()
        self.directus = DirectusService()

    def _is_version_enabled(self, feature_flag_version: str) -> bool:
        try:
            current_version = version.parse(self.version)
            flag_version = version.parse(feature_flag_version)
            return current_version >= flag_version
        except version.InvalidVersion:
            return False

    async def get_feature_flags(self) -> List[FeatureFlagResponse]:
        try:
            query_path = Path(__file__).parent.parent / "graphql" / "feature_flags_query.graphql"
            response = self.directus.execute_query_file(
                query_file_path=query_path,
            )

            # Get feature flags from the nested data structure
            feature_flags_data = response.get("data", {}).get("feature_flags", [])

            return [
                FeatureFlagResponse(id=flag["id"], enabled=self._is_version_enabled(flag["version"]))
                for flag in feature_flags_data
            ]
        except Exception as e:
            raise e

from pydantic import BaseModel


class FeatureFlagResponse(BaseModel):
    id: str
    enabled: bool

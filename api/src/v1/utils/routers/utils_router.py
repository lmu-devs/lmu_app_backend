from fastapi import APIRouter
from shared.src.services.favicon_service import FaviconService
from shared.src.services.alias_generation_service import AliasGenerationService

router = APIRouter()

favicon_service = FaviconService()
alias_service = AliasGenerationService()

@router.get("/favicon", description="Get favicon URL for a given website URL")
async def get_favicon(url: str):
    return {"favicon_url": favicon_service.get_favicon_url(url)}

@router.post("/aliases", description="Generate aliases for a given title and description")
async def generate_aliases(title: str, description: str = ""):
    result = alias_service.generate_alias(title, description)
    return {"aliases": result.aliases} 
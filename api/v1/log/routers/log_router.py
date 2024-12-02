import os
from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.responses import FileResponse

from api.v1.core import APIKey
from shared.core.exceptions import ConfigurationError
from shared.core.logging import get_food_api_logger

from ..services.log_service import LogService

router = APIRouter()
logger = get_food_api_logger(__name__)


@router.get("/logs", 
    response_class=FileResponse,
    description="Get all logs as a compressed zip file. Requires system API key.")
async def get_logs(
    authorized: Annotated[bool, Depends(APIKey.verify_admin_api_key)]
):
    """Endpoint to retrieve compressed log files."""
    try:
        log_service = LogService()
        zip_path = log_service.create_log_archive()
        
        logger.info("Sending compressed log files")
        return FileResponse(
            path=zip_path,
            filename=os.path.basename(zip_path),
            media_type='application/zip'
        )
    except Exception as e:
        logger.error(f"Error while creating log archive: {str(e)}")
        raise ConfigurationError(
            detail="Failed to create log archive",
            extra={"error": str(e)}
        )

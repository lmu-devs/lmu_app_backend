import logging
from typing import Union, Any, Dict
from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError

from shared.core.exceptions import BaseException, APIException

logger = logging.getLogger(__name__)

def create_error_response(error_code: str, message: str, extra: Dict[str, Any] = None) -> Dict:
    return {
        "error": {
            "code": error_code,
            "message": message,
            "extra": extra or {}
        }
    }

def handle_error(exc: Exception) -> Dict:
    if isinstance(exc, (BaseException, APIException)):
        return create_error_response(
            error_code=exc.error_code,
            message=exc.detail,
            extra=exc.extra
        )
    
    if isinstance(exc, SQLAlchemyError):
        logger.error(f"Database error: {str(exc)}")
        return create_error_response(
            error_code="DATABASE_ERROR",
            message="A database error occurred"
        )

    # Log unexpected errors
    logger.error(f"Unexpected error: {str(exc)}", exc_info=True)
    return create_error_response(
        error_code="INTERNAL_SERVER_ERROR",
        message="An unexpected error occurred"
    )

# FastAPI specific handler
async def api_error_handler(request: Any, exc: Union[Exception, APIException]) -> JSONResponse:
    error_response = handle_error(exc)
    status_code = exc.status_code if isinstance(exc, APIException) else 500
    return JSONResponse(
        status_code=status_code,
        content=error_response
    ) 
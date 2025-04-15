from typing import Any, Dict, Union

from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError

from .exceptions import APIException, BaseException


def create_error_response(error_code: str, message: str, extra: Dict[str, Any] = None) -> Dict:
    return {"error": {"code": error_code, "message": message, "extra": extra or {}}}


def handle_error(exc: Exception, context: str = "API") -> Dict:
    if isinstance(exc, (BaseException, APIException)):
        return create_error_response(error_code=exc.error_code, message=exc.detail, extra=exc.extra)

    if isinstance(exc, SQLAlchemyError):
        return create_error_response(error_code="DATABASE_ERROR", message="A database error occurred")

    return create_error_response(error_code="INTERNAL_SERVER_ERROR", message="An unexpected error occurred")


# FastAPI specific handler
async def api_error_handler(request: Any, exc: Union[Exception, APIException]) -> JSONResponse:
    if isinstance(exc, APIException):
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "detail": str(exc.detail),
                "code": str(exc.error_code),
                "extra": {k: str(v) for k, v in (exc.extra or {}).items()},
            },
        )

    error_response = handle_error(exc, context="API")
    return JSONResponse(
        status_code=500,
        content=(error_response),
    )

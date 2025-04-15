from typing import Any, Dict, Optional

from fastapi import HTTPException, status


class BaseException(Exception):
    def __init__(self, detail: str, error_code: str, extra: Optional[Dict[str, Any]] = None):
        super().__init__(detail)
        self.detail = detail
        self.error_code = error_code
        self.extra = extra or {}


class APIException(HTTPException):
    def __init__(
        self,
        status_code: int,
        detail: str,
        error_code: str,
        extra: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(status_code=status_code, detail=detail)
        self.error_code = error_code
        self.extra = extra or {}


# API Specific Exceptions
class NotFoundError(APIException):
    def __init__(self, detail: str, extra: Optional[Dict[str, Any]] = None):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=detail,
            error_code="NOT_FOUND",
            extra=extra,
        )


class AuthorizationError(APIException):
    def __init__(self, detail: str, extra: Optional[Dict[str, Any]] = None):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=detail,
            error_code="AUTHORIZATION_ERROR",
            extra=extra,
        )


class AuthenticationError(APIException):
    def __init__(self, detail: str, extra: Optional[Dict[str, Any]] = None):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
            error_code="AUTHENTICATION_ERROR",
            extra=extra,
        )


class RateLimitError(APIException):
    def __init__(self, detail: str, extra: Optional[Dict[str, Any]] = None):
        super().__init__(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=detail,
            error_code="RATE_LIMIT_ERROR",
            extra=extra,
        )


# Shared Exceptions
class DatabaseError(BaseException):
    def __init__(
        self,
        detail: str = "Database error occurred",
        extra: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(detail=detail, error_code="DATABASE_ERROR", extra=extra)


class DataFetchError(BaseException):
    def __init__(self, detail: str, extra: Optional[Dict[str, Any]] = None):
        super().__init__(detail=detail, error_code="DATA_FETCH_ERROR", extra=extra)


class ValidationError(BaseException):
    def __init__(self, detail: str, extra: Optional[Dict[str, Any]] = None):
        super().__init__(detail=detail, error_code="VALIDATION_ERROR", extra=extra)


class ExternalAPIError(BaseException):
    def __init__(self, detail: str, service: str, extra: Optional[Dict[str, Any]] = None):
        super().__init__(
            detail=detail,
            error_code="EXTERNAL_API_ERROR",
            extra={"service": service, **(extra or {})},
        )


class DataProcessingError(BaseException):
    def __init__(self, detail: str, extra: Optional[Dict[str, Any]] = None):
        super().__init__(detail=detail, error_code="DATA_PROCESSING_ERROR", extra=extra)


class ConfigurationError(BaseException):
    def __init__(self, detail: str, extra: Optional[Dict[str, Any]] = None):
        super().__init__(detail=detail, error_code="CONFIGURATION_ERROR", extra=extra)

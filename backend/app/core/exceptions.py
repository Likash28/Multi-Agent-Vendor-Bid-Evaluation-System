"""
Custom Exceptions and Exception Handlers
"""

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from typing import Optional


class AppException(Exception):
    """Base application exception"""
    def __init__(
        self,
        message: str,
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
        details: Optional[dict] = None,
    ):
        self.message = message
        self.status_code = status_code
        self.details = details or {}
        super().__init__(message)


class NotFoundException(AppException):
    """Resource not found exception"""
    def __init__(self, resource: str, resource_id: str):
        super().__init__(
            message=f"{resource} with id '{resource_id}' not found",
            status_code=status.HTTP_404_NOT_FOUND,
            details={"resource": resource, "id": resource_id},
        )


class BadRequestException(AppException):
    """Bad request exception"""
    def __init__(self, message: str, details: Optional[dict] = None):
        super().__init__(
            message=message,
            status_code=status.HTTP_400_BAD_REQUEST,
            details=details,
        )


class UnauthorizedException(AppException):
    """Unauthorized exception"""
    def __init__(self, message: str = "Unauthorized"):
        super().__init__(
            message=message,
            status_code=status.HTTP_401_UNAUTHORIZED,
        )


class ForbiddenException(AppException):
    """Forbidden exception"""
    def __init__(self, message: str = "Access forbidden"):
        super().__init__(
            message=message,
            status_code=status.HTTP_403_FORBIDDEN,
        )


class ConflictException(AppException):
    """Conflict exception (e.g., duplicate resource)"""
    def __init__(self, message: str, details: Optional[dict] = None):
        super().__init__(
            message=message,
            status_code=status.HTTP_409_CONFLICT,
            details=details,
        )


class ValidationException(AppException):
    """Validation exception"""
    def __init__(self, message: str, errors: Optional[list] = None):
        super().__init__(
            message=message,
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            details={"errors": errors or []},
        )


def setup_exception_handlers(app: FastAPI) -> None:
    """Setup exception handlers for the application"""

    @app.exception_handler(AppException)
    async def app_exception_handler(request: Request, exc: AppException):
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": True,
                "message": exc.message,
                "details": exc.details,
            },
        )

    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception):
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "error": True,
                "message": "An unexpected error occurred",
                "details": {"type": type(exc).__name__},
            },
        )

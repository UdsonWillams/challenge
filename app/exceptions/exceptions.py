from typing import Any, Dict, Optional

from fastapi import HTTPException, status


class DefaultApiException(HTTPException):
    def __init__(
        self,
        status_code: int,
        detail: Any = None,
        headers: Dict[str, str] | None = None,
    ) -> None:
        super().__init__(status_code, detail, headers)


class NotFoundError(DefaultApiException):
    """Exception raised when a requested resource is not found."""

    def __init__(
        self,
        detail: Any = "Resource not found",
        headers: Optional[Dict[str, str]] = None,
    ) -> None:
        super().__init__(status.HTTP_404_NOT_FOUND, detail, headers)


class UnauthorizedError(DefaultApiException):
    """Exception raised when authentication is required or has failed."""

    def __init__(
        self,
        detail: Any = "Authentication required",
        headers: Optional[Dict[str, str]] = None,
    ) -> None:
        super().__init__(status.HTTP_401_UNAUTHORIZED, detail, headers)


class ForbiddenError(DefaultApiException):
    """Exception raised when access to a resource is forbidden."""

    def __init__(
        self,
        detail: Any = "Access forbidden",
        headers: Optional[Dict[str, str]] = None,
    ) -> None:
        super().__init__(status.HTTP_403_FORBIDDEN, detail, headers)


class InternalServerErrorException(DefaultApiException):
    def __init__(
        self,
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail: Any = {"error": "Some error ocurred!"},
        headers: Dict[str, str] | None = None,
    ) -> None:
        super().__init__(status_code, detail, headers)


class ApiInvalidResponseException(DefaultApiException):
    def __init__(
        self,
        status_code: int = 403,
        detail: Any = {"error": "Invalid values for the api"},
        headers: Dict[str, str] | None = None,
    ) -> None:
        super().__init__(status_code, detail, headers)


class RepositoryError(DefaultApiException):
    """Exception raised when there's an error in the repository layer."""

    def __init__(
        self,
        detail: Any = "Database operation failed",
        headers: Optional[Dict[str, str]] = None,
    ) -> None:
        super().__init__(status.HTTP_500_INTERNAL_SERVER_ERROR, detail, headers)

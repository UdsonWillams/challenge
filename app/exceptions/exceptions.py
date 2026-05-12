from http import HTTPStatus
from typing import Any

from fastapi import HTTPException


class DefaultApiException(HTTPException):
    def __init__(
        self,
        status_code: int,
        detail: Any = None,
        headers: dict[str, str] | None = None,
    ) -> None:
        super().__init__(status_code, detail, headers)


class NotFoundError(DefaultApiException):
    def __init__(
        self,
        detail: Any = "Resource not found",
        headers: dict[str, str] | None = None,
    ) -> None:
        super().__init__(HTTPStatus.NOT_FOUND, detail, headers)


class UnauthorizedError(DefaultApiException):
    def __init__(
        self,
        detail: Any = "Authentication required",
        headers: dict[str, str] | None = None,
    ) -> None:
        super().__init__(HTTPStatus.UNAUTHORIZED, detail, headers)


class ForbiddenError(DefaultApiException):
    def __init__(
        self,
        detail: Any = "Access forbidden",
        headers: dict[str, str] | None = None,
    ) -> None:
        super().__init__(HTTPStatus.FORBIDDEN, detail, headers)


class InternalServerErrorException(DefaultApiException):
    def __init__(
        self,
        status_code: int = HTTPStatus.INTERNAL_SERVER_ERROR,
        detail: Any = {"error": "Some error ocurred!"},
        headers: dict[str, str] | None = None,
    ) -> None:
        super().__init__(status_code, detail, headers)


class ApiInvalidResponseException(DefaultApiException):
    def __init__(
        self,
        status_code: int = HTTPStatus.BAD_GATEWAY,
        detail: Any = {"error": "Invalid response from external API"},
        headers: dict[str, str] | None = None,
    ) -> None:
        super().__init__(status_code, detail, headers)


class RepositoryError(DefaultApiException):
    def __init__(
        self,
        detail: Any = "Database operation failed",
        headers: dict[str, str] | None = None,
    ) -> None:
        super().__init__(HTTPStatus.INTERNAL_SERVER_ERROR, detail, headers)

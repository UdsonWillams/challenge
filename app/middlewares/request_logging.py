from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response

from app.core.logger import logger
from app.core.settings import get_settings

settings = get_settings()


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    BODY_METHODS = {"POST", "PUT", "PATCH"}
    MAX_BODY_LENGTH = 1024
    SANITIZED_HEADERS = {"authorization", "cookie", "x-api-key"}

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        if settings.APP_ENVIRONMENT not in ("local", "development"):
            return await call_next(request)

        body = None
        if request.method.upper() in self.BODY_METHODS:
            try:
                raw_body = await request.body()
                body = raw_body.decode("utf-8")[: self.MAX_BODY_LENGTH]
            except Exception:
                body = "<unreadable>"

        response = await call_next(request)

        extra = {
            "method": request.method,
            "path": request.url.path,
            "query_params": str(request.query_params),
            "status_code": response.status_code,
        }

        if body:
            extra["body"] = body

        logger.debug("API Request", extra=extra)
        return response

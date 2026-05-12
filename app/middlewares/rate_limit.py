import time
from collections import defaultdict
from http import HTTPStatus

from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import JSONResponse

from app.core.settings import get_settings

settings = get_settings()


class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app):
        super().__init__(app)
        self._clients: dict[str, list[float]] = defaultdict(list)

    def _get_client_key(self, request: Request) -> str:
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            return forwarded.split(",")[0].strip()
        return request.client.host if request.client else "unknown"

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint):
        client_key = self._get_client_key(request)
        now = time.time()

        window = 60
        self._clients[client_key] = [t for t in self._clients[client_key] if now - t < window]
        self._clients[client_key].append(now)

        if len(self._clients[client_key]) > settings.RATE_LIMIT_PER_MINUTE:
            return JSONResponse(
                content={"detail": "Rate limit exceeded. Try again later."},
                status_code=HTTPStatus.TOO_MANY_REQUESTS,
            )

        return await call_next(request)

from time import time

from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response

from app.core.logger import logger


class ResponseTimeMiddleware(BaseHTTPMiddleware):
    """
    A ideia desse middleware é de retornar o valor de tempo de
    resposta dos endpoints chamados.
    """

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        initial_time = time()
        response = await call_next(request)
        final_time = time() - initial_time
        elapsed_time = str(round(final_time, 3))
        logger.info(
            "Request completed",
            extra={
                "method": request.method,
                "path": request.url.path,
                "status_code": response.status_code,
                "response_time": elapsed_time,
            },
        )
        response.headers.update({"X-Response-Time": elapsed_time})
        return response

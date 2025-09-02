from contextvars import ContextVar
from uuid import uuid4

from starlette.types import (
    ASGIApp,
    Receive,
    Scope,
    Send,
)

TRACE_ID_CTX_KEY = "trace_id"

_trace_id_ctx_var: ContextVar[str] = ContextVar(TRACE_ID_CTX_KEY, default=None)


class CreateTraceIdMiddleware:
    def __init__(
        self,
        app: ASGIApp,
    ) -> None:
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] not in ["http", "websocket"]:
            await self.app(scope, receive, send)
            return

        headers_list: list = scope.get("headers")
        header: tuple
        trace_id = str(uuid4())

        try:
            for header in headers_list:
                header_name: bytes = header[0]
                header_value: bytes = header[1]
                if header_name.decode().lower() == "x-trace-id":
                    trace_id = header_value.decode()
                    break
        except Exception:  # nosec
            pass

        trace_id = _trace_id_ctx_var.set(trace_id)
        await self.app(scope, receive, send)
        _trace_id_ctx_var.reset(trace_id)


def get_trace_id() -> str:
    trace_id = _trace_id_ctx_var.get()
    if not trace_id:
        trace_id = "not_initialized_yet"
    return trace_id

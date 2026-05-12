from http import HTTPStatus

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api import api_router
from app.core.lifespan import lifespan
from app.core.logger import logger
from app.core.settings import get_settings
from app.exceptions.exceptions import DefaultApiException
from app.middlewares.rate_limit import RateLimitMiddleware
from app.middlewares.request_logging import RequestLoggingMiddleware
from app.middlewares.response_time import ResponseTimeMiddleware
from app.middlewares.security_headers import SecurityHeadersMiddleware
from app.middlewares.trace_id import CreateTraceIdMiddleware, get_trace_id

settings = get_settings()

app = FastAPI(
    title="FastAPI Boilerplate",
    description="Base para novos projetos FastAPI com banco de dados",
    docs_url="/swagger",
    redoc_url="/docs",
    separate_input_output_schemas=True,
    lifespan=lifespan,
)


@app.exception_handler(DefaultApiException)
async def api_exception_handler(request, exc: DefaultApiException):
    logger.error(
        f"API Exception | {type(exc).__name__} | {exc.detail}",
        extra={"status_code": exc.status_code, "trace_id": get_trace_id()},
    )
    return JSONResponse(
        content={"detail": exc.detail, "trace_id": get_trace_id()},
        status_code=exc.status_code,
        headers=exc.headers or {},
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    if isinstance(exc, DefaultApiException):
        logger.error(
            f"Unhandled API Exception: {type(exc).__name__} | {exc}",
            extra={"trace_id": get_trace_id()},
        )
        return JSONResponse(
            content={"detail": exc.detail, "trace_id": get_trace_id()},
            status_code=exc.status_code,
        )

    logger.error(
        f"Unhandled exception | {type(exc).__name__} | {exc}",
        exc_info=True,
        extra={"trace_id": get_trace_id()},
    )

    if settings.APP_ENVIRONMENT in ("local", "development"):
        return JSONResponse(
            content={
                "detail": str(exc),
                "type": type(exc).__name__,
                "trace_id": get_trace_id(),
            },
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
        )

    return JSONResponse(
        content={
            "detail": "An internal error occurred",
            "trace_id": get_trace_id(),
        },
        status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
    )


app.add_middleware(CreateTraceIdMiddleware)
app.add_middleware(RateLimitMiddleware)
app.add_middleware(RequestLoggingMiddleware)
app.add_middleware(ResponseTimeMiddleware)
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.APP_CORS_LIST,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router=api_router)

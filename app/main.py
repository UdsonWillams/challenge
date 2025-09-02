import contextlib
from typing import AsyncIterator

from alembic.command import upgrade
from alembic.config import Config as alembic_config
from fastapi import FastAPI, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.applications import Starlette

from app.api import api_router
from app.core.logger import logger
from app.core.settings import get_settings
from app.exceptions.exceptions import DefaultApiException
from app.middlewares.response_time import ResponseTimeMiddleware
from app.middlewares.trace_id import CreateTraceIdMiddleware

config_file = alembic_config()
settings = get_settings()

config_file.set_main_option("script_location", settings.APP_MIGRATIONS_FOLDER)
config_file.set_main_option("sqlalchemy.url", settings.DATABASE_URL)


@contextlib.asynccontextmanager
async def lifespan(app: Starlette) -> AsyncIterator:
    logger.info("Running database migrations...")
    upgrade(config_file, "head")
    yield


app = FastAPI(
    title="Challenger FastAPI ",
    description="Api para servir de base para novos projetos",
    docs_url="/swagger",
    redoc_url="/docs",
    separate_input_output_schemas=True,
    lifespan=lifespan,
)


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """
    Handle general exceptions. For ApiException types, re-raise them to be handled
    by FastAPI's built-in exception handlers. For other exceptions, return a generic
    error response while logging the actual error details.
    """
    logger.error(f"Erro ao processar execução | Tipo do erro: {type(exc)} | {exc}")
    if isinstance(exc, DefaultApiException):
        raise exc
    if settings.APP_ENVIRONMENT in ["local"]:
        return JSONResponse(
            content={"message": f"Error: {type(exc)} - {exc}"},
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
    return JSONResponse(
        content={"message": "An Internal Error Occurred"},
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
    )


app.add_middleware(CreateTraceIdMiddleware)
app.add_middleware(ResponseTimeMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.APP_CORS_LIST,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router=api_router)

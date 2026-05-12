import contextlib
from collections.abc import AsyncIterator

from alembic.command import upgrade
from alembic.config import Config as AlembicConfig
from starlette.applications import Starlette

from app.core.logger import logger
from app.core.settings import get_settings

settings = get_settings()


@contextlib.asynccontextmanager
async def lifespan(app: Starlette) -> AsyncIterator:
    logger.info("Starting application...")
    config = AlembicConfig()
    config.set_main_option("script_location", settings.APP_MIGRATIONS_FOLDER)
    config.set_main_option("sqlalchemy.url", settings.DATABASE_URL_SYNC)
    logger.info("Running database migrations...")
    upgrade(config, "head")
    logger.info("Migrations complete")

    if settings.APP_ENVIRONMENT in ("local", "development"):
        _warn_default_settings()

    yield

    logger.info("Shutting down application...")


def _warn_default_settings():
    if settings.SECRET_KEY == "sua-chave-secreta-super-segura-aqui-mude-em-producao":
        logger.warning("WARNING: Using default SECRET_KEY. Change it in production!")
    if settings.APP_CORS == "*":
        logger.warning("WARNING: CORS is set to wildcard. Restrict in production!")

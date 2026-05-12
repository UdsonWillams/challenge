from http import HTTPStatus

from fastapi import APIRouter
from fastapi.responses import JSONResponse
from redis.asyncio import Redis
from sqlalchemy import text

from app.core.logger import logger
from app.core.settings import get_settings
from app.database.unit_of_work import _get_engine_and_factory

router = APIRouter(tags=["Health Check"])
settings = get_settings()


@router.get("/healthcheck", status_code=HTTPStatus.OK)
async def check_health() -> JSONResponse:
    db_status = "ok"
    redis_status = "ok"

    try:
        engine, _ = await _get_engine_and_factory()
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
    except Exception:
        db_status = "error"
        logger.error("Database healthcheck failed", exc_info=True)

    try:
        r = Redis(host=settings.REDIS_HOST, port=settings.REDIS_PORT, decode_responses=True)
        await r.ping()
        await r.close()
    except Exception:
        redis_status = "error"
        logger.error("Redis healthcheck failed", exc_info=True)

    overall = "ok" if db_status == "ok" and redis_status == "ok" else "degraded"

    return JSONResponse(
        content={
            "status": overall,
            "database": db_status,
            "redis": redis_status,
        }
    )

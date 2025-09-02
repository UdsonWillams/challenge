from fastapi import APIRouter

from app.api.health_check import router as healthcheck_router
from app.api.v1 import v1_router

api_router = APIRouter()


api_router.include_router(healthcheck_router, prefix="/api")
api_router.include_router(v1_router, prefix="/api")

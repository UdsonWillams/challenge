from fastapi import APIRouter

from app.api.v1.auth.views import router as auth_router
from app.api.v1.customers.views import router as customers_router
from app.api.v1.products.views import router as products_router

v1_router = APIRouter(prefix="/v1")

v1_router.include_router(auth_router, tags=["Auth"])
v1_router.include_router(customers_router, tags=["Customers"])
v1_router.include_router(products_router, tags=["Products"])

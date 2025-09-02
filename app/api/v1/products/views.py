from typing import List

from fastapi import APIRouter

from app.schemas.domain.products import output
from app.services.external.products import ProductsApiService

router = APIRouter(prefix="/products", tags=["Products"])


@router.get("/{product_id}", response_model=output.ProductsResponse)
async def get_product(product_id: str):
    service = ProductsApiService()
    product = await service.get_product(product_id)
    return product


@router.get("", response_model=List[output.ProductsResponse])
async def get_products():
    service = ProductsApiService()
    product = await service.get_products()
    return product

from fastapi import status
from httpx import AsyncClient, Response

from app.core.logger import logger
from app.core.settings import get_settings
from app.database.repositories.redis import RedisRepository
from app.exceptions.exceptions import ApiInvalidResponseException
from app.schemas.domain.products.output import ExternalProductResponse, ProductsResponse

settings = get_settings()


class ProductsApiService:
    def __init__(self):
        self.cache = RedisRepository()

    async def _execute(
        self, url: str, method: str, headers: str = None, params: str = None
    ) -> Response:
        async with AsyncClient(timeout=15) as http_client:
            request = http_client.build_request(
                method, url, headers=headers, params=params
            )
            response = await http_client.send(request)
        return response

    async def get_products(self) -> list[ProductsResponse]:
        url = f"{settings.EXTERNAL_PRODUCTS_BASE_URL}/produtos"
        data: dict = self.cache.get("products")
        all_products = []
        if not data:
            response = await self._execute(url, "GET")
            if response.status_code != status.HTTP_200_OK:
                logger.error(
                    f"Get Products error | Status: {response.status_code} | Response: {response.text}",
                    extra={"response": response.text},
                )
                raise ApiInvalidResponseException()
            self.cache.create("products", response.json())
        for product in data.get("produtos"):
            try:
                all_products.append(
                    ExternalProductResponse.model_validate(product).model_dump(
                        mode="json"
                    )
                )
            except Exception as e:
                logger.error(f"Error parsing product data: {e}", extra={"error": e})
                continue
        return all_products

    async def get_product(self, product_id: int) -> ProductsResponse:
        url = f"{settings.EXTERNAL_PRODUCTS_BASE_URL}/produtos/{product_id}"
        data = self.cache.get(product_id)
        if not data:
            response = await self._execute(url, "GET")
            if response.status_code != status.HTTP_200_OK:
                logger.error(
                    f"Get Product {product_id} error | Status: {response.status_code} | Response: {response.text}",
                    extra={"response": response.text},
                )
                raise ApiInvalidResponseException()
            data = response.json()
            self.cache.create(product_id, data)
        return ExternalProductResponse.model_validate(data).model_dump(mode="json")

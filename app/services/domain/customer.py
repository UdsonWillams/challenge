from uuid import UUID

from app.database.models.base import Customer
from app.database.repositories.customer import CustomerRepository
from app.database.unit_of_work import UnitOfWorkConnection
from app.exceptions.exceptions import NotFoundError, UnauthorizedError
from app.schemas.auth import AuthenticatedUser
from app.schemas.domain.customers import output
from app.schemas.domain.customers.input import CreateCustomer
from app.schemas.domain.favorites import FavoriteCreate
from app.services.external.products import ProductsApiService


class CustomerService:
    def __init__(self, uow: UnitOfWorkConnection, user: AuthenticatedUser = None):
        self.uow = uow
        self.user = user
        self.repository = CustomerRepository(uow)

    async def create_customer(self, payload: CreateCustomer):
        customer = await self.repository.create(Customer(**payload.model_dump()))
        return customer.to_dict()

    async def list_all(
        self,
        sort_by: str = "-updated_at",
        filters: dict = {},
        page_size: int = 100,
        page: int = 0,
    ):
        customers = await self.repository.get(filters, sort_by, page_size, page)
        data = []
        for customer in customers:
            data.append(output.CustomerResponse(**customer.to_dict()))

        return {"items": data, "count": len(data) if data else 0}

    async def get_by_id(self, customer_id: int):
        customer = await self.repository.get_by_id_with_favorites(customer_id)
        if not customer:
            raise NotFoundError
        result = customer.to_dict()
        result["favorites"] = [fav.to_dict() for fav in customer.favorites]
        return result

    async def get_by_email(self, email: str):
        customer = await self.repository.get_by_email_with_favorites(email)
        if not customer:
            raise NotFoundError
        result = customer.to_dict()
        result["favorites"] = [fav.to_dict() for fav in customer.favorites]
        return result

    async def update(self, customer_id: int, payload: dict):
        if self.user and str(self.user.id) != str(customer_id) and self.user.role != "admin":
            raise UnauthorizedError
        updated_customer = await self.repository.update(
            customer_id, payload, self.user.email if self.user else "system"
        )
        if not updated_customer:
            raise NotFoundError
        return updated_customer.to_dict()

    async def delete(self, customer_id: int):
        if self.user and str(self.user.id) != str(customer_id) and self.user.role != "admin":
            raise UnauthorizedError
        if not await self.repository.delete(customer_id):
            raise NotFoundError

    async def add_favorite(self, customer_id: UUID, payload: FavoriteCreate):
        if self.user and str(self.user.id) != str(customer_id) and self.user.role != "admin":
            raise UnauthorizedError
        products_service = ProductsApiService()
        product_external = await products_service.get_product(payload.external_id)
        if not product_external:
            raise NotFoundError
        data = {
            "external_id": str(product_external.get("id")),
            "title": product_external.get("title"),
            "price": product_external.get("price"),
            "description": product_external.get("description"),
            "category": product_external.get("category"),
            "image": product_external.get("image"),
            "review": (product_external.get("rating") or {}).get("rate")
            if isinstance(product_external.get("rating"), dict)
            else None,
        }
        return await self.repository.add_favorite(customer_id, data)

    async def remove_favorite(self, customer_id: UUID, product_id: UUID) -> bool:
        if self.user and str(self.user.id) != str(customer_id) and self.user.role != "admin":
            raise UnauthorizedError
        return await self.repository.remove_favorite(customer_id, product_id)

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from app.schemas.domain.products.output import ProductsToCustomerResponse


class CustomerResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    email: str
    favorites: list[ProductsToCustomerResponse] = []
    created_at: datetime
    updated_at: datetime


class CreateCustomerResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    email: str


class CustomerList(BaseModel):
    items: list[CustomerResponse]
    count: int
    total: int | None = None

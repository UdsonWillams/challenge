from datetime import datetime
from typing import List
from uuid import UUID

from pydantic import BaseModel

from app.schemas.domain.products.output import ProductsToCustomerResponse


class CustomerResponse(BaseModel):
    id: UUID
    name: str
    email: str
    favorites: List[ProductsToCustomerResponse] = []
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class CreateCustomerResponse(BaseModel):
    id: UUID
    name: str
    email: str

    class Config:
        from_attributes = True


class CustomerList(BaseModel):
    items: List[CustomerResponse]
    count: int

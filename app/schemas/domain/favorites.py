from uuid import UUID

from pydantic import BaseModel


class FavoriteCreate(BaseModel):
    external_id: str


class FavoriteProductResponse(BaseModel):
    id: UUID
    external_id: str
    title: str
    price: float
    description: str | None = None
    category: str | None = None
    image: str | None = None
    review: float | None = None
    customer_id: UUID

from typing import Optional
from uuid import UUID

from pydantic import BaseModel


class FavoriteCreate(BaseModel):
    external_id: str


class FavoriteProductResponse(BaseModel):
    id: UUID
    external_id: str
    title: str
    price: float
    description: Optional[str] = None
    category: Optional[str] = None
    image: Optional[str] = None
    review: Optional[float] = None
    customer_id: UUID

"""
Schemas baseados nas tabelas do banco de dados utilizando o Pydantic

A ideia é poder utilizar do valores que a ORM do sqlalchemy nos trás com
as funções auxiliadoras do Pydantic.
Ex.: model_dump, model_dump_json
"""

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel as PydanticBase
from pydantic import ConfigDict


class BaseModel(PydanticBase):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    created_by: str | None = None
    created_at: datetime
    updated_by: str | None = None
    updated_at: datetime | None = None
    deleted_by: str | None = None
    deleted_at: datetime | None = None


class Customer(BaseModel):
    name: str
    email: str
    favorites: list["Product"] = []
    password: str
    role: str
    is_active: bool


class Product(BaseModel):
    id: UUID
    external_id: str
    title: str
    price: float
    description: Optional[str] = None
    category: Optional[str] = None
    image: Optional[str] = None
    review: Optional[float] = None

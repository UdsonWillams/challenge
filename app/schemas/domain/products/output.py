from uuid import UUID

from pydantic import BaseModel, Field


class ExternalProductResponse(BaseModel):
    id: str = Field(alias="_id")
    title: str = Field(alias="nome")
    image: str | None = Field(default=None, alias="imagem")
    price: float | None = Field(alias="preco")
    description: str | None = Field(alias="descricao")
    review: float | None = 0.0
    quantity: int | None = Field(alias="quantidade")


class ProductsResponse(BaseModel):
    id: str
    title: str
    image: str | None = None
    price: float | None = None
    description: str | None = None
    review: float | None = 0.0
    quantity: int | None = None


class ProductsToCustomerResponse(BaseModel):
    id: UUID
    external_id: str
    title: str
    image: str | None = None
    price: float | None = None
    description: str | None = None
    review: float | None = 0.0
    quantity: int | None = None

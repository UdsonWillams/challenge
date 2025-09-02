from pydantic import BaseModel


class AddFavoriteProduct(BaseModel):
    product_id: str

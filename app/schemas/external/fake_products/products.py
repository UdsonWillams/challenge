from pydantic import BaseModel


class Products(BaseModel):
    id: int
    title: str
    price: float
    image: str
    review: str

from sqlalchemy import select

from app.core.logger import logger
from app.database.models.base import Product
from app.database.repositories.base import BaseRepository
from app.database.unit_of_work import UnitOfWorkConnection
from app.exceptions.exceptions import RepositoryError


class ProductRepository(BaseRepository[Product]):
    def __init__(self, uow: UnitOfWorkConnection):
        super().__init__(Product, uow)

    async def get_by_external_id(self, external_id: str) -> Product:
        session = await self.uow.get_session()
        query = select(self.model).filter(self.model.external_id == external_id).first()
        result = await session.execute(query)
        try:
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"Error fetching {self.model.__name__} by ID: {e}")
            raise RepositoryError

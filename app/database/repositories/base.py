from datetime import datetime, timezone
from typing import Generic, Optional, Type, TypeVar
from uuid import UUID

from sqlalchemy import desc, func, or_, select

from app.core.logger import logger
from app.database.models.base import Base
from app.database.unit_of_work import UnitOfWorkConnection
from app.exceptions.exceptions import RepositoryError

T = TypeVar("T", bound=Base)  # type: ignore


class BaseRepository(Generic[T]):
    def __init__(self, model: Type[T], uow: UnitOfWorkConnection):
        self.model = model
        self.uow = uow

    async def get_by_id(self, id: UUID) -> Optional[T]:
        try:
            session = await self.uow.get_session()
            query = (
                select(self.model)
                .filter(self.model.id == id)
                .filter(
                    self.model.deleted_at.is_(None),
                    self.model.deleted_by.is_(None),
                )
            )
            result = await session.execute(query)
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"Error fetching {self.model.__name__} by ID: {e}")
            raise RepositoryError

    async def create(self, data: T) -> T:
        try:
            session = await self.uow.get_session()
            session.add(data)
            await session.commit()
            await session.refresh(data)
            return data
        except Exception as e:
            logger.error(f"Error creating {self.model.__name__}: {e}")
            raise RepositoryError

    async def update(self, id: UUID, data: dict, updated_by="system") -> Optional[T]:
        try:
            session = await self.uow.get_session()
            query = select(self.model).filter(self.model.id == id)
            result = await session.execute(query)
            existing_record = result.scalar_one_or_none()

            if not existing_record:
                return None

            for key, value in data.items():
                if key == "id" or not hasattr(existing_record, key):
                    continue
                setattr(existing_record, key, value)

            existing_record.updated_at = datetime.now(timezone.utc)
            existing_record.updated_by = updated_by

            await session.commit()
            await session.refresh(existing_record)
            return existing_record
        except Exception as e:
            logger.error(f"Error updating {self.model.__name__}: {e}")
            raise RepositoryError

    async def delete(self, id: UUID, deleted_by="system", hard_delete=False) -> bool:
        try:
            session = await self.uow.get_session()
            query = select(self.model).filter(self.model.id == id)
            result = await session.execute(query)
            existing_record = result.scalar_one_or_none()

            if not existing_record:
                return False

            if hard_delete:
                await session.delete(existing_record)
            else:
                existing_record.deleted_at = datetime.now(timezone.utc)
                existing_record.deleted_by = deleted_by

            await session.commit()
            return True
        except Exception as e:
            logger.error(f"Error deleting {self.model.__name__}: {e}")
            raise RepositoryError

    async def get(
        self,
        filters: dict = None,
        sort_by: str | list[str] = None,
        page_size: int = 100,
        page: int = 1,
    ) -> list[T]:
        try:
            session = await self.uow.get_session()
            query = select(self.model).filter(
                self.model.deleted_at.is_(None),
                self.model.deleted_by.is_(None),
            )

            # Filtros
            if filters:
                if "$or" in filters:
                    or_conditions = []
                    for condition in filters["$or"]:
                        for key, value in condition.items():
                            if hasattr(self.model, key):
                                column = getattr(self.model, key)
                                if isinstance(value, str) and "%" in value:
                                    or_conditions.append(column.ilike(value))
                                else:
                                    or_conditions.append(column == value)
                    if or_conditions:
                        query = query.filter(or_(*or_conditions))
                for key, value in filters.items():
                    if key == "$or":
                        continue
                    if hasattr(self.model, key):
                        if isinstance(value, str) and "%" in value:
                            query = query.filter(getattr(self.model, key).ilike(value))
                        else:
                            query = query.filter(getattr(self.model, key) == value)

            # Ordenação
            query = self._apply_ordering(query, sort_by)

            # Paginação
            offset = (page - 1) * page_size
            query = query.offset(offset).limit(page_size)

            result = await session.execute(query)
            return result.scalars().all()
        except Exception as e:
            logger.error(f"Error fetching {self.model.__name__} list: {e}")
            raise RepositoryError

    async def count(self, filters: dict = None) -> int:
        try:
            session = await self.uow.get_session()
            query = (
                select(func.count())
                .select_from(self.model)
                .filter(
                    self.model.deleted_at.is_(None),
                    self.model.deleted_by.is_(None),
                )
            )

            if filters:
                if "$or" in filters:
                    or_conditions = []
                    for condition in filters["$or"]:
                        for key, value in condition.items():
                            if hasattr(self.model, key):
                                column = getattr(self.model, key)
                                if isinstance(value, str) and "%" in value:
                                    or_conditions.append(column.ilike(value))
                                else:
                                    or_conditions.append(column == value)
                    if or_conditions:
                        query = query.filter(or_(*or_conditions))
                for key, value in filters.items():
                    if key == "$or":
                        continue
                    if hasattr(self.model, key):
                        if isinstance(value, str) and "%" in value:
                            query = query.filter(getattr(self.model, key).ilike(value))
                        else:
                            query = query.filter(getattr(self.model, key) == value)

            result = await session.execute(query)
            return result.scalar()
        except Exception as e:
            logger.error(f"Error counting {self.model.__name__} records: {e}")
            raise RepositoryError

    def _apply_ordering(self, query, order_by):
        if not order_by:
            return query
        if isinstance(order_by, str):
            order_by = [order_by]

        for field in order_by:
            if field.startswith("-"):
                field_name = field[1:]
                if hasattr(self.model, field_name):
                    query = query.order_by(desc(getattr(self.model, field_name)))
            else:
                if hasattr(self.model, field):
                    query = query.order_by(getattr(self.model, field))
        return query

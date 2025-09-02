from datetime import datetime, timezone
from typing import Any, Optional

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import selectinload

from app.core.logger import logger
from app.database.models.base import Customer, Product
from app.database.repositories.base import BaseRepository
from app.database.unit_of_work import UnitOfWorkConnection
from app.exceptions.exceptions import RepositoryError


class CustomerRepository(BaseRepository[Customer]):
    def __init__(self, uow: UnitOfWorkConnection):
        super().__init__(Customer, uow)

    async def get_user_by_email(self, email: str) -> Customer | None:
        session = await self.uow.get_session()
        query = select(self.model).filter(self.model.email == email)
        result = await session.execute(query)
        return result.scalar_one_or_none()

    async def create(self, data: Customer) -> Customer:
        try:
            session = await self.uow.get_session()
            from app.services.auth.authentication import AuthService

            crypt_service = AuthService()
            data.password = await crypt_service.get_password_hash(data.password)
            session.add(data)
            await session.commit()
            await session.refresh(data)
            return data
        except Exception as e:
            logger.error(f"Error creating {self.model.__name__}: {e}")
            raise RepositoryError

    async def update(self, id: Any, data: dict, updated_by="system") -> Customer | None:
        try:
            session = await self.uow.get_session()
            query = select(self.model).filter(self.model.id == id)
            result = await session.execute(query)
            existing_record = result.scalar_one_or_none()

            if not existing_record:
                return None

            for key, value in data.items():
                if (key == "id" or key == "favorites") or not hasattr(
                    existing_record, key
                ):
                    continue
                setattr(existing_record, key, value)

            if "password" in data:
                from app.services.auth.authentication import AuthService

                crypt_service = AuthService()
                existing_record.password = await crypt_service.get_password_hash(
                    data["password"]
                )

            existing_record.updated_at = datetime.now(timezone.utc)
            existing_record.updated_by = updated_by

            await session.commit()
            await session.refresh(existing_record)
            return existing_record
        except IntegrityError as ie:
            logger.error(f"Integrity error updating {self.model.__name__}: {ie}")
            raise RepositoryError("Integrity error")
        except Exception as e:
            logger.error(f"Error updating {self.model.__name__}: {e}")
            raise RepositoryError

    async def add_favorite(self, customer_id, data: dict) -> Product:
        session = await self.uow.get_session()
        customer_q = select(self.model).filter(self.model.id == customer_id)
        customer_res = await session.execute(customer_q)
        customer = customer_res.scalar_one_or_none()

        if not customer:
            raise RepositoryError("Customer not found")

        ext_id = data.get("external_id")
        existing_q = select(Product).filter(
            Product.external_id == ext_id, Product.customer_id == customer_id
        )
        existing_res = await session.execute(existing_q)
        existing = existing_res.scalar_one_or_none()
        if existing:
            return existing

        product = Product(
            external_id=ext_id,
            title=data.get("title"),
            price=data.get("price") or 0,
            description=data.get("description"),
            category=data.get("category"),
            image=data.get("image"),
            review=data.get("review"),
            customer_id=customer_id,
        )
        session.add(product)
        await session.commit()
        await session.refresh(product)
        return product

    async def remove_favorite(self, customer_id, product_id) -> bool:
        session = await self.uow.get_session()
        q = select(Product).filter(
            Product.id == product_id, Product.customer_id == customer_id
        )
        res = await session.execute(q)
        product = res.scalar_one_or_none()
        if not product:
            return False
        await session.delete(product)
        await session.commit()
        return True

    async def get_by_id_with_favorites(self, customer_id: Any) -> Optional[Customer]:
        try:
            session = await self.uow.get_session()
            query = (
                select(self.model)
                .options(selectinload(self.model.favorites))
                .filter(self.model.id == customer_id)
            )
            result = await session.execute(query)
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"Error getting {self.model.__name__} with favorites: {e}")
            return None

    async def get_by_email_with_favorites(self, email: str) -> Optional[Customer]:
        try:
            session = await self.uow.get_session()
            query = (
                select(self.model)
                .options(selectinload(self.model.favorites))
                .filter(self.model.email == email)
            )
            result = await session.execute(query)
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(
                f"Error getting {self.model.__name__} by email with favorites: {e}"
            )
            return None

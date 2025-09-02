import uuid
from datetime import datetime, timezone

from sqlalchemy import Boolean, Column, Float, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.types import TIMESTAMP

Base = declarative_base()


class BaseModel(Base):
    __abstract__ = True
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    created_by = Column(String(150), nullable=False, default="system")
    created_at = Column(
        type_=TIMESTAMP(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updated_by = Column(String(150), nullable=False, default="system")
    updated_at = Column(
        type_=TIMESTAMP(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    deleted_by = Column(String(150), nullable=True)
    deleted_at = Column(type_=TIMESTAMP(timezone=True), nullable=True)

    def to_dict(self):
        return {
            column.name: getattr(self, column.name) for column in self.__table__.columns
        }


class Customer(BaseModel):
    __tablename__ = "customers"

    email = Column(String(150), nullable=False, unique=True)
    password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    name = Column(String(150), nullable=False)
    role = Column(String(50), nullable=False, default="user")

    favorites = relationship(
        "Product", back_populates="customer", cascade="all, delete-orphan"
    )


class Product(BaseModel):
    __tablename__ = "products"

    external_id = Column(String(50), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    price = Column(Float, nullable=False)
    description = Column(String(1000), nullable=True)
    category = Column(String(100), nullable=True)
    image = Column(String(500), nullable=True)
    review = Column(Float, nullable=True)
    customer_id = Column(UUID(as_uuid=True), ForeignKey("customers.id"), nullable=False)
    customer = relationship("Customer", back_populates="favorites")

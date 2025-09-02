import sys

sys.path.append("app/")

import os

import pytest_asyncio
from pytest_postgresql import factories
from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import scoped_session, sessionmaker

from app.core.settings import get_settings
from app.database.models.base import Base
from app.database.unit_of_work import UnitOfWorkConnection


def load_database(**kwargs):
    connection = f"postgresql+psycopg2://{kwargs['user']}:@{kwargs['host']}:{kwargs['port']}/{kwargs['dbname']}"
    engine = create_engine(
        connection,
        pool_pre_ping=True,
        pool_recycle=3600,
        connect_args={
            "keepalives": 1,
            "keepalives_idle": 60,
            "keepalives_interval": 30,
            "keepalives_count": 5,
        },
    )

    Base.metadata.create_all(engine)
    session = scoped_session(sessionmaker(bind=engine))
    session.commit()
    session.close()
    engine.dispose()


postgresql_proc = factories.postgresql_proc(port=None, load=[load_database])
postgresql = factories.postgresql("postgresql_proc")


@pytest_asyncio.fixture
async def async_session(postgresql):
    connection = f"postgresql+asyncpg://{postgresql.info.user}:@{postgresql.info.host}:{postgresql.info.port}/{postgresql.info.dbname}"
    engine = create_async_engine(connection, echo=True)

    async_session_maker = sessionmaker(
        bind=engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    # important steps for caching current envs and making UOW Work
    get_settings()

    os.environ["POSTGRES_USER"] = postgresql.info.user
    os.environ["POSTGRES_PASSWORD"] = ""
    os.environ["POSTGRES_DB"] = postgresql.info.dbname
    os.environ["POSTGRES_HOST"] = postgresql.info.host
    os.environ["POSTGRES_PORT"] = str(postgresql.info.port)

    async with async_session_maker() as session:
        yield session


@pytest_asyncio.fixture
async def uow(async_session):
    yield UnitOfWorkConnection(session=async_session)

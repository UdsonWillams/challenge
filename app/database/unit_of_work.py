import json
from typing import AsyncGenerator, Optional

from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from app.core.logger import logger
from app.core.settings import get_settings

# Global engine and session factory for reuse
_engine: Optional[AsyncEngine] = None
_session_factory: Optional[sessionmaker] = None
settings = get_settings()


async def _get_engine_and_factory():
    """Get or create engine and session factory."""
    global _engine, _session_factory
    if _engine is None:
        logger.debug("Initializing database connection")
        _engine = create_async_engine(
            settings.DATABASE_URL,
            echo=False,
            json_serializer=lambda obj: json.dumps(obj, ensure_ascii=False),
        )
        _session_factory = sessionmaker(
            autocommit=False, autoflush=False, bind=_engine, class_=AsyncSession
        )
    return _engine, _session_factory


class UnitOfWorkConnection:
    """Unit of Work pattern for managing database transactions."""

    def __init__(self, session: Optional[AsyncSession] = None) -> None:
        """Initialize Unit of Work.

        Args:
            session: Optional existing session to use.
        """
        self._session = session
        self._should_close_session = session is None
        self._committed = False

    async def __aenter__(self) -> "UnitOfWorkConnection":
        """Enter async context and create session if needed."""
        if self._session is None:
            _, session_factory = await _get_engine_and_factory()
            self._session = session_factory()
            logger.debug("New database session created")
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """Exit async context and cleanup session."""
        try:
            if exc_type is None and not self._committed:
                await self.commit()
            else:
                await self.rollback()
        except Exception as e:
            logger.error(f"Error during transaction cleanup: {e}")
            try:
                await self.rollback()
            except Exception:
                logger.error("Failed to rollback transaction during cleanup")
        finally:
            if self._should_close_session and self._session:
                await self._session.close()
                logger.debug("Database session closed")

    async def get_session(self) -> AsyncSession:
        """Get current database session.

        Returns:
            AsyncSession: Current database session.

        Raises:
            RuntimeError: If session is not available.
        """
        if self._session is None:
            raise RuntimeError("Session not available. Use async context manager.")
        return self._session

    async def commit(self) -> None:
        """Commit current transaction."""
        if self._session and not self._committed:
            try:
                await self._session.commit()
                self._committed = True
                logger.debug("Transaction committed")
            except Exception as e:
                logger.error(f"Failed to commit transaction: {e}")
                await self.rollback()
                raise e

    async def rollback(self) -> None:
        """Rollback current transaction."""
        if self._session:
            try:
                await self._session.rollback()
                logger.debug("Transaction rolled back")
            except Exception as e:
                logger.error(f"Failed to rollback transaction: {e}")
                raise e

    async def refresh(self, obj) -> None:
        """Refresh object from database.

        Args:
            obj: Database object to refresh.
        """
        if self._session:
            await self._session.refresh(obj)


async def get_uow() -> AsyncGenerator[UnitOfWorkConnection, None]:
    """FastAPI dependency to get Unit of Work instance.

    Yields:
        UnitOfWorkConnection: Unit of Work instance.
    """
    async with UnitOfWorkConnection() as uow:
        yield uow

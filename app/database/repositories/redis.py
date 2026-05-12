import json

from redis.asyncio import Redis

from app.core.logger import logger
from app.core.settings import get_settings
from app.exceptions.exceptions import RepositoryError

TWO_HOURS = 7200
settings = get_settings()


class RedisRepository:
    def __init__(self, ttl=TWO_HOURS) -> None:
        self._client = None
        self.ttl = ttl

    async def _get_client(self) -> Redis:
        if self._client is None:
            self._client = Redis(
                host=settings.REDIS_HOST,
                port=settings.REDIS_PORT,
                decode_responses=True,
            )
        return self._client

    async def create(self, key, value):
        try:
            client = await self._get_client()
            return await client.set(key, json.dumps(value), ex=self.ttl)
        except Exception as error:
            logger.error(
                "Error setting cache",
                exc_info=True,
                extra={"error": error},
            )
            raise RepositoryError

    async def get(self, key):
        try:
            client = await self._get_client()
            if not await client.exists(key):
                return None
            value = await client.get(key)
            return json.loads(value)
        except Exception as error:
            logger.error(
                f"Error get cache - {error}",
                exc_info=True,
                extra={"error": error},
            )
            return None

    async def delete(self, key):
        try:
            client = await self._get_client()
            return await client.delete(key)
        except Exception as error:
            logger.error(
                f"Error deleting cache - {error}",
                exc_info=True,
                extra={"error": error},
            )
            raise RepositoryError

    async def close(self):
        if self._client is not None:
            await self._client.close()
            self._client = None

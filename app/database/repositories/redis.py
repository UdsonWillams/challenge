import json

from redis import Redis

from app.core.logger import logger
from app.core.settings import get_settings
from app.exceptions.exceptions import RepositoryError

TWO_HOURS = 7200
settings = get_settings()


class RedisRepository:
    def __init__(self, ttl=TWO_HOURS) -> None:
        self.client = Redis(
            host=settings.REDIS_HOST, port=settings.REDIS_PORT, decode_responses=True
        )
        self.ttl = ttl

    def create(self, key, value):
        try:
            return self.client.set(key, json.dumps(value), ex=self.ttl)
        except Exception as error:
            logger.error(
                "Error setting cache",
                exc_info=True,
                stack_info=True,
                extra={"error": error},
            )
            raise RepositoryError

    def get(self, key):
        try:
            if not self.client.exists(key):
                return None
            value = self.client.get(key)
            decoded_value = json.loads(value)
            return decoded_value
        except Exception as error:
            logger.error(
                f"Error get cache - {error}",
                exc_info=True,
                stack_info=True,
                extra={"error": error},
            )
            return None

    def delete(self, key):
        try:
            return self.client.delete(key)
        except Exception as error:
            logger.error(
                f"Error deleting cache - {error}",
                exc_info=True,
                stack_info=True,
                extra={"error": error},
            )
            raise RepositoryError

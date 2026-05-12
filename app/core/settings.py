from datetime import timedelta
from functools import lru_cache

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    model_config = {"extra": "ignore"}

    APP_CORS: str = "*"

    @property
    def APP_CORS_LIST(self):
        return self.APP_CORS.split(";")

    APP_ENVIRONMENT: str = "production"
    LOG_ENVIRONMENT: str = "INFO"
    HOST: str = "localhost"
    PORT: str = "8000"
    WORKERS: int = 3

    APP_MIGRATIONS_FOLDER: str = "./migrations"

    POSTGRES_USER: str = "myuser"
    POSTGRES_PASSWORD: str = "mypassword"
    POSTGRES_DB: str = "challenger_db"
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: str = "5432"

    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379

    @property
    def DATABASE_URL(self):
        return f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"

    @property
    def DATABASE_URL_SYNC(self):
        return f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"

    EXTERNAL_PRODUCTS_BASE_URL: str = "https://serverest.dev"

    SECRET_KEY: str = "sua-chave-secreta-super-segura-aqui-mude-em-producao"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    @property
    def ACCESS_TOKEN_EXPIRE_DELTA(self) -> timedelta:
        return timedelta(minutes=self.ACCESS_TOKEN_EXPIRE_MINUTES)

    @property
    def REFRESH_TOKEN_EXPIRE_DELTA(self) -> timedelta:
        return timedelta(days=self.REFRESH_TOKEN_EXPIRE_DAYS)

    ADMIN_DEFAULT_EMAIL: str = "admin@mail.com"
    ADMIN_DEFAULT_PASSWORD: str = "pass@word"
    ADMIN_DEFAULT_ROLE: str = "admin"

    RATE_LIMIT_PER_SECOND: int = 5
    RATE_LIMIT_PER_MINUTE: int = 60
    RATE_LIMIT_PER_HOUR: int = 1000


@lru_cache
def get_settings() -> Settings:
    return Settings(_env_file=".env", _env_file_encoding="utf-8")

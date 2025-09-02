from datetime import timedelta
from functools import lru_cache

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Settings Configuration
    model_config = {"extra": "ignore"}

    # Application Configuration
    APP_CORS: str = "*"

    @property
    def APP_CORS_LIST(self):
        return self.APP_CORS.split(";")

    APP_ENVIRONMENT: str = "production"
    LOG_ENVIROMENT: str = "INFO"
    HOST: str = "localhost"
    PORT: str = "8000"
    WORKERS: int = 3

    # Alembic
    APP_MIGRATIONS_FOLDER: str = "./migrations"

    # Mongo
    MONGO_USER: str = "root"
    MONGO_PASSWORD: str = "pass"
    MONGO_PORT: int = 27017

    # Database
    POSTGRES_USER: str = "myuser"
    POSTGRES_PASSWORD: str = "mypassword"
    POSTGRES_DB: str = "challenger_db"
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: str = "5432"

    # Redis
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379

    @property
    def DATABASE_URL(self):  # pragma: no cover
        return f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"

    @property
    def DATABASE_URL_SYNC(self):  # pragma: no cover
        return f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"

    # fake store api
    EXTERNAL_PRODUCTS_BASE_URL: str = "https://serverest.dev"

    # Security (pode sobrescrever via .env: SECRET_KEY, ACCESS_TOKEN_EXPIRE_MINUTES)
    SECRET_KEY: str = "sua-chave-secreta-super-segura-aqui-mude-em-producao"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    @property
    def ACCESS_TOKEN_EXPIRE_DELTA(self) -> timedelta:
        return timedelta(minutes=self.ACCESS_TOKEN_EXPIRE_MINUTES)

    # Admin to validations purposes
    ADMIN_DEFAULT_EMAIL: str = "admin@mail.com"
    ADMIN_DEFAULT_PASSWORD: str = "pass@word"
    ADMIN_DEFAULT_ROLE: str = "admin"


@lru_cache
def get_settings() -> Settings:
    return Settings(_env_file=".env", _env_file_encoding="utf-8")

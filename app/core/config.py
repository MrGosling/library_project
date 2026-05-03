from functools import lru_cache

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    postgres_user: str = 'POSTGRES_USER'
    postgres_password: str = 'POSTGRES_PASSWORD'
    postgres_db: str = 'POSTGRES_DB'
    postgres_host: str = 'POSTGRES_HOST'
    postgres_port: int = 'POSTGRES_PORT'

    @property
    def database_url(self) -> str:
        return f'postgresql+asyncpg://{self.postgres_user}:{self.postgres_password}@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}'

    secret: str = 'your-secret-key-here'
    first_superuser_email: str | None = 'FIRST_SUPERUSER_EMAIL'
    first_superuser_password: str | None = 'FIRST_SUPERUSER_PASSWORD'

    model_config = {'env_file': '.env', 'env_file_encoding': 'utf-8', 'extra': 'ignore'}


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings: Settings = get_settings()

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DB_HOST: str = "localhost"
    REDIS_HOST: str = "localhost"
    RABBITMQ_HOST: str = "localhost"

    @property
    def postgres_dsn(self) -> str:
        return f"postgresql+asyncpg://postgres:postgres@{self.DB_HOST}:5432/betmaker"

    @property
    def redis_dsn(self) -> str:
        return f"redis://{self.REDIS_HOST}:6379/1"

    @property
    def rabbitmq_host(self) -> str:
        return f"amqp://guest:guest@{self.RABBITMQ_HOST}:5672/"


settings = Settings()
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    RABBITMQ_HOST: str = 'localhost'

    @property
    def rabbitmq_host(self) -> str:
        return f"amqp://guest:guest@{self.RABBITMQ_HOST}:5672/"


settings = Settings()
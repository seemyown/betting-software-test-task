from typing import AsyncGenerator

from redis.asyncio import Redis
from app.infrastructure.settings import settings


async def get_redis() -> AsyncGenerator:
    redis = Redis.from_url(settings.redis_dsn)
    yield redis
    await redis.close()
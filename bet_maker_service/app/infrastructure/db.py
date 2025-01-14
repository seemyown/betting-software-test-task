from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from app.infrastructure.settings import settings

engine = create_async_engine(
    settings.postgres_dsn
)

async_sessionmaker = async_sessionmaker(bind=engine, autocommit=False, expire_on_commit=False)


async def get_db() -> AsyncGenerator:
    async with async_sessionmaker() as session:
        yield session
        await session.close()
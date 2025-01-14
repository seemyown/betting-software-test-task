from typing import Protocol, TypeVar

from pydantic import BaseModel

T = TypeVar("T", bound=BaseModel)


class BaseStorage(Protocol):
    async def add(self, data: T) -> None:
        raise NotImplementedError()

    async def get(self, field_name: str, field_value: str) -> T:
        raise NotImplementedError()

    async def get_all(self) -> list[T]:
        raise NotImplementedError()

from typing import Union

from storage.storage import BaseStorage, T
from app_types import EventState


class LocalStorage(BaseStorage):
    def __init__(self):
        self.data_list: list[Union[T, None]] = list()

    async def add(self, data: T) -> None:
        self.data_list.append(data)

    async def get_all(self) -> list[T]:
        return self.data_list

    async def get(self, field_name: str, field_value: str) -> T | None:
        for data in self.data_list:
            try:
                if getattr(data, field_name) == field_value:
                    return data
                else:
                    return None
            except AttributeError:
                return None

    async def update_state(self, event_id: str, new_state: EventState) -> None:
        event = await self.get("event_id", event_id)
        if event is None:
            return
        self.data_list.remove(event)
        event.state = new_state
        return
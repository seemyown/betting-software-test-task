import asyncio
import random
import time
import uuid
from decimal import Decimal

from fastapi import Depends
from faststream.rabbit import RabbitBroker
from icecream import ic

from storage.local_storage import LocalStorage
from storage.storage import BaseStorage
from app_types import EventModel, EventState


class EventProvider:
    _storage: LocalStorage

    def __init__(self, storage: LocalStorage):
        self._storage = storage

    async def create_new_event(self, coefficient: float, deadline: int, broker: RabbitBroker) -> EventModel:
        event_id: str = str(uuid.uuid4())
        event = EventModel(
            event_id=event_id,
            coefficient=coefficient,
            deadline=deadline,
            state=EventState.NEW,
        )
        ic(f"Создано новое событие: {event}")
        await self._storage.add(event)
        await broker.publish(
            event, queue="events.new"
        )
        ic("Новое событие опубликовано")
        return event

    async def update_event(self, event_id: str, new_state: EventState, broker: RabbitBroker):
        ic(f"Изменение события <{event_id}> => {new_state.name}")
        await self._storage.update_state(event_id, new_state)
        message = {
            "event_id": event_id,
            "state": new_state.value
        }
        await broker.publish(
            message, queue="events.close"
        )

    async def event_factory(self, broker: RabbitBroker):
        while True:
            await self.create_new_event(
                coefficient=round(random.random() + 1.01, 2),
                deadline=int(time.time() + random.randint(60, 120)),
                broker=broker
            )
            await asyncio.sleep(random.randint(5, 15))

    async def event_controller(self, broker: RabbitBroker):
        possible_exodus = [EventState.FINISHED_WIN, EventState.FINISHED_LOSE]
        while True:
            events: list[EventModel] = await self._storage.get_all()
            for event in events:
                if event.state == EventState.NEW:
                    continue
                if event.deadline < time.time():
                    event_exodus: EventState = random.choice(possible_exodus)
                    ic(f"Событие <{event.event_id}> завершилось со статусом {event_exodus.name}")
                    await self.update_event(event.event_id, event_exodus, broker)
                else:
                    continue
            await asyncio.sleep(5)


async def get_provider(storage: LocalStorage = Depends()):
    return EventProvider(storage)

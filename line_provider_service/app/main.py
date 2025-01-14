import asyncio
from faststream import FastStream
from faststream.rabbit import RabbitBroker

from services.event_provider import EventProvider
from storage.local_storage import LocalStorage
from settings import settings

broker = RabbitBroker(settings.rabbitmq_host)
app = FastStream(broker)


@app.on_startup
async def line_provider():
    provider = EventProvider(LocalStorage())
    await broker.connect()

    await asyncio.gather(
        provider.event_factory(broker),
        provider.event_controller(broker)
    )

if __name__ == '__main__':
    asyncio.run(app.run())
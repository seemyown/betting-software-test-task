import json
import time
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI, HTTPException
from fastapi.params import Depends
from faststream.rabbit.fastapi import RabbitRouter
from redis.asyncio import Redis

from app.infrastructure.redis import get_redis
from app.infrastructure.settings import settings
from app.models.models import EventModel, BetModel, BetDTO
from app.repository.models import create_tables
from app.service.bet_service import BettingService, get_bet_service

@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncGenerator:
    await create_tables()
    yield

app = FastAPI(
    title="Betting Maker", lifespan=lifespan
)

rabbit_router = RabbitRouter(settings.rabbitmq_host)


@rabbit_router.get("/events")
async def get_events(redis: Redis = Depends(get_redis)) -> list[dict[str, Any]]:
    events_ids: list[str | None] = await redis.keys("eventID::*")
    events: list[dict] = list()
    for event_id in events_ids:
        event_encode: bytes | None = await redis.get(event_id)
        if event_encode:
            event: str = event_encode.decode()
            events.append(json.loads(event.replace("'", '"')))
    return events


@rabbit_router.post("/bet")
async def bet_event(
        body: BetModel, redis: Redis = Depends(get_redis),
        service: BettingService = Depends(get_bet_service)
) -> dict[str, int]:
    try:
        return await service.create_bet(body, redis)
    except service.EventNotFound as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e),
        )


@rabbit_router.get("/bets")
async def get_bets(
        offset: int = 0, limit: int = 20,
        service: BettingService = Depends(get_bet_service)
) -> list[BetDTO]:
    try:
        return await service.get_bets(offset, limit)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@rabbit_router.subscriber("events.new")
async def new_event(data: EventModel, redis: Redis = Depends(get_redis)) -> None:
    ttl: int = int(data.deadline - time.time())
    await redis.setex(f"eventID::{data.event_id}", time=ttl, value=str(data.model_dump(mode="json")))



@rabbit_router.subscriber("events.close")
async def new_event(data: EventModel, service: BettingService = Depends(get_bet_service)) -> None:
    event_id = data.event_id
    state = data.state
    await service.set_bet_status(event_id, state)

app.include_router(rabbit_router)
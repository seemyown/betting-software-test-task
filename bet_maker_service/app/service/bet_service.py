import asyncio
import json

from fastapi import Depends
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.db import get_db
from app.models.models import BetModel, EventState, BetDTO
from app.repository.models import Bets
from app.repository.repository import BetRepository


class BettingService:
    def __init__(self, repository: BetRepository):
        self._repository = repository

    class EventNotFound(Exception):
        pass

    async def create_bet(self, bet: BetModel, redis: Redis) -> dict[str, int]:
        event_decoded = await redis.get(f"eventID::{bet.event_id}")
        if not event_decoded:
            raise self.EventNotFound(f"Событие {bet.event_id} не найдено")
        event: dict[str, str | int] = json.loads(event_decoded.decode().replace("'", '"'))
        bet_dto = BetDTO(
            event_id=bet.event_id,
            bet_sum=bet.bet_sum,
            coefficient=event.get("coefficient", 1),
            status=event.get("state", EventState.NEW),
        )
        bet_id: int = await self._repository.create_bet(bet_dto)
        return dict(id=bet_id)

    async def get_bets(self, offset: int, limit: int) -> list[BetDTO]:
        bets: list[Bets] = await self._repository.get_all(offset, limit)
        if not bets:
            return list()
        return list(
            bet.dump for bet in bets
        )

    async def set_bet_status(self, event_id: str, status: EventState):
        bets_on_event: list[Bets] = await self._repository.get_bets_by_event_id(event_id)
        if not bets_on_event:
            return
        tasks = list()
        for bet in bets_on_event:
            new_data = dict(status=status, event_id=event_id)
            if status == EventState.FINISHED_WIN:
                new_data["payout"] = bet.bet_sum * bet.coefficient
            else:
                new_data["payout"] = 0
            tasks.append(self._repository.set_status(**new_data))
        await asyncio.gather(*tasks)
        await self._repository.commit()


async def get_bet_service(session: AsyncSession = Depends(get_db)) -> BettingService:
    return BettingService(BetRepository(session))
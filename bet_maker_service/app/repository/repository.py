from icecream import ic
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.models import BetDTO, EventState
from app.repository.models import Bets


class BetRepository:
    def __init__(self, session: AsyncSession):
        self._session = session

    async def create_bet(self, data: BetDTO) -> int:
        new_bet = Bets(
            **data.model_dump(exclude={"id"}),
        )
        self._session.add(new_bet)
        await self._session.flush()
        bet_id: int = new_bet.id
        await self._session.commit()
        return bet_id

    async def get_all(self, offset: int, limit: int) -> list[Bets]:
        statement = select(Bets).offset(offset).limit(limit)
        result = await self._session.execute(statement)
        return list(result.scalars().all())

    async def get_bets_by_event_id(self, event_id: str) -> list[Bets]:
        statement = select(Bets).filter_by(event_id=event_id)
        result = await self._session.execute(statement)
        return list(result.scalars().all())

    async def set_status(self, event_id: str, status: EventState, payout: float) -> None:
        ic(f"Установка статуса для {event_id} {status.value}")
        statement = update(Bets).filter_by(event_id=event_id).values(
            status=status,
            payout=payout,
        )
        await self._session.execute(statement)

    async def commit(self) -> None:
        await self._session.commit()


from sqlalchemy import BigInteger
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from app.infrastructure.db import engine
from app.models.models import EventState, BetDTO


class Base(DeclarativeBase):
    pass


class Bets(Base):
    __tablename__ = 'bets'

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    event_id: Mapped[str] = mapped_column(unique=True)
    coefficient: Mapped[float]
    bet_sum: Mapped[float]
    payout: Mapped[float] = mapped_column(default=0)
    status: Mapped[EventState]

    @property
    def dump(self) -> BetDTO:
        return BetDTO(
            event_id=self.event_id,
            coefficient=self.coefficient,
            bet_sum=self.bet_sum,
            payout=self.payout,
            status=self.status,
            id=self.id
        )

async def create_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


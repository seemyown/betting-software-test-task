import decimal
import enum
from typing import Optional

from fastapi import HTTPException
from pydantic import BaseModel, field_validator
from pydantic_core import ValidationError


class EventState(enum.Enum):
    NEW = 1
    FINISHED_WIN = 2
    FINISHED_LOSE = 3


class EventCreateModel(BaseModel):
    coefficient: Optional[float] = None
    deadline: Optional[int] = None


class EventModel(EventCreateModel):
    event_id: str
    state: Optional[EventState] = None



class BetModel(BaseModel):
    event_id: str
    bet_sum: float

    @field_validator("bet_sum")
    def validate_bet_sum(cls, v):
        if v <= 0:
            raise HTTPException(status_code=422, detail="Число должно быть положительное")

        if round(v, 2) != v:
            raise HTTPException(status_code=422, detail="Число должно иметь не более двух знаков после запятой")

        return v

class BetDTO(BaseModel):
    id: Optional[int] = None
    event_id: str
    coefficient: float
    bet_sum: float
    payout: float = 0
    status: EventState

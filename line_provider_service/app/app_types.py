import decimal
import enum
from typing import Optional

from pydantic import BaseModel, NonNegativeFloat


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

from pydantic import BaseModel
from models import BaseEntity, EntityId
from typing import ClassVar
from datetime import datetime


class Seat(BaseEntity):
    entity_id_prefix: ClassVar[str] = 's'

    event_id: EntityId
    seat_number: str
    price: float
    is_available: bool

    created_at: datetime | None = None
    updated_at: datetime | None = None


class CreateSeatRequest(BaseModel):
    event_id: str
    seat_number: str
    price: float

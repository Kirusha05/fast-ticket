from enum import Enum
from pydantic import BaseModel, model_validator
from datetime import datetime
from models import BaseEntity
from typing import ClassVar
from models import EventTier, EventSeat


class EventType(str, Enum):
    OPEN_FIELD = "open_field"
    SEATED = "seated"


class Event(BaseEntity):
    entity_id_prefix: ClassVar[str] = 'e'

    name: str
    description: str
    venue: str
    event_date: datetime
    event_type: EventType

    # Open field events use these
    total_tickets: int | None = None
    available_tickets: int | None = None

    # Join fields
    seats: list[EventSeat] = []
    tiers: list[EventTier] = []

    created_at: datetime | None = None
    updated_at: datetime | None = None


class EventSeatInput(BaseModel):
    seat_number: str
    price: float


class EventTierInput(BaseModel):
    name: str
    price: float
    total_tickets: int


class CreateEventRequest(BaseModel):
    name: str
    description: str
    venue: str
    event_date: datetime
    event_type: EventType
    seats: list[EventSeatInput] = []
    tiers: list[EventTierInput] = []

    @model_validator(mode='after')
    def validate_event_type(self):
        if self.event_type == EventType.SEATED and not self.seats:
            raise ValueError("Seated events require seats")
        if self.event_type == EventType.OPEN_FIELD and not self.tiers:
            raise ValueError("Open field events require tiers")
        return self


class UpdateEventRequest(BaseModel):
    name: str | None
    description: str | None
    venue: str | None
    event_date: datetime | None

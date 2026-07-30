from enum import Enum
from pydantic import BaseModel, model_validator
from datetime import datetime
from models import BaseEntity
from typing import ClassVar
from models import EventTier, EventSeat


class EventType(str, Enum):
    TIERED = "tiered"
    SEATED = "seated"


class Event(BaseEntity):
    entity_id_prefix: ClassVar[str] = 'e'

    name: str
    description: str
    venue: str
    event_date: datetime
    event_type: EventType
    banner_url: str

    # Tiered events use these
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
    banner_url: str
    seats: list[EventSeatInput] = []
    tiers: list[EventTierInput] = []

    @model_validator(mode='after')
    def validate_event_type(self):
        if self.event_type == EventType.SEATED and not self.seats:
            raise ValueError("Seated events require seats")
        if self.event_type == EventType.TIERED and not self.tiers:
            raise ValueError("Tiered events require tiers")
        return self


class UpdateEventRequest(BaseModel):
    name: str | None
    description: str | None
    venue: str | None
    event_date: datetime | None
    banner_url: str | None

from enum import Enum
from pydantic import BaseModel
from datetime import datetime
from models import BaseEntity
from typing import ClassVar


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

    created_at: datetime | None = None
    updated_at: datetime | None = None


class CreateEventRequest(BaseModel):
    name: str
    description: str
    venue: str
    event_date: datetime
    event_type: EventType
    total_tickets: int | None = None

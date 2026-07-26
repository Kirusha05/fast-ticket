from pydantic import BaseModel, model_validator
from datetime import datetime
from models import BaseEntity, EntityId, Event, EventSeat, EventTier, Booking
from typing import ClassVar
from enum import Enum


class TicketStatus(str, Enum):
    UNUSED = "unused"
    USED = "used"


class Ticket(BaseEntity):
    entity_id_prefix: ClassVar[str] = "t"

    booking_id: EntityId
    event_id: EntityId

    # Exactly one of these two must be set
    seat_id: EntityId | None = None
    tier_id: EntityId | None = None

    status: TicketStatus
    checked_in_at: datetime | None = None

    # Join fields
    event: Event | None = None
    seat: EventSeat | None = None
    tier: EventTier | None = None

    created_at: datetime | None = None
    updated_at: datetime | None = None

    @model_validator(mode="after")
    def validate_seat_xor_tier(self) -> "Ticket":
        has_seat = self.seat_id is not None
        has_tier = self.tier_id is not None
        if has_seat == has_tier:
            raise ValueError(
                "Ticket must have exactly one of seat_id or tier_id."
            )
        return self


class ValidateTicketRequest(BaseModel):
    ticket_id: str
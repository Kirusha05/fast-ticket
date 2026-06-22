from pydantic import BaseModel, field_validator
from datetime import datetime
from models import BaseEntity, EntityId, Seat
from typing import ClassVar


class Booking(BaseEntity):
    entity_id_prefix: ClassVar[str] = 'b'

    user_id: EntityId
    event_id: EntityId
    status: str  # confirmed etc.

    # For open_field events
    ticket_count: int = None

    # Join fields
    booking_seats: list[Seat] = []

    created_at: datetime | None = None
    updated_at: datetime | None = None


class CreateBookingRequest(BaseModel):
    event_id: str
    seat_ids: list[str] = None
    ticket_count: int = None

    @field_validator('seat_ids', 'ticket_count', mode='after')
    @classmethod
    def validate_booking_type(cls, v, values, **kwargs):
        seat_ids = values.get('seat_ids')
        ticket_count = values.get('ticket_count')
        if seat_ids is None and ticket_count is None:
            raise ValueError("Must provide either seat_ids or ticket_count")
        if seat_ids is not None and ticket_count is not None:
            raise ValueError("Must provide only one of seat_ids or ticket_count")
        if ticket_count is not None and ticket_count < 1:
            raise ValueError("ticket_count must be at least 1")
        return v

from pydantic import BaseModel, model_validator
from datetime import datetime
from models import BaseEntity, EntityId, Seat
from typing import ClassVar


class Booking(BaseEntity):
    entity_id_prefix: ClassVar[str] = 'b'

    user_id: EntityId
    event_id: EntityId
    status: str  # confirmed etc.
    ticket_count: int

    # Join fields
    booking_seats: list[Seat] = []

    created_at: datetime | None = None
    updated_at: datetime | None = None


# Booking.ticket_count will be derived either from ticket_count or len(sets_ids)
class CreateBookingRequest(BaseModel):
    event_id: str
    seat_ids: list[str] | None = None
    ticket_count: int | None = None

    @model_validator(mode='after')
    def validate_booking_type(self):
        if self.seat_ids is None and self.ticket_count is None:
            raise ValueError("Must provide either seat_ids or ticket_count")

        if self.seat_ids is not None and self.ticket_count is not None:
            raise ValueError("Must provide only one of seat_ids or ticket_count")

        return self

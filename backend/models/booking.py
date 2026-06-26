from pydantic import BaseModel, model_validator, Field
from datetime import datetime
from models import BaseEntity, EntityId, EventSeat, BookingTieredTicket
from typing import ClassVar


class Booking(BaseEntity):
    entity_id_prefix: ClassVar[str] = 'b'

    user_id: EntityId
    event_id: EntityId
    status: str  # confirmed etc.
    ticket_count: int
    total_price: float = 0.0

    # Join fields
    seated_tickets: list[EventSeat] = []
    tiered_tickets: list[BookingTieredTicket] = []

    created_at: datetime | None = None
    updated_at: datetime | None = None


class TicketInput(BaseModel):
    tier_id: str
    count: int


class CreateBookingRequest(BaseModel):
    event_id: str
    seat_ids: list[str] | None = None
    tiered_tickets: list[TicketInput] | None = None

    @model_validator(mode='after')
    def validate_booking_type(self):
        if self.seat_ids is None and self.tiered_tickets is None:
            raise ValueError("Must provide either seat_ids or tiered_tickets")

        if self.seat_ids is not None and self.tiered_tickets is not None:
            raise ValueError("Must provide only one of seat_ids or tiered_tickets")

        if self.seat_ids is not None and len(self.seat_ids) == 0:
            raise ValueError("seat_ids must not be empty")

        if self.tiered_tickets is not None:
            if len(self.tiered_tickets) == 0:
                raise ValueError("tiered_tickets must not be empty")
            for t in self.tiered_tickets:
                if t.count <= 0:
                    raise ValueError("Ticket count must be at least 1")

        return self
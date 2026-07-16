from pydantic import BaseModel, model_validator
from datetime import datetime
from models import BaseEntity, EntityId, Event, EventSeat, BookingTieredTicket
from typing import ClassVar
from enum import Enum


class BookingStatus(str, Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    PAYMENT_FAILED = "payment_failed"
    EXPIRED = "expired"
    CANCELLED = "cancelled"


class Booking(BaseEntity):
    entity_id_prefix: ClassVar[str] = "b"

    user_id: EntityId
    event_id: EntityId
    ticket_count: int
    total_price: float = 0.0
    currency: str = "usd"
    status: BookingStatus
    expires_at: datetime | None
    stripe_checkout_session_id: str | None
    stripe_payment_intent_id: str | None

    # Join fields
    event: Event | None = None
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

    @model_validator(mode="after")
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


class BookingEventSeat(BaseModel):
    id: EntityId
    seat_number: str
    price: float
    booking_id: EntityId
    is_available: bool


class BookingEventTier(BaseModel):
    id: EntityId
    tier_name: str
    unit_price: float
    booking_id: EntityId
    tier_id: EntityId


class BookingResponse(BaseModel):
    id: EntityId
    status: str
    ticket_count: int
    total_price: float
    event_id: EntityId

    event: Event | None = None
    seated_tickets: list[BookingEventSeat] = []
    tiered_tickets: list[BookingEventTier] = []

    created_at: datetime | None = None
    updated_at: datetime | None = None

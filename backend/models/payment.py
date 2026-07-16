from datetime import datetime
from models import BaseEntity, EntityId
from typing import ClassVar
from enum import Enum


class PaymentStatus(str, Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    PAYMENT_FAILED = "payment_failed"
    EXPIRED = "expired"
    CANCELLED = "cancelled"


class Payment(BaseEntity):
    entity_id_prefix: ClassVar[str] = "p"

    booking_id: EntityId
    stripe_checkout_session_id: str
    stripe_payment_intent_id: str | None
    amount_cents: int
    currency: str = "usd"
    status: PaymentStatus

    created_at: datetime | None = None
    updated_at: datetime | None = None
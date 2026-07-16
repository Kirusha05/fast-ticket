from datetime import datetime
from models import BaseEntity, EntityId
from typing import ClassVar
from enum import Enum
from pydantic import BaseModel


class PaymentStatus(str, Enum):
    PENDING = "pending"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    EXPIRED = "expired"


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


class PaymentSessionResponse(BaseModel):
    checkout_url: str
    session_id: str
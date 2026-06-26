from models import BaseEntity, EntityId
from typing import ClassVar
from datetime import datetime


class BookingTieredTicket(BaseEntity):
    entity_id_prefix: ClassVar[str] = 'bt'

    booking_id: EntityId
    ticket_tier_id: EntityId
    unit_price: float

    created_at: datetime | None = None
    updated_at: datetime | None = None
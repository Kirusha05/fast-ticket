from models import BaseEntity, EntityId
from typing import ClassVar
from datetime import datetime


class EventTier(BaseEntity):
    entity_id_prefix: ClassVar[str] = 'et'

    event_id: EntityId
    name: str
    price: float
    total_tickets: int
    available_tickets: int

    created_at: datetime | None = None
    updated_at: datetime | None = None
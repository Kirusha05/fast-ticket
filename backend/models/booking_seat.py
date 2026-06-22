from pydantic import BaseModel
from datetime import datetime
from models import  EntityId


class BookingSeat(BaseModel):
    booking_id: EntityId
    seat_id: EntityId
    created_at: datetime | None = None
    updated_at: datetime | None = None
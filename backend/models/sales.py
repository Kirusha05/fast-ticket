from pydantic import BaseModel
from models import EntityId
from datetime import datetime
from enum import Enum


class SalesGranularity(str, Enum):
    DAY = "day"
    WEEK = "week"
    MONTH = "month"


class SalesSummary(BaseModel):
    confirmed_revenue: float
    lost_revenue: float
    confirmed_bookings_count: int
    sold_tickets: int


class TimeSeriesPoint(BaseModel):
    timestamp: datetime
    revenue: float
    tickets_sold: int


class EventSalesSummary(BaseModel):
    event_id: EntityId
    event_name: str
    event_date: datetime
    confirmed_revenue: float
    sold_tickets: int
    confirmed_bookings_count: int
    sell_through_rate: float


class TierSalesSummary(BaseModel):
    tier_id: EntityId
    tier_name: str
    event_id: EntityId
    sold_tickets: int
    revenue: float
    sell_through_rate: float

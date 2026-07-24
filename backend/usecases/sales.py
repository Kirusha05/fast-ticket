from fastapi import HTTPException
from psycopg import AsyncConnection
from datetime import datetime
from repositories import SalesRepository
from models import EntityId, User, UserRole
from models.sales import SalesSummary, TimeSeriesPoint, EventSalesSummary, TierSalesSummary, SalesGranularity


class SalesUseCase:
    def __init__(self, db_session: AsyncConnection):
        self.db_session = db_session
        self._sales_repository = SalesRepository(db_session)

    async def get_sales_summary(
        self, user: User, start_date: datetime, end_date: datetime
    ) -> SalesSummary:
        if user.role != UserRole.ADMIN:
            raise HTTPException(status_code=403, detail="You are not allowed to perform this action")

        if start_date >= end_date:
            raise HTTPException(status_code=400, detail="start_date must be before end_date")

        summary = await self._sales_repository.get_sales_summary(start_date, end_date)
        if not summary:
            raise HTTPException(status_code=404, detail="No sales data found for the given period")
        return summary

    async def get_sales_over_time(
        self,
        user: User,
        start_date: datetime,
        end_date: datetime,
        granularity: SalesGranularity
    ) -> list[TimeSeriesPoint]:
        if user.role != UserRole.ADMIN:
            raise HTTPException(status_code=403, detail="You are not allowed to perform this action")

        if start_date >= end_date:
            raise HTTPException(status_code=400, detail="start_date must be before end_date")

        return await self._sales_repository.get_sales_over_time(start_date, end_date, granularity)

    async def get_top_events_sales(
        self, user: User, start_date: datetime, end_date: datetime, top_k: int
    ) -> list[EventSalesSummary]:
        if user.role != UserRole.ADMIN:
            raise HTTPException(status_code=403, detail="You are not allowed to perform this action")

        if start_date >= end_date:
            raise HTTPException(status_code=400, detail="start_date must be before end_date")

        if top_k <= 0:
            raise HTTPException(status_code=400, detail="top_k must be a positive integer")

        return await self._sales_repository.get_sales_summaries_for_top_k_events(start_date, end_date, top_k)

    async def get_event_sales_summary(
        self, user: User, event_id: EntityId, start_date: datetime, end_date: datetime
    ) -> EventSalesSummary:
        if user.role != UserRole.ADMIN:
            raise HTTPException(status_code=403, detail="You are not allowed to perform this action")

        if start_date >= end_date:
            raise HTTPException(status_code=400, detail="start_date must be before end_date")

        summary = await self._sales_repository.get_sales_summary_by_event_id(start_date, end_date, event_id)
        if not summary:
            raise HTTPException(status_code=404, detail="No sales data found for this event or date range")
        return summary

    async def get_event_tiers_sales_summaries(
        self, user: User, event_id: EntityId, start_date: datetime, end_date: datetime
    ) -> list[TierSalesSummary]:
        if user.role != UserRole.ADMIN:
            raise HTTPException(status_code=403, detail="You are not allowed to perform this action")

        if start_date >= end_date:
            raise HTTPException(status_code=400, detail="start_date must be before end_date")

        return await self._sales_repository.get_tiers_sales_summaries_by_event_id(event_id, start_date, end_date)

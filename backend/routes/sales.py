from fastapi import APIRouter, Depends, Query
from datetime import datetime

from usecases import SalesUseCase
from config.db_session import get_db_session
from models import User, EntityId
from models.sales import SalesSummary, TimeSeriesPoint, EventSalesSummary, TierSalesSummary, SalesGranularity
from routes.deps.auth import get_current_user

router = APIRouter()


@router.get("/summary")
async def get_sales_summary(
    start_date: datetime = Query(...),
    end_date: datetime = Query(...),
    db=Depends(get_db_session),
    user: User = Depends(get_current_user),
) -> SalesSummary:
    sales_use_case = SalesUseCase(db)
    result = await sales_use_case.get_sales_summary(user, start_date, end_date)
    return result


@router.get("/over-time")
async def get_sales_over_time(
    start_date: datetime = Query(...),
    end_date: datetime = Query(...),
    granularity: SalesGranularity = Query(SalesGranularity.DAY),
    db=Depends(get_db_session),
    user: User = Depends(get_current_user),
) -> list[TimeSeriesPoint]:
    sales_use_case = SalesUseCase(db)
    result = await sales_use_case.get_sales_over_time(user, start_date, end_date, granularity)
    return result


# must be defined before /events/{event_id}
@router.get("/events/top")
async def get_top_events_sales(
    start_date: datetime = Query(...),
    end_date: datetime = Query(...),
    top_k: int = Query(10, gt=0),
    db=Depends(get_db_session),
    user: User = Depends(get_current_user),
) -> list[EventSalesSummary]:
    sales_use_case = SalesUseCase(db)
    result = await sales_use_case.get_top_events_sales(user, start_date, end_date, top_k)
    return result


@router.get("/events/{event_id}")
async def get_event_sales_summary(
    event_id: str,
    start_date: datetime = Query(...),
    end_date: datetime = Query(...),
    db=Depends(get_db_session),
    user: User = Depends(get_current_user),
) -> EventSalesSummary:
    sales_use_case = SalesUseCase(db)
    event_id = EntityId.from_string(event_id)
    result = await sales_use_case.get_event_sales_summary(user, event_id, start_date, end_date)
    return result


@router.get("/events/{event_id}/tiers")
async def get_event_tiers_sales_summaries(
    event_id: str,
    start_date: datetime = Query(...),
    end_date: datetime = Query(...),
    db=Depends(get_db_session),
    user: User = Depends(get_current_user),
) -> list[TierSalesSummary]:
    sales_use_case = SalesUseCase(db)
    event_id = EntityId.from_string(event_id)
    result = await sales_use_case.get_event_tiers_sales_summaries(user, event_id, start_date, end_date)
    return result
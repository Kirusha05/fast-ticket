from fastapi import APIRouter, Depends, status
from usecases import EventsUseCase
from config.db_session import get_db_session
from models import Event, CreateEventRequest, EventType


router = APIRouter()

@router.get("/")
async def get_all_events(
    db=Depends(get_db_session),
    event_type: EventType | None = None,
):
    events_use_case = EventsUseCase(db)
    return await events_use_case.list_events(event_type)


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_event(
    event: CreateEventRequest, db=Depends(get_db_session)
) -> Event:
    events_use_case = EventsUseCase(db)
    result = await events_use_case.create(event)
    return result
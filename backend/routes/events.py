from fastapi import APIRouter, Depends, status
from usecases import EventsUseCase
from config.db_session import get_db_session
from models import Event, CreateEventRequest, EventType, User, EntityId
from routes.deps.auth import get_current_user
import time


router = APIRouter()

@router.get("")
async def get_all_events(
    db=Depends(get_db_session),
    event_type: EventType | None = None,
):
    events_use_case = EventsUseCase(db)
    # time.sleep(0.5)
    return await events_use_case.list_events(event_type)


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_event(
    event: CreateEventRequest, db=Depends(get_db_session),
    user: User =Depends(get_current_user)
) -> Event:
    events_use_case = EventsUseCase(db)
    result = await events_use_case.create(event)
    return result


@router.get("/{event_id}")
async def get_event(
    event_id: str,
    db=Depends(get_db_session),
) -> Event:
    events_use_case = EventsUseCase(db)
    event_id = EntityId.from_string(event_id)
    result = await events_use_case.get_event(event_id)
    # time.sleep(2)
    return result
from fastapi import HTTPException
from psycopg import AsyncConnection
from repositories import BookingsRepository, EventsRepository
from models import EntityId, Event, CreateEventRequest, UpdateEventRequest

class EventsUseCase:
    def __init__(self, db_session: AsyncConnection):
        self.db_session = db_session
        self._bookings_repository = BookingsRepository(db_session)
        self._events_repository = EventsRepository(db_session)

    async def create(self, event_request: CreateEventRequest) -> Event:
        new_event = Event(
            id=Event.generate_entity_id(),
            name=event_request.name,
            description=event_request.description,
            venue=event_request.venue,
            event_date=event_request.event_date,
            event_type=event_request.event_type,
            total_tickets=event_request.total_tickets,
            available_tickets=event_request.total_tickets
        )
        created_event = await self._events_repository.create(new_event)
        return created_event

    async def list_events(self) -> list[Event]:
        events = await self._events_repository.get_all()
        return events

    async def update_event(self, event_id: EntityId, event_request: UpdateEventRequest) -> Event:
        existing_event = await self._events_repository.get_by_id(event_id)
        if not existing_event:
            raise HTTPException(404, "Event not found")

        updated_event = Event(
            id=event_id,
            name=event_request.name if event_request.name else existing_event.name,
            description=event_request.description if event_request.description else existing_event.description,
            venue=event_request.venue if event_request.venue else existing_event.venue,
            event_date=event_request.event_date if event_request.event_date else existing_event.event_date,
            event_type=existing_event.event_type,
            total_tickets=existing_event.total_tickets,
            available_tickets=existing_event.available_tickets
        )
        updated_event = await self._events_repository.update(event_id, updated_event)
        return updated_event

    async def delete_event(self, event_id: EntityId) -> None:
        await self._events_repository.delete(event_id)

    async def get_event(self, event_id: EntityId) -> Event:
        existing_event = await self._events_repository.get_by_id(event_id)
        if not existing_event:
            raise HTTPException(404, "Event not found")
        return existing_event

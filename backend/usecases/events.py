from fastapi import HTTPException
from psycopg import AsyncConnection
from repositories import EventsRepository, EventSeatsRepository, EventTiersRepository
from models import EntityId, Event, EventSeat, EventTier, CreateEventRequest, UpdateEventRequest, EventType


class EventsUseCase:
    def __init__(self, db_session: AsyncConnection):
        self.db_session = db_session
        self._events_repository = EventsRepository(db_session)
        self._event_seats_repository = EventSeatsRepository(db_session)
        self._event_tiers_repository = EventTiersRepository(db_session)

    async def create(self, event_request: CreateEventRequest) -> Event:
        if event_request.event_type == EventType.SEATED:
            total_tickets = len(event_request.seats)
        elif event_request.event_type == EventType.OPEN_FIELD:
            total_tickets = sum(t.total_tickets for t in event_request.tiers)
        else:
            raise HTTPException(status_code=400, detail=f"Unknown event type: {event_request.event_type}")

        new_event = Event(
            id=Event.generate_entity_id(),
            name=event_request.name,
            description=event_request.description,
            venue=event_request.venue,
            event_date=event_request.event_date,
            event_type=event_request.event_type,
            banner_url=event_request.banner_url,
            total_tickets=total_tickets,
            available_tickets=total_tickets
        )
        created_event = await self._events_repository.create(new_event)

        if event_request.seats:
            seats = [
                EventSeat(
                    id=EventSeat.generate_entity_id(),
                    event_id=created_event.id,
                    seat_number=seat_input.seat_number,
                    price=seat_input.price,
                    is_available=True
                )
                for seat_input in event_request.seats
            ]
            await self._event_seats_repository.create_multiple(seats)

        if event_request.tiers:
            tiers = [
                EventTier(
                    id=EventTier.generate_entity_id(),
                    event_id=created_event.id,
                    name=tier_input.name,
                    price=tier_input.price,
                    total_tickets=tier_input.total_tickets,
                    available_tickets=tier_input.total_tickets
                )
                for tier_input in event_request.tiers
            ]
            await self._event_tiers_repository.create_multiple(tiers)

        return created_event

    async def list_events(self, event_type: EventType | None = None) -> list[Event]:
        events = await self._events_repository.get_all(event_type)
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
            banner_url=event_request.banner_url if event_request.banner_url else existing_event.banner_url,
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
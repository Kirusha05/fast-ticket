from fastapi import HTTPException
from psycopg import AsyncConnection
from repositories import BookingsRepository, EventsRepository, SeatsRepository, BookingSeatsRepository
from models import Booking, EntityId, Event, CreateBookingRequest, EventType, Seat


class BookingsUseCase:
    def __init__(self, db_session: AsyncConnection):
        self.db_session = db_session
        self._bookings_repository = BookingsRepository(db_session)
        self._events_repository = EventsRepository(db_session)
        self._seats_repository = SeatsRepository(db_session)
        self._booking_seats_repository = BookingSeatsRepository(db_session)

    async def create(self, user_id: EntityId, booking_request: CreateBookingRequest) -> Booking:
        event_id = EntityId.from_string(booking_request.event_id)
        
        event = await self._events_repository.get_by_id(event_id)
        if not event:
            raise HTTPException(status_code=404, detail="Event not found")
        
        if event.event_type == EventType.SEATED:
            if not booking_request.seat_ids:
                raise HTTPException(status_code=400, detail="Seated events require seat_ids")
            return await self._create_seated_booking(user_id, event, booking_request)
        
        elif event.event_type == EventType.OPEN_FIELD:
            if booking_request.ticket_count is None:
                raise HTTPException(status_code=400, detail="Open field events require ticket_count")
            return await self._create_open_field_booking(user_id, event, booking_request)
        
        else:
            raise HTTPException(status_code=400, detail=f"Unknown event type: {event.event_type}")

    async def _create_seated_booking(
        self, user_id: EntityId, event: Event, booking_request: CreateBookingRequest
    ) -> Booking:
        seat_ids = [EntityId.from_string(sid) for sid in booking_request.seat_ids]
        
        seats = await self._seats_repository.get_seats_by_ids_for_update(seat_ids)
        
        if len(seats) != len(seat_ids):
            missing_seat_ids = set(sid.value for sid in seat_ids) - set(s.id.value for s in seats)
            missing_seat_ids = [str(Seat.build_entity_id_from_uuid(seat_id)) for seat_id in missing_seat_ids]
            raise HTTPException(status_code=404, detail=f"Seats not found: {", ".join(missing_seat_ids)}")
        
        for seat in seats:
            if seat.event_id.value != event.id.value:
                raise HTTPException(
                    status_code=400,
                    detail=f"Seat {seat.id} does not belong to event {event.id}"
                )
        
        unavailable_seats = [s for s in seats if not s.is_available]
        if unavailable_seats:
            unavailable_seat_numbers = [s.seat_number for s in unavailable_seats]
            raise HTTPException(
                status_code=409,
                detail=f"One or more seats are already taken: {', '.join(unavailable_seat_numbers)}"
            )
        
        booking = Booking(
            id=Booking.generate_entity_id(),
            user_id=user_id,
            event_id=event.id,
            status="confirmed",
            ticket_count=len(seats),
            booking_seats=seats
        )
        
        created_booking = await self._bookings_repository.create(booking)
        if not created_booking:
            raise HTTPException(status_code=500, detail="Failed to create booking")
        
        await self._seats_repository.mark_seats_as_unavailable(seat_ids)
        await self._booking_seats_repository.create_multiple(created_booking.id, seat_ids)
        await self._events_repository.decrement_available_tickets(
            event.id, booking.ticket_count
        )
        
        final_booking = await self._bookings_repository.get_by_id(created_booking.id)
        return final_booking

    async def _create_open_field_booking(
        self, user_id: EntityId, event: Event, booking_request: CreateBookingRequest
    ) -> Booking:
        ticket_count = booking_request.ticket_count
        
        if ticket_count <= 0:
            raise HTTPException(status_code=400, detail="Ticket count must be at least 1")
        
        if event.total_tickets is None or event.available_tickets is None:
            raise HTTPException(
                status_code=400,
                detail="Event is not properly configured for open field bookings"
            )
        
        if ticket_count > event.available_tickets:
            raise HTTPException(
                status_code=409,
                detail=f"Not enough tickets available. Requested: {ticket_count}, Available: {event.available_tickets}"
            )
        
        success = await self._events_repository.decrement_available_tickets(event.id, ticket_count)
        
        if not success:
            raise HTTPException(
                status_code=409,
                detail="The last tickets were already booked by another user"
            )
        
        booking = Booking(
            id=Booking.generate_entity_id(),
            user_id=user_id,
            event_id=event.id,
            status="confirmed",
            ticket_count=ticket_count
        )
        
        created_booking = await self._bookings_repository.create(booking)
        if not created_booking:
            raise HTTPException(status_code=500, detail="Failed to create booking")
        
        return created_booking

    async def get_booking(self, user_id: EntityId, booking_id: EntityId) -> Booking:
        booking = await self._bookings_repository.get_by_id(booking_id)
        if not booking:
            raise HTTPException(status_code=404, detail="Booking not found")

        if booking.user_id.value != user_id.value:
            raise HTTPException(status_code=403, detail="You are not allowed to view this booking")

        return booking

    async def list_bookings(self) -> list[Booking]:
        return await self._bookings_repository.get_all()

    async def list_user_bookings(self, user_id: EntityId) -> list[Booking]:
        return await self._bookings_repository.get_by_user_id(user_id)

    async def list_event_bookings(self, event_id: EntityId) -> list[Booking]:
        return await self._bookings_repository.get_by_event_id(event_id)

    async def cancel_booking(self, user_id: EntityId, booking_id: EntityId) -> Booking:
        booking = await self._bookings_repository.get_by_id(booking_id)
        if not booking:
            raise HTTPException(status_code=404, detail="Booking not found")
        
        if booking.user_id.value != user_id.value:
            raise HTTPException(status_code=403, detail="You are not allowed to cancel this booking")
        
        if booking.status == "cancelled":
            raise HTTPException(status_code=400, detail="Booking already cancelled")
        
        event = await self._events_repository.get_by_id(booking.event_id)
        if not event:
            raise HTTPException(status_code=404, detail="Event no longer exists")
        
        if event.event_type == EventType.SEATED:
            seat_ids = [bs.id for bs in booking.booking_seats]
            if seat_ids:
                await self._seats_repository.mark_seats_as_available(seat_ids)
                await self._booking_seats_repository.delete_by_booking_id(booking_id)
                await self._events_repository.increment_available_tickets(
                    event.id, booking.ticket_count
                )
        
        elif event.event_type == EventType.OPEN_FIELD:
            if booking.ticket_count:
                await self._events_repository.increment_available_tickets(
                    event.id, booking.ticket_count
                )
        
        booking.status = "cancelled"
        updated_booking = await self._bookings_repository.update(booking_id, booking)
        return updated_booking
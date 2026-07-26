from fastapi import HTTPException
from psycopg import AsyncConnection
from repositories import TicketsRepository, BookingsRepository
from models import EntityId, Ticket, User, UserRole, TicketStatus, ValidateTicketRequest
from datetime import datetime, timezone


class TicketsUseCase:
    def __init__(self, db_session: AsyncConnection):
        self.db_session = db_session
        self._bookings_repository = BookingsRepository(db_session)
        self._tickets_repository = TicketsRepository(db_session)

    async def get_booking_tickets(self, user_id: EntityId, booking_id: EntityId) -> list[Ticket]:
        booking = await self._bookings_repository.get_by_id(booking_id)
        if not booking:
            raise HTTPException(status_code=404, detail="Booking not found")

        if booking.user_id.value != user_id.value:
            raise HTTPException(status_code=403, detail="You are not allowed access this booking")

        tickets = await self._tickets_repository.get_by_booking_id(booking_id)
        return tickets

    async def validate_ticket(self, user: User, validate_request: ValidateTicketRequest) -> bool:
        if user.role != UserRole.ADMIN:
            raise HTTPException(status_code=403, detail="You are not allowed to perform this action")

        ticket_id = EntityId.from_string(validate_request.ticket_id)
        ticket = await self._tickets_repository.get_by_id(ticket_id)
        if not ticket:
            raise HTTPException(status_code=404, detail="Ticket not found")

        ticket.status = TicketStatus.USED
        ticket.checked_in_at = datetime.now(timezone.utc)
        updated_ticket = await self._tickets_repository.update(ticket.id, ticket)
        return updated_ticket

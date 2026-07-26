# repositories/tickets.py
from repositories.base import BaseRepository
from psycopg import AsyncConnection
from models import Ticket, EntityId, Event, EventSeat, EventTier, Booking


class TicketsRepository(BaseRepository):
    def __init__(self, db_session: AsyncConnection):
        super().__init__(db_session)

    def _map_db_model_to_entity(self, ticket_row) -> Ticket:
        return Ticket(
            id=Ticket.build_entity_id_from_uuid(ticket_row["id"]),
            booking_id=Booking.build_entity_id_from_uuid(ticket_row["booking_id"]),
            event_id=Event.build_entity_id_from_uuid(ticket_row["event_id"]),
            seat_id=EventSeat.build_entity_id_from_uuid(ticket_row["seat_id"]) if ticket_row.get("seat_id") else None,
            tier_id=EventTier.build_entity_id_from_uuid(ticket_row["tier_id"]) if ticket_row.get("tier_id") else None,
            status=ticket_row["status"],
            checked_in_at=ticket_row["checked_in_at"],
            created_at=ticket_row["created_at"],
            updated_at=ticket_row["updated_at"],
        )

    async def create(self, ticket: Ticket) -> Ticket | None:
        pass

    async def create_many(self, tickets: list[Ticket]) -> bool:
        values = [
            (
                t.id.value,
                t.booking_id.value,
                t.event_id.value,
                t.seat_id.value if t.seat_id else None,
                t.tier_id.value if t.tier_id else None,
                t.status,
                t.checked_in_at,
            )
            for t in tickets
        ]
        if not values:
            return False
        
        async with self.db_session.cursor() as cursor:
            await cursor.executemany("""
                INSERT INTO tickets (id, booking_id, event_id, seat_id, tier_id, status, checked_in_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, values)
            return True

    async def get_by_id(self, id: EntityId) -> Ticket | None:
        async with self.db_session.cursor() as cursor:
            await cursor.execute(
                "SELECT * FROM tickets WHERE id = %s",
                (id.value,),
            )
            db_ticket = await cursor.fetchone()
            if not db_ticket:
                return None
            return self._map_db_model_to_entity(db_ticket)

    async def get_by_booking_id(self, booking_id: EntityId) -> list[Ticket]:
        async with self.db_session.cursor() as cursor:
            await cursor.execute(
                "SELECT * FROM tickets WHERE booking_id = %s",
                (booking_id.value,),
            )
            db_tickets = await cursor.fetchall()
            return [self._map_db_model_to_entity(db_ticket) for db_ticket in db_tickets]

    async def get_all(self) -> list[Ticket]:
        pass

    # used for "how many checked in for this event"
    # async def get_checked_in_count_by_event_id(self, event_id: EntityId) -> int:
        # async with self.db_session.cursor() as cursor:
        #     await cursor.execute(
        #         "SELECT COUNT(*) AS count FROM tickets WHERE event_id = %s AND status = 'used'",
        #         (event_id.value,),
        #     )
        #     row = await cursor.fetchone()
        #     return row["count"] if row else 0

    async def update(self, id: EntityId, ticket: Ticket) -> Ticket | None:
        async with self.db_session.cursor() as cursor:
            await cursor.execute(
                """
                UPDATE tickets
                SET 
                    status = %s,
                    checked_in_at = %s,
                    updated_at = NOW()
                WHERE id = %s
                RETURNING *
                """,
                (ticket.status, ticket.checked_in_at, id.value),
            )
            db_ticket = await cursor.fetchone()
            if not db_ticket:
                return None
            return self._map_db_model_to_entity(db_ticket)

    async def delete(self, id: EntityId) -> bool:
        async with self.db_session.cursor() as cursor:
            await cursor.execute("DELETE FROM tickets WHERE id = %s", (id.value,))
            return cursor.rowcount > 0
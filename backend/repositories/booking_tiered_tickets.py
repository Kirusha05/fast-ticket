from repositories.base import BaseRepository
from psycopg import AsyncConnection
from models import BookingTieredTicket, EntityId, EventTier
from typing import Any


class BookingTieredTicketsRepository(BaseRepository):
    def __init__(self, db_session: AsyncConnection):
        super().__init__(db_session)

    def _map_db_model_to_entity(self, data: dict) -> BookingTieredTicket:
        return BookingTieredTicket(
            id=BookingTieredTicket.build_entity_id_from_uuid(data['id']),
            booking_id=BookingTieredTicket.build_entity_id_from_uuid(data['booking_id']),
            ticket_tier_id=EventTier.build_entity_id_from_uuid(data['ticket_tier_id']),
            unit_price=float(data['unit_price']),
            created_at=data['created_at'],
            updated_at=data['updated_at'],
        )

    async def create_multiple(self, booking_id: EntityId, tiered_tickets: list[dict[str, Any]]) -> bool:
        """
        Insert multiple tiered ticket rows for a booking.

        Each item in tiered_tickets must have keys:
          - tier_id: EntityId
          - unit_price: float
        """
        values = [
            (BookingTieredTicket.generate_entity_id().value,
             booking_id.value,
             t["tier_id"].value,
             t["unit_price"])
            for t in tiered_tickets
        ]
        if not values:
            return False
        async with self.db_session.cursor() as cursor:
            await cursor.executemany("""
                INSERT INTO booking_tiered_tickets (id, booking_id, ticket_tier_id, unit_price)
                VALUES (%s, %s, %s, %s)
            """, values)
            return True

    async def get_by_booking_id(self, booking_id: EntityId) -> list[BookingTieredTicket]:
        async with self.db_session.cursor() as cursor:
            await cursor.execute(
                "SELECT * FROM booking_tiered_tickets WHERE booking_id = %s",
                (booking_id.value,)
            )
            rows = await cursor.fetchall()
            return [self._map_db_model_to_entity(row) for row in rows]

    async def delete_by_booking_id(self, booking_id: EntityId) -> bool:
        async with self.db_session.cursor() as cursor:
            await cursor.execute(
                "DELETE FROM booking_tiered_tickets WHERE booking_id = %s",
                (booking_id.value,)
            )
            return cursor.rowcount > 0

    async def create(self, booking_id: EntityId, tier_id: EntityId, unit_price: float) -> BookingTieredTicket | None:
        async with self.db_session.cursor() as cursor:
            ticket_id = BookingTieredTicket.generate_entity_id()
            await cursor.execute("""
                INSERT INTO booking_tiered_tickets (id, booking_id, ticket_tier_id, unit_price)
                VALUES (%s, %s, %s, %s)
                RETURNING *
            """, (ticket_id.value, booking_id.value, tier_id.value, unit_price))
            row = await cursor.fetchone()
            if not row:
                return None
            return self._map_db_model_to_entity(row)

    async def get_by_id(self, ticket_id: EntityId) -> BookingTieredTicket | None:
        async with self.db_session.cursor() as cursor:
            await cursor.execute(
                "SELECT * FROM booking_tiered_tickets WHERE id = %s",
                (ticket_id.value,)
            )
            row = await cursor.fetchone()
            if not row:
                return None
            return self._map_db_model_to_entity(row)

    async def get_all(self) -> list[BookingTieredTicket]:
        async with self.db_session.cursor() as cursor:
            await cursor.execute("SELECT * FROM booking_tiered_tickets")
            rows = await cursor.fetchall()
            return [self._map_db_model_to_entity(row) for row in rows]

    async def update(self, ticket_id: EntityId, ticket: BookingTieredTicket) -> BookingTieredTicket | None:
        async with self.db_session.cursor() as cursor:
            await cursor.execute("""
                UPDATE booking_tiered_tickets
                SET unit_price = %s, updated_at = NOW()
                WHERE id = %s
                RETURNING *
            """, (ticket.unit_price, ticket_id.value))
            row = await cursor.fetchone()
            if not row:
                return None
            return self._map_db_model_to_entity(row)

    async def delete(self, ticket_id: EntityId) -> bool:
        async with self.db_session.cursor() as cursor:
            await cursor.execute(
                "DELETE FROM booking_tiered_tickets WHERE id = %s",
                (ticket_id.value,)
            )
            return cursor.rowcount > 0
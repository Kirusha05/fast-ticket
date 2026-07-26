from repositories.base import BaseRepository
from psycopg import AsyncConnection
from models import EntityId, EventSeat, BookingEventSeat, Booking
from typing import Any


class BookingSeatedTicketsRepository(BaseRepository):
    def __init__(self, db_session: AsyncConnection):
        super().__init__(db_session)

    async def create(self, booking_id: EntityId, seat_id: EntityId) -> bool:
        async with self.db_session.cursor() as cursor:
            await cursor.execute("""
                INSERT INTO booking_seated_tickets (booking_id, seat_id)
                VALUES (%s, %s)
                RETURNING *
            """, (booking_id.value, seat_id.value))
            return cursor.rowcount > 0

    async def create_many(self, booking_id: EntityId, seat_ids: list[EntityId]) -> bool:
        values = [
            (booking_id.value, seat_id.value)
            for seat_id in seat_ids
        ]
        if not values:
            return False

        async with self.db_session.cursor() as cursor:
            await cursor.executemany("""
                INSERT INTO booking_seated_tickets (booking_id, seat_id)
                VALUES (%s, %s)
            """, values)
            return True

    async def delete_by_booking_id(self, booking_id: EntityId) -> bool:
        async with self.db_session.cursor() as cursor:
            await cursor.execute(
                "DELETE FROM booking_seated_tickets WHERE booking_id = %s",
                (booking_id.value,)
            )
            return cursor.rowcount > 0

    async def delete_by_seat_id(self, seat_id: EntityId) -> bool:
        async with self.db_session.cursor() as cursor:
            await cursor.execute(
                "DELETE FROM booking_seated_tickets WHERE seat_id = %s",
                (seat_id.value,)
            )
            return cursor.rowcount > 0

    def _map_db_model_to_booking_event_seat(self, data) -> BookingEventSeat:
        return BookingEventSeat(
            id=EventSeat.build_entity_id_from_uuid(data['seat_id']),
            seat_number=data['seat_number'],
            price=float(data['price']),
            booking_id=Booking.build_entity_id_from_uuid(data['booking_id']),
            is_available=data['is_available']
        )

    async def get_seated_tickets_by_booking_ids(self, booking_ids: list[EntityId]) -> list[BookingEventSeat]:
        if not booking_ids:
            return []
        
        async with self.db_session.cursor() as cursor:
            await cursor.execute("""
                SELECT * FROM booking_seated_tickets bst
                LEFT JOIN event_seats es ON bst.seat_id = es.id
                WHERE booking_id = ANY(%s)
            """, ([id.value for id in booking_ids],))
            db_booking_seats = await cursor.fetchall()
            return [self._map_db_model_to_booking_event_seat(db_bs) for db_bs in db_booking_seats]

    # Stubs for abstract base class methods
    def _map_db_model_to_entity(self, data):
        pass

    async def get_by_id(self, id: EntityId) -> Any:
        pass

    async def get_all(self) -> list[Any]:
        pass

    async def update(self, id: EntityId, data: Any) -> Any:
        pass

    async def delete(self, id: EntityId, data: Any) -> Any:
        pass
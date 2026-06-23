from repositories.base import BaseRepository
from psycopg import AsyncConnection
from models import EntityId
from typing import Any


class BookingSeatsRepository(BaseRepository):
    def __init__(self, db_session: AsyncConnection):
        super().__init__(db_session)

    async def create(self, booking_id: EntityId, seat_id: EntityId) -> bool:
        async with self.db_session.cursor() as cursor:
            await cursor.execute("""
                INSERT INTO booking_seats (booking_id, seat_id)
                VALUES (%s, %s)
                RETURNING *
            """, (booking_id.value, seat_id.value))
            return cursor.rowcount > 0

    async def create_multiple(self, booking_id: EntityId, seat_ids: list[EntityId]) -> bool:
        async with self.db_session.cursor() as cursor:
            for seat_id in seat_ids:
                await cursor.execute("""
                    INSERT INTO booking_seats (booking_id, seat_id)
                    VALUES (%s, %s)
                """, (booking_id.value, seat_id.value))
            return len(seat_ids) > 0

    async def delete_by_booking_id(self, booking_id: EntityId) -> bool:
        async with self.db_session.cursor() as cursor:
            await cursor.execute(
                "DELETE FROM booking_seats WHERE booking_id = %s",
                (booking_id.value,)
            )
            return cursor.rowcount > 0

    async def delete_by_seat_id(self, seat_id: EntityId) -> bool:
        async with self.db_session.cursor() as cursor:
            await cursor.execute(
                "DELETE FROM booking_seats WHERE seat_id = %s",
                (seat_id.value,)
            )
            return cursor.rowcount > 0

    async def delete(self, booking_id: EntityId, seat_id: EntityId) -> bool:
        async with self.db_session.cursor() as cursor:
            await cursor.execute(
                "DELETE FROM booking_seats WHERE booking_id = %s AND seat_id = %s",
                (booking_id.value, seat_id.value)
            )
            return cursor.rowcount > 0

    # There need to be desined as this repository inherits from an abstract class
    def _map_db_model_to_entity(self, data):
        pass
    
    async def get_by_id(self, id: EntityId) -> Any:
        pass

    async def get_all(self) -> list[Any]:
        pass

    async def update(self, id: EntityId, data: Any) -> Any:
        pass
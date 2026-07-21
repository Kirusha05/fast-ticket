from repositories.base import BaseRepository
from psycopg import AsyncConnection
from models import EventSeat, EntityId, Event


class EventSeatsRepository(BaseRepository):
    def __init__(self, db_session: AsyncConnection):
        super().__init__(db_session)

    def _map_db_model_to_entity(self, data: dict) -> EventSeat:
        return EventSeat(
            id=EventSeat.build_entity_id_from_uuid(data['id']),
            event_id=Event.build_entity_id_from_uuid(data['event_id']),
            seat_number=data['seat_number'],
            price=float(data['price']),
            is_available=data['is_available'],
            created_at=data['created_at'],
            updated_at=data['updated_at']
        )

    async def create(self, seat: EventSeat) -> EventSeat | None:
        async with self.db_session.cursor() as cursor:
            await cursor.execute("""
                INSERT INTO event_seats (id, event_id, seat_number, price, is_available)
                VALUES (%s, %s, %s, %s, %s)
                RETURNING *
            """,
                (seat.id.value, seat.event_id.value, seat.seat_number,
                 seat.price, seat.is_available))
            db_seat = await cursor.fetchone()
            if not db_seat:
                return None
            return self._map_db_model_to_entity(db_seat)

    async def create_multiple(self, seats: list[EventSeat]) -> list[EventSeat]:
        if not seats:
            return []
        values = [
            (seat.id.value, seat.event_id.value, seat.seat_number,
             seat.price, seat.is_available)
            for seat in seats
        ]
        async with self.db_session.cursor() as cursor:
            await cursor.executemany("""
                INSERT INTO event_seats (id, event_id, seat_number, price, is_available)
                VALUES (%s, %s, %s, %s, %s)
            """, values)
            return seats

    async def get_by_id(self, id: EntityId) -> EventSeat | None:
        async with self.db_session.cursor() as cursor:
            await cursor.execute("SELECT * FROM event_seats WHERE id = %s", (id.value,))
            db_seat = await cursor.fetchone()
            if not db_seat:
                return None
            return self._map_db_model_to_entity(db_seat)

    async def get_all(self) -> list[EventSeat]:
        async with self.db_session.cursor() as cursor:
            await cursor.execute("SELECT * FROM event_seats")
            db_seats = await cursor.fetchall()
            return [self._map_db_model_to_entity(db_seat) for db_seat in db_seats]

    async def update(self, id: EntityId, seat: EventSeat) -> EventSeat | None:
        async with self.db_session.cursor() as cursor:
            await cursor.execute("""
                UPDATE event_seats
                SET event_id = %s, seat_number = %s, price = %s, is_available = %s, updated_at = NOW()
                WHERE id = %s
                RETURNING *
            """,
                (seat.event_id.value, seat.seat_number, seat.price,
                 seat.is_available, id.value))
            db_seat = await cursor.fetchone()
            if not db_seat:
                return None
            return self._map_db_model_to_entity(db_seat)

    async def delete(self, id: EntityId) -> bool:
        async with self.db_session.cursor() as cursor:
            await cursor.execute("DELETE FROM event_seats WHERE id = %s", (id.value,))
            return cursor.rowcount > 0

    async def get_seats_by_ids(self, seat_ids: list[EntityId]) -> list[EventSeat]:
        async with self.db_session.cursor() as cursor:
            await cursor.execute(
                "SELECT * FROM event_seats WHERE id = ANY(%s)",
                ([id.value for id in seat_ids],)
            )
            db_seats = await cursor.fetchall()
            return [self._map_db_model_to_entity(db_seat) for db_seat in db_seats]

    async def get_seats_by_ids_for_update(self, seat_ids: list[EntityId]) -> list[EventSeat]:
        async with self.db_session.cursor() as cursor:
            # ORDER BY id, so Postgres acquires locks in a predictable order
            await cursor.execute("""
                SELECT * FROM event_seats
                WHERE id = ANY(%s)
                ORDER BY id
                FOR UPDATE
            """, ([id.value for id in seat_ids],))
            db_seats = await cursor.fetchall()
            return [self._map_db_model_to_entity(db_seat) for db_seat in db_seats]

    async def mark_seats_as_unavailable(self, seat_ids: list[EntityId]) -> bool:
        async with self.db_session.cursor() as cursor:
            await cursor.execute("""
                UPDATE event_seats
                SET is_available = FALSE
                WHERE id = ANY(%s)
            """, ([id.value for id in seat_ids],))
            return cursor.rowcount > 0

    async def mark_seats_as_available(self, seat_ids: list[EntityId]) -> bool:
        async with self.db_session.cursor() as cursor:
            await cursor.execute("""
                UPDATE event_seats
                SET is_available = TRUE
                WHERE id = ANY(%s)
            """, ([id.value for id in seat_ids],))
            return cursor.rowcount > 0

    async def get_available_seats_by_event(self, event_id: EntityId) -> list[EventSeat]:
        async with self.db_session.cursor() as cursor:
            await cursor.execute(
                "SELECT * FROM event_seats WHERE event_id = %s AND is_available = TRUE",
                (event_id.value,)
            )
            db_seats = await cursor.fetchall()
            return [self._map_db_model_to_entity(db_seat) for db_seat in db_seats]
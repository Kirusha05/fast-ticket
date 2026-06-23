from repositories.base import BaseRepository
from psycopg import AsyncConnection
from models import Booking, EntityId, User, Event, Seat


class BookingsRepository(BaseRepository):
    def __init__(self, db_session: AsyncConnection):
        super().__init__(db_session)

    def _map_db_model_to_entity(self, booking_row, seats: list[Seat]) -> Booking:
        return Booking(
            id=Booking.build_entity_id_from_uuid(booking_row['id']),
            user_id=User.build_entity_id_from_uuid(booking_row['user_id']),
            event_id=Event.build_entity_id_from_uuid(booking_row['event_id']),
            status=booking_row['status'],
            ticket_count=booking_row.get('ticket_count'),
            booking_seats=seats,
            created_at=booking_row['created_at'],
            updated_at=booking_row['updated_at']
        )

    def _map_seat_row(self, data) -> list[Seat]:
        return Seat(
            id=Seat.build_entity_id_from_uuid(data['seat_id']),
            event_id=Event.build_entity_id_from_uuid(data['event_id']),
            seat_number=data['seat_number'],
            price=data['price'],
            is_available=data['is_available'],
            created_at=data['created_at'],
            updated_at=data['updated_at']
        )

    async def create(self, booking: Booking) -> Booking | None:
        async with self.db_session.cursor() as cursor:
            await cursor.execute("""
                INSERT INTO bookings (id, user_id, event_id, status, ticket_count)
                VALUES (%s, %s, %s, %s, %s)
                RETURNING *
            """,
                (booking.id.value, booking.user_id.value, booking.event_id.value,
                 booking.status, booking.ticket_count))
            db_booking = await cursor.fetchone()
            if not db_booking:
                return None
            return self._map_db_model_to_entity(db_booking, [])

    async def get_by_id(self, id: EntityId) -> Booking | None:
        async with self.db_session.cursor() as cursor:
            await cursor.execute("""
                SELECT
                    b.id AS booking_id,
                    b.user_id,
                    b.event_id,
                    b.status,
                    b.ticket_count,
                    b.created_at,
                    b.updated_at,
                    s.id AS seat_id,
                    s.seat_number,
                    s.price,
                    s.is_available,
                    s.section
                FROM bookings b
                LEFT JOIN booking_seats bs ON b.id = bs.booking_id
                LEFT JOIN seats s ON s.id = bs.seat_id
                WHERE b.id = %s
            """, (id.value,))
            rows = await cursor.fetchall()
            if not rows:
                return None

            # use the first one to get the shared booking data
            booking_row = rows[0]

            seats = [
                self._map_seat_row(row)
                for row in rows
                if row["seat_id"] is not None
            ]
            return self._map_db_model_to_entity(booking_row, seats)

    async def get_all(self) -> list[Booking]:
        async with self.db_session.cursor() as cursor:
            await cursor.execute("SELECT * FROM bookings")
            db_bookings = await cursor.fetchall()
            return [self._map_db_model_to_entity(db_booking, []) for db_booking in db_bookings]

    async def update(self, id: EntityId, booking: Booking) -> Booking | None:
        async with self.db_session.cursor() as cursor:
            await cursor.execute("""
                UPDATE bookings 
                SET user_id = %s, event_id = %s, status = %s, ticket_count = %s, updated_at = NOW()
                WHERE id = %s
                RETURNING *
            """,
                (booking.user_id.value, booking.event_id.value, booking.status,
                 booking.ticket_count, id.value))
            db_booking = await cursor.fetchone()
            if not db_booking:
                return None
            return self._map_db_model_to_entity(db_booking, [])

    async def delete(self, id: EntityId) -> bool:
        async with self.db_session.cursor() as cursor:
            await cursor.execute("DELETE FROM bookings WHERE id = %s", (id.value,))
            return cursor.rowcount > 0

    async def get_by_user_id(self, user_id: EntityId) -> list[Booking]:
        async with self.db_session.cursor() as cursor:
            await cursor.execute(
                "SELECT * FROM bookings WHERE user_id = %s",
                (user_id.value,)
            )
            db_bookings = await cursor.fetchall()
            return [self._map_db_model_to_entity(db_booking, []) for db_booking in db_bookings]

    async def get_by_event_id(self, event_id: EntityId) -> list[Booking]:
        async with self.db_session.cursor() as cursor:
            await cursor.execute(
                "SELECT * FROM bookings WHERE event_id = %s",
                (event_id.value,)
            )
            db_bookings = await cursor.fetchall()
            return [self._map_db_model_to_entity(db_booking, []) for db_booking in db_bookings]

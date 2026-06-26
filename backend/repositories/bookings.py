from repositories.base import BaseRepository
from psycopg import AsyncConnection
from models import Booking, EntityId, User, Event, EventSeat, BookingTieredTicket, EventTier


class BookingsRepository(BaseRepository):
    def __init__(self, db_session: AsyncConnection):
        super().__init__(db_session)

    def _map_db_model_to_entity(self, booking_row, seated_tickets: list[EventSeat] | None = None,
                                tiered_tickets: list[BookingTieredTicket] | None = None) -> Booking:
        return Booking(
            id=Booking.build_entity_id_from_uuid(booking_row['id']),
            user_id=User.build_entity_id_from_uuid(booking_row['user_id']),
            event_id=Event.build_entity_id_from_uuid(booking_row['event_id']),
            status=booking_row['status'],
            ticket_count=booking_row['ticket_count'],
            total_price=float(booking_row['total_price']) if booking_row.get('total_price') else 0.0,
            seated_tickets=seated_tickets or [],
            tiered_tickets=tiered_tickets or [],
            created_at=booking_row['created_at'],
            updated_at=booking_row['updated_at']
        )

    def _map_seat_row(self, data: dict) -> EventSeat:
        return EventSeat(
            id=EventSeat.build_entity_id_from_uuid(data['seat_id']),
            event_id=Event.build_entity_id_from_uuid(data['seat_event_id']),
            seat_number=data['seat_number'],
            price=float(data['seat_price']),
            is_available=data['is_available'],
            created_at=data['seat_created_at'],
            updated_at=data['seat_updated_at']
        )

    def _map_tiered_ticket_row(self, data: dict) -> BookingTieredTicket:
        return BookingTieredTicket(
            id=BookingTieredTicket.build_entity_id_from_uuid(data['tiered_ticket_id']),
            booking_id=Booking.build_entity_id_from_uuid(data['id']),
            ticket_tier_id=EventTier.build_entity_id_from_uuid(data['ticket_tier_id']),
            unit_price=float(data['unit_price']),
            created_at=data['created_at'],
            updated_at=data['updated_at']
        )

    async def create(self, booking: Booking) -> Booking | None:
        async with self.db_session.cursor() as cursor:
            await cursor.execute("""
                INSERT INTO bookings (id, user_id, event_id, status, ticket_count, total_price)
                VALUES (%s, %s, %s, %s, %s, %s)
                RETURNING *
            """,
                (booking.id.value, booking.user_id.value, booking.event_id.value,
                 booking.status, booking.ticket_count, booking.total_price))
            db_booking = await cursor.fetchone()
            if not db_booking:
                return None
            return self._map_db_model_to_entity(db_booking)

    async def get_by_id(self, id: EntityId) -> Booking | None:
        async with self.db_session.cursor() as cursor:
            await cursor.execute("""
                SELECT
                    b.*,
                    es.id AS seat_id,
                    es.event_id AS seat_event_id,
                    es.seat_number,
                    es.price AS seat_price,
                    es.is_available,
                    es.created_at AS seat_created_at,
                    es.updated_at AS seat_updated_at,
                    btt.id AS tiered_ticket_id,
                    btt.ticket_tier_id,
                    btt.unit_price,
                    btt.created_at AS tt_created_at,
                    btt.updated_at AS tt_updated_at
                FROM bookings b
                LEFT JOIN booking_seated_tickets bst ON b.id = bst.booking_id
                LEFT JOIN event_seats es ON es.id = bst.seat_id
                LEFT JOIN booking_tiered_tickets btt ON b.id = btt.booking_id
                WHERE b.id = %s
            """, (id.value,))
            rows = await cursor.fetchall()
            if not rows:
                return None

            booking_row = rows[0]
            seated_tickets = [
                self._map_seat_row(row)
                for row in rows
                if row["seat_id"] is not None
            ]
            tiered_tickets = [
                self._map_tiered_ticket_row(row)
                for row in rows
                if row["tiered_ticket_id"] is not None
            ]
            return self._map_db_model_to_entity(booking_row, seated_tickets, tiered_tickets)

    async def get_all(self) -> list[Booking]:
        async with self.db_session.cursor() as cursor:
            await cursor.execute("SELECT * FROM bookings")
            db_bookings = await cursor.fetchall()
            return [self._map_db_model_to_entity(db_booking) for db_booking in db_bookings]

    async def update(self, id: EntityId, booking: Booking) -> Booking | None:
        async with self.db_session.cursor() as cursor:
            await cursor.execute("""
                UPDATE bookings
                SET user_id = %s, event_id = %s, status = %s, ticket_count = %s, total_price = %s, updated_at = NOW()
                WHERE id = %s
                RETURNING *
            """,
                (booking.user_id.value, booking.event_id.value, booking.status,
                 booking.ticket_count, booking.total_price, id.value))
            db_booking = await cursor.fetchone()
            if not db_booking:
                return None
            return self._map_db_model_to_entity(db_booking)

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
            return [self._map_db_model_to_entity(db_booking) for db_booking in db_bookings]

    async def get_by_event_id(self, event_id: EntityId) -> list[Booking]:
        async with self.db_session.cursor() as cursor:
            await cursor.execute(
                "SELECT * FROM bookings WHERE event_id = %s",
                (event_id.value,)
            )
            db_bookings = await cursor.fetchall()
            return [self._map_db_model_to_entity(db_booking) for db_booking in db_bookings]
from repositories.base import BaseRepository
from psycopg import AsyncConnection
from models import Event, EntityId, EventTier, EventSeat, EventType


class EventsRepository(BaseRepository):
    def __init__(self, db_session: AsyncConnection):
        super().__init__(db_session)

    def _map_db_model_to_entity(self, data: dict, seats: list[EventSeat] | None = None,
                                tiers: list[EventTier] | None = None) -> Event:
        return Event(
            id=Event.build_entity_id_from_uuid(data['id']),
            name=data['name'],
            description=data['description'],
            venue=data['venue'],
            event_date=data['event_date'],
            event_type=data['event_type'],
            total_tickets=data.get('total_tickets'),
            available_tickets=data.get('available_tickets'),
            seats=seats or [],
            tiers=tiers or [],
            created_at=data['created_at'],
            updated_at=data['updated_at']
        )

    def _map_seat_row(self, data: dict) -> EventSeat:
        return EventSeat(
            id=EventSeat.build_entity_id_from_uuid(data['seat_id']),
            event_id=Event.build_entity_id_from_uuid(data['id']),
            seat_number=data['seat_number'],
            price=float(data['seat_price']),
            is_available=data['seat_is_available'],
            created_at=data['seat_created_at'],
            updated_at=data['seat_updated_at']
        )

    def _map_tier_row(self, data: dict) -> EventTier:
        return EventTier(
            id=EventTier.build_entity_id_from_uuid(data['tier_id']),
            event_id=Event.build_entity_id_from_uuid(data['id']),
            name=data['tier_name'],
            price=float(data['tier_price']),
            total_tickets=data['tier_total_tickets'],
            available_tickets=data['tier_available_tickets'],
            created_at=data['tier_created_at'],
            updated_at=data['tier_updated_at']
        )

    async def create(self, event: Event) -> Event | None:
        async with self.db_session.cursor() as cursor:
            await cursor.execute("""
                INSERT INTO events (id, name, description, venue, event_date, event_type, total_tickets, available_tickets)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING *
            """,
                (event.id.value, event.name, event.description, event.venue, 
                 event.event_date, event.event_type.value, 
                 event.total_tickets, event.available_tickets))
            db_event = await cursor.fetchone()
            if not db_event:
                return None
            return self._map_db_model_to_entity(db_event)

    async def get_by_id(self, id: EntityId) -> Event | None:
        async with self.db_session.cursor() as cursor:
            await cursor.execute("""
                SELECT
                    e.*,
                    es.id AS seat_id,
                    es.seat_number,
                    es.price AS seat_price,
                    es.is_available AS seat_is_available,
                    es.created_at AS seat_created_at,
                    es.updated_at AS seat_updated_at,
                    et.id AS tier_id,
                    et.name AS tier_name,
                    et.price AS tier_price,
                    et.total_tickets AS tier_total_tickets,
                    et.available_tickets AS tier_available_tickets,
                    et.created_at AS tier_created_at,
                    et.updated_at AS tier_updated_at
                FROM events e
                LEFT JOIN event_seats es ON e.id = es.event_id
                LEFT JOIN event_tiers et ON e.id = et.event_id
                WHERE e.id = %s
            """, (id.value,))
            rows = await cursor.fetchall()
            if not rows:
                return None

            event_row = rows[0]
            seats = [
                self._map_seat_row(row)
                for row in rows
                if row["seat_id"] is not None
            ]
            tiers = [
                self._map_tier_row(row)
                for row in rows
                if row["tier_id"] is not None
            ]
            return self._map_db_model_to_entity(event_row, seats, tiers)

    async def get_all(self, event_type: EventType | None = None) -> list[Event]:
        async with self.db_session.cursor() as cursor:
            if event_type:
                await cursor.execute(
                    "SELECT * FROM events WHERE event_type = %s",
                    (event_type.value,)
                )
            else:
                await cursor.execute("SELECT * FROM events")
            db_events = await cursor.fetchall()
            return [self._map_db_model_to_entity(db_event) for db_event in db_events]

    async def update(self, id: EntityId, event: Event) -> Event | None:
        async with self.db_session.cursor() as cursor:
            await cursor.execute("""
                UPDATE events 
                SET name = %s, description = %s, venue = %s, event_date = %s, 
                    event_type = %s, total_tickets = %s, available_tickets = %s, updated_at = NOW()
                WHERE id = %s
                RETURNING *
            """,
                (event.name, event.description, event.venue, event.event_date,
                 event.event_type.value, event.total_tickets, event.available_tickets, id.value))
            db_event = await cursor.fetchone()
            if not db_event:
                return None
            return self._map_db_model_to_entity(db_event)

    async def delete(self, id: EntityId) -> bool:
        async with self.db_session.cursor() as cursor:
            await cursor.execute("DELETE FROM events WHERE id = %s", (id.value,))
            return cursor.rowcount > 0

    async def decrement_available_tickets(self, event_id: EntityId, count: int) -> bool:
        async with self.db_session.cursor() as cursor:
            await cursor.execute("""
                UPDATE events
                SET available_tickets = available_tickets - %s
                WHERE id = %s AND available_tickets >= %s
                RETURNING id
            """, (count, event_id.value, count))
            result = await cursor.fetchone()
            return result is not None

    async def increment_available_tickets(self, event_id: EntityId, count: int) -> bool:
        async with self.db_session.cursor() as cursor:
            await cursor.execute("""
                UPDATE events
                SET available_tickets = available_tickets + %s
                WHERE id = %s
                RETURNING id
            """, (count, event_id.value))
            result = await cursor.fetchone()
            return result is not None

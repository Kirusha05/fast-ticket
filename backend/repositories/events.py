from repositories.base import BaseRepository
from psycopg import AsyncConnection
from models import Event, EntityId


class EventsRepository(BaseRepository):
    def __init__(self, db_session: AsyncConnection):
        super().__init__(db_session)

    def _map_db_model_to_entity(self, data: dict) -> Event:
        print("EVENT DATABASE DATA: ------------", data)
        return Event(
            id=Event.build_entity_id_from_uuid(data['id']),
            name=data['name'],
            description=data['description'],
            venue=data['venue'],
            event_date=data['event_date'],
            event_type=data['event_type'],
            total_tickets=data.get('total_tickets'),
            available_tickets=data.get('available_tickets'),
            created_at=data['created_at'],
            updated_at=data['updated_at']
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
            await cursor.execute("SELECT * FROM events WHERE id = %s", (id.value,))
            db_event = await cursor.fetchone()
            if not db_event:
                return None
            return self._map_db_model_to_entity(db_event)

    async def get_all(self) -> list[Event]:
        async with self.db_session.cursor() as cursor:
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
        """
        Atomically decrement available_tickets for an open_field event.
        Returns True if successful, False if not enough tickets available.
        """
        async with self.db_session.cursor() as cursor:
            await cursor.execute("""
                UPDATE events
                SET available_tickets = available_tickets - %s
                WHERE id = %s AND available_tickets >= %s
                RETURNING id
            """, (count, event_id.value, count))
            result = await cursor.fetchone()
            return result is not None

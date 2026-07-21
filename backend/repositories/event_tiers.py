from repositories.base import BaseRepository
from psycopg import AsyncConnection, sql
from models import EventTier, EntityId


class EventTiersRepository(BaseRepository):
    def __init__(self, db_session: AsyncConnection):
        super().__init__(db_session)

    def _map_db_model_to_entity(self, data: dict) -> EventTier:
        return EventTier(
            id=EventTier.build_entity_id_from_uuid(data['id']),
            event_id=EventTier.build_entity_id_from_uuid(data['event_id']),
            name=data['name'],
            price=float(data['price']),
            total_tickets=data['total_tickets'],
            available_tickets=data['available_tickets'],
            created_at=data['created_at'],
            updated_at=data['updated_at'],
        )

    async def create(self, tier: EventTier) -> EventTier | None:
        async with self.db_session.cursor() as cursor:
            await cursor.execute("""
                INSERT INTO event_tiers (id, event_id, name, price, total_tickets, available_tickets)
                VALUES (%s, %s, %s, %s, %s, %s)
                RETURNING *
            """, (tier.id.value, tier.event_id.value, tier.name,
                  tier.price, tier.total_tickets, tier.available_tickets))
            db_tier = await cursor.fetchone()
            if not db_tier:
                return None
            return self._map_db_model_to_entity(db_tier)

    async def create_multiple(self, tiers: list[EventTier]) -> list[EventTier]:
        if not tiers:
            return []
        values = [
            (t.id.value, t.event_id.value, t.name, t.price,
             t.total_tickets, t.available_tickets)
            for t in tiers
        ]
        async with self.db_session.cursor() as cursor:
            await cursor.executemany("""
                INSERT INTO event_tiers (id, event_id, name, price, total_tickets, available_tickets)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, values)
            return tiers

    async def get_by_id(self, tier_id: EntityId) -> EventTier | None:
        async with self.db_session.cursor() as cursor:
            await cursor.execute("SELECT * FROM event_tiers WHERE id = %s", (tier_id.value,))
            db_tier = await cursor.fetchone()
            if not db_tier:
                return None
            return self._map_db_model_to_entity(db_tier)

    async def get_by_ids(self, tier_ids: list[EntityId]) -> list[EventTier]:
        async with self.db_session.cursor() as cursor:
            await cursor.execute("""
                SELECT * FROM event_tiers
                WHERE id = ANY(%s)
            """, ([id.value for id in tier_ids],))
            rows = await cursor.fetchall()
            return [self._map_db_model_to_entity(row) for row in rows]

    async def get_by_ids_for_update(self, tier_ids: list[EntityId]) -> list[EventTier]:
        async with self.db_session.cursor() as cursor:
            await cursor.execute("""
                SELECT * FROM event_tiers
                WHERE id = ANY(%s)
                ORDER BY id
                FOR UPDATE
            """, ([id.value for id in tier_ids],))
            rows = await cursor.fetchall()
            return [self._map_db_model_to_entity(row) for row in rows]

    async def get_by_event_id(self, event_id: EntityId) -> list[EventTier]:
        async with self.db_session.cursor() as cursor:
            await cursor.execute(
                "SELECT * FROM event_tiers WHERE event_id = %s ORDER BY name",
                (event_id.value,)
            )
            rows = await cursor.fetchall()
            return [self._map_db_model_to_entity(row) for row in rows]

    async def decrement_available_tickets(self, tier_id: EntityId, count: int) -> bool:
        async with self.db_session.cursor() as cursor:
            await cursor.execute("""
                UPDATE event_tiers
                SET available_tickets = available_tickets - %s
                WHERE id = %s AND available_tickets >= %s
                RETURNING id
            """, (count, tier_id.value, count))
            result = await cursor.fetchone()
            return result is not None

    async def increment_available_tickets(self, tier_id: EntityId, count: int) -> bool:
        async with self.db_session.cursor() as cursor:
            await cursor.execute("""
                UPDATE event_tiers
                SET available_tickets = available_tickets + %s
                WHERE id = %s
                RETURNING id
            """, (count, tier_id.value))
            result = await cursor.fetchone()
            return result is not None

    async def get_all(self) -> list[EventTier]:
        async with self.db_session.cursor() as cursor:
            await cursor.execute("SELECT * FROM event_tiers")
            rows = await cursor.fetchall()
            return [self._map_db_model_to_entity(row) for row in rows]

    async def update(self, tier_id: EntityId, tier: EventTier) -> EventTier | None:
        async with self.db_session.cursor() as cursor:
            await cursor.execute("""
                UPDATE event_tiers
                SET name = %s, price = %s, total_tickets = %s, available_tickets = %s, updated_at = NOW()
                WHERE id = %s
                RETURNING *
            """, (tier.name, tier.price, tier.total_tickets, tier.available_tickets, tier_id.value))
            db_tier = await cursor.fetchone()
            if not db_tier:
                return None
            return self._map_db_model_to_entity(db_tier)

    async def delete(self, tier_id: EntityId) -> bool:
        async with self.db_session.cursor() as cursor:
            await cursor.execute("DELETE FROM event_tiers WHERE id = %s", (tier_id.value,))
            return cursor.rowcount > 0
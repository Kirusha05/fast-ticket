from repositories.base import BaseRepository
from psycopg import AsyncConnection
from models import User, EntityId


class UsersRepository(BaseRepository):
    def __init__(self, db_session: AsyncConnection):
        super().__init__(db_session)

    def _map_db_model_to_entity(self, data: dict) -> User:
        return User(
            id=User.build_entity_id_from_uuid(data['id']),
            name=data['name'],
            email=data['email'],
            auth0_id=data['auth0_id'],
            role=data['role'],
            created_at=data['created_at'],
            updated_at=data['updated_at']
        )

    async def create(self, user: User) -> User | None:
        async with self.db_session.cursor() as cursor:
            await cursor.execute("""
                INSERT INTO users (id, name, email, auth0_id, role) 
                VALUES (%s, %s, %s, %s, %s)
                RETURNING *
            """,
            (user.id.value, user.name, user.email, user.auth0_id, user.role))
            db_user = await cursor.fetchone()
            if not db_user:
                return None
            return self._map_db_model_to_entity(db_user)

    async def get_by_id(self, id: EntityId) -> User | None:
        async with self.db_session.cursor() as cursor:
            await cursor.execute("SELECT * FROM users WHERE id = %s", (id.value,))
            db_user = await cursor.fetchone()
            if not db_user:
                return None
            return self._map_db_model_to_entity(db_user)

    async def get_by_email(self, email: str) -> User | None:
        async with self.db_session.cursor() as cursor:
            await cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
            db_user = await cursor.fetchone()
            if not db_user:
                return None
            return self._map_db_model_to_entity(db_user)
            
    async def get_by_auth0_id(self, auth0_id: str) -> User | None:
        async with self.db_session.cursor() as cursor:
            await cursor.execute(
                "SELECT * FROM users WHERE auth0_id = %s", 
                (auth0_id,)
            )
            db_user = await cursor.fetchone()
            if not db_user:
                return None
            return self._map_db_model_to_entity(db_user)

    async def get_all(self) -> list[User]:
        async with self.db_session.cursor() as cursor:
            await cursor.execute("SELECT * FROM users")
            db_users = await cursor.fetchall()
            return [self._map_db_model_to_entity(db_user) for db_user in db_users]

    async def update(self, id: EntityId, user: User) -> User | None:
        async with self.db_session.cursor() as cursor:
            # can set ISOLATION LEVEL like this if needed
            # await cursor.execute("SET TRANSACTION ISOLATION LEVEL SERIALIZABLE")
            
            await cursor.execute("""
                UPDATE users SET name = %s, email = %s, auth0_id = %s, updated_at = NOW() WHERE id = %s
                RETURNING *
            """,
            (user.name, user.email, user.auth0_id, id.value))
            db_user = await cursor.fetchone()
            if not db_user:
                return None
            return self._map_db_model_to_entity(db_user)

    async def delete(self, id: EntityId) -> bool:
        async with self.db_session.cursor() as cursor:
            await cursor.execute("DELETE FROM users WHERE id = %s", (id.value,))
            return cursor.rowcount > 0
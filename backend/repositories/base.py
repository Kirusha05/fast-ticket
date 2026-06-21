from abc import ABC, abstractmethod
from typing import Any
from psycopg import AsyncConnection
from models import EntityId


class BaseRepository(ABC):
    def __init__(self, db_session: AsyncConnection):
        self.db_session = db_session

    @abstractmethod
    def _map_db_model_to_entity(self, data: Any) -> Any:
        pass

    @abstractmethod
    async def create(self, data: Any):
        pass

    @abstractmethod
    async def get_by_id(self, id: EntityId) -> Any:
        pass

    @abstractmethod
    async def get_all(self) -> list[Any]:
        pass

    @abstractmethod
    async def update(self, id: EntityId, data: Any) -> Any:
        pass

    @abstractmethod
    async def delete(self, id: EntityId):
        pass
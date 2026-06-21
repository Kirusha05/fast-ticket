import uuid
from typing import ClassVar, Self
from pydantic import BaseModel, Field, model_serializer


class BaseValueObject(BaseModel):
    class Config:
        validate_assignment = True
        frozen = True


class EntityId(BaseValueObject):
    value: uuid.UUID = Field()
    prefix: str = Field()

    @classmethod
    def from_string(cls, entity_id: str) -> Self:
        prefix, value = entity_id.split('-', maxsplit=1)
        return cls(value=uuid.UUID(value), prefix=prefix)

    @classmethod
    def from_uuid(cls, value: uuid.UUID, prefix: str) -> Self:
        return cls(value=value, prefix=prefix)

    @classmethod
    def generate_new(cls, prefix: str) -> Self:
        return cls(value=EntityId.generate_uuid(), prefix=prefix)

    @staticmethod
    def generate_uuid() -> uuid.UUID:
        """
        Generates a random UUID with the first 2 parts being time ordered and the rest being random.
        This improves DB performance when using UUID as primary key.
        """
        time_ordered_uuid = str(uuid.uuid1()).split('-')
        random_uuid = str(uuid.uuid4()).split('-')
        random_uuid[0], random_uuid[1] = time_ordered_uuid[0], time_ordered_uuid[1]

        return uuid.UUID('-'.join(random_uuid))

    def __str__(self):
        return f'{self.prefix}-{self.value}'

    def __repr__(self):
        return f'{self.prefix}-{self.value}'

    @model_serializer
    def serializer(self) -> str:
        return str(self)


class BaseEntity(BaseValueObject):
    entity_id_prefix: ClassVar[str | None] = None

    id: EntityId = Field()

    @classmethod
    def generate_entity_id(cls) -> EntityId:
        if cls.entity_id_prefix is None:
            raise RuntimeError(f'Please set valid id prefix for the {cls.__name__} model')
        return EntityId.generate_new(prefix=cls.entity_id_prefix)

    @classmethod
    def build_entity_id_from_uuid(cls, id_value: uuid.UUID) -> EntityId:
        if cls.entity_id_prefix is None:
            raise RuntimeError(f'Please set valid id prefix for the {cls.__name__} model')
        return EntityId.from_uuid(value=id_value, prefix=cls.entity_id_prefix)

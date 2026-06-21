from pydantic import BaseModel
from datetime import datetime
from models import BaseEntity
from typing import ClassVar


class User(BaseEntity):
    entity_id_prefix: ClassVar[str] = 'u'
    
    name: str
    email: str
    auth0_id: str
    created_at: datetime | None = None
    updated_at: datetime | None = None


class CreateUserRequest(BaseModel):
    name: str
    email: str
    auth0_id: str


class UpdateUserRequest(BaseModel):
    name: str
from datetime import datetime
from models import BaseEntity
from typing import ClassVar
from enum import Enum


class UserRole(str, Enum):
    USER = "user"
    ADMIN = "admin"


class User(BaseEntity):
    entity_id_prefix: ClassVar[str] = 'u'
    
    name: str
    email: str
    auth0_id: str
    role: UserRole
    created_at: datetime | None = None
    updated_at: datetime | None = None
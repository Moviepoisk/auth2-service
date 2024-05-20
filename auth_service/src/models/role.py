from enum import Enum
from uuid import UUID

from pydantic import BaseModel
from src.models.user import UserInDB


class RoleInDB(BaseModel):
    class Config:
        from_attributes = True

    id: UUID
    name: str

    def __str__(self) -> str:
        return self.name


class RoleCRUD(BaseModel):
    name: str


class UserRole(BaseModel):
    user: UserInDB | None = None
    role: RoleInDB | None = None


class RoleEnum(Enum):
    user = "user"
    admin = "admin"
    staff = "staff"

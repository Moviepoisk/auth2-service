import uuid
from datetime import datetime
from typing import List

from sqlalchemy import UUID, Column, DateTime, ForeignKey, String, Integer
from sqlalchemy.orm import Mapped, relationship
from src.models.db.base import Base
from src.models.db.role import Role, association_table
from werkzeug.security import check_password_hash, generate_password_hash


class User(Base):
    __tablename__ = "users"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        unique=True,
        nullable=False,
    )
    email = Column(String(64), unique=True, nullable=False)
    password = Column(String(255), nullable=False)
    first_name = Column(String(50), nullable=True)
    last_name = Column(String(50), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    access_level = Column(Integer, nullable=False, default=0)

    login_history = relationship(
        "UserLoginHistory",
        back_populates="user",
        lazy="select",
        passive_deletes=True,
    )
    roles: Mapped[List["Role"]] = relationship(secondary=association_table)

    def __init__(
        self, email: str, password: str, first_name: str = None, last_name: str = None, access_level: int = 0
    ) -> None:
        self.email = email
        self.password = generate_password_hash(password)
        self.first_name = first_name
        self.last_name = last_name
        self.access_level = access_level

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password, password)

    def set_password(self, password: str) -> None:
        self.password = generate_password_hash(password)

    def __repr__(self) -> str:
        return f"<User {self.email}>"


class UserLoginHistory(Base):
    __tablename__ = "users_login_history"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID, ForeignKey("users.id", ondelete="CASCADE"))
    user_agent = Column(String(255), nullable=True)
    ip_address = Column(String(15), nullable=True)
    login_time = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="login_history")

    def __repr__(self) -> str:
        return f"<UserLoginHistory {self.user_id}>"

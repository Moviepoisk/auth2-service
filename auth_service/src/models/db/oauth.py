import uuid

from sqlalchemy import UUID, Column, ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import relationship, backref
from src.models.db.base import Base


class OAuthUser(Base):
    __tablename__ = "oauth_users"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        unique=True,
        nullable=False,
    )

    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    user = relationship("User", backref=backref("oauth_user", lazy="dynamic"))

    oauth_id = Column(String, nullable=False)
    oauth_name = Column(String, nullable=False)

    __table_args__ = (UniqueConstraint("oauth_id", "oauth_name", name="oauth_key"),)

    def __repr__(self):
        return f"<OAuthUser {self.oauth_id}:{self.oauth_name}>"

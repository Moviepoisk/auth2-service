import datetime
import secrets
import string
from uuid import UUID

from pydantic import BaseModel, Field, field_validator, EmailStr, validate_email
from pydantic.networks import email_validator


def generate_random_password(length=12):
    """Generate a random password."""
    characters = string.ascii_letters + string.digits + string.punctuation
    return "".join(secrets.choice(characters) for _ in range(length))


class UserCreate(BaseModel):
    email: EmailStr | str | None = Field(..., min_length=8, max_length=64)
    password: str | None = Field(None, min_length=8, max_length=255)
    first_name: str | None = None
    last_name: str | None = None
    access_level: int = 0

    @field_validator("email")
    @classmethod
    def validate_email(cls, value):
        try:
            validate_email(value)
        except email_validator.EmailNotValidError:
            raise ValueError("Invalid email format")
        return value

    @field_validator("access_level")
    def validate_access_level(cls, v):
        if not 0 <= v <= 5:
            raise ValueError("Level must be between 0 and 5")
        return v

    def __init__(self, **data):
        super().__init__(**data)
        if self.password is None:
            self.password = generate_random_password()


class UserUpdateCredentials(BaseModel):
    old_password: str = Field(..., min_length=8, max_length=255)
    new_password: str = Field(..., min_length=8, max_length=255)


class UserInDB(BaseModel):
    id: UUID
    first_name: str | None = None
    last_name: str | None = None
    access_level: int = 0

    class Config:
        from_attributes = True


class UserLogin(BaseModel):
    email: str
    password: str


class UserTokens(BaseModel):
    access_token: str
    refresh_token: str


class UserResponse(BaseModel):
    msg: str


class UserLoginHistoryCreate(BaseModel):
    user_id: UUID
    user_agent: str | None = None
    ip_address: str | None = None
    login_time: datetime.datetime | None = None


class UserLoginHistoryInDB(BaseModel):
    user_id: UUID
    login_time: datetime.datetime
    user_agent: str | None
    ip_address: str | None

    class Config:
        from_attributes = True

from datetime import datetime

from beanie import Document, Indexed
from pydantic import ConfigDict, EmailStr, Field


class User(Document):
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "email": "user@example.com",
                "hashed_password": "hashedpw123",
                "is_active": True,
                "is_admin": False,
            }
        }
    )

    email: Indexed(EmailStr, unique=True)
    hashed_password: str
    is_active: bool = True
    is_admin: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime | None = None
    reset_token: str | None = None
    reset_token_expires: datetime | None = None

    class Settings:
        name = "users"
        use_state_management = True

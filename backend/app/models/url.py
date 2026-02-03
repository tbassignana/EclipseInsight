from datetime import datetime

from beanie import Document, Indexed, Link
from pydantic import ConfigDict, Field

from app.models.user import User


class ShortURL(Document):
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "original_url": "https://example.com/very/long/url",
                "short_code": "abc123",
                "clicks": 0,
                "is_active": True,
                "tags": ["technology", "news"],
                "summary": "An article about technology trends",
                "suggested_alias": "tech-trends",
            }
        }
    )

    original_url: str
    short_code: Indexed(str, unique=True)
    user: Link[User]
    custom_alias: str | None = None
    clicks: int = 0
    expiration: datetime | None = None
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime | None = None

    # URL Preview metadata
    preview_title: str | None = None
    preview_description: str | None = None
    preview_image: str | None = None

    # AI Analysis fields
    tags: list[str] = Field(default_factory=list)
    summary: str | None = None
    suggested_alias: str | None = None
    is_toxic: bool = False
    ai_analyzed: bool = False
    ai_analyzed_at: datetime | None = None

    # Preview screenshot (GridFS file ID)
    preview_screenshot_id: str | None = None

    class Settings:
        name = "short_urls"
        use_state_management = True

    @property
    def is_expired(self) -> bool:
        if self.expiration is None:
            return False
        return datetime.utcnow() > self.expiration

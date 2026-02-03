from datetime import datetime

from beanie import Document
from pydantic import ConfigDict, Field


class ClickLog(Document):
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "short_url_id": "507f1f77bcf86cd799439011",
                "ip_address": "192.168.1.1",
                "user_agent": "Mozilla/5.0...",
                "referrer": "https://google.com",
                "device_type": "desktop",
            }
        }
    )

    short_url_id: str  # Reference to ShortURL document ID
    ip_address: str | None = None
    user_agent: str | None = None
    referrer: str | None = None
    country: str | None = None
    city: str | None = None
    device_type: str | None = None  # mobile, desktop, tablet
    browser: str | None = None
    os: str | None = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "click_logs"
        use_state_management = True

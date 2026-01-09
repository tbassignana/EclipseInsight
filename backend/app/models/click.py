from beanie import Document
from pydantic import Field, ConfigDict
from datetime import datetime
from typing import Optional


class ClickLog(Document):
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "short_url_id": "507f1f77bcf86cd799439011",
                "ip_address": "192.168.1.1",
                "user_agent": "Mozilla/5.0...",
                "referrer": "https://google.com",
                "device_type": "desktop"
            }
        }
    )

    short_url_id: str  # Reference to ShortURL document ID
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    referrer: Optional[str] = None
    country: Optional[str] = None
    city: Optional[str] = None
    device_type: Optional[str] = None  # mobile, desktop, tablet
    browser: Optional[str] = None
    os: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "click_logs"
        use_state_management = True

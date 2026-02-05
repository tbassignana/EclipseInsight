from datetime import datetime

from pydantic import BaseModel, Field


class URLCreate(BaseModel):
    original_url: str = Field(..., description="The original URL to shorten")
    custom_alias: str | None = Field(
        None,
        min_length=4,
        max_length=20,
        pattern="^[a-zA-Z0-9_-]+$",
        description="Custom alias for the short URL",
    )
    expiration_days: int | None = Field(
        None, ge=1, le=365, description="Number of days until URL expires"
    )
    skip_ai_analysis: bool = Field(False, description="Skip AI content analysis")
    use_ai_suggested_alias: bool = Field(
        False, description="Use AI-suggested alias instead of random code (if available)"
    )


class AIAnalysis(BaseModel):
    """AI analysis results for a URL."""

    tags: list[str] = Field(default_factory=list)
    summary: str | None = None
    suggested_alias: str | None = None
    is_toxic: bool = False
    analyzed: bool = False
    analyzed_at: datetime | None = None
    error: str | None = None


class URLResponse(BaseModel):
    id: str
    original_url: str
    short_code: str
    short_url: str
    clicks: int
    expiration: datetime | None
    created_at: datetime
    preview_title: str | None = None
    preview_description: str | None = None
    preview_image: str | None = None
    # AI Analysis fields
    ai: AIAnalysis | None = None


class URLStats(BaseModel):
    short_code: str
    original_url: str
    total_clicks: int
    clicks_today: int
    clicks_this_week: int
    top_referrers: list[dict]
    clicks_by_country: list[dict]
    clicks_by_device: list[dict]
    clicks_over_time: list[dict]


class URLUpdate(BaseModel):
    original_url: str | None = Field(None, description="New destination URL")
    custom_alias: str | None = Field(
        None,
        min_length=4,
        max_length=20,
        pattern="^[a-zA-Z0-9_-]+$",
        description="New custom alias",
    )
    expiration_days: int | None = Field(
        None, ge=1, le=365, description="New expiration in days from now"
    )


class BulkDeleteRequest(BaseModel):
    short_codes: list[str] = Field(
        ..., min_length=1, max_length=100, description="List of short codes to delete (max 100)"
    )


class BulkDeleteResponse(BaseModel):
    deleted: list[str] = Field(default_factory=list, description="Short codes successfully deleted")
    failed: list[str] = Field(
        default_factory=list, description="Short codes that could not be deleted"
    )
    total_deleted: int = 0
    total_failed: int = 0


class URLPreview(BaseModel):
    title: str | None = None
    description: str | None = None
    image: str | None = None
    url: str

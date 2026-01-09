from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class URLCreate(BaseModel):
    original_url: str = Field(..., description="The original URL to shorten")
    custom_alias: Optional[str] = Field(
        None,
        min_length=4,
        max_length=20,
        pattern="^[a-zA-Z0-9_-]+$",
        description="Custom alias for the short URL"
    )
    expiration_days: Optional[int] = Field(
        None,
        ge=1,
        le=365,
        description="Number of days until URL expires"
    )
    skip_ai_analysis: bool = Field(
        False,
        description="Skip AI content analysis"
    )
    use_ai_suggested_alias: bool = Field(
        False,
        description="Use AI-suggested alias instead of random code (if available)"
    )


class AIAnalysis(BaseModel):
    """AI analysis results for a URL."""
    tags: list[str] = Field(default_factory=list)
    summary: Optional[str] = None
    suggested_alias: Optional[str] = None
    is_toxic: bool = False
    analyzed: bool = False
    analyzed_at: Optional[datetime] = None
    error: Optional[str] = None


class URLResponse(BaseModel):
    id: str
    original_url: str
    short_code: str
    short_url: str
    clicks: int
    expiration: Optional[datetime]
    created_at: datetime
    preview_title: Optional[str] = None
    preview_description: Optional[str] = None
    preview_image: Optional[str] = None
    # AI Analysis fields
    ai: Optional[AIAnalysis] = None


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


class URLPreview(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    image: Optional[str] = None
    url: str

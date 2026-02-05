import logging
import re
import secrets
import string
from datetime import UTC, datetime, timedelta

import aiohttp
from bs4 import BeautifulSoup

from app.core.config import settings
from app.models.click import ClickLog
from app.models.url import ShortURL
from app.models.user import User
from app.schemas.url import URLCreate, URLPreview, URLStats, URLUpdate
from app.services.ai import ai_service

logger = logging.getLogger(__name__)

# Base62 character set for URL-safe short codes
BASE62_CHARS = string.digits + string.ascii_lowercase + string.ascii_uppercase


def generate_short_code(length: int = None) -> str:
    """Generate a random base62 short code."""
    if length is None:
        length = settings.SHORT_CODE_LENGTH
    return "".join(secrets.choice(BASE62_CHARS) for _ in range(length))


async def is_short_code_available(short_code: str) -> bool:
    """Check if a short code is available (not already in use)."""
    existing = await ShortURL.find_one({"short_code": short_code})
    return existing is None


async def generate_unique_short_code(max_attempts: int = 10) -> str:
    """Generate a unique short code with collision detection."""
    for _ in range(max_attempts):
        code = generate_short_code()
        if await is_short_code_available(code):
            return code
    raise ValueError("Could not generate unique short code after max attempts")


def is_valid_custom_alias(alias: str) -> bool:
    """Validate custom alias format."""
    if not alias:
        return False
    pattern = r"^[a-zA-Z0-9_-]+$"
    return bool(re.match(pattern, alias)) and 4 <= len(alias) <= 20


async def fetch_url_preview(url: str) -> URLPreview:
    """Fetch Open Graph metadata from a URL for preview."""
    preview = URLPreview(url=url)

    try:
        timeout = aiohttp.ClientTimeout(total=5)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.get(url, allow_redirects=True) as response:
                if response.status != 200:
                    return preview

                html = await response.text()
                soup = BeautifulSoup(html, "html.parser")

                # Try Open Graph tags first
                og_title = soup.find("meta", property="og:title")
                og_desc = soup.find("meta", property="og:description")
                og_image = soup.find("meta", property="og:image")

                if og_title:
                    preview.title = og_title.get("content", "")[:200]
                elif soup.title:
                    preview.title = soup.title.string[:200] if soup.title.string else None

                if og_desc:
                    preview.description = og_desc.get("content", "")[:500]
                else:
                    meta_desc = soup.find("meta", attrs={"name": "description"})
                    if meta_desc:
                        preview.description = meta_desc.get("content", "")[:500]

                if og_image:
                    preview.image = og_image.get("content", "")

    except Exception:
        logger.exception("Failed to fetch preview for %s", url)

    return preview


async def check_user_url_quota(user: User) -> None:
    """Check if user has exceeded their URL creation quota.

    Raises ValueError if the quota is exceeded. Admins bypass the quota.
    """
    max_urls = settings.MAX_URLS_PER_USER
    if max_urls <= 0 or user.is_admin:
        return  # Unlimited or admin

    active_count = await ShortURL.find({"user.$id": user.id, "is_active": True}).count()
    if active_count >= max_urls:
        raise ValueError(
            f"URL quota exceeded. You have {active_count}/{max_urls} active URLs. "
            "Delete some URLs to create new ones."
        )


async def create_short_url(url_data: URLCreate, user: User, fetch_preview: bool = True) -> ShortURL:
    """Create a new shortened URL with AI analysis."""
    # Check quota before doing anything else
    await check_user_url_quota(user)

    # Run AI analysis if enabled
    ai_result = None
    if not url_data.skip_ai_analysis and ai_service.is_available:
        ai_result = await ai_service.analyze_url(url_data.original_url)

        # Reject toxic content
        if ai_result.is_toxic:
            raise ValueError(
                "Content has been flagged as potentially harmful and cannot be shortened. "
                "If you believe this is an error, please contact support."
            )

    # Determine which short code to use
    if url_data.custom_alias:
        # User provided custom alias
        if not is_valid_custom_alias(url_data.custom_alias):
            raise ValueError("Invalid custom alias format")
        if not await is_short_code_available(url_data.custom_alias):
            raise ValueError("Custom alias is already taken")
        short_code = url_data.custom_alias
    elif url_data.use_ai_suggested_alias and ai_result and ai_result.suggested_alias:
        # Use AI-suggested alias if requested and available
        suggested = ai_result.suggested_alias
        if is_valid_custom_alias(suggested) and await is_short_code_available(suggested):
            short_code = suggested
        else:
            # Fall back to random code if suggested alias is taken or invalid
            short_code = await generate_unique_short_code()
    else:
        # Generate random short code
        short_code = await generate_unique_short_code()

    # Calculate expiration date if provided
    expiration = None
    if url_data.expiration_days:
        expiration = datetime.now(UTC) + timedelta(days=url_data.expiration_days)

    # Fetch URL preview metadata
    preview_title = None
    preview_description = None
    preview_image = None

    if fetch_preview:
        try:
            preview = await fetch_url_preview(url_data.original_url)
            preview_title = preview.title
            preview_description = preview.description
            preview_image = preview.image
        except Exception:
            logger.exception(
                "Preview fetch failed during URL creation for %s", url_data.original_url
            )

    # Prepare AI fields
    tags = []
    summary = None
    suggested_alias = None
    is_toxic = False
    ai_analyzed = False
    ai_analyzed_at = None

    if ai_result:
        tags = ai_result.tags
        summary = ai_result.summary
        suggested_alias = ai_result.suggested_alias
        is_toxic = ai_result.is_toxic
        ai_analyzed = ai_result.error is None
        ai_analyzed_at = datetime.now(UTC) if ai_analyzed else None

    short_url = ShortURL(
        original_url=url_data.original_url,
        short_code=short_code,
        user=user,
        custom_alias=url_data.custom_alias,
        expiration=expiration,
        preview_title=preview_title,
        preview_description=preview_description,
        preview_image=preview_image,
        # AI fields
        tags=tags,
        summary=summary,
        suggested_alias=suggested_alias,
        is_toxic=is_toxic,
        ai_analyzed=ai_analyzed,
        ai_analyzed_at=ai_analyzed_at,
        created_at=datetime.now(UTC),
    )

    await short_url.insert()
    return short_url


async def get_short_url_by_code(short_code: str) -> ShortURL | None:
    """Find a short URL by its short code."""
    return await ShortURL.find_one({"short_code": short_code})


async def get_user_urls(user: User, skip: int = 0, limit: int = 100) -> list[ShortURL]:
    """Get all URLs created by a user."""
    return (
        await ShortURL.find({"user.$id": user.id, "is_active": True})
        .skip(skip)
        .limit(limit)
        .to_list()
    )


async def update_short_url(short_code: str, update_data: URLUpdate, user: User) -> ShortURL | None:
    """Update a short URL's original_url, custom_alias, or expiration. Returns updated URL or None."""
    short_url = await get_short_url_by_code(short_code)
    if not short_url or not short_url.is_active:
        return None

    # Check ownership (unless admin)
    if not user.is_admin:
        user_ref = short_url.user
        user_id = user_ref.ref.id if hasattr(user_ref, "ref") else getattr(user_ref, "id", None)
        if user_id != user.id:
            return None

    fields = update_data.model_dump(exclude_unset=True)

    if "original_url" in fields:
        short_url.original_url = fields["original_url"]

    if "custom_alias" in fields:
        alias = fields["custom_alias"]
        if not is_valid_custom_alias(alias):
            raise ValueError("Invalid custom alias format")
        if alias != short_url.short_code and not await is_short_code_available(alias):
            raise ValueError("Custom alias is already taken")
        short_url.short_code = alias
        short_url.custom_alias = alias

    if "expiration_days" in fields:
        short_url.expiration = datetime.now(UTC) + timedelta(days=fields["expiration_days"])

    short_url.updated_at = datetime.now(UTC)
    await short_url.save()
    return short_url


async def delete_short_url(short_code: str, user: User) -> bool:
    """Soft delete a short URL (mark as inactive)."""
    short_url = await get_short_url_by_code(short_code)
    if not short_url:
        return False

    # Check ownership (unless admin)
    if not user.is_admin and short_url.user.ref.id != user.id:
        return False

    short_url.is_active = False
    short_url.updated_at = datetime.now(UTC)
    await short_url.save()
    return True


async def bulk_delete_short_urls(short_codes: list[str], user: User) -> tuple[list[str], list[str]]:
    """Bulk soft-delete short URLs. Returns (deleted, failed) lists."""
    deleted = []
    failed = []

    for code in short_codes:
        success = await delete_short_url(code, user)
        if success:
            deleted.append(code)
        else:
            failed.append(code)

    return deleted, failed


async def get_url_stats(short_url: ShortURL) -> URLStats:
    """Get detailed statistics for a shortened URL."""
    url_id = str(short_url.id)
    # Use timezone-naive UTC to match ClickLog.timestamp format
    now = datetime.utcnow()
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    week_start = today_start - timedelta(days=7)

    # Get all clicks for this URL
    all_clicks = await ClickLog.find({"short_url_id": url_id}).to_list()

    # Calculate basic stats
    total_clicks = len(all_clicks)
    clicks_today = sum(1 for c in all_clicks if c.timestamp >= today_start)
    clicks_this_week = sum(1 for c in all_clicks if c.timestamp >= week_start)

    # Aggregate referrers
    referrer_counts: dict[str, int] = {}
    for click in all_clicks:
        ref = click.referrer or "Direct"
        referrer_counts[ref] = referrer_counts.get(ref, 0) + 1
    top_referrers = [
        {"referrer": k, "count": v}
        for k, v in sorted(referrer_counts.items(), key=lambda x: x[1], reverse=True)[:10]
    ]

    # Aggregate by country
    country_counts: dict[str, int] = {}
    for click in all_clicks:
        country = click.country or "Unknown"
        country_counts[country] = country_counts.get(country, 0) + 1
    clicks_by_country = [
        {"country": k, "count": v}
        for k, v in sorted(country_counts.items(), key=lambda x: x[1], reverse=True)[:10]
    ]

    # Aggregate by device
    device_counts: dict[str, int] = {}
    for click in all_clicks:
        device = click.device_type or "Unknown"
        device_counts[device] = device_counts.get(device, 0) + 1
    clicks_by_device = [
        {"device": k, "count": v}
        for k, v in sorted(device_counts.items(), key=lambda x: x[1], reverse=True)
    ]

    # Clicks over time (last 7 days)
    clicks_over_time = []
    for i in range(7):
        day = today_start - timedelta(days=6 - i)
        day_end = day + timedelta(days=1)
        day_clicks = sum(1 for c in all_clicks if day <= c.timestamp < day_end)
        clicks_over_time.append({"date": day.strftime("%b %d"), "count": day_clicks})

    return URLStats(
        short_code=short_url.short_code,
        original_url=short_url.original_url,
        total_clicks=total_clicks,
        clicks_today=clicks_today,
        clicks_this_week=clicks_this_week,
        top_referrers=top_referrers,
        clicks_by_country=clicks_by_country,
        clicks_by_device=clicks_by_device,
        clicks_over_time=clicks_over_time,
    )

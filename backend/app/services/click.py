import logging
from datetime import datetime, timezone
from typing import Optional
import re

from app.models.click import ClickLog
from app.models.url import ShortURL
from app.core.database import get_redis

logger = logging.getLogger(__name__)


def parse_user_agent(user_agent: str) -> dict:
    """Parse user agent string to extract device, browser, and OS info."""
    result = {
        "device_type": "desktop",
        "browser": "unknown",
        "os": "unknown"
    }

    if not user_agent:
        return result

    ua_lower = user_agent.lower()

    # Detect device type
    if any(mobile in ua_lower for mobile in ["mobile", "android", "iphone", "ipad"]):
        if "tablet" in ua_lower or "ipad" in ua_lower:
            result["device_type"] = "tablet"
        else:
            result["device_type"] = "mobile"

    # Detect browser
    if "chrome" in ua_lower and "edg" not in ua_lower:
        result["browser"] = "Chrome"
    elif "firefox" in ua_lower:
        result["browser"] = "Firefox"
    elif "safari" in ua_lower and "chrome" not in ua_lower:
        result["browser"] = "Safari"
    elif "edg" in ua_lower:
        result["browser"] = "Edge"
    elif "opera" in ua_lower or "opr" in ua_lower:
        result["browser"] = "Opera"

    # Detect OS (order matters - check specific platforms before generic ones)
    if "android" in ua_lower:
        result["os"] = "Android"
    elif "iphone" in ua_lower or "ipad" in ua_lower or "ios" in ua_lower:
        result["os"] = "iOS"
    elif "windows" in ua_lower:
        result["os"] = "Windows"
    elif "mac os" in ua_lower or "macintosh" in ua_lower:
        result["os"] = "macOS"
    elif "linux" in ua_lower:
        result["os"] = "Linux"

    return result


async def log_click(
    short_url: ShortURL,
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None,
    referrer: Optional[str] = None
) -> ClickLog:
    """Log a click event for analytics."""
    # Parse user agent for device info
    ua_info = parse_user_agent(user_agent or "")

    click_log = ClickLog(
        short_url_id=str(short_url.id),
        ip_address=ip_address,
        user_agent=user_agent,
        referrer=referrer,
        device_type=ua_info["device_type"],
        browser=ua_info["browser"],
        os=ua_info["os"],
        timestamp=datetime.now(timezone.utc)
    )

    await click_log.insert()

    # Update click count in the URL document
    short_url.clicks += 1
    short_url.updated_at = datetime.now(timezone.utc)
    await short_url.save()

    # Also increment in Redis for real-time analytics
    try:
        redis = get_redis()
        if redis:
            await redis.incr(f"clicks:{short_url.short_code}")
            await redis.incr(f"clicks:{short_url.short_code}:today")
            # Set expiry for daily counter (24 hours)
            await redis.expire(f"clicks:{short_url.short_code}:today", 86400)
    except Exception:
        logger.exception("Redis click counter update failed for %s", short_url.short_code)

    return click_log


async def get_click_count(short_code: str) -> int:
    """Get total click count from Redis or database."""
    try:
        redis = get_redis()
        if redis:
            count = await redis.get(f"clicks:{short_code}")
            if count:
                return int(count)
    except Exception:
        logger.exception("Redis click count lookup failed for %s", short_code)

    # Fallback to database query
    from app.models.url import ShortURL
    url = await ShortURL.find_one({"short_code": short_code})
    return url.clicks if url else 0

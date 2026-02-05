import csv
import io
from collections import Counter
from datetime import UTC, datetime, timedelta

from app.core.database import get_redis
from app.models.click import ClickLog
from app.models.url import ShortURL
from app.schemas.url import URLStats


async def get_url_stats(
    short_code: str,
    date_from: datetime | None = None,
    date_to: datetime | None = None,
) -> URLStats | None:
    """Get comprehensive statistics for a shortened URL.

    Args:
        short_code: The short code to get stats for.
        date_from: Optional start date to filter clicks (inclusive).
        date_to: Optional end date to filter clicks (inclusive, end of day).
    """
    # Find the URL
    short_url = await ShortURL.find_one({"short_code": short_code})
    if not short_url:
        return None

    short_url_id = str(short_url.id)
    now = datetime.now(UTC)
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    week_start = today_start - timedelta(days=7)

    # Build query with optional date range filter
    query = {"short_url_id": short_url_id}
    if date_from or date_to:
        timestamp_filter = {}
        if date_from:
            timestamp_filter["$gte"] = date_from
        if date_to:
            # Include the entire end day
            end_of_day = date_to.replace(hour=23, minute=59, second=59, microsecond=999999)
            timestamp_filter["$lte"] = end_of_day
        query["timestamp"] = timestamp_filter

    # Get click logs (filtered by date range if provided)
    all_clicks = await ClickLog.find(query).to_list()

    # Calculate click counts
    total_clicks = len(all_clicks)
    clicks_today = sum(1 for c in all_clicks if c.timestamp >= today_start)
    clicks_this_week = sum(1 for c in all_clicks if c.timestamp >= week_start)

    # Calculate top referrers
    referrers = [c.referrer for c in all_clicks if c.referrer]
    referrer_counts = Counter(referrers)
    top_referrers = [
        {"referrer": ref or "Direct", "count": count}
        for ref, count in referrer_counts.most_common(10)
    ]

    # Add "Direct" for clicks without referrer
    direct_count = sum(1 for c in all_clicks if not c.referrer)
    if direct_count > 0:
        top_referrers.append({"referrer": "Direct", "count": direct_count})
        top_referrers.sort(key=lambda x: x["count"], reverse=True)
        top_referrers = top_referrers[:10]

    # Calculate clicks by country
    countries = [c.country for c in all_clicks if c.country]
    country_counts = Counter(countries)
    clicks_by_country = [
        {"country": country or "Unknown", "count": count}
        for country, count in country_counts.most_common(10)
    ]

    # Calculate clicks by device
    devices = [c.device_type for c in all_clicks if c.device_type]
    device_counts = Counter(devices)
    clicks_by_device = [
        {"device": device, "count": count} for device, count in device_counts.most_common()
    ]

    # Calculate clicks over time — use custom range or default last 30 days
    range_start = date_from if date_from else (now - timedelta(days=30))
    range_end = date_to if date_to else now
    daily_clicks = {}

    for click in all_clicks:
        if click.timestamp >= range_start:
            date_key = click.timestamp.strftime("%Y-%m-%d")
            daily_clicks[date_key] = daily_clicks.get(date_key, 0) + 1

    # Fill in missing days with zeros
    clicks_over_time = []
    current_date = range_start
    while current_date <= range_end:
        date_key = current_date.strftime("%Y-%m-%d")
        clicks_over_time.append({"date": date_key, "count": daily_clicks.get(date_key, 0)})
        current_date += timedelta(days=1)

    return URLStats(
        short_code=short_code,
        original_url=short_url.original_url,
        total_clicks=total_clicks,
        clicks_today=clicks_today,
        clicks_this_week=clicks_this_week,
        top_referrers=top_referrers,
        clicks_by_country=clicks_by_country,
        clicks_by_device=clicks_by_device,
        clicks_over_time=clicks_over_time,
    )


async def get_real_time_clicks(short_code: str) -> int:
    """Get real-time click count from Redis."""
    try:
        redis = get_redis()
        if redis:
            count = await redis.get(f"clicks:{short_code}")
            if count:
                return int(count)
    except Exception:
        pass

    # Fallback to database
    short_url = await ShortURL.find_one({"short_code": short_code})
    return short_url.clicks if short_url else 0


async def get_top_urls(limit: int = 10) -> list[dict]:
    """Get top URLs by click count (admin function)."""
    # Use aggregation to get top URLs with user info
    pipeline = [
        {"$match": {"is_active": True}},
        {"$sort": {"clicks": -1}},
        {"$limit": limit},
        {
            "$lookup": {
                "from": "users",
                "localField": "user.$id",
                "foreignField": "_id",
                "as": "user_info",
            }
        },
        {
            "$project": {
                "short_code": 1,
                "original_url": 1,
                "clicks": 1,
                "created_at": 1,
                "user_email": {"$arrayElemAt": ["$user_info.email", 0]},
            }
        },
    ]

    results = await ShortURL.aggregate(pipeline).to_list()

    return [
        {
            "id": str(r["_id"]),
            "short_code": r["short_code"],
            "original_url": r["original_url"],
            "clicks": r["clicks"],
            "user_email": r.get("user_email", "Unknown"),
        }
        for r in results
    ]


async def get_browser_stats(short_code: str) -> list[dict]:
    """Get browser breakdown for a URL."""
    short_url = await ShortURL.find_one({"short_code": short_code})
    if not short_url:
        return []

    clicks = await ClickLog.find({"short_url_id": str(short_url.id)}).to_list()
    browsers = [c.browser for c in clicks if c.browser]
    browser_counts = Counter(browsers)

    return [{"browser": browser, "count": count} for browser, count in browser_counts.most_common()]


async def get_os_stats(short_code: str) -> list[dict]:
    """Get OS breakdown for a URL."""
    short_url = await ShortURL.find_one({"short_code": short_code})
    if not short_url:
        return []

    clicks = await ClickLog.find({"short_url_id": str(short_url.id)}).to_list()
    os_list = [c.os for c in clicks if c.os]
    os_counts = Counter(os_list)

    return [{"os": os_name, "count": count} for os_name, count in os_counts.most_common()]


async def export_clicks_csv(
    short_code: str,
    date_from: datetime | None = None,
    date_to: datetime | None = None,
) -> str | None:
    """Export click logs for a URL as CSV string.

    Returns CSV content as a string, or None if the URL doesn't exist.
    """
    short_url = await ShortURL.find_one({"short_code": short_code})
    if not short_url:
        return None

    short_url_id = str(short_url.id)

    # Build query with optional date range
    query = {"short_url_id": short_url_id}
    if date_from or date_to:
        timestamp_filter = {}
        if date_from:
            timestamp_filter["$gte"] = date_from
        if date_to:
            end_of_day = date_to.replace(hour=23, minute=59, second=59, microsecond=999999)
            timestamp_filter["$lte"] = end_of_day
        query["timestamp"] = timestamp_filter

    clicks = await ClickLog.find(query).to_list()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow([
        "timestamp", "referrer", "browser", "os", "device_type", "country", "city"
    ])

    for click in clicks:
        writer.writerow([
            click.timestamp.isoformat() if click.timestamp else "",
            click.referrer or "",
            click.browser or "",
            click.os or "",
            click.device_type or "",
            click.country or "",
            click.city or "",
        ])

    return output.getvalue()

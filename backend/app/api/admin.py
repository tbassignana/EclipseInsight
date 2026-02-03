from datetime import UTC

from fastapi import APIRouter, Depends, HTTPException, status

from app.core.security import get_current_active_admin
from app.models.user import User
from app.services.analytics import get_top_urls
from app.services.url import delete_short_url, get_short_url_by_code

router = APIRouter(
    prefix="/admin",
    tags=["Admin"],
    responses={403: {"description": "Admin access required"}},
)


@router.get("/top-urls")
async def get_top_urls_list(
    limit: int = 10, current_admin: User = Depends(get_current_active_admin)
):
    """
    Get top-performing URLs by click count.

    View the most clicked shortened URLs across the EclipseInsight platform,
    including their AI-generated tags and content analysis status.

    - **limit**: Maximum URLs to return (1-100, default: 10)
    """
    if limit > 100:
        limit = 100

    top_urls = await get_top_urls(limit=limit)
    return {"urls": top_urls, "count": len(top_urls)}


@router.delete("/urls/{short_code}")
async def admin_delete_url(
    short_code: str, current_admin: User = Depends(get_current_active_admin)
):
    """
    Remove a shortened URL from the platform.

    Admins can delete any URL, including those flagged by AI toxicity detection
    or reported by users. This is a soft delete that deactivates the short link.

    - **short_code**: The unique identifier of the URL to delete
    """
    short_url = await get_short_url_by_code(short_code)

    if not short_url:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="URL not found")

    success = await delete_short_url(short_code, current_admin)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to delete URL"
        )

    return {"message": "URL deleted successfully", "short_code": short_code}


@router.get("/stats/summary")
async def get_admin_summary(current_admin: User = Depends(get_current_active_admin)):
    """
    Get EclipseInsight platform overview statistics.

    Returns comprehensive metrics including total URLs created, click counts,
    user registrations, and activity trends for today and the past week.
    Useful for monitoring platform health and growth.
    """
    from datetime import datetime, timedelta

    from app.models.click import ClickLog
    from app.models.url import ShortURL
    from app.models.user import User as UserModel

    now = datetime.now(UTC)
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    week_start = today_start - timedelta(days=7)

    # Get counts
    total_urls = await ShortURL.count()
    total_clicks = await ClickLog.count()
    total_users = await UserModel.count()

    # Get today's activity
    urls_today = await ShortURL.find({"created_at": {"$gte": today_start}}).count()
    clicks_today = await ClickLog.find({"timestamp": {"$gte": today_start}}).count()

    # Get this week's activity
    urls_this_week = await ShortURL.find({"created_at": {"$gte": week_start}}).count()
    clicks_this_week = await ClickLog.find({"timestamp": {"$gte": week_start}}).count()

    return {
        "total_urls": total_urls,
        "total_clicks": total_clicks,
        "total_users": total_users,
        "urls_today": urls_today,
        "clicks_today": clicks_today,
        "urls_this_week": urls_this_week,
        "clicks_this_week": clicks_this_week,
    }

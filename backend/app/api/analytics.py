from fastapi import APIRouter, HTTPException, status, Depends

from app.core.security import get_current_user, get_current_active_admin
from app.schemas.url import URLStats
from app.services.analytics import (
    get_url_stats,
    get_real_time_clicks,
    get_top_urls,
    get_browser_stats,
    get_os_stats
)
from app.services.url import get_short_url_by_code
from app.models.user import User

router = APIRouter(
    prefix="/stats",
    tags=["Analytics"],
    responses={404: {"description": "URL not found"}},
)


@router.get("/{short_code}", response_model=URLStats)
async def get_url_statistics(
    short_code: str,
    current_user: User = Depends(get_current_user)
):
    """
    Get comprehensive analytics for a shortened URL.

    Returns detailed insights including:
    - Total click counts and trends
    - Referrer sources analysis
    - Device and browser breakdown
    - Geographic distribution
    - Time series click data for visualization
    """
    # Verify the URL exists and user has access
    short_url = await get_short_url_by_code(short_code)

    if not short_url:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="URL not found"
        )

    # Check ownership (unless admin)
    if not current_user.is_admin:
        user_ref = short_url.user
        user_id = user_ref.ref.id if hasattr(user_ref, 'ref') else getattr(user_ref, 'id', None)
        if user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to view these stats"
            )

    stats = await get_url_stats(short_code)
    if not stats:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Statistics not found"
        )

    return stats


@router.get("/{short_code}/realtime")
async def get_realtime_clicks(
    short_code: str,
    current_user: User = Depends(get_current_user)
):
    """
    Get real-time click count for live dashboard updates.

    Uses Redis cache for sub-millisecond response times.
    Ideal for dashboard polling and live analytics displays.
    """
    short_url = await get_short_url_by_code(short_code)

    if not short_url:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="URL not found"
        )

    # Check ownership
    if not current_user.is_admin:
        user_ref = short_url.user
        user_id = user_ref.ref.id if hasattr(user_ref, 'ref') else getattr(user_ref, 'id', None)
        if user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized"
            )

    clicks = await get_real_time_clicks(short_code)
    return {"short_code": short_code, "clicks": clicks}


@router.get("/{short_code}/browsers")
async def get_browser_breakdown(
    short_code: str,
    current_user: User = Depends(get_current_user)
):
    """
    Get browser usage breakdown for URL clicks.

    Returns distribution of clicks across different browsers
    (Chrome, Firefox, Safari, Edge, etc.) for audience analysis.
    """
    short_url = await get_short_url_by_code(short_code)

    if not short_url:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="URL not found"
        )

    if not current_user.is_admin:
        user_ref = short_url.user
        user_id = user_ref.ref.id if hasattr(user_ref, 'ref') else getattr(user_ref, 'id', None)
        if user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized"
            )

    browsers = await get_browser_stats(short_code)
    return {"short_code": short_code, "browsers": browsers}


@router.get("/{short_code}/os")
async def get_os_breakdown(
    short_code: str,
    current_user: User = Depends(get_current_user)
):
    """
    Get operating system breakdown for URL clicks.

    Returns distribution of clicks across different operating systems
    (Windows, macOS, iOS, Android, Linux) for audience insights.
    """
    short_url = await get_short_url_by_code(short_code)

    if not short_url:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="URL not found"
        )

    if not current_user.is_admin:
        user_ref = short_url.user
        user_id = user_ref.ref.id if hasattr(user_ref, 'ref') else getattr(user_ref, 'id', None)
        if user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized"
            )

    os_stats = await get_os_stats(short_code)
    return {"short_code": short_code, "operating_systems": os_stats}

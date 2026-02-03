import logging
from datetime import datetime, timezone
from fastapi import APIRouter, HTTPException, status, Request
from fastapi.responses import RedirectResponse, Response

from app.services.url import get_short_url_by_code
from app.services.click import log_click
from app.services.preview import preview_service

logger = logging.getLogger(__name__)

router = APIRouter(
    tags=["Redirect"],
    responses={
        404: {"description": "Short URL not found"},
        410: {"description": "URL has expired or been deactivated"}
    },
)


def is_expired(expiration: datetime | None) -> bool:
    """Check if a datetime has expired, handling both naive and aware datetimes."""
    if not expiration:
        return False
    now = datetime.now(timezone.utc)
    # If expiration is naive, treat it as UTC
    if expiration.tzinfo is None:
        expiration = expiration.replace(tzinfo=timezone.utc)
    return now > expiration


@router.get("/{short_code}")
async def redirect_to_url(short_code: str, request: Request):
    """
    Redirect to the original URL and log analytics.

    Uses 302 redirect (not 301) to ensure every click is tracked.
    Captures IP, user agent, and referrer for analytics insights.
    """
    short_url = await get_short_url_by_code(short_code)

    if not short_url:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="URL not found"
        )

    if not short_url.is_active:
        raise HTTPException(
            status_code=status.HTTP_410_GONE,
            detail="URL has been deactivated"
        )

    # Check expiration
    if is_expired(short_url.expiration):
        raise HTTPException(
            status_code=status.HTTP_410_GONE,
            detail="URL has expired"
        )

    # Log the click asynchronously (fire and forget pattern)
    client_ip = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent")
    referrer = request.headers.get("referer")

    try:
        await log_click(
            short_url=short_url,
            ip_address=client_ip,
            user_agent=user_agent,
            referrer=referrer
        )
    except Exception:
        logger.exception("Click logging failed for %s", short_code)

    # 302 redirect (not 301) to ensure we always track clicks
    return RedirectResponse(
        url=short_url.original_url,
        status_code=status.HTTP_302_FOUND
    )


@router.get("/{short_code}/preview")
async def get_url_preview_page(short_code: str):
    """
    Get URL preview with AI-generated metadata.

    Returns Open Graph data, AI-generated tags, and content summary
    without redirecting. Ideal for preview cards and link tooltips.
    """
    short_url = await get_short_url_by_code(short_code)

    if not short_url or not short_url.is_active:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="URL not found"
        )

    # Check expiration
    if is_expired(short_url.expiration):
        raise HTTPException(
            status_code=status.HTTP_410_GONE,
            detail="URL has expired"
        )

    return {
        "original_url": short_url.original_url,
        "title": short_url.preview_title,
        "description": short_url.preview_description,
        "image": short_url.preview_image,
        "tags": short_url.tags,
        "summary": short_url.summary
    }


@router.get("/{short_code}/screenshot")
async def get_url_screenshot(short_code: str):
    """
    Get a visual preview screenshot of the destination page.

    Returns a PNG screenshot if cached, or generates one on-demand.
    Screenshots are stored in GridFS for efficient retrieval.
    """
    short_url = await get_short_url_by_code(short_code)

    if not short_url or not short_url.is_active:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="URL not found"
        )

    # Check expiration
    if is_expired(short_url.expiration):
        raise HTTPException(
            status_code=status.HTTP_410_GONE,
            detail="URL has expired"
        )

    # Try to get existing screenshot
    if short_url.preview_screenshot_id:
        screenshot_data = await preview_service.get_screenshot(
            short_url.preview_screenshot_id
        )
        if screenshot_data:
            return Response(
                content=screenshot_data,
                media_type="image/png",
                headers={
                    "Cache-Control": "public, max-age=86400",
                    "Content-Disposition": f"inline; filename=preview_{short_code}.png"
                }
            )

    # Generate new screenshot if none exists
    screenshot_data = await preview_service.generate_screenshot(
        short_url.original_url
    )

    if screenshot_data is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Screenshot service unavailable"
        )

    # Store for future use
    file_id = await preview_service.store_screenshot(
        screenshot_data,
        short_code,
        short_url.original_url
    )

    if file_id:
        # Update the ShortURL with the screenshot ID
        short_url.preview_screenshot_id = file_id
        await short_url.save()

    return Response(
        content=screenshot_data,
        media_type="image/png",
        headers={
            "Cache-Control": "public, max-age=86400",
            "Content-Disposition": f"inline; filename=preview_{short_code}.png"
        }
    )

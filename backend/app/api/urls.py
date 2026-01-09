from fastapi import APIRouter, HTTPException, status, Depends, Request
from slowapi import Limiter
from slowapi.util import get_remote_address

from app.core.config import settings
from app.core.security import get_current_user
from app.schemas.url import URLCreate, URLResponse, URLPreview, URLStats, AIAnalysis
from app.services.url import (
    create_short_url,
    get_short_url_by_code,
    get_user_urls,
    delete_short_url,
    fetch_url_preview as fetch_preview_service,
    get_url_stats
)
from app.models.user import User
from app.models.url import ShortURL

router = APIRouter(
    prefix="/urls",
    tags=["URLs"],
    responses={404: {"description": "URL not found"}},
)
limiter = Limiter(key_func=get_remote_address)


def build_url_response(short_url: ShortURL) -> URLResponse:
    """Build a URLResponse with AI analysis data."""
    ai = None
    if short_url.ai_analyzed or short_url.tags or short_url.summary:
        ai = AIAnalysis(
            tags=short_url.tags,
            summary=short_url.summary,
            suggested_alias=short_url.suggested_alias,
            is_toxic=short_url.is_toxic,
            analyzed=short_url.ai_analyzed,
            analyzed_at=short_url.ai_analyzed_at
        )

    return URLResponse(
        id=str(short_url.id),
        original_url=short_url.original_url,
        short_code=short_url.short_code,
        short_url=f"{settings.BASE_URL}/{short_url.short_code}",
        clicks=short_url.clicks,
        expiration=short_url.expiration,
        created_at=short_url.created_at,
        preview_title=short_url.preview_title,
        preview_description=short_url.preview_description,
        preview_image=short_url.preview_image,
        ai=ai
    )


@router.post("/shorten", response_model=URLResponse, status_code=status.HTTP_201_CREATED)
@limiter.limit(settings.RATE_LIMIT_SHORTEN)
async def shorten_url(
    request: Request,
    url_data: URLCreate,
    current_user: User = Depends(get_current_user)
):
    """
    Create a shortened URL with AI-powered content analysis.

    - **original_url**: The URL to shorten
    - **custom_alias**: Optional custom alias (4-20 chars, alphanumeric, dash, underscore)
    - **expiration_days**: Optional days until expiration (1-365)
    - **skip_ai_analysis**: Skip AI analysis (default: false)
    - **use_ai_suggested_alias**: Use AI-suggested alias as short code

    AI Analysis (when enabled):
    - Generates 5 relevant tags
    - Creates a 1-sentence summary
    - Suggests a memorable alias
    - Detects potentially harmful content (rejected if toxic)
    """
    try:
        short_url = await create_short_url(url_data, current_user)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

    return build_url_response(short_url)


@router.get("", response_model=list[URLResponse])
async def list_user_urls(
    current_user: User = Depends(get_current_user),
    skip: int = 0,
    limit: int = 100
):
    """
    List all URLs created by the current user.
    """
    urls = await get_user_urls(current_user, skip=skip, limit=limit)
    return [build_url_response(url) for url in urls]


@router.get("/preview", response_model=URLPreview)
async def get_url_preview(url: str):
    """
    Fetch preview metadata for a URL (Open Graph data).
    """
    preview = await fetch_preview_service(url)
    return preview


@router.get("/{short_code}/stats", response_model=URLStats)
async def get_url_statistics(
    short_code: str,
    current_user: User = Depends(get_current_user)
):
    """
    Get detailed statistics for a shortened URL.
    """
    short_url = await get_short_url_by_code(short_code)

    if not short_url or not short_url.is_active:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="URL not found"
        )

    # Verify ownership (unless admin)
    if not current_user.is_admin:
        # Get user ID from the Link reference
        user_ref = short_url.user
        user_id = user_ref.ref.id if hasattr(user_ref, 'ref') else getattr(user_ref, 'id', None)
        if user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to access this URL"
            )

    return await get_url_stats(short_url)


@router.get("/{short_code}", response_model=URLResponse)
async def get_url_details(
    short_code: str,
    current_user: User = Depends(get_current_user)
):
    """
    Get details of a specific shortened URL.
    """
    short_url = await get_short_url_by_code(short_code)

    if not short_url or not short_url.is_active:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="URL not found"
        )

    # Verify ownership (unless admin)
    if not current_user.is_admin:
        # Get user ID from the Link reference
        user_ref = short_url.user
        user_id = user_ref.ref.id if hasattr(user_ref, 'ref') else getattr(user_ref, 'id', None)
        if user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to access this URL"
            )

    return build_url_response(short_url)


@router.delete("/{short_code}", status_code=status.HTTP_200_OK)
async def delete_url(
    short_code: str,
    current_user: User = Depends(get_current_user)
):
    """
    Delete a shortened URL (soft delete).
    """
    success = await delete_short_url(short_code, current_user)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="URL not found or not authorized"
        )

    return {"message": "URL deleted successfully"}

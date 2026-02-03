from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, Request, status
from slowapi import Limiter
from slowapi.util import get_remote_address

from app.core.config import settings
from app.core.security import create_access_token, get_current_user
from app.models.user import User
from app.schemas.user import (
    ForgotPasswordRequest,
    ResetPasswordRequest,
    Token,
    UserCreate,
    UserLogin,
    UserResponse,
)
from app.services.auth import (
    authenticate_user,
    create_password_reset_token,
    create_user,
    get_user_by_email,
    reset_password,
)

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
    responses={401: {"description": "Invalid credentials"}},
)
limiter = Limiter(key_func=get_remote_address)


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
@limiter.limit(settings.RATE_LIMIT_REGISTER)
async def register(request: Request, user_data: UserCreate):
    """
    Register a new EclipseInsight account.

    Create an account to access AI-powered URL shortening with content analysis,
    auto-tagging, summaries, and toxicity detection.

    - **email**: Valid email address (unique)
    - **password**: Minimum 8 characters
    """
    # Check if email already exists
    existing_user = await get_user_by_email(user_data.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered"
        )

    # Create new user
    user = await create_user(user_data)

    return UserResponse(
        id=str(user.id),
        email=user.email,
        is_active=user.is_active,
        is_admin=user.is_admin,
        created_at=user.created_at,
    )


@router.post("/login", response_model=Token)
async def login(user_data: UserLogin):
    """
    Authenticate and receive a Bearer token for EclipseInsight API access.

    Use the returned token in the Authorization header for all protected endpoints:
    `Authorization: Bearer <token>`

    - **email**: Registered email address
    - **password**: Account password
    """
    user = await authenticate_user(user_data.email, user_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Inactive user account")

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email, "user_id": str(user.id)}, expires_delta=access_token_expires
    )

    return Token(access_token=access_token, token_type="bearer")


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """
    Get the current authenticated user's profile.

    Returns account details including admin status for accessing
    EclipseInsight's advanced analytics and management features.
    """
    return UserResponse(
        id=str(current_user.id),
        email=current_user.email,
        is_active=current_user.is_active,
        is_admin=current_user.is_admin,
        created_at=current_user.created_at,
    )


@router.post("/forgot-password")
async def forgot_password(request: Request, data: ForgotPasswordRequest):
    """
    Request a password reset token.

    If the email exists, a reset token is generated and logged to the server console.
    The response is always the same to avoid revealing whether the email is registered.
    """
    await create_password_reset_token(data.email)
    return {
        "message": "If an account with that email exists, a reset token has been generated. Check server logs."
    }


@router.post("/reset-password")
async def reset_password_endpoint(data: ResetPasswordRequest):
    """
    Reset password using a valid reset token.

    - **token**: The reset token from the forgot-password step
    - **new_password**: New password (minimum 8 characters)
    """
    success = await reset_password(data.token, data.new_password)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid or expired reset token"
        )
    return {"message": "Password has been reset successfully"}
